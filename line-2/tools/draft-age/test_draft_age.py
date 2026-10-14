import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft_age as age


class DraftAgeTests(unittest.TestCase):
    def setUp(self):
        self.inputs = list(copy.deepcopy(age.demo_inputs()))

    def check(self, maximum=0):
        return age.check(*self.inputs, maximum)

    def advance(self, blocks):
        ref = self.inputs[4]['block']
        ref['number'] = hex(age.lens.quantity(ref['number']) + blocks)
        ref['timestamp'] = hex(age.lens.quantity(ref['timestamp']) + blocks * 12)
        # Use an actual different header hash from ancestor evidence for a synthetic mutation.
        ref['hash'] = age.gate.changes.flatten(self.inputs[1])['block_hash']

    def test_real_same_height_releases_only_for_owner_review(self):
        result = self.check()
        self.assertTrue(result['accepted'])
        self.assertEqual(result['age_blocks'], 0)
        self.assertEqual(result['owner_review_candidate'], self.inputs[0])
        self.assertEqual(result['pair_review']['current_balance_raw'], '0')
        self.assertFalse(result['complete_wallet_audit'])

    def test_limit_is_inclusive_and_stale_draft_is_withheld(self):
        self.advance(8)
        self.assertTrue(self.check(8)['accepted'])
        denied = self.check(7)
        self.assertEqual(denied['status'], 'stale_pair_evidence')
        self.assertIsNone(denied['owner_review_candidate'])

    def test_future_observation_and_same_height_fork_refused(self):
        self.advance(-1)
        with self.assertRaisesRegex(ValueError, 'reference precedes'):
            self.check()
        self.inputs = list(copy.deepcopy(age.demo_inputs()))
        self.advance(0)
        with self.assertRaisesRegex(ValueError, 'same-height'):
            self.check()

    def test_reference_identity_and_limits_are_strict(self):
        for limit in (-1, True, 1.5, '8'):
            with self.assertRaises(ValueError):
                self.check(limit)
        for key, value in [('chain_id', True), ('source', 'https://example.com'),
                           ('schema', 'other')]:
            original = copy.deepcopy(self.inputs[4])
            self.inputs[4][key] = value
            with self.assertRaises(ValueError):
                self.check()
            self.inputs[4] = original

    def test_cleared_and_changed_permissions_never_release_old_candidate(self):
        for word, expected in [('0', 'permission_cleared'), ('1', 'changed_active_permission')]:
            self.inputs[3]['raw']['allowances'][0]['result'] = '0x' + word.rjust(64, '0')
            result = self.check()
            self.assertFalse(result['accepted'])
            self.assertEqual(result['status'], expected)
            self.assertIsNone(result['owner_review_candidate'])

    def test_altered_draft_rejected_and_input_digest_changes(self):
        first = self.check()
        self.advance(1)
        second = self.check(1)
        self.assertNotEqual(first['input_sha256']['reference'], second['input_sha256']['reference'])
        self.inputs[0]['transaction']['data'] = self.inputs[0]['transaction']['data'][:-1] + '1'
        with self.assertRaises(ValueError):
            self.check(1)

    def test_cli_offline_and_partial_input_refusal(self):
        with patch.object(age.lens, 'RPC', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(age.main([]), 0)
            self.assertTrue(json.loads(output.getvalue())['demonstration'])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(age.main(['--maximum-age-blocks', '8']), 1)


if __name__ == '__main__':
    unittest.main()
