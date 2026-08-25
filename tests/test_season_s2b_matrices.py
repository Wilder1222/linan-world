import json
import unittest
from pathlib import Path

from scripts.audit_season_s2b_matrices import (
    audit_activity,
    audit_humor,
    audit_mystery,
    audit_ledger_bindings,
)


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"


class SeasonS2BMatrixTests(unittest.TestCase):
    def test_all_s2b_matrices_pass_and_cover_the_season(self):
        mystery_result, mystery_findings = audit_mystery(
            json.loads((SEASON_DIR / "mystery-reversal-matrix.json").read_text(encoding="utf-8"))
        )
        activity_result, activity_findings = audit_activity(
            json.loads((SEASON_DIR / "song-life-activity-matrix.json").read_text(encoding="utf-8"))
        )
        humor_result, humor_findings = audit_humor(
            json.loads((SEASON_DIR / "humor-register-matrix.json").read_text(encoding="utf-8"))
        )

        self.assertEqual([], mystery_findings)
        self.assertEqual([], activity_findings)
        self.assertEqual([], humor_findings)
        self.assertEqual(36, mystery_result["episode_binding_total"])
        self.assertEqual(36, activity_result["entry_total"])
        self.assertEqual(36, humor_result["entry_total"])
        self.assertEqual([], audit_ledger_bindings())

    def test_s2b_reports_are_full_season_inputs(self):
        for filename in ("season-mystery-review.json", "season-activity-review.json", "season-humor-review.json"):
            report = json.loads((ROOT / "qa/reviews" / filename).read_text(encoding="utf-8"))
            self.assertEqual("REVIEWED-SEASON-PASS", report["status"], filename)


if __name__ == "__main__":
    unittest.main()
