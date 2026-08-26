from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "qa/reviews/p3-e01-episode-gate-review.json"


class P3E01EpisodeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def test_design_review_passes_but_gate_remains_open(self) -> None:
        self.assertEqual(self.report["status"], "REVIEWED-P3-DESIGN-GATE-PASS")
        self.assertEqual(self.report["decision"], "HOLD-OPEN-DEFERRED")
        self.assertFalse(self.report["eligible_for_episode_gate_pass"])
        self.assertEqual(self.report["episode_gate_status"], "OPEN")

    def test_nine_dimensions_score_at_least_ninety_and_aigc_is_deferred(self) -> None:
        dimensions = self.report["dimensions"]
        self.assertEqual(len(dimensions), 10)
        for key, item in dimensions.items():
            if key == "aigc_stability":
                self.assertIsNone(item["score"])
                self.assertEqual(item["status"], "DEFERRED-EVIDENCE-REQUIRED")
            else:
                self.assertGreaterEqual(item["score"], 90)
                self.assertEqual(item["status"], "SCORED-DESIGN-REVIEW")

    def test_scene_rollup_covers_all_eighteen_chapters(self) -> None:
        expected = [f"S1-E01-M{index:02d}" for index in range(1, 19)]
        rows = self.report["scene_rollup"]
        self.assertEqual([row["chapter_id"] for row in rows], expected)
        self.assertTrue(all(row["structural_status"] == "PASS" for row in rows))
        self.assertTrue(all(row["shot_count"] == 3 for row in rows))

    def test_execution_and_human_boundaries_are_explicit(self) -> None:
        self.assertEqual(self.report["execution"]["provider_calls"], 0)
        self.assertFalse(self.report["execution"]["external_execution"])
        self.assertEqual(self.report["execution"]["media_evidence"], "NOT_PROVIDED")
        self.assertEqual(self.report["human_signoff"]["status"], "REQUIRED")
        self.assertIsNone(self.report["human_signoff"]["reviewer"])


if __name__ == "__main__":
    unittest.main()
