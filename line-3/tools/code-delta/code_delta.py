#!/usr/bin/env python3
"""Compare proof-backed historical Ethereum runtime and supported proxy paths."""
import argparse
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / 'code-ancestry'))
import code_ancestry as ancestry
sys.path.insert(0, str(TOOLS / 'code-opcodes'))
import code_opcodes as opcodes

proof = ancestry.proof
lens = proof.lens
require = lens.require
PREVIEW = 8


def instructions(code):
    """Linear decoding of all bytes, including data and compiler metadata."""
    require(isinstance(code, bytes) and len(code) <= lens.MAX_CODE,
            'invalid or oversized runtime')
    result, pc = [], 0
    while pc < len(code):
        opcode = code[pc]
        width = opcode - 0x5f if 0x60 <= opcode <= 0x7f else 0
        end = min(len(code), pc + 1 + width)
        # Retain missing operand bytes: truncated PUSH is not the same as a full one.
        result.append((pc, end, code[pc:end], pc + 1 + width - end))
        pc = end
    return result


def signature(item):
    return item[2], item[3]


def describe(item):
    pc, end, raw, missing = item
    opcode = raw[0]
    label = (('PUSH' + str(opcode - 0x5f)) if 0x60 <= opcode <= 0x7f
             else 'PUSH0' if opcode == 0x5f
             else opcodes.INTERESTING.get(opcode, 'OP_0x%02x' % opcode))
    return {'pc': pc, 'end_pc_exclusive': end, 'opcode': label,
            'bytes': '0x' + raw.hex(), 'missing_push_bytes': missing}


def window(code, decoded, start, end):
    """Bounded preview plus an exact byte span and digest of the entire window."""
    lo = decoded[start][0] if start < len(decoded) else len(code)
    hi = decoded[end][0] if end < len(decoded) else len(code)
    count = end - start
    indices = list(range(start, min(end, start + PREVIEW)))
    indices += list(range(max(start + PREVIEW, end - PREVIEW), end))
    return {'byte_range': [lo, hi], 'instruction_count': count,
            'bytes_keccak256': lens.digest(code[lo:hi]),
            'preview': [describe(decoded[i]) for i in indices],
            'omitted_instruction_count': count - len(indices)}


def runtime_delta(before, after):
    """Trim matching instruction prefix/suffix in O(n), without alignment guessing."""
    left, right = instructions(before), instructions(after)
    prefix = 0
    while prefix < min(len(left), len(right)) and signature(left[prefix]) == signature(right[prefix]):
        prefix += 1
    suffix = 0
    while (suffix < min(len(left), len(right)) - prefix
           and signature(left[len(left)-1-suffix]) == signature(right[len(right)-1-suffix])):
        suffix += 1
    old_meta, new_meta = opcodes.solidity_metadata(before), opcodes.solidity_metadata(after)
    result = {'runtime_equal': before == after,
              'before_runtime_bytes': len(before), 'after_runtime_bytes': len(after),
              'before_instruction_count': len(left), 'after_instruction_count': len(right),
              'matching_prefix_instructions': prefix, 'matching_suffix_instructions': suffix,
              'before_recognized_metadata': old_meta, 'after_recognized_metadata': new_meta,
              'prefix_before_metadata_equal':
                  before[:old_meta['start']] == after[:new_meta['start']]
                  if old_meta is not None and new_meta is not None else None,
              'changed_window': None}
    if before != after:
        result['changed_window'] = {
            'before': window(before, left, prefix, len(left)-suffix),
            'after': window(after, right, prefix, len(right)-suffix)}
    return result


def identity(node):
    if node is None:
        return None
    return {'address': lens.address(node['address']),
            'code_hash': lens.fixed_hex(node['code_hash'], 32), 'kind': node['kind'],
            'next_address': lens.address(node['next_address']) if node['next_address'] else None,
            'storage': {name: lens.fixed_hex(value, 32) for name, value in node['storage'].items()}}


def beacons(observation):
    return {lens.address(node['beacon']['address']): node['beacon']
            for node in observation['nodes'] if 'beacon' in node}


def compare(before, after, before_anchor=None, after_anchor=None):
    # Reconstruct every raw account/storage proof, not a saved success summary.
    old_check = proof.verify(before, before_anchor)
    new_check = proof.verify(after, after_anchor)
    old, new = before['observation'], after['observation']
    require(lens.address(old['target']) == lens.address(new['target']), 'different target addresses')
    require(lens.quantity(new['block']['number']) > lens.quantity(old['block']['number']),
            'after block must be strictly later than before block')
    entries = []
    for index in range(max(len(old['nodes']), len(new['nodes']))):
        a = old['nodes'][index] if index < len(old['nodes']) else None
        b = new['nodes'][index] if index < len(new['nodes']) else None
        entries.append({'path_index': index, 'before': identity(a), 'after': identity(b),
                        'status': 'added' if a is None else 'removed' if b is None
                                  else 'same-identity' if identity(a) == identity(b) else 'changed-identity',
                        'runtime_comparison': runtime_delta(lens.code_bytes(a['code']), lens.code_bytes(b['code']))
                                              if a is not None and b is not None else None})
    old_beacons, new_beacons = beacons(old), beacons(new)
    beacon_entries = []
    for address in sorted(set(old_beacons) | set(new_beacons)):
        a, b = old_beacons.get(address), new_beacons.get(address)
        beacon_entries.append({'address': address,
                               'before_code_hash': lens.fixed_hex(a['code_hash'], 32) if a else None,
                               'after_code_hash': lens.fixed_hex(b['code_hash'], 32) if b else None,
                               'runtime_comparison': runtime_delta(lens.code_bytes(a['code']), lens.code_bytes(b['code']))
                                                     if a and b else None})
    same = all(entry['status'] == 'same-identity' for entry in entries)
    same_beacons = all(entry['before_code_hash'] == entry['after_code_hash'] for entry in beacon_entries)
    return {'schema': 'code-delta-v1', 'chain_id': 1, 'target': lens.address(old['target']),
            'before_block': ancestry.block_identity(old['block']),
            'after_block': ancestry.block_identity(new['block']),
            'block_distance': lens.quantity(new['block']['number']) - lens.quantity(old['block']['number']),
            'endpoint_identity_equal': same and same_beacons,
            'path_entries': entries, 'beacon_entries': beacon_entries,
            'before_proof': old_check, 'after_proof': new_check,
            'anchor_authenticity_verified': False, 'common_chain_ancestry_verified': False,
            'scope': 'Historical endpoint comparison only, never an acceptance or safety gate. '
                     'Each supplied block hash is checked, but its authenticity is external. '
                     'No common-chain ancestry or absence of changes between blocks is proved. '
                     'Path entries are compared by candidate-path position; changed addresses '
                     'are explicit. Linear decoding includes unreachable bytes and metadata. '
                     'The changed window is bounded by equal instruction prefix/suffix, not '
                     'a minimal diff or semantic equivalence claim. Metadata recognition does '
                     'not prove those bytes cannot execute. Beacon call results, routing '
                     'semantics, source equivalence and present-day code remain unverified.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, help='workspace-local raw Code Proof bundle')
    parser.add_argument('--after', required=True, help='raw bundle at a strictly later block')
    parser.add_argument('--before-anchor-hash', help='separately obtained old execution block hash')
    parser.add_argument('--after-anchor-hash', help='separately obtained new execution block hash')
    args = parser.parse_args()
    try:
        result = compare(ancestry.read_json(args.before), ancestry.read_json(args.after),
                         args.before_anchor_hash, args.after_anchor_hash)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, OverflowError, AttributeError,
            IndexError, RecursionError) as error:
        print('Code Delta: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
