#!/usr/bin/env python3
"""Bounded, read-only ZTO-first ERC-20 allowance audits; standard library only."""

import argparse
import datetime
import json
import math
import multiprocessing
from pathlib import Path
import re
import sys
import urllib.request

TOKENS = {
    'ZTO': '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e',
    'IMD': '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7',
}
PUBLIC_RPC = 'https://ethereum-rpc.publicnode.com'
PUBLIC_ENDPOINTS = {PUBLIC_RPC, 'https://eth.drpc.org'}
ASSIGNMENT_RPC = 'http://127.0.0.1:43135/rpc/1'
ENDPOINTS = PUBLIC_ENDPOINTS | {ASSIGNMENT_RPC}
APPROVAL = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'
MAX_UINT = (1 << 256) - 1
MAX_BLOCKS, MAX_LOGS, MAX_PAIRS = 2000, 128, 64
SCHEMA = 'allowance-lens-observation-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def address(value):
    require(isinstance(value, str) and re.fullmatch(r'0x[0-9a-fA-F]{40}', value),
            'expected a 20-byte address')
    require(int(value, 16) != 0, 'zero address is not an owner or spender')
    return value.lower()


def hexdata(value, size):
    require(isinstance(value, str) and re.fullmatch(r'0x[0-9a-fA-F]{' + str(size * 2) + '}', value),
            'invalid fixed-width hex data')
    return value.lower()


def quantity(value):
    require(isinstance(value, str) and re.fullmatch(r'0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)', value),
            'invalid RPC quantity')
    return int(value, 16)


def word(value):
    return int(hexdata(value, 32), 16)


def address_arg(value):
    return address(value)[2:].rjust(64, '0')


def topic_address(value):
    value = hexdata(value, 32)
    require(value[2:26] == '0' * 24, 'noncanonical address topic')
    return address('0x' + value[-40:])


def units(value, decimals):
    if decimals == 0:
        return str(value)
    whole, part = divmod(value, 10 ** decimals)
    return (str(whole) + '.' + str(part).zfill(decimals)).rstrip('0').rstrip('.')


def workspace_path(value):
    path = Path(value).resolve()
    require(path.is_relative_to(Path.cwd().resolve()), 'files must be inside the current workspace')
    return path


def header(value):
    require(isinstance(value, dict), 'block unavailable')
    quantity(value['number'])
    quantity(value['timestamp'])
    hexdata(value['hash'], 32)
    return {key: value[key] for key in ('number', 'hash', 'timestamp')}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('RPC redirects are not accepted')


class RPC:
    METHODS = {'eth_chainId', 'eth_getBlockByNumber', 'eth_getLogs', 'eth_call'}

    def __init__(self, endpoint):
        require(endpoint in ENDPOINTS, 'use a documented public RPC or the assignment endpoint')
        self.endpoint = endpoint
        self.counter = 0
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def call(self, method, params):
        require(method in self.METHODS, 'RPC method is not read-only allowlisted')
        self.counter += 1
        req = urllib.request.Request(self.endpoint, data=json.dumps({
            'jsonrpc': '2.0', 'id': self.counter, 'method': method, 'params': params,
        }).encode(), headers={'Content-Type': 'application/json',
                              'User-Agent': 'Pepeolithic-AllowanceLens/1.0'})
        with self.opener.open(req, timeout=25) as response:
            data = response.read(1_000_001)
        require(len(data) <= 1_000_000, 'RPC response exceeds byte limit')
        result = json.loads(data)
        require(isinstance(result, dict) and result.get('jsonrpc') == '2.0'
                and type(result.get('id')) is int and result['id'] == self.counter,
                'RPC response envelope mismatch')
        require('error' not in result, 'RPC error: ' + json.dumps(result.get('error')))
        require('result' in result, 'RPC response missing result')
        return result['result']


def _bounded_worker(connection, function, args, kwargs):
    """Only the parent writes deliverables; a terminated read leaves no partial file."""
    try:
        connection.send((True, function(*args, **kwargs)))
    except Exception as exc:
        connection.send((False, str(exc)))
    finally:
        connection.close()


def run_bounded(function, args=(), kwargs=None, timeout=90):
    """Bound an entire live read, including DNS and slow response bodies.

    A separate process is required: urllib socket timeouts alone do not bound
    multiple requests, DNS, or a server slowly streaming its response.
    Callers must use the usual __main__ guard when using this from scripts.
    """
    require(type(timeout) in (int, float) and math.isfinite(timeout)
            and 0 < timeout <= 600, 'timeout must be finite and in (0, 600] seconds')
    context = multiprocessing.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_bounded_worker,
                              args=(sender, function, args, kwargs or {}))
    try:
        process.start()
        sender.close()
        if not receiver.poll(timeout):
            raise TimeoutError('live read exceeded total deadline of ' + str(timeout) + ' seconds')
        try:
            ok, result = receiver.recv()
        except EOFError as exc:
            raise ValueError('live read worker exited without a result') from exc
        require(ok, result if not ok else '')
        return result
    finally:
        receiver.close()
        sender.close()
        if process.pid is not None:
            process.join(0.1)
            if process.is_alive():
                process.terminate()
                process.join(0.5)
            if process.is_alive():
                process.kill()
                process.join(0.5)
            process.close()


def capture_endpoint(endpoint, *args):
    return capture(RPC(endpoint), *args)


def decode_logs(logs, token, start, end, owner=None):
    require(isinstance(logs, list) and len(logs) <= MAX_LOGS, 'too many logs; narrow the window')
    pairs, seen, decoded = set(), set(), []
    for log in logs:
        require(isinstance(log, dict) and log.get('removed') is False, 'removed or malformed log')
        require(address(log['address']) == token, 'log belongs to a different token')
        topics = log['topics']
        require(isinstance(topics, list) and len(topics) == 3
                and topics[0] == APPROVAL, 'not a canonical ERC-20 Approval event')
        pair = (topic_address(topics[1]), topic_address(topics[2]))
        require(owner is None or pair[0] == owner, 'log owner does not match filter')
        number = quantity(log['blockNumber'])
        require(start <= number <= end, 'log outside requested block window')
        block_hash = hexdata(log['blockHash'], 32)
        hexdata(log['transactionHash'], 32)
        tx_index, index = quantity(log['transactionIndex']), quantity(log['logIndex'])
        identity = (number, index)
        require(identity not in seen, 'duplicate log position')
        seen.add(identity)
        pairs.add(pair)
        decoded.append((number, tx_index, index, pair, word(log['data']), block_hash))
    require(len(pairs) <= MAX_PAIRS, 'too many pairs; narrow the window')
    return sorted(pairs), sorted(decoded)


def capture(rpc, token_name='ZTO', block_tag='finalized', window=1500, owner=None, spenders=()):
    require(token_name in TOKENS, 'unsupported token')
    require(type(window) is int and 1 <= window <= MAX_BLOCKS, 'window must be 1..2000 blocks')
    owner = address(owner) if owner is not None else None
    spenders = sorted({address(s) for s in spenders})
    require(not spenders or owner is not None, 'explicit spenders require an owner')
    require(len(spenders) <= MAX_PAIRS, 'too many spenders')
    require(block_tag in ('finalized', 'safe', 'latest') or
            (isinstance(block_tag, str) and re.fullmatch(r'0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)', block_tag)),
            'invalid block selector')
    require(rpc.call('eth_chainId', []) == '0x1', 'expected Ethereum chain 1')
    block = header(rpc.call('eth_getBlockByNumber', [block_tag, False]))
    end = quantity(block['number'])
    if block_tag.startswith('0x'):
        require(end == quantity(block_tag), 'RPC returned a different block than requested')
    start = max(0, end - window + 1)
    token, logs, log_headers = TOKENS[token_name], [], {}
    pin = {'blockHash': block['hash'], 'requireCanonical': True}
    if spenders:
        pairs = [(owner, spender) for spender in spenders]
        mode = 'explicit_pairs'
    else:
        mode = 'approval_window'
        topics = [APPROVAL] + (['0x' + address_arg(owner)] if owner else [])
        for first in range(start, end + 1, 250):
            chunk = rpc.call('eth_getLogs', [{'address': token, 'topics': topics,
                            'fromBlock': hex(first), 'toBlock': hex(min(first + 249, end))}])
            decode_logs(chunk, token, first, min(first + 249, end), owner)
            logs.extend(chunk)
            require(len(logs) <= MAX_LOGS, 'too many logs; narrow the window')
        pairs, decoded = decode_logs(logs, token, start, end, owner)
        for number, _, _, _, _, block_hash in decoded:
            key = hex(number)
            if key not in log_headers:
                log_headers[key] = header(rpc.call('eth_getBlockByNumber', [key, False]))
            require(log_headers[key]['number'] == key and log_headers[key]['hash'] == block_hash,
                    'Approval event is not in its canonical block')

    def call(data):
        return rpc.call('eth_call', [{'to': token, 'data': data}, pin])

    raw = {'decimals': call('0x313ce567'), 'balances': [], 'allowances': []}
    for account in sorted({pair[0] for pair in pairs}):
        data = '0x70a08231' + address_arg(account)
        raw['balances'].append({'owner': account, 'data': data, 'result': call(data)})
    for account, spender in pairs:
        data = '0xdd62ed3e' + address_arg(account) + address_arg(spender)
        raw['allowances'].append({'owner': account, 'spender': spender, 'data': data, 'result': call(data)})
    after = header(rpc.call('eth_getBlockByNumber', [block['number'], False]))
    require(after == block, 'block changed during capture; discard and retry')
    observation = {
        'schema': SCHEMA, 'source': PUBLIC_RPC if rpc.endpoint.startswith('http:') else rpc.endpoint,
        'chain_id': 1, 'token': token_name, 'token_address': token, 'block': block,
        'query': {'mode': mode, 'from_block': start, 'to_block': end,
                  'owner': owner, 'spenders': spenders},
        'logs': logs, 'log_headers': log_headers, 'raw': raw,
    }
    report(observation)
    return observation


def report(observation):
    require(isinstance(observation, dict) and observation['schema'] == SCHEMA,
            'unsupported observation schema')
    require(type(observation['chain_id']) is int and observation['chain_id'] == 1, 'wrong chain')
    name = observation['token']
    require(name in TOKENS and observation['token_address'] == TOKENS[name], 'wrong token')
    require(observation['source'] in PUBLIC_ENDPOINTS, 'invalid source')
    block = header(observation['block'])
    end = quantity(block['number'])
    query = observation['query']
    start = query['from_block']
    require(type(start) is int and 0 <= start <= end and end-start < MAX_BLOCKS
            and type(query['to_block']) is int and query['to_block'] == end, 'invalid observation window')
    owner = address(query['owner']) if query['owner'] is not None else None
    require(isinstance(query['spenders'], list), 'spenders must be a list')
    spenders = [address(s) for s in query['spenders']]
    require(len(set(spenders)) == len(spenders) <= MAX_PAIRS, 'duplicate or too many spenders')
    if query['mode'] == 'approval_window':
        require(not spenders, 'window mode cannot contain explicit spenders')
        pairs, decoded = decode_logs(observation['logs'], TOKENS[name], start, end, owner)
        expected_headers = {hex(item[0]) for item in decoded}
        require(set(observation['log_headers']) == expected_headers, 'log header set mismatch')
        for number, _, _, _, _, block_hash in decoded:
            h = header(observation['log_headers'][hex(number)])
            require(h['number'] == hex(number) and h['hash'] == block_hash, 'log block hash mismatch')
            if number == end:
                require(h == block, 'end block and log header disagree')
    else:
        require(query['mode'] == 'explicit_pairs' and owner is not None and spenders,
                'invalid explicit pair query')
        require(observation['logs'] == [] and observation['log_headers'] == {},
                'explicit query must not claim log discovery')
        pairs, decoded = sorted((owner, s) for s in spenders), []
    raw = observation['raw']
    decimals = word(raw['decimals'])
    require(decimals <= 36, 'token decimals above 36 are unsupported')
    balances = {}
    require(isinstance(raw['balances'], list) and len(raw['balances']) <= MAX_PAIRS,
            'invalid balance list')
    for item in raw['balances']:
        account = address(item['owner'])
        require(account not in balances and item['data'] == '0x70a08231' + address_arg(account),
                'duplicate balance or balance calldata mismatch')
        balances[account] = word(item['result'])
    require(set(balances) == {p[0] for p in pairs}, 'missing or extra owner balance')
    allowances = {}
    require(isinstance(raw['allowances'], list) and len(raw['allowances']) <= MAX_PAIRS,
            'invalid allowance list')
    for item in raw['allowances']:
        pair = (address(item['owner']), address(item['spender']))
        require(pair not in allowances and item['data'] == '0xdd62ed3e' + ''.join(address_arg(a) for a in pair),
                'duplicate allowance or allowance calldata mismatch')
        allowances[pair] = word(item['result'])
    require(set(allowances) == set(pairs), 'missing or extra allowance result')
    latest = {item[3]: item for item in decoded}
    rows = []
    for pair in pairs:
        account, spender = pair
        amount, balance = allowances[pair], balances[account]
        event = latest.get(pair)
        rows.append({
            'owner': account, 'spender': spender,
            'allowance_raw': str(amount), 'allowance': units(amount, decimals),
            'balance_raw': str(balance), 'balance': units(balance, decimals),
            'spendable_upper_bound_raw': str(min(amount, balance)),
            'spendable_upper_bound': units(min(amount, balance), decimals),
            'max_uint256': amount == MAX_UINT,
            'status': 'no_current_allowance' if amount == 0 else
                      'active_zero_balance' if balance == 0 else 'active_with_balance',
            'last_observed_approval': None if event is None else {
                'block_number': event[0], 'log_index': event[2], 'amount_raw': str(event[4]),
                'differs_from_current_allowance': event[4] != amount,
            },
        })
    owners = []
    for account, balance in sorted(balances.items()):
        cap = min(balance, sum(v for (a, _), v in allowances.items() if a == account))
        owners.append({'owner': account, 'balance_raw': str(balance),
                       'combined_spendable_upper_bound_raw': str(cap),
                       'combined_spendable_upper_bound': units(cap, decimals)})
    return {
        'schema': 'allowance-lens-report-v1', 'chain_id': 1, 'token': name,
        'token_address': TOKENS[name], 'decimals': decimals,
        'block_number': end, 'block_hash': block['hash'],
        'block_time_utc': datetime.datetime.fromtimestamp(quantity(block['timestamp']),
                            datetime.timezone.utc).isoformat(),
        'source': observation['source'], 'discovery': query,
        'complete_wallet_audit': False,
        'pair_count': len(rows), 'approval_event_count': len(decoded),
        'active_pair_count': sum(row['allowance_raw'] != '0' for row in rows),
        'pairs': rows, 'owners': owners,
        'limitations': [
            'Only the listed pairs are checked. A bounded event window can miss older approvals.',
            'Zero balance does not revoke permission; future receipts may become spendable.',
            'Upper bounds assume standard ERC-20 semantics; transfers may fail or have other restrictions.',
            'Per-spender bounds overlap. Owner totals cap their sum at the same owner balance.',
            'Permit2 sub-permissions, unused signatures, other tokens and chains are not inspected.',
            'RPC responses are trusted, not cryptographic proofs; saved observations are historical.',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--live', action='store_true', help='read Ethereum; no transactions')
    source.add_argument('--snapshot', help='replay a workspace observation JSON')
    parser.add_argument('--rpc', default=PUBLIC_RPC, choices=sorted(ENDPOINTS))
    parser.add_argument('--token', choices=sorted(TOKENS), default='ZTO')
    parser.add_argument('--block', default='finalized', help='finalized, safe, latest, or decimal number')
    parser.add_argument('--window', type=int, default=1500, help='discovery window, 1..2000 blocks')
    parser.add_argument('--owner', help='filter discovery, or owner for explicit spenders')
    parser.add_argument('--spender', action='append', default=[], help='explicit spender; repeat as needed')
    parser.add_argument('--save', help='save a live observation inside the workspace')
    parser.add_argument('--timeout', type=float, default=90,
                        help='total live-read deadline in seconds, 0 < timeout <= 600 (default 90)')
    args = parser.parse_args(argv)
    try:
        if args.live:
            tag = hex(int(args.block)) if args.block.isdecimal() else args.block
            observation = run_bounded(capture_endpoint,
                (args.rpc, args.token, tag, args.window, args.owner, args.spender), timeout=args.timeout)
        else:
            require(not args.save and not args.owner and not args.spender
                    and args.token == 'ZTO' and args.window == 1500 and args.block == 'finalized'
                    and args.rpc == PUBLIC_RPC and args.timeout == 90,
                    'query and save options require --live')
            path = workspace_path(args.snapshot or Path(__file__).with_name('observation.json'))
            with path.open('rb') as stream:
                data = stream.read(98_305)
            require(len(data) <= 98_304, 'observation exceeds 96 KiB')
            observation = json.loads(data)
        result = report(observation)
        if args.save:
            encoded = json.dumps(observation, indent=2) + '\n'
            require(len(encoded.encode()) <= 98_304, 'observation exceeds 96 KiB; narrow the query')
            # Refuse to overwrite any existing deliverable or follow a symlink.
            with workspace_path(args.save).open('x', encoding='utf-8') as stream:
                stream.write(encoded)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
