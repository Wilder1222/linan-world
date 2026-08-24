import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_project import (
    scan_forbidden,
    validate_canon_facts,
    validate_manifest,
    validate_required_paths,
    validate_scope,
)


ROOT = Path(__file__).resolve().parents[1]
TIMELINE = [
    "PRE-Y13", "Y-13", "Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END",
    "ARC4-END", "ARC5-END", "ARC6-END", "ENDING", "Y+1",
]


def make_fact(*, value: object, authority_path: str, priority: int,
              effective_from: str = "Y0-OPEN", effective_until: str | None = None) -> dict[str, object]:
    return {
        "fact_id": "WORLD.TEST_FACT", "value": value, "authority_path": authority_path,
        "authority_anchor": "测试锚点", "priority": priority, "effective_from": effective_from,
        "effective_until": effective_until, "status": "ACTIVE", "change_id": "CR-TEST",
    }


def make_registry(*facts: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 1, "timeline_order": TIMELINE, "facts": list(facts)}


class ManifestTests(unittest.TestCase):
    def test_committed_manifest_is_internally_consistent(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_manifest(data))

    def test_pov_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["pov_quotas"]["L1"] -= 1
        self.assertIn("pov_total=647 expected=648", validate_manifest(data))

    def test_function_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["primary_function_quotas"]["daily_life"] -= 1
        self.assertIn("function_total=647 expected=648", validate_manifest(data))

    def test_scanner_is_case_insensitive_and_never_scans_qa(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "canon").mkdir()
            (root / "qa").mkdir()
            (root / "canon/fact.md").write_text("ToDo", encoding="utf-8")
            (root / "qa/rule.md").write_text("TODO", encoding="utf-8")
            errors = scan_forbidden("canon", root=root)
            self.assertEqual(1, len(errors))
            self.assertIn("path=canon/fact.md", errors[0])

    def test_delivery_scope_stays_closed_until_delivery_validator_is_installed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "qa").mkdir()
            manifest = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
            (root / "qa/project-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            status = {"baseline": "APPROVED", "canon_gate": "OPEN", "character_foundation_gate": "OPEN",
                      "season_gate": "OPEN", "episode_gate": "OPEN", "character_final_gate": "OPEN",
                      "delivery_gate": "OPEN"}
            (root / "qa/production-status.json").write_text(json.dumps(status), encoding="utf-8")
            self.assertIn("delivery_validator_not_installed", validate_scope("delivery", strict=False, root=root))


class CanonPathTests(unittest.TestCase):
    def test_all_required_canon_paths_exist(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_required_paths(data, "canon", root=ROOT))


class CanonFactTests(unittest.TestCase):
    def test_conflicting_fact_effective_intervals_fail(self):
        registry = make_registry(
            make_fact(value={"state": "open"}, authority_path="canon/01-world-bible.md", priority=1, effective_until="ARC4-END"),
            make_fact(value={"state": "closed"}, authority_path="canon/02-city-atlas.md", priority=1, effective_from="ARC2-END"),
        )
        errors = validate_canon_facts(registry)
        self.assertIn("fact_conflict=fact_id=WORLD.TEST_FACT first=0 second=1", errors)

    def test_lower_priority_override_fails(self):
        registry = make_registry(
            make_fact(value="canon-value", authority_path="canon/01-world-bible.md", priority=1),
            make_fact(value="season-value", authority_path="story/season-01.md", priority=3),
        )
        errors = validate_canon_facts(registry)
        self.assertIn("lower_priority_override=fact_id=WORLD.TEST_FACT high=0 low=1", errors)


if __name__ == "__main__":
    unittest.main()
