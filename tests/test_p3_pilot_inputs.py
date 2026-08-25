import json
import unittest
from pathlib import Path

from scripts.prepare_p3_pilot_inputs import prepare


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/reviews/p3-pilot-input-freeze-review.json"


class P3PilotInputTests(unittest.TestCase):
    def test_e01_to_e03_input_freeze_passes(self):
        report = prepare()
        self.assertEqual("REVIEWED-P3-INPUT-PASS", report["status"])
        self.assertEqual(["S1-E01", "S1-E02", "S1-E03"], report["pilot_episodes"])
        self.assertEqual(54, report["chapter_total"])
        self.assertEqual([], report["findings"])

    def test_pilot_report_preserves_episode_gate_boundaries(self):
        prepare()
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual("DEFERRED-UNTIL-EPISODE-GATE", report["deferred_boundary"]["final_dialogue"])
        self.assertTrue(any("Episode Gate" in item for item in report["deferred_followup"]))


if __name__ == "__main__":
    unittest.main()
