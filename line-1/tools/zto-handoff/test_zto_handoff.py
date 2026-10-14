"""Offline tests for the bounded ZTO/IMD planning handoff."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch

import zto_handoff as h


class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observation = h.review.read_json(h.review.DEFAULT_SNAPSHOT)
        cls.report = h.review.read_json(h.review.DEFAULT_REPORT)
        cls.policy = h.review.read_json(h.review.HERE / 'demo-policy.json')

    def test_real_evidence_makes_one_complete_zto_handoff(self):
        result = h.handoff(self.observation, self.report, self.policy, '100000000')
        self.assertEqual(result['status'], 'ready_for_human_review')
        self.assertEqual(result['requested_input_raw'], str(10**26))
        self.assertEqual(result['minimum_output_raw'], '1184169088029408336486')
        self.assertEqual(result['settlement'], 'unspecified')
        self.assertIsNone(result['transaction'])
        self.assertEqual(result['handoff_sha256'], h.review.digest(
            {key: value for key, value in result.items() if key != 'handoff_sha256'}))

    def test_unreviewed_or_partial_amount_refused(self):
        for amount in ('1000000000', '2'):
            with self.assertRaises(ValueError):
                h.handoff(self.observation, self.report, self.policy, amount)

    def test_review_mismatch_is_not_handed_off(self):
        changed = copy.deepcopy(self.report)
        changed['candidates'][1]['minimum_output_raw'] = '1'
        with self.assertRaisesRegex(ValueError, 'review did not accept'):
            h.handoff(self.observation, changed, self.policy, '100000000')

    def test_cli_is_offline_and_uses_exact_decimal(self):
        with patch.object(h.review.sizes.path.z, 'RPC', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(h.main(['--demo', '--amount', '100000000']), 0)
        self.assertEqual(json.loads(output.getvalue())['input_token'], 'ZTO')
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(h.main(['--demo', '--amount', '3']), 1)
        self.assertIn('error', json.loads(error.getvalue()))


if __name__ == '__main__':
    unittest.main()
