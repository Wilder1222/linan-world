import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_characters import (
    LA_STATES,
    parse_profile_toml,
    validate_background,
    validate_profile,
    validate_relationships,
    validate_relationship_slots,
    validate_roster,
    validate_unit_slots,
    validate_final,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_profile(root: Path, *, guard_answers: int = 7, missing_state: str | None = None,
                  relation_count: int = 2, malformed: bool = False) -> Path:
    path = root / "characters/central/chr-l1-01-shen-heng.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if malformed:
        path.write_text("---\nid = 'CHR-L1-01'\n---\n", encoding="utf-8")
        return path
    front = """+++\nid = \"CHR-L1-01\"\ntier = \"L1\"\nname = \"沈蘅\"\naliases = []\nage_y0 = 22\noccupation = \"香铺调香师\"\nresidence = \"鹤鸣巷\"\neconomic_source = \"香铺收入\"\npov_budget = 52\nminimum_episode_coverage = 24\nstatus = \"FOUNDATION-DRAFT\"\n+++\n"""
    sections = ["## 身份与外在", "## 内在与行为", "## 现实与关系", "## 坚守七问"]
    sections.append("\n".join(f"{index}. 守住具体的人和事实" for index in range(1, guard_answers + 1)))
    sections.extend(["## 非中央关系", "- REL-101 CHR-A1-01 非中央关系证据", "- REL-102 CHR-B-001 跨生活圈关系证据"][:1 + relation_count])
    sections.extend(["## 状态与选择链", "## 待集成人同步"])
    for state in LA_STATES:
        if state != missing_state:
            sections.append(f"### {state}\n目标、误判、选择、代价、关系变化和状态移交。")
    path.write_text(front + "\n\n".join(sections) + "\n", encoding="utf-8")
    return path


class CharacterValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.qa = self.root / "qa"
        self.qa.mkdir(parents=True)
        roster = json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
        write_json(self.qa / "character-roster.json", roster)
        write_json(self.qa / "relationship-slots.json", json.loads((ROOT / "qa/relationship-slots.json").read_text(encoding="utf-8")))

    def tearDown(self):
        self.temp.cleanup()

    def roster(self) -> dict:
        path = self.qa / "character-roster.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return data

    def save_roster(self, data: dict) -> None:
        write_json(self.qa / "character-roster.json", data)

    def test_duplicate_character_id_fails(self):
        data = self.roster(); data["named_characters"][1]["id"] = data["named_characters"][0]["id"]; self.save_roster(data)
        self.assertTrue(any("duplicate_character_id" in item for item in validate_roster(self.root)))

    def test_duplicate_alias_without_declaration_fails(self):
        data = self.roster(); data["named_characters"][0]["aliases"] = ["崔老板"]; self.save_roster(data)
        self.assertTrue(any("duplicate_alias_without_declaration" in item for item in validate_roster(self.root)))

    def test_wrong_tier_count_fails(self):
        data = self.roster(); data["named_characters"][0]["tier"] = "L2"; self.save_roster(data)
        self.assertTrue(any("wrong_tier_count" in item for item in validate_roster(self.root)))

    def test_wrong_individual_pov_budget_fails(self):
        data = self.roster(); data["named_characters"][0]["pov_budget"] = 51; self.save_roster(data)
        errors = validate_roster(self.root)
        self.assertTrue(any("wrong_individual_pov_budget" in item for item in errors))

    def test_missing_guard_answer_fails(self):
        write_profile(self.root, guard_answers=6)
        errors = validate_profile(self.root, "CHR-L1-01")
        self.assertTrue(any("missing_guard_answer" in item for item in errors))

    def test_missing_noncentral_relationship_fails(self):
        write_profile(self.root, relation_count=0)
        errors = validate_profile(self.root, "CHR-L1-01")
        self.assertTrue(any("missing_noncentral_relationship" in item for item in errors))

    def test_missing_state_checkpoint_fails(self):
        write_profile(self.root, missing_state="ARC3-END")
        errors = validate_profile(self.root, "CHR-L1-01")
        self.assertTrue(any("missing_state_checkpoint" in item and "ARC3-END" in item for item in errors))

    def test_relationship_pair_duplicate_fails(self):
        data = json.loads((self.qa / "relationship-slots.json").read_text(encoding="utf-8"))
        data["relationships"].append({"id":"REL-999","left":"CHR-L1-01","right":"CHR-L1-05","kind":"duplicate","dimensions":7,"snapshots":8})
        write_json(self.qa / "relationship-slots.json", data)
        self.assertTrue(any("relationship_pair_duplicate" in item for item in validate_relationship_slots(self.root)))

    def test_relationship_dimension_without_evidence_fails(self):
        path = self.root / "characters/relations/core/rel-001.md"; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# REL-001\n\n## 七维状态\n\n只有信任证据。\n", encoding="utf-8")
        self.assertTrue(any("relationship_dimension_without_evidence" in item for item in validate_relationships(self.root)))

    def test_unit_slot_count_fails(self):
        data = self.roster(); data["unit_slots"]["ranges"][0]["end"] = 29; self.save_roster(data)
        self.assertTrue(any("unit_slot_count" in item for item in validate_unit_slots(self.root)))

    def test_background_archetype_count_fails(self):
        data = self.roster(); data["background_archetypes"]["ecosystem_ranges"][0]["end"] = 19; self.save_roster(data)
        self.assertTrue(any("background_archetype_count" in item for item in validate_background(self.root)))

    def test_unit_finalization_before_episode_lock_fails(self):
        errors = validate_final(self.root)
        self.assertTrue(any("unit_finalization_before_episode_lock" in item for item in errors))

    def test_non_toml_or_malformed_front_matter_fails(self):
        path = write_profile(self.root, malformed=True)
        _, errors = parse_profile_toml(path)
        self.assertTrue(any("malformed_front_matter" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
