"""Offline boundaries for explicit rehearsal expiry; evidence mutations are synthetic."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest

import rehearsal_expiry as tool


class ExpiryTests(unittest.TestCase):
    def setUp(self):
        self.evidence = tool.read_json(tool.HERE.parent / 'call-rehearsal' / 'zto-observation.json')
        self.policy = tool.read_json(tool.HERE / 'zto-expiry-policy.json')

    def test_real_zto_demo_window_matches(self):
        result = tool.evaluate(self.evidence, self.policy)
        self.assertEqual(result['verdict'], 'match')
        self.assertEqual(result['age_seconds'], 3600)
        self.assertEqual(result['observed_at'], self.evidence['block']['timestamp'])

    def test_exact_boundary_matches_and_one_second_later_stales(self):
        p = copy.deepcopy(self.policy)
        p['as_of'] = hex(int(self.evidence['block']['timestamp'], 16) + 7200)
        self.assertEqual(tool.evaluate(self.evidence, p)['verdict'], 'match')
        p['as_of'] = hex(int(p['as_of'], 16) + 1)
        self.assertEqual(tool.evaluate(self.evidence, p)['verdict'], 'mismatch')

    def test_before_block_is_inconclusive(self):
        p = copy.deepcopy(self.policy)
        p['as_of'] = hex(int(self.evidence['block']['timestamp'], 16) - 1)
        self.assertEqual(tool.evaluate(self.evidence, p)['verdict'], 'inconclusive')

    def test_changed_call_or_return_cannot_be_fresh(self):
        for patch in ({'data': '0xfffffffe'}, {'value': '0x1'}):
            with self.subTest(patch=patch):
                changed_call = copy.deepcopy(self.evidence)
                # Once it stops being the token's harmless no-sender default,
                # an explicit real-format sender is required by the inherited validator.
                changed_call['call'].update(patch)
                changed_call['call']['from'] = tool.core.TOKENS['IMD']
                self.assertEqual(tool.evaluate(changed_call, self.policy)['verdict'], 'inconclusive')
        changed = copy.deepcopy(self.evidence)
        changed['outcome']['result'] = '0x' + format(1, '064x')
        self.assertEqual(tool.evaluate(changed, self.policy)['verdict'], 'mismatch')

    def test_policy_limits_and_unknown_fields_rejected(self):
        for patch in ({'max_age_seconds': True}, {'max_age_seconds': 2678401},
                      {'as_of': '0x' + 'f' * 64}, {'extra': 1}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                tool.policy(dict(self.policy, **patch))

    def test_cli_demo_and_invalid_file_exit(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main(['demo']), 0)
            with tempfile.TemporaryDirectory(dir=tool.HERE) as folder:
                bad = Path(folder) / 'bad.json'
                bad.write_text('{}')
                self.assertEqual(tool.main(['check', str(bad), str(bad)]), 2)


if __name__ == '__main__':
    unittest.main()
