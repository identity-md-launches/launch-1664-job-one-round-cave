#!/usr/bin/env python3
"""Offline replay of two historical real ZTO/IMD code endpoints."""
import json
from pathlib import Path
import code_delta as delta


def main():
    folder = Path(__file__).resolve().parent
    results = []
    for token in ('zto', 'imd'):
        before = delta.ancestry.read_json(folder.parent / 'code-proof' / (token + '-proof.json'))
        after = delta.ancestry.read_json(folder / (token + '-later-proof.json'))
        result = delta.compare(before, after)
        delta.require(result['endpoint_identity_equal'], 'saved endpoints unexpectedly changed')
        delta.require(all(p['runtime_comparison']['changed_window'] is None
                          for p in result['path_entries']), 'unexpected runtime window')
        delta.require(result['before_proof']['anchor'] == result['after_proof']['anchor']
                      == 'unanchored-rpc-header', 'demo must not invent trust')
        results.append({'token': token.upper(), 'target': result['target'],
                        'before_block': result['before_block'], 'after_block': result['after_block'],
                        'block_distance': result['block_distance'],
                        'endpoint_identity_equal': result['endpoint_identity_equal'],
                        'runtime_bytes': result['path_entries'][0]['runtime_comparison']['after_runtime_bytes'],
                        'code_hash': result['path_entries'][0]['after']['code_hash'],
                        'anchor': result['after_proof']['anchor']})
    return {'demonstration_passed': True, 'results': results,
            'limitation': 'Unanchored historical endpoints only; no continuous stability or safety claim.'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
