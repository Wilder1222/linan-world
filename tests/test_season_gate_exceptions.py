import json
import unittest
from pathlib import Path

from scripts.audit_season_gate_exceptions import audit


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/reviews/season-gate-exception-ledger.json"


class SeasonGateExceptionTests(unittest.TestCase):
    def test_exception_ledger_passes_with_only_explicit_deferrals(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(0, report["blocking_open"])
        self.assertEqual(0, report["major_open"])
        self.assertEqual(5, report["deferred_total"])
        self.assertEqual([], report["findings"])
        self.assertTrue(all(item["severity"] == "DEFERRED" for item in report["exceptions"]))

    def test_report_points_to_season_gate_decision(self):
        audit()
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual("SG-04 Season Gate decision", report["next_gate"])
        self.assertTrue(report["checks"]["boundaries_preserved"])


if __name__ == "__main__":
    unittest.main()
