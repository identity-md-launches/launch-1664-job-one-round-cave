"""Adversarial endpoint and decoding checks; synthetic fixtures stay in tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
import code_delta as delta

FOLDER = Path(__file__).resolve().parent


def read(token='zto', later=False):
    folder = FOLDER if later else FOLDER.parent / 'code-proof'
    return delta.ancestry.read_json(folder / (token + ('-later-proof.json' if later else '-proof.json')))


def synthetic_runtime(code):
    """Single synthetic account/state trie, using ZTO's address as a test key."""
    bundle = read()
    node = bundle['observation']['nodes'][0]
    node.update(code='0x' + code.hex(), code_bytes=len(code), code_hash=delta.lens.digest(code))
    zero = '0x' + '00' * 32
    node['storage'] = {'implementation': zero, 'beacon': zero}
    bundle['observation']['effective_code_hash'] = node['code_hash']
    account = delta.proof.rlp_encode([b'\x01', b'', delta.proof.EMPTY_TRIE,
                                     bytes.fromhex(node['code_hash'][2:])])
    path = delta.proof.keccak256(bytes.fromhex(node['address'][2:]))
    leaf = delta.proof.rlp_encode([b'\x20' + path, account])
    fields = delta.proof.rlp_decode(bytes.fromhex(bundle['header_rlp'][2:]))
    fields[3] = delta.proof.keccak256(leaf)
    fields[8] = delta.proof.integer_bytes(delta.lens.quantity(bundle['observation']['block']['number']) + 1)
    raw = delta.proof.rlp_encode(fields)
    bundle['header_rlp'] = '0x' + raw.hex()
    bundle['observation']['block'] = {'hash': delta.lens.digest(raw),
                                    'number': hex(delta.proof.scalar(fields[8]))}
    bundle['proofs'] = [{'address': node['address'], 'nonce': '0x1', 'balance': '0x0',
                         'storageHash': '0x' + delta.proof.EMPTY_TRIE.hex(),
                         'codeHash': node['code_hash'], 'accountProof': ['0x' + leaf.hex()],
                         'storageProof': [{'key': key, 'value': '0x0', 'proof': []}
                                          for key in delta.lens.SLOTS.values()]}]
    return bundle


class DeltaTests(unittest.TestCase):
    def test_real_both_tokens(self):
        for token in ('zto', 'imd'):
            result = delta.compare(read(token), read(token, True))
            self.assertTrue(result['endpoint_identity_equal'])
            self.assertGreater(result['block_distance'], 0)
            self.assertFalse(result['common_chain_ancestry_verified'])
            self.assertFalse(result['anchor_authenticity_verified'])
            self.assertEqual(result['before_proof']['anchor'], 'unanchored-rpc-header')
            self.assertIsNone(result['path_entries'][0]['runtime_comparison']['changed_window'])

    def test_proved_changed_runtime(self):
        result = delta.compare(read(), synthetic_runtime(b'\x60\x01\xf4\x00'))
        self.assertFalse(result['endpoint_identity_equal'])
        entry = result['path_entries'][0]
        self.assertEqual(entry['status'], 'changed-identity')
        self.assertEqual(entry['runtime_comparison']['after_runtime_bytes'], 4)
        self.assertTrue(result['after_proof']['state_inclusion_verified'])

    def test_added_removed_path_and_unproven_beacon(self):
        spec = importlib.util.spec_from_file_location('ancestor_fixture',
                        FOLDER.parent / 'code-proof/test_code_proof.py')
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        bundle = fixture.synthetic_beacon_bundle()
        fields = delta.proof.rlp_decode(bytes.fromhex(bundle['header_rlp'][2:]))
        fields[8] = delta.proof.integer_bytes(delta.proof.scalar(fields[8]) + 1)
        raw = delta.proof.rlp_encode(fields)
        bundle['header_rlp'] = '0x' + raw.hex()
        bundle['observation']['block'] = {'hash': delta.lens.digest(raw),
                                        'number': hex(delta.proof.scalar(fields[8]))}
        added = delta.compare(read(), bundle)
        self.assertEqual(added['path_entries'][1]['status'], 'added')
        self.assertIsNone(added['beacon_entries'][0]['before_code_hash'])
        self.assertEqual(added['after_proof']['unproven_beacon_call_results'], [delta.lens.IMD])
        removed = delta.compare(bundle, read(later=True))
        self.assertEqual(removed['path_entries'][1]['status'], 'removed')
        self.assertIsNone(removed['beacon_entries'][0]['after_code_hash'])
        self.assertFalse(removed['endpoint_identity_equal'])

    def test_different_targets(self):
        with self.assertRaisesRegex(ValueError, 'different target'):
            delta.compare(read(), read('imd', True))

    def test_reverse_and_equal_heights(self):
        for before, after in ((read(later=True), read()), (read(), read())):
            with self.assertRaisesRegex(ValueError, 'strictly later'):
                delta.compare(before, after)

    def test_separate_anchors_are_checked(self):
        old, new = read(), read(later=True)
        old_hash, new_hash = (b['observation']['block']['hash'] for b in (old, new))
        result = delta.compare(old, new, old_hash, new_hash)
        self.assertEqual(result['before_proof']['anchor'], 'caller-supplied-block-hash')
        self.assertFalse(result['anchor_authenticity_verified'])
        with self.assertRaisesRegex(ValueError, 'independent block hash'):
            delta.compare(old, new, new_hash, new_hash)
        with self.assertRaisesRegex(ValueError, 'independent block hash'):
            delta.compare(old, new, old_hash, old_hash)
        self.assertEqual(delta.compare(old, new, old_hash)['after_proof']['anchor'], 'unanchored-rpc-header')

    def test_forged_runtime_consistent_report_is_rejected(self):
        old, new = read(), read(later=True)
        node = new['observation']['nodes'][0]
        node.update(code='0x6001', code_bytes=2, code_hash=delta.lens.digest(b'\x60\x01'))
        new['observation']['effective_code_hash'] = node['code_hash']
        new['proofs'][0]['codeHash'] = node['code_hash']
        self.assertTrue(delta.lens.verify(new['observation']))
        with self.assertRaisesRegex(ValueError, 'proven code hash'):
            delta.compare(old, new)

    def test_corrupt_either_raw_proof(self):
        for side in (0, 1):
            pair = [read(), read(later=True)]
            pair[side]['proofs'][0]['accountProof'].pop(0)
            with self.assertRaises(ValueError):
                delta.compare(*pair)

    def test_invalid_storage_and_header(self):
        for change in ('storage', 'header'):
            new = read(later=True)
            if change == 'storage':
                new['proofs'][0]['storageProof'][0]['value'] = '0x1'
            else:
                new['header_rlp'] = new['header_rlp'][:-2] + 'ff'
            with self.assertRaises(ValueError):
                delta.compare(read(), new)

    def test_hex_case_is_not_identity_change(self):
        new = read(later=True)
        node = new['observation']['nodes'][0]
        node['address'] = '0x' + node['address'][2:].upper()
        node['code_hash'] = '0x' + node['code_hash'][2:].upper()
        new['observation']['effective_address'] = node['address']
        new['observation']['effective_code_hash'] = node['code_hash']
        self.assertTrue(delta.compare(read(), new)['endpoint_identity_equal'])

    def test_push_data_is_not_instruction(self):
        result = delta.runtime_delta(b'\x61\xf4\xff\x00', b'\x61\xf4\xfe\x00')
        changed = result['changed_window']
        self.assertEqual(changed['before']['byte_range'], [0, 3])
        self.assertEqual(changed['before']['preview'][0]['opcode'], 'PUSH2')
        self.assertEqual(result['matching_suffix_instructions'], 1)

    def test_insert_and_delete_ranges(self):
        for a, b in ((b'\x00\x5b', b'\x00\x60\x01\x5b'),
                     (b'\x00\x60\x01\x5b', b'\x00\x5b')):
            result = delta.runtime_delta(a, b)
            for side, code in (('before', a), ('after', b)):
                win = result['changed_window'][side]
                lo, hi = win['byte_range']
                self.assertEqual(win['bytes_keccak256'], delta.lens.digest(code[lo:hi]))
            self.assertEqual(result['matching_prefix_instructions'], 1)
            self.assertEqual(result['matching_suffix_instructions'], 1)

    def test_truncated_push_keeps_actual_span(self):
        result = delta.runtime_delta(b'\x7f\x01', b'\x7f\x01\x00')
        old = result['changed_window']['before']
        self.assertEqual(old['byte_range'], [0, 2])
        self.assertEqual(old['preview'][0]['missing_push_bytes'], 31)
        self.assertEqual(result['changed_window']['after']['preview'][0]['missing_push_bytes'], 30)

    def test_preview_bound_and_nonminimal_window(self):
        result = delta.runtime_delta(b'\x01' + b'\x00' * 100 + b'\x02',
                                     b'\x03' + b'\x00' * 100 + b'\x04')
        win = result['changed_window']['before']
        self.assertEqual(win['instruction_count'], 102)
        self.assertEqual(len(win['preview']), 16)
        self.assertEqual(win['omitted_instruction_count'], 86)
        self.assertEqual(len({p['pc'] for p in win['preview']}), 16)

    def test_small_preview_no_duplicates(self):
        for count in range(1, 18):
            result = delta.runtime_delta(b'\x01' * count, b'\x02' * count)
            win = result['changed_window']['before']
            self.assertEqual(len(win['preview']), min(16, count))
            self.assertEqual(len({p['pc'] for p in win['preview']}), min(16, count))

    def test_recognized_metadata_is_still_compared(self):
        def runtime(version):
            metadata = bytes.fromhex('a164736f6c6343') + version
            return b'\x00' + metadata + len(metadata).to_bytes(2, 'big')
        result = delta.runtime_delta(runtime(b'\x00\x08\x19'), runtime(b'\x00\x08\x1a'))
        self.assertTrue(result['prefix_before_metadata_equal'])
        self.assertFalse(result['runtime_equal'])
        self.assertIsNotNone(result['changed_window'])

    def test_unrecognized_tail_not_silently_removed(self):
        result = delta.runtime_delta(b'\x00\x01\x00\x01', b'\x00\x02\x00\x01')
        self.assertIsNone(result['before_recognized_metadata'])
        self.assertIsNone(result['prefix_before_metadata_equal'])
        self.assertEqual(result['changed_window']['before']['byte_range'], [1, 2])

    def test_bounded_repetitive_input(self):
        result = delta.runtime_delta(b'\x00' * delta.lens.MAX_CODE,
                                     b'\x01' * delta.lens.MAX_CODE)
        self.assertEqual(result['changed_window']['before']['instruction_count'], delta.lens.MAX_CODE)
        self.assertLess(len(json.dumps(result)), 10000)
        with self.assertRaises(ValueError):
            delta.runtime_delta(b'\x00' * (delta.lens.MAX_CODE + 1), b'\x00')

    def test_cli_wrong_anchor_has_no_partial_json(self):
        result = subprocess.run([sys.executable, '-B', str(FOLDER / 'code_delta.py'),
                                 '--before', str(FOLDER.parent / 'code-proof/zto-proof.json'),
                                 '--after', str(FOLDER / 'zto-later-proof.json'),
                                 '--after-anchor-hash', read()['observation']['block']['hash']],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')

    def test_parser_duplicate_keys_and_outside_workspace(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"schema":1,"schema":2}', object_pairs_hook=delta.ancestry.no_duplicates)
        with self.assertRaisesRegex(ValueError, 'inside workspace'):
            delta.ancestry.read_json(Path.cwd().parent / 'outside.json')

    def test_demo(self):
        import demo
        self.assertTrue(demo.main()['demonstration_passed'])


if __name__ == '__main__':
    unittest.main()
