#!/usr/bin/env python3
"""Make one explicit, non-sending ZTO/IMD bound handoff after review."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'zto-review'))
import zto_review as review

HERE = Path(__file__).resolve().parent
SCHEMA = 'zto-bound-handoff-v1'


def handoff(observation, report, policy, amount):
    """Re-review evidence and select precisely one complete candidate amount.

    This deliberately contains no recipient, router, calldata, gas, signature,
    or transaction fields.  It is a finite planning handoff, not an order.
    """
    result = review.review(observation, report, policy)
    review.sizes.path.z.require(result['status'] == 'accepted',
                                'review did not accept a usable bound')
    review.sizes.path.z.require(isinstance(amount, str) and len(amount) <= 100,
                                'amount must be a short decimal string')
    state, _, _ = review.sizes.path.decode(observation)
    input_token = policy['input_token']
    output_token = 'IMD' if input_token == 'ZTO' else 'ZTO'
    input_decimals = state['decimals'][1 if input_token == 'ZTO' else 0]
    output_decimals = state['decimals'][0 if input_token == 'ZTO' else 1]
    raw = str(review.sizes.path.z.parse_amount(amount, input_decimals))
    matches = [row for row in result['usable_bounds']
               if row['requested_input_raw'] == raw]
    review.sizes.path.z.require(len(matches) == 1,
                                'amount is not exactly one reviewed usable bound')
    chosen = matches[0]
    output = {
        'schema': SCHEMA,
        'status': 'ready_for_human_review',
        'chain_id': result['chain_id'],
        'pool_id': result['pool_id'],
        'block': result['block'],
        'source_digests': {
            'snapshot_sha256': result['snapshot_sha256'],
            'policy_sha256': result['policy_sha256'],
            'report_sha256': result['report_sha256'],
        },
        'input_token': input_token,
        'output_token': output_token,
        'requested_input_raw': chosen['requested_input_raw'],
        'requested_input': review.sizes.path.z.units(
            int(chosen['requested_input_raw']), input_decimals),
        'minimum_output_raw': chosen['minimum_output_raw'],
        'minimum_output': review.sizes.path.z.units(
            int(chosen['minimum_output_raw']), output_decimals),
        'slippage_bps': policy['slippage_bps'],
        'review_reference_block': result['reference_block'],
        'review_age_blocks': result['age_blocks'],
        'settlement': 'unspecified',
        'transaction': None,
        'limitations': [
            'No recipient, router, calldata, gas setting, signature, or transaction is prepared.',
            'The minimum is a reviewed planning bound, not an enforced or guaranteed receipt.',
            'Historical evidence is not a current quote, execution simulation, or settlement proof.',
        ],
    }
    output['handoff_sha256'] = review.digest(output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--demo', action='store_true',
                      help='offline handoff from bundled historical real-pool evidence')
    mode.add_argument('--policy', help='review policy JSON inside this workspace')
    parser.add_argument('--snapshot', help='ZTO Path snapshot JSON inside this workspace')
    parser.add_argument('--report', help='ZTO Sizes report JSON inside this workspace')
    parser.add_argument('--amount', required=True,
                        help='one exact decimal candidate amount from the reviewed policy')
    args = parser.parse_args(argv)
    try:
        if args.demo:
            if args.snapshot or args.report:
                raise ValueError('--demo cannot be combined with custom files')
            policy_file = review.HERE / 'demo-policy.json'
            snapshot_file, report_file = review.DEFAULT_SNAPSHOT, review.DEFAULT_REPORT
        else:
            if not args.snapshot or not args.report:
                raise ValueError('--policy requires --snapshot and --report')
            policy_file, snapshot_file, report_file = args.policy, args.snapshot, args.report
        result = handoff(review.read_json(snapshot_file), review.read_json(report_file),
                         review.read_json(policy_file), args.amount)
        result['mode'] = 'historical_demo' if args.demo else 'caller_policy'
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, AttributeError, OSError, OverflowError,
            RecursionError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
