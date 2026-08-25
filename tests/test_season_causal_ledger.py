import unittest

from scripts.audit_season_causal_ledger import audit


class SeasonCausalLedgerTests(unittest.TestCase):
    def test_s2a_sample_pass_and_scaffold_boundary(self):
        report = audit()

        self.assertEqual("REVIEWED-SAMPLE-PASS", report["status"])
        self.assertEqual(36, report["episode_total"])
        self.assertEqual(6, report["sample_complete"])
        self.assertEqual(30, report["draft_scaffold_total"])
        self.assertEqual([], report["findings"])


if __name__ == "__main__":
    unittest.main()
