import unittest

from scripts.audit_season_s2c import audit


class SeasonS2CTests(unittest.TestCase):
    def test_full_ledger_and_648_hooks_pass(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(36, report["episode_total"])
        self.assertEqual(648, report["chapter_total"])
        self.assertEqual([], report["findings"])


if __name__ == "__main__":
    unittest.main()
