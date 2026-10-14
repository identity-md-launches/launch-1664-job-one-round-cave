#!/usr/bin/env python3
"""Require caller-bounded block age before releasing a reviewed revoke candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'draft-refresh'))
import draft_refresh as refresh
lens, gate = refresh.lens, refresh.gate
REFERENCE_SCHEMA = 'permission-reference-block-v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def check(candidate, before, policy, after, reference, maximum_age_blocks):
    lens.require(type(maximum_age_blocks) is int and maximum_age_blocks >= 0,
                 'maximum age must be a nonnegative integer number of blocks')
    gate.exact_keys(reference, ('schema', 'chain_id', 'source', 'block'), 'reference')
    lens.require(reference['schema'] == REFERENCE_SCHEMA and
                 type(reference['chain_id']) is int and reference['chain_id'] == 1,
                 'reference must select Ethereum chain 1')
    lens.require(reference['source'] in lens.PUBLIC_ENDPOINTS, 'invalid reference source')
    gate.exact_keys(reference['block'], ('number', 'hash', 'timestamp'), 'reference block')
    head = lens.header(reference['block'])
    measured = refresh.compare(candidate, before, policy, after)
    height = lens.quantity(head['number'])
    age = height - measured['current_block_number']
    lens.require(age >= 0, 'reference precedes the pair observation')
    lens.require(lens.quantity(head['timestamp']) >= lens.quantity(after['block']['timestamp']),
                 'reference timestamp precedes the pair observation')
    if age == 0:
        lens.require(head['hash'].lower() == measured['current_block_hash'].lower() and
                     lens.quantity(head['timestamp']) == lens.quantity(after['block']['timestamp']),
                     'same-height reference differs from observed block')
    fresh = age <= maximum_age_blocks
    unchanged = measured['status'] == 'same_active_permission'
    accepted = fresh and unchanged
    return {
        'schema': 'allowance-draft-age-v1',
        'status': 'release_for_owner_review' if accepted else
                  ('stale_pair_evidence' if not fresh else measured['status']),
        'accepted': accepted,
        'reference_block_number': height,
        'reference_block_hash': head['hash'].lower(),
        'age_blocks': age,
        'maximum_age_blocks': maximum_age_blocks,
        'within_age_limit': fresh,
        'pair_review': measured,
        'input_sha256': {name: digest(value) for name, value in
                         [('candidate', candidate), ('before', before), ('policy', policy),
                          ('after', after), ('reference', reference)]},
        'owner_review_candidate': candidate if accepted else None,
        'complete_wallet_audit': False,
        'limitations': [
            'Age is relative to the caller-supplied reference height, not the wall clock or current tip.',
            'Saved RPC evidence and reference headers are trusted inputs, not independently proven state.',
            'A later reference header alone does not prove the older block remains canonical.',
            'Only the exact measured token-owner-spender pair is covered; other permissions remain unknown.',
            'Release is for owner review only; no signature, authorization, simulation or sending occurs.',
        ],
    }


def demo_inputs():
    before = gate.load(refresh.witness_tool.DEFAULT_OBSERVATION)
    policy = gate.load(refresh.witness_tool.DEFAULT_POLICY)
    candidate = refresh.drafts.build(before, policy)['drafts'][0]
    after = gate.load(HERE / 'live-after.json')
    reference = gate.load(HERE / 'live-reference.json')
    return candidate, before, policy, after, reference


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('draft', 'before', 'policy', 'after', 'reference'):
        parser.add_argument('--' + name, help='workspace JSON input')
    parser.add_argument('--maximum-age-blocks', type=int, help='inclusive caller-chosen age limit')
    args = parser.parse_args(argv)
    try:
        paths = [args.draft, args.before, args.policy, args.after, args.reference]
        demo = not any(paths) and args.maximum_age_blocks is None
        lens.require(demo or (all(paths) and args.maximum_age_blocks is not None),
                     'supply all five inputs and --maximum-age-blocks, or none for the historical demo')
        inputs = demo_inputs() if demo else tuple(gate.load(path) for path in paths)
        result = check(*inputs, 0 if demo else args.maximum_age_blocks)
        result['demonstration'] = demo
        print(json.dumps(result, indent=2))
        return 0 if result['accepted'] else 3
    except (ValueError, KeyError, TypeError, OSError, OverflowError, IndexError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
