import json
import unittest
from pathlib import Path

from scripts.audit_season_gate_causal_mystery import audit


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/reviews/season-gate-causal-mystery-review.json"


class SeasonGateCausalMysteryTests(unittest.TestCase):
    def test_independent_season_gate_review_passes(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(36, report["episode_total"])
        self.assertEqual(18, report["mystery_total"])
        self.assertEqual(648, report["chapter_total"])
        self.assertEqual([], report["findings"])

    def test_report_is_rebuildable_and_keeps_season_boundary(self):
        audit()
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertTrue(report["checks"]["mystery_phase_traceable"])
        self.assertTrue(report["checks"]["episode_tail_hooks_bound"])
        self.assertTrue(any("Season Gate" in item for item in report["deferred_followup"]))


if __name__ == "__main__":
    unittest.main()
