from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TIERS = ("L1", "L2", "L3", "A1", "A2", "A3", "B")
EXPECTED_COUNTS = {"L1": 5, "L2": 4, "L3": 3, "A1": 8, "A2": 8, "A3": 8, "B": 48}
EXPECTED_POV = {"L1": 230, "L2": 108, "L3": 72, "A1": 80, "A2": 48, "A3": 16, "B": 72}
EXPECTED_INDIVIDUAL_POV = {
    "CHR-L1-01": 52, "CHR-L1-02": 44, "CHR-L1-03": 42, "CHR-L1-04": 46, "CHR-L1-05": 46,
    "CHR-L2-01": 30, "CHR-L2-02": 28, "CHR-L2-03": 26, "CHR-L2-04": 24,
    "CHR-L3-01": 28, "CHR-L3-02": 24, "CHR-L3-03": 20,
}
PROFILE_KEYS = {
    "id", "tier", "name", "aliases", "age_y0", "occupation", "residence",
    "economic_source", "pov_budget", "minimum_episode_coverage", "status",
}
LA_HEADINGS = (
    "## 身份与外在", "## 内在与行为", "## 现实与关系", "## 坚守七问",
    "## 状态与选择链", "## 待集成人同步",
)
LA_STATES = ("Y-13", "Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END", "ARC6-END", "ENDING", "Y+1")
B_HEADINGS = ("## 基础状态", "## 坚守七问", "## 非中央关系", "## 终局职业回响")


class CharacterValidationError(ValueError):
    pass


def _error(code: str, stable_id: str = "-", path: str = "-", field: str = "-") -> str:
    return f"{code}|{stable_id}|{path}|{field}"


def load_roster(root: Path = ROOT) -> dict[str, Any]:
    path = root / "qa/character-roster.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _range_ids(prefix: str, start: int, end: int) -> list[str]:
    width = 3
    return [f"{prefix}{number:0{width}d}" for number in range(start, end + 1)]


def expand_unit_ids(roster: dict[str, Any]) -> list[str]:
    ranges = roster.get("unit_slots", {}).get("ranges", [])
    ids: list[str] = []
    for item in ranges:
        ids.extend(_range_ids(roster["unit_slots"]["prefix"], item["start"], item["end"]))
    return ids


def expand_background_ids(roster: dict[str, Any]) -> list[str]:
    prefix = roster.get("background_archetypes", {}).get("prefix", "CHR-BG-")
    ids: list[str] = []
    for item in roster.get("background_archetypes", {}).get("ecosystem_ranges", []):
        ids.extend(_range_ids(prefix, item["start"], item["end"]))
    return ids


def validate_roster(root: Path = ROOT) -> list[str]:
    try:
        roster = load_roster(root)
    except (OSError, json.JSONDecodeError) as exc:
        return [_error("roster_unreadable", path="qa/character-roster.json", field=str(exc))]
    errors: list[str] = []
    records = roster.get("named_characters")
    if not isinstance(records, list):
        return [_error("named_characters_must_be_list", path="qa/character-roster.json", field="named_characters")]
    ids: list[str] = []
    aliases: dict[str, str] = {}
    tier_counts = {tier: 0 for tier in TIERS}
    pov_totals = {tier: 0 for tier in TIERS}
    seen_paths: set[str] = set()
    id_pattern = re.compile(r"^CHR-(?:L[123]|A[123]|B)-\d{2,3}$")
    for record in records:
        stable_id = str(record.get("id", "-"))
        if stable_id in ids:
            errors.append(_error("duplicate_character_id", stable_id))
        ids.append(stable_id)
        tier = record.get("tier")
        if tier not in TIERS:
            errors.append(_error("unknown_tier", stable_id, field="tier"))
        else:
            tier_counts[tier] += 1
            pov_totals[tier] += int(record.get("pov_budget", -1))
        if not id_pattern.match(stable_id):
            errors.append(_error("invalid_character_id", stable_id, field="id"))
        name = record.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(_error("missing_character_name", stable_id, field="name"))
        aliases_for_record = record.get("aliases", [])
        if not isinstance(aliases_for_record, list):
            errors.append(_error("aliases_must_be_list", stable_id, field="aliases"))
            aliases_for_record = []
        for alias in aliases_for_record:
            if not isinstance(alias, str) or not alias.strip():
                errors.append(_error("invalid_alias", stable_id, field="aliases"))
                continue
            owner = aliases.get(alias)
            if owner is not None and owner != stable_id:
                errors.append(_error("duplicate_alias_without_declaration", stable_id, field=alias))
            else:
                aliases[alias] = stable_id
            if alias == name:
                errors.append(_error("alias_equals_primary_name", stable_id, field="aliases"))
        profile_path = record.get("profile_path")
        if not isinstance(profile_path, str) or not profile_path.startswith("characters/"):
            errors.append(_error("invalid_profile_path", stable_id, field="profile_path"))
        elif profile_path in seen_paths:
            errors.append(_error("duplicate_profile_path", stable_id, field=profile_path))
        else:
            seen_paths.add(profile_path)
        expected_budget = EXPECTED_INDIVIDUAL_POV.get(stable_id)
        if expected_budget is None and tier in {"A1", "A2", "A3"}:
            expected_budget = {"A1": 10, "A2": 6, "A3": 2}.get(tier)
        if tier == "B":
            if record.get("pov_budget") not in {1, 2}:
                errors.append(_error("invalid_b_pov_budget", stable_id, field="pov_budget"))
        elif expected_budget is not None and record.get("pov_budget") != expected_budget:
            errors.append(_error("wrong_individual_pov_budget", stable_id, field="pov_budget"))
    for tier, expected in EXPECTED_COUNTS.items():
        if tier_counts[tier] != expected:
            errors.append(_error("wrong_tier_count", tier, field=f"{tier}:{tier_counts[tier]} expected={expected}"))
    for tier, expected in EXPECTED_POV.items():
        if pov_totals[tier] != expected:
            errors.append(_error("wrong_tier_pov_total", tier, field=f"{tier}:{pov_totals[tier]} expected={expected}"))
    if len(records) != 84:
        errors.append(_error("stable_named_character_total", field=f"{len(records)} expected=84"))
    unit = roster.get("unit_slots", {})
    unit_ranges = unit.get("ranges", [])
    unit_ids = expand_unit_ids(roster)
    if len(unit_ids) != 120 or len(set(unit_ids)) != 120:
        errors.append(_error("unit_slot_count", field=f"{len(unit_ids)} expected=120"))
    if len(unit_ranges) != 4 or any(item.get("end", 0) - item.get("start", 0) + 1 != 30 for item in unit_ranges):
        errors.append(_error("unit_slot_category_count", field="four categories of 30 required"))
    if unit.get("pov_slot_count") != 22:
        errors.append(_error("unit_pov_slot_count", field="pov_slot_count"))
    if unit.get("pov_candidate_minimum", 0) < 44:
        errors.append(_error("unit_pov_candidate_pool", field="pov_candidate_minimum"))
    if unit.get("natural_return_minimum", 0) < 40:
        errors.append(_error("unit_return_candidate_pool", field="natural_return_minimum"))
    background = roster.get("background_archetypes", {})
    bg_ids = expand_background_ids(roster)
    if len(bg_ids) < int(background.get("minimum_count", 300)) or len(set(bg_ids)) != len(bg_ids):
        errors.append(_error("background_archetype_count", field=f"{len(bg_ids)} expected>={background.get('minimum_count', 300)}"))
    if len(background.get("ecosystem_ranges", [])) != 15:
        errors.append(_error("background_ecosystem_count", field="ecosystem_ranges"))
    return sorted(errors)


def parse_profile_toml(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    relative = path.as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [_error("profile_missing", path=relative, field=str(exc))]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "+++":
        return None, [_error("malformed_front_matter", path=relative, field="opening")]
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "+++")
    except StopIteration:
        return None, [_error("malformed_front_matter", path=relative, field="closing")]
    try:
        data = tomllib.loads("\n".join(lines[1:closing]) + "\n")
    except tomllib.TOMLDecodeError as exc:
        return None, [_error("malformed_toml", path=relative, field=str(exc))]
    if not isinstance(data, dict):
        return None, [_error("front_matter_must_be_table", path=relative)]
    unknown = sorted(set(data) - PROFILE_KEYS)
    errors = [_error("unknown_profile_field", path=relative, field=key) for key in unknown]
    missing = sorted(PROFILE_KEYS - set(data))
    errors.extend(_error("missing_profile_field", path=relative, field=key) for key in missing)
    return data, sorted(errors)


def _record_for(root: Path, character_id: str) -> dict[str, Any] | None:
    roster = load_roster(root)
    return next((item for item in roster.get("named_characters", []) if item.get("id") == character_id), None)


def validate_profile(root: Path, character_id: str) -> list[str]:
    record = _record_for(root, character_id)
    if record is None:
        return [_error("unknown_character_id", character_id, path="qa/character-roster.json")]
    path = root / record["profile_path"]
    data, errors = parse_profile_toml(path)
    if data is None:
        return sorted(errors)
    errors = list(errors)
    relative = record["profile_path"]
    for key in ("id", "tier", "name", "pov_budget", "minimum_episode_coverage"):
        if data.get(key) != record.get(key):
            errors.append(_error("profile_roster_mismatch", character_id, relative, key))
    text = path.read_text(encoding="utf-8")
    tier = record["tier"]
    required = LA_HEADINGS if tier in {"L1", "L2", "L3", "A1", "A2", "A3"} else B_HEADINGS
    for heading in required:
        if heading not in text:
            errors.append(_error("missing_profile_section", character_id, relative, heading))
    if tier in {"L1", "L2", "L3", "A1", "A2", "A3"}:
        for state in LA_STATES:
            if not re.search(rf"(?:^|\n)###\s+{re.escape(state)}\b", text):
                errors.append(_error("missing_state_checkpoint", character_id, relative, state))
        guard_section = text.split("## 坚守七问", 1)[-1].split("## ", 1)[0] if "## 坚守七问" in text else ""
        guard_answers = len(re.findall(r"(?m)^\s*(?:[1-7][\.、]|[-*])\s+\S+", guard_section))
        if guard_answers < 7:
            errors.append(_error("missing_guard_answer", character_id, relative, f"{guard_answers}/7"))
        relation_section = text.split("## 非中央关系", 1)[-1].split("## ", 1)[0] if "## 非中央关系" in text else ""
        relations = re.findall(r"(?m)^\s*[-*]\s+(?:REL-[A-Z0-9-]+|CHR-[A-Z0-9-]+)", relation_section)
        if len(relations) < 2:
            errors.append(_error("missing_noncentral_relationship", character_id, relative, f"{len(relations)}<2"))
    return sorted(errors)


def validate_profiles(root: Path, tiers: set[str], character_id: str | None = None) -> list[str]:
    roster = load_roster(root)
    records = [item for item in roster.get("named_characters", []) if item.get("tier") in tiers]
    if character_id:
        records = [item for item in records if item.get("id") == character_id]
    errors: list[str] = []
    for record in records:
        errors.extend(validate_profile(root, record["id"]))
    return sorted(errors)


def validate_unit_slots(root: Path) -> list[str]:
    errors = validate_roster(root)
    roster = load_roster(root)
    if errors:
        errors = [item for item in errors if item.split("|", 1)[0] in {"unit_slot_count", "unit_slot_category_count", "unit_pov_slot_count", "unit_pov_candidate_pool", "unit_return_candidate_pool"}]
    path = root / "qa/unit-slots.json"
    if not path.exists():
        return sorted(errors + [_error("unit_registry_missing", path="qa/unit-slots.json")])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return sorted(errors + [_error("unit_registry_unreadable", path="qa/unit-slots.json", field=str(exc))])
    slots = data.get("slots", [])
    expected_ids = set(expand_unit_ids(roster))
    actual_ids = {slot.get("id") for slot in slots}
    if len(slots) != 120 or actual_ids != expected_ids:
        errors.append(_error("unit_registry_slot_count", path="qa/unit-slots.json", field=f"{len(slots)} expected=120"))
    if data.get("pov_slot_count") != 22:
        errors.append(_error("unit_registry_pov_slot_count", path="qa/unit-slots.json", field="pov_slot_count"))
    if data.get("pov_candidate_count", 0) < 44:
        errors.append(_error("unit_registry_pov_candidate_pool", path="qa/unit-slots.json", field="pov_candidate_count"))
    if data.get("natural_return_candidate_count", 0) < 40:
        errors.append(_error("unit_registry_return_candidate_pool", path="qa/unit-slots.json", field="natural_return_candidate_count"))
    for slot in slots:
        for field in ("category", "window", "relation_slot", "eligible_profession_families", "status"):
            if not slot.get(field):
                errors.append(_error("unit_registry_missing_field", slot.get("id", "-"), "qa/unit-slots.json", field))
        if slot.get("status") != "RESERVED":
            errors.append(_error("unit_registry_invalid_status", slot.get("id", "-"), "qa/unit-slots.json", "status"))
    return sorted(errors)


def validate_background(root: Path) -> list[str]:
    errors = validate_roster(root)
    errors = [item for item in errors if item.split("|", 1)[0].startswith("background_")]
    path = root / "qa/background-usage.json"
    if not path.exists():
        return sorted(errors + [_error("background_registry_missing", path="qa/background-usage.json")])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return sorted(errors + [_error("background_registry_unreadable", path="qa/background-usage.json", field=str(exc))])
    archetypes = data.get("archetypes", [])
    expected_ids = set(expand_background_ids(load_roster(root)))
    actual_ids = {item.get("id") for item in archetypes}
    if len(archetypes) < 300 or actual_ids != expected_ids:
        errors.append(_error("background_registry_count", path="qa/background-usage.json", field=f"{len(archetypes)} expected=300"))
    if data.get("static_decoration_records") != 0:
        errors.append(_error("background_static_decoration_forbidden", path="qa/background-usage.json", field="static_decoration_records"))
    required = ("ecosystem", "age_band", "occupation_family", "class_band", "region", "family_state", "active_time", "materials", "eligible_location_ids", "eligible_time_windows", "eligible_work_states", "microchapter_ids", "extension_ids", "status")
    for item in archetypes:
        for field in required:
            # Empty usage arrays are intentional while the Season/Episode gates
            # have not yet bound a BG archetype to concrete microchapters.
            if field not in item or item[field] in (None, ""):
                errors.append(_error("background_registry_missing_field", item.get("id", "-"), "qa/background-usage.json", field))
        if item.get("static_decoration_record"):
            errors.append(_error("background_static_decoration_forbidden", item.get("id", "-"), "qa/background-usage.json", "static_decoration_record"))
    return sorted(errors)


def validate_relationship_slots(root: Path) -> list[str]:
    path = root / "qa/relationship-slots.json"
    if not path.exists():
        return [_error("relationship_slots_missing", path="qa/relationship-slots.json")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [_error("relationship_slots_unreadable", path="qa/relationship-slots.json", field=str(exc))]
    relations = data.get("relationships", [])
    errors: list[str] = []
    ids: set[str] = set()
    pairs: dict[tuple[str, str], str] = {}
    for relation in relations:
        relation_id = relation.get("id", "-")
        if relation_id in ids:
            errors.append(_error("duplicate_relationship_id", relation_id))
        ids.add(relation_id)
        left, right = relation.get("left"), relation.get("right")
        if not left or not right:
            errors.append(_error("relationship_pair_missing", relation_id))
            continue
        pair = tuple(sorted((left, right)))
        if pair in pairs and relation.get("kind") != "五信协作群":
            errors.append(_error("relationship_pair_duplicate", relation_id, field=f"{pairs[pair]}:{pair[0]}:{pair[1]}"))
        if relation.get("kind") != "五信协作群":
            pairs[pair] = relation_id
        if relation.get("dimensions") != 7:
            errors.append(_error("relationship_dimension_count", relation_id, field="dimensions"))
        if relation.get("snapshots") != 8:
            errors.append(_error("relationship_snapshot_count", relation_id, field="snapshots"))
    if len(relations) != 17:
        errors.append(_error("relationship_slot_count", field=f"{len(relations)} expected=17"))
    return sorted(errors)


def validate_relationships(root: Path) -> list[str]:
    errors = validate_relationship_slots(root)
    evidence_path = root / "qa/relationship-evidence.json"
    evidence_data: dict = {}
    if not evidence_path.exists():
        errors.append(_error("relationship_evidence_registry_missing", path="qa/relationship-evidence.json"))
    else:
        try:
            evidence_data = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(_error("relationship_evidence_registry_unreadable", path="qa/relationship-evidence.json", field=str(exc)))
        if evidence_data.get("status") != "FOUNDATION-EVIDENCE":
            errors.append(_error("relationship_evidence_registry_status", path="qa/relationship-evidence.json", field="status"))
    evidence_records = evidence_data.get("relationships", [])
    evidence_by_relation = {item.get("relation_id"): item for item in evidence_records}
    expected_evidence_relations = {f"REL-{number:03d}" for number in range(1, 17)} | {"REL-G01"}
    if {item.get("relation_id") for item in evidence_records} != expected_evidence_relations:
        errors.append(_error("relationship_evidence_relation_ids", path="qa/relationship-evidence.json", field="relation_id"))
    if len(evidence_records) != 17:
        errors.append(_error("relationship_evidence_relation_count", path="qa/relationship-evidence.json", field=f"{len(evidence_records)} expected=17"))
    relation_dir = root / "characters/relations/core"
    expected = {f"rel-{number:03d}.md" for number in range(1, 17)} | {"rel-g01.md"}
    actual = {path.name for path in relation_dir.glob("rel-*.md")}
    for missing in sorted(expected - actual):
        errors.append(_error("relationship_profile_missing", path=f"characters/relations/core/{missing}"))
    for extra in sorted(actual - expected):
        errors.append(_error("relationship_profile_unexpected", path=f"characters/relations/core/{extra}"))
    for path in sorted(relation_dir.glob("rel-*.md")):
        text = path.read_text(encoding="utf-8")
        relation_id = path.stem.upper()
        if "## 七维状态" not in text:
            errors.append(_error("relationship_dimension_without_evidence", path=path.relative_to(root).as_posix(), field="七维状态"))
        if "## 八个快照" not in text:
            errors.append(_error("relationship_snapshot_without_evidence", path=path.relative_to(root).as_posix(), field="八个快照"))
        for dimension in ("亲近", "信任", "亏欠", "依赖", "敬意", "怨恨", "共同秘密"):
            if dimension not in text:
                errors.append(_error("relationship_dimension_without_evidence", path=path.relative_to(root).as_posix(), field=dimension))
        relation_evidence = evidence_by_relation.get(relation_id, {})
        snapshots = relation_evidence.get("snapshots", [])
        if len(snapshots) != 8:
            errors.append(_error("relationship_evidence_snapshot_count", relation_id, field=f"{len(snapshots)} expected=8"))
        expected_fields = ("evidence_id", "relation_id", "snapshot", "episode_window", "scene_status", "space", "object", "phase", "observable_action", "dialogue_intent", "irreversible_cost", "continuity_delta")
        for item in snapshots:
            for field in expected_fields:
                if item.get(field) in (None, ""):
                    errors.append(_error("relationship_evidence_missing_field", relation_id, item.get("evidence_id", "-"), field))
            if item.get("scene_status") != "RESERVED-UNTIL-SEASON-GATE":
                errors.append(_error("relationship_evidence_scene_status", relation_id, item.get("evidence_id", "-"), "scene_status"))
    return sorted(errors)


def validate_emotional_spines(root: Path) -> list[str]:
    path = root / "qa/emotional-spines.json"
    if not path.exists():
        return [_error("emotional_spines_missing", path="qa/emotional-spines.json")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [_error("emotional_spines_unreadable", path="qa/emotional-spines.json", field=str(exc))]
    spines = data.get("spines", [])
    errors: list[str] = []
    if len(spines) != 6:
        errors.append(_error("emotional_spine_count", field=f"{len(spines)} expected=6"))
    for spine in spines:
        if len(spine.get("arc_states", [])) != 6:
            errors.append(_error("emotional_spine_arc_count", spine.get("id", "-"), field="arc_states"))
        for state in spine.get("arc_states", []):
            for field in ("id", "relation_id", "mixed_emotions", "choice", "cost", "aftermath", "observable_evidence"):
                if not state.get(field):
                    errors.append(_error("emotional_spine_state_missing_field", state.get("id", spine.get("id", "-")), field=field))
    return sorted(errors)


def validate_foundation(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_roster(root))
    errors.extend(validate_profiles(root, {"L1", "L2", "L3", "A1", "A2", "A3", "B"}))
    errors.extend(validate_unit_slots(root))
    errors.extend(validate_background(root))
    errors.extend(validate_relationship_slots(root))
    errors.extend(validate_relationships(root))
    errors.extend(validate_emotional_spines(root))
    return sorted(set(errors))


def validate_final(root: Path = ROOT) -> list[str]:
    errors = validate_foundation(root)
    cert = root / "qa/gates/episode-gate.json"
    if not cert.exists():
        errors.append(_error("unit_finalization_before_episode_lock", path="qa/gates/episode-gate.json"))
    else:
        try:
            data = json.loads(cert.read_text(encoding="utf-8"))
            if data.get("status") != "LOCKED":
                errors.append(_error("unit_finalization_before_episode_lock", path="qa/gates/episode-gate.json", field="status"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(_error("episode_gate_certificate_unreadable", path="qa/gates/episode-gate.json", field=str(exc)))
    return sorted(set(errors))


def stage_errors(stage: str, root: Path, character_id: str | None = None) -> list[str]:
    if stage == "roster":
        return validate_roster(root)
    if stage == "profile":
        return validate_profile(root, character_id) if character_id else [_error("character_id_required", field="--character-id")]
    if stage == "central":
        return validate_profiles(root, {"L1", "L2", "L3"}, character_id)
    if stage == "important":
        return validate_profiles(root, {"A1", "A2", "A3"}, character_id)
    if stage == "recurring":
        return validate_profiles(root, {"B"}, character_id)
    if stage == "unit-slots":
        return validate_unit_slots(root)
    if stage == "unit-final":
        return validate_final(root)
    if stage == "background":
        return validate_background(root)
    if stage == "relationship-slots":
        return validate_relationship_slots(root)
    if stage == "relationships":
        return validate_relationships(root)
    if stage == "emotional-spines":
        return validate_emotional_spines(root)
    if stage == "foundation":
        return validate_foundation(root)
    if stage == "final":
        return validate_final(root)
    return [_error("unknown_stage", field=stage)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("roster", "profile", "central", "important", "recurring", "unit-slots", "unit-final", "background", "relationship-slots", "relationships", "emotional-spines", "foundation", "final"))
    parser.add_argument("--character-id")
    parser.add_argument("--write-generated-views", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    errors = stage_errors(args.stage, Path.cwd(), args.character_id)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"FAIL stage={args.stage} errors={len(errors)}")
        return 1
    print(f"PASS stage={args.stage} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
