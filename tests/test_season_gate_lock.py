import json
import unittest
from pathlib import Path

from scripts.lock_season_gate import audit


ROOT = Path(__file__).resolve().parents[1]


class SeasonGateLockTests(unittest.TestCase):
    def test_season_gate_is_locked_and_rebuildable(self):
        report = audit()
        self.assertEqual("REVIEWED-SEASON-PASS", report["status"])
        self.assertEqual(27, report["input_item_total"])
        certificate = json.loads((ROOT / "qa/gates/season-gate.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "qa/gates/input-manifests/season.json").read_text(encoding="utf-8"))
        scope = json.loads((ROOT / "qa/gates/scope-definitions/season.json").read_text(encoding="utf-8"))
        self.assertEqual("LOCKED", certificate["status"])
        self.assertEqual("season", certificate["gate"])
        self.assertEqual(27, len(manifest["items"]))
        self.assertEqual(scope["declared_frozen_items"], [item["id"] for item in scope["items"]])


if __name__ == "__main__":
    unittest.main()
