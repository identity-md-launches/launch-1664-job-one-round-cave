#!/usr/bin/env python3
"""Bound an expected call rehearsal by an explicit, reviewable time window."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'call-expectation'))
import call_expectation as expectation

core = expectation.core
HERE = Path(__file__).resolve().parent
SCHEMA = 'rehearsal-expiry-v1'
MAX_AGE = 31 * 24 * 60 * 60
LIMITS = ('An untrusted, historical RPC rehearsal is only compared with a declared Unix '
          'time. A current verdict does not prove a transaction is safe, executable, canonical, '
          'included, or unchanged now. It does not obtain a clock or make a network request. '
          'Nothing is signed, sent, paid, or deployed.')


def timestamp(value, name):
    """Accept one canonical hexadecimal Unix timestamp below uint256."""
    number = core.quantity(value)
    core.require(number <= 2**63 - 1, name + ' exceeds supported Unix time range')
    return number


def policy(value):
    """Validate a fixed call expectation plus the review time it expires against."""
    core.require(isinstance(value, dict) and set(value) ==
                 {'schema', 'as_of', 'max_age_seconds', 'expectation'},
                 'expiry policy must have exactly schema, as_of, max_age_seconds, expectation')
    core.require(value['schema'] == SCHEMA, 'unsupported expiry policy schema')
    as_of = timestamp(value['as_of'], 'as_of')
    core.require(type(value['max_age_seconds']) is int and 0 <= value['max_age_seconds'] <= MAX_AGE,
                 'max_age_seconds must be an integer from 0 through 2678400')
    reviewed = expectation.policy(value['expectation'])
    return {'schema': SCHEMA, 'as_of': hex(as_of), 'max_age_seconds': value['max_age_seconds'],
            'expectation': reviewed}


def evaluate(evidence, value):
    """Return match/mismatch/inconclusive, separating stale evidence from a bad result."""
    chosen = policy(value)
    call_result = expectation.evaluate(evidence, chosen['expectation'])
    report = {
        'schema': SCHEMA, 'verdict': 'inconclusive', 'reason': '',
        'call_expectation': call_result, 'as_of': chosen['as_of'],
        'max_age_seconds': chosen['max_age_seconds'], 'limits': LIMITS,
    }
    if call_result['verdict'] != 'match':
        report.update(verdict=call_result['verdict'],
                      reason='call expectation is ' + call_result['verdict'])
        return report
    if isinstance(evidence, dict) and evidence.get('schema') == expectation.witness.SCHEMA:
        block = evidence['observations'][0]['block']
    else:
        block = evidence['block']
    observed = timestamp(block['timestamp'], 'evidence block timestamp')
    as_of = timestamp(chosen['as_of'], 'as_of')
    if as_of < observed:
        report.update(reason='declared review time precedes the evidence block', observed_at=hex(observed))
        return report
    age = as_of - observed
    report.update(observed_at=hex(observed), age_seconds=age)
    if age <= chosen['max_age_seconds']:
        report.update(verdict='match', reason='expected call evidence is within the declared age window')
    else:
        report.update(verdict='mismatch', reason='expected call evidence is older than the declared age window')
    return report


def read_json(path):
    return expectation.read_json(path)


def exit_code(result):
    return {'match': 0, 'mismatch': 1, 'inconclusive': 2}[result['verdict']]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo', help='recheck saved real ZTO evidence offline at its declared review time')
    check = commands.add_parser('check', help='check EVIDENCE against an explicit expiry policy offline')
    check.add_argument('evidence')
    check.add_argument('policy')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            evidence = read_json(HERE.parent / 'call-rehearsal' / 'zto-observation.json')
            selected = read_json(HERE / 'zto-expiry-policy.json')
        else:
            evidence, selected = read_json(args.evidence), read_json(args.policy)
        result = evaluate(evidence, selected)
        print(json.dumps(result, indent=2, allow_nan=False))
        return exit_code(result)
    except (ValueError, KeyError, TypeError, OSError, RecursionError, core.RPCError) as exc:
        print(json.dumps({'schema': SCHEMA, 'verdict': 'inconclusive', 'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
