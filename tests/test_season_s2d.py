import json
import unittest
from pathlib import Path

from scripts.audit_season_u_candidates import audit


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "story/season/u-candidate-selection.json"


class SeasonS2DTests(unittest.TestCase):
    def test_u_candidates_and_boundary_pass(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(120, report["slot_total"])
        self.assertEqual(22, report["pov_slot_total"])
        self.assertGreaterEqual(report["natural_return_candidate_total"], 40)
        self.assertEqual([], report["findings"])

    def test_selection_does_not_assign_identity_or_bg_bindings(self):
        data = json.loads(SELECTION.read_text(encoding="utf-8"))
        self.assertTrue(all(item["named_identity"] is None for item in data["slots"]))
        self.assertTrue(all(item["binding_status"] == "RESERVED-UNTIL-SEASON-GATE" for item in data["slots"]))
        self.assertTrue(data["boundary_rules"]["bg_microchapter_binding"] == "FORBIDDEN-UNTIL-EPISODE-GATE")


if __name__ == "__main__":
    unittest.main()
