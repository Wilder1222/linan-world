import json
import unittest
from pathlib import Path

from scripts.audit_season_gate_relationship_life_humor import audit


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/reviews/season-gate-relationship-life-humor-review.json"


class SeasonGateRelationshipLifeHumorTests(unittest.TestCase):
    def test_independent_relationship_life_humor_review_passes(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(17, report["relationship_total"])
        self.assertEqual(36, report["activity_entry_total"])
        self.assertEqual(36, report["humor_entry_total"])
        self.assertEqual(120, report["u_slot_total"])
        self.assertEqual(300, report["bg_archetype_total"])
        self.assertEqual([], report["findings"])

    def test_report_keeps_replacement_and_episode_gate_boundaries(self):
        audit()
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["checks"]["u_candidates_replaceable"])
        self.assertTrue(report["checks"]["bg_remains_reserved_and_unbound"])
        self.assertTrue(any("Episode Gate" in item for item in report["deferred_followup"]))


if __name__ == "__main__":
    unittest.main()
