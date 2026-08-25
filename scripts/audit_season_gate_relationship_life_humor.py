from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"
REPORT = ROOT / "qa/reviews/season-gate-relationship-life-humor-review.json"
EPISODES = [f"S1-E{index:02d}" for index in range(1, 37)]
SNAPSHOTS = {"Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END", "ARC6-END", "Y+1"}
ARC_BY_EPISODE = {episode_id: f"ARC-{((index - 1) // 6) + 1:02d}" for index, episode_id in enumerate(EPISODES, 1)}
ACTIVITY_FIELDS = (
    "binding_id", "activity_id", "episode_id", "arc_id", "activity", "historical_anchor",
    "interpretation_note", "season_and_location", "modern_emotional_entry", "lead_characters",
    "surface_goal", "obstacle", "relationship_ids", "relationship_delta", "clue_delta", "choice",
    "state_transfer", "continuity_cost", "opening_hook", "ending_button",
)
HUMOR_FIELDS = (
    "humor_id", "episode_id", "arc_id", "speaker", "humor_type", "scene_context", "surface_line",
    "relationship_ids", "speaker_intent", "subtext", "listener_reaction", "reaction_order",
    "laugh_release", "emotional_recovery", "forbidden_target", "tonal_safety", "era_translation",
    "no_modern_terms",
)
MODERN_TERMS = ["内卷", "破防", "CPU", "老六", "社死", "你礼貌吗", "外卖", "手机", "互联网", "平台"]
FUNCTIONAL_FIELDS = {"scene_id", "dialogue_id", "shot_id"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def finding(code: str, severity: str = "BLOCKING", **details: object) -> dict:
    return {"code": code, "severity": severity, **details}


def known_ids() -> tuple[set[str], set[str], set[str]]:
    characters = {item["id"] for item in load(ROOT / "qa/character-roster.json")["named_characters"]}
    relationships = {item["id"] for item in load(ROOT / "qa/relationship-slots.json")["relationships"]}
    locations = {
        line.split("|")[1].strip()
        for line in (ROOT / "canon/city/00-city-index.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and "LOC-" in line
    }
    return characters, relationships, locations


def audit_relationships(ledger: dict, activity: dict, humor: dict) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    characters, relationships, locations = known_ids()
    slots = load(ROOT / "qa/relationship-slots.json").get("relationships", [])
    evidence_rows = load(ROOT / "qa/relationship-evidence.json").get("relationships", [])
    spines = load(ROOT / "qa/emotional-spines.json").get("spines", [])
    slot_ids = {item.get("id") for item in slots}
    evidence_ids = {item.get("relation_id") for item in evidence_rows}
    if len(slots) != 17 or slot_ids != relationships:
        findings.append(finding("relationship_slot_total_or_identity_invalid", actual=len(slots)))
    for relation in slots:
        if relation.get("status") not in {"SKELETON", "GROUP-SKELETON"}:
            findings.append(finding("relationship_slot_status_changed", relation_id=relation.get("id")))
        if relation.get("dimensions") != 7 or relation.get("snapshots") != 8:
            findings.append(finding("relationship_slot_dimensions_invalid", relation_id=relation.get("id")))
    expected_snapshot_ids = SNAPSHOTS
    snapshot_count = 0
    for relation in evidence_rows:
        relation_id = relation.get("relation_id")
        if relation_id not in relationships:
            findings.append(finding("relationship_evidence_unknown_relation", relation_id=relation_id))
        snapshots = relation.get("snapshots", [])
        snapshot_count += len(snapshots)
        if len(snapshots) != 8 or {item.get("snapshot") for item in snapshots} != expected_snapshot_ids:
            findings.append(finding("relationship_snapshot_coverage_invalid", relation_id=relation_id))
        for snapshot in snapshots:
            if snapshot.get("scene_status") != "RESERVED-UNTIL-SEASON-GATE":
                findings.append(finding("relationship_scene_bound_too_early", relation_id=relation_id, severity="MAJOR"))
            for field in ("evidence_id", "phase", "observable_action", "dialogue_intent", "irreversible_cost", "continuity_delta"):
                if not nonempty(snapshot.get(field)):
                    findings.append(finding("relationship_evidence_field_missing", relation_id=relation_id, field=field))
    if len(evidence_rows) != 17 or evidence_ids != relationships:
        findings.append(finding("relationship_evidence_total_or_identity_invalid", actual=len(evidence_rows)))
    if snapshot_count != 136:
        findings.append(finding("relationship_snapshot_total_invalid", actual=snapshot_count))

    spine_ids: set[str] = set()
    for spine in spines:
        states = spine.get("arc_states", [])
        spine_ids.update(spine.get("relation_ids", []))
        if len(states) != 6:
            findings.append(finding("emotional_spine_arc_state_total_invalid", spine_id=spine.get("id")))
        for state in states:
            for field in ("relation_id", "mixed_emotions", "seven_dimension_before", "seven_dimension_after", "choice", "cost", "aftermath", "observable_evidence"):
                if not nonempty(state.get(field)):
                    findings.append(finding("emotional_spine_state_field_missing", spine_id=spine.get("id"), field=field))
    if set(spine_ids) != relationships:
        findings.append(finding("emotional_spine_relationship_coverage_incomplete", missing=sorted(relationships - spine_ids)))

    used_relations: set[str] = set()
    for episode in ledger.get("episodes", []):
        relation = episode.get("relationship_choice") or {}
        relation_ids = relation.get("relation_ids", [])
        used_relations.update(relation_ids)
        unknown = [item for item in relation_ids if item not in relationships]
        unknown_characters = [item for item in relation.get("character_ids", []) if item not in characters]
        if unknown or unknown_characters:
            findings.append(finding("season_relationship_reference_unknown", episode_id=episode.get("episode_id"), relationships=unknown, characters=unknown_characters))
        for field in ("relation_ids", "character_ids", "choice", "delta", "evidence_ids"):
            if not nonempty(relation.get(field)):
                findings.append(finding("season_relationship_choice_incomplete", episode_id=episode.get("episode_id"), field=field))
    for entry in activity.get("entries", []):
        used_relations.update(entry.get("relationship_ids", []))
    for entry in humor.get("entries", []):
        used_relations.update(entry.get("relationship_ids", []))
    if used_relations != relationships:
        findings.append(finding("all_relationships_not_used_in_season_inputs", missing=sorted(relationships - used_relations), severity="MAJOR"))

    return {
        "relationship_total": len(slots),
        "relationship_evidence_total": len(evidence_rows),
        "relationship_snapshot_total": snapshot_count,
        "emotional_spine_total": len(spines),
        "relationship_choice_episode_total": len(ledger.get("episodes", [])),
        "all_relationships_used": used_relations == relationships,
    }, findings


def audit_activities(data: dict, characters: set[str], relationships: set[str], locations: set[str]) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = data.get("entries", [])
    bindings = data.get("episode_bindings", [])
    if data.get("status") != "SEASON-DRAFT":
        findings.append(finding("activity_matrix_status_not_season_draft", actual=data.get("status")))
    if len(entries) != 36 or len(bindings) != 36:
        findings.append(finding("activity_row_total_invalid", entries=len(entries), bindings=len(bindings)))
    entry_by_episode: dict[str, list[dict]] = defaultdict(list)
    state_by_activity: dict[str, list[str]] = defaultdict(list)
    entry_ids: set[str] = set()
    for entry in entries:
        episode_id = entry.get("episode_id")
        entry_by_episode[episode_id].append(entry)
        entry_ids.add(entry.get("binding_id"))
        missing = [field for field in ACTIVITY_FIELDS if not nonempty(entry.get(field))]
        if missing:
            findings.append(finding("activity_entry_missing_fields", binding_id=entry.get("binding_id"), fields=missing))
            continue
        if episode_id not in EPISODES or entry.get("arc_id") != ARC_BY_EPISODE.get(episode_id):
            findings.append(finding("activity_episode_or_arc_invalid", binding_id=entry.get("binding_id")))
        window = entry.get("season_and_location", {})
        if episode_id not in window.get("episode_window", []):
            findings.append(finding("activity_window_not_bound_to_episode", binding_id=entry.get("binding_id"), severity="MAJOR"))
        unknown_locations = [item for item in window.get("location_ids", []) if item not in locations]
        unknown_characters = [item for item in entry.get("lead_characters", []) if item not in characters]
        unknown_relationships = [item for item in entry.get("relationship_ids", []) if item not in relationships]
        if unknown_locations or unknown_characters or unknown_relationships:
            findings.append(finding("activity_reference_unknown", binding_id=entry.get("binding_id"), locations=unknown_locations, characters=unknown_characters, relationships=unknown_relationships))
        if not nonempty(entry.get("relationship_delta")) and not nonempty(entry.get("clue_delta")):
            findings.append(finding("activity_has_no_relationship_or_clue_delta", binding_id=entry.get("binding_id"), severity="MAJOR"))
        state_by_activity[entry.get("activity_id")].append(entry.get("state_transfer"))
    if len(entry_ids) != len(entries):
        findings.append(finding("activity_binding_ids_not_unique"))
    if set(entry_by_episode) != set(EPISODES) or any(len(entry_by_episode[episode_id]) != 1 for episode_id in EPISODES):
        findings.append(finding("activity_episode_coverage_invalid"))
    for activity_id, transfers in state_by_activity.items():
        if len(transfers) != len(set(transfers)):
            findings.append(finding("activity_repeat_state_transfer_unchanged", activity_id=activity_id, severity="MAJOR"))
    binding_map = {item.get("episode_id"): item for item in bindings}
    for binding in bindings:
        episode_id = binding.get("episode_id")
        if episode_id not in EPISODES or binding.get("arc_id") != ARC_BY_EPISODE.get(episode_id):
            findings.append(finding("activity_episode_binding_invalid", episode_id=episode_id))
        expected = {entry.get("activity_id") for entry in entry_by_episode.get(episode_id, [])}
        if set(binding.get("activity_ids", [])) != expected:
            findings.append(finding("activity_episode_binding_mismatch", episode_id=episode_id, severity="MAJOR"))
    if set(binding_map) != set(EPISODES):
        findings.append(finding("activity_episode_bindings_incomplete"))
    return {
        "activity_entry_total": len(entries),
        "activity_binding_total": len(bindings),
        "activity_episode_coverage": len(entry_by_episode) == 36 and all(len(entry_by_episode[item]) == 1 for item in EPISODES),
        "activity_state_transfers_differ": not any(item["code"] == "activity_repeat_state_transfer_unchanged" for item in findings),
    }, findings


def audit_humor(data: dict, characters: set[str], relationships: set[str]) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = data.get("entries", [])
    bindings = data.get("episode_bindings", [])
    if data.get("status") != "SEASON-DRAFT":
        findings.append(finding("humor_matrix_status_not_season_draft", actual=data.get("status")))
    if len(entries) != 36 or len(bindings) != 36:
        findings.append(finding("humor_row_total_invalid", entries=len(entries), bindings=len(bindings)))
    entry_by_episode: dict[str, list[dict]] = defaultdict(list)
    humor_ids: set[str] = set()
    humor_types: list[str] = []
    for entry in entries:
        episode_id = entry.get("episode_id")
        entry_by_episode[episode_id].append(entry)
        humor_ids.add(entry.get("humor_id"))
        missing = [field for field in HUMOR_FIELDS if not nonempty(entry.get(field))]
        if missing:
            findings.append(finding("humor_entry_missing_fields", humor_id=entry.get("humor_id"), fields=missing))
            continue
        humor_types.append(entry.get("humor_type"))
        if episode_id not in EPISODES or entry.get("arc_id") != ARC_BY_EPISODE.get(episode_id):
            findings.append(finding("humor_episode_or_arc_invalid", humor_id=entry.get("humor_id")))
        if entry.get("speaker") not in characters:
            findings.append(finding("humor_speaker_unknown", humor_id=entry.get("humor_id")))
        unknown_relationships = [item for item in entry.get("relationship_ids", []) if item not in relationships]
        if unknown_relationships:
            findings.append(finding("humor_relationship_reference_unknown", humor_id=entry.get("humor_id"), relationships=unknown_relationships))
        searchable = " ".join(str(entry.get(field, "")) for field in ("scene_context", "surface_line", "speaker_intent", "subtext", "listener_reaction", "laugh_release"))
        found_terms = [term for term in MODERN_TERMS if term in searchable]
        if found_terms:
            findings.append(finding("humor_modern_term_found", humor_id=entry.get("humor_id"), terms=found_terms, severity="MAJOR"))
        if episode_id in {f"S1-E{index:02d}" for index in range(25, 37)} and not nonempty(entry.get("tonal_safety")):
            findings.append(finding("high_stakes_humor_safety_missing", humor_id=entry.get("humor_id"), severity="MAJOR"))
        if not isinstance(entry.get("reaction_order"), list) or len(entry.get("reaction_order", [])) < 2:
            findings.append(finding("humor_reaction_order_incomplete", humor_id=entry.get("humor_id"), severity="MAJOR"))
    if len(humor_ids) != len(entries):
        findings.append(finding("humor_ids_not_unique"))
    if set(entry_by_episode) != set(EPISODES) or any(len(entry_by_episode[episode_id]) != 1 for episode_id in EPISODES):
        findings.append(finding("humor_episode_coverage_invalid"))
    for index in range(2, len(humor_types)):
        if humor_types[index] == humor_types[index - 1] == humor_types[index - 2]:
            findings.append(finding("three_adjacent_humor_types_repeat", index=index + 1, severity="MAJOR"))
    binding_map = {item.get("episode_id"): item for item in bindings}
    for binding in bindings:
        episode_id = binding.get("episode_id")
        expected = {entry.get("humor_id") for entry in entry_by_episode.get(episode_id, [])}
        if episode_id not in EPISODES or binding.get("arc_id") != ARC_BY_EPISODE.get(episode_id):
            findings.append(finding("humor_episode_binding_invalid", episode_id=episode_id))
        if set(binding.get("humor_ids", [])) != expected:
            findings.append(finding("humor_episode_binding_mismatch", episode_id=episode_id, severity="MAJOR"))
    if set(binding_map) != set(EPISODES):
        findings.append(finding("humor_episode_bindings_incomplete"))
    return {
        "humor_entry_total": len(entries),
        "humor_binding_total": len(bindings),
        "humor_episode_coverage": len(entry_by_episode) == 36 and all(len(entry_by_episode[item]) == 1 for item in EPISODES),
        "humor_types_varied": not any(item["code"] == "three_adjacent_humor_types_repeat" for item in findings),
    }, findings


def audit_u_bg() -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    selection = load(SEASON_DIR / "u-candidate-selection.json")
    source = load(ROOT / "qa/unit-slots.json")
    background = load(ROOT / "qa/background-usage.json")
    source_slots = {item.get("id"): item for item in source.get("slots", [])}
    slots = selection.get("slots", [])
    if selection.get("status") != "SEASON-DRAFT" or len(slots) != 120 or selection.get("slot_total") != 120:
        findings.append(finding("u_selection_status_or_total_invalid"))
    if {item.get("slot_id") for item in slots} != set(source_slots) or len({item.get("slot_id") for item in slots}) != len(slots):
        findings.append(finding("u_slot_identity_invalid"))
    for slot in slots:
        if slot.get("source_status") != "RESERVED" or slot.get("binding_status") != "RESERVED-UNTIL-SEASON-GATE" or slot.get("named_identity") is not None:
            findings.append(finding("u_slot_locked_too_early", slot_id=slot.get("slot_id"), severity="MAJOR"))
        if any(slot.get(field) is not None for field in FUNCTIONAL_FIELDS):
            findings.append(finding("u_functional_binding_present", slot_id=slot.get("slot_id"), severity="MAJOR"))
    pov = selection.get("pov_selections", [])
    returns = selection.get("natural_return_selections", [])
    if len(pov) != 22 or len(returns) < 40:
        findings.append(finding("u_candidate_counts_invalid", pov=len(pov), natural_returns=len(returns)))
    for item in pov + returns:
        if item.get("named_identity") is not None or item.get("binding_status") != "RESERVED-UNTIL-SEASON-GATE":
            findings.append(finding("u_candidate_identity_or_binding_locked", slot_id=item.get("slot_id"), severity="MAJOR"))
        if not nonempty(item.get("replacement_rule")):
            findings.append(finding("u_replacement_rule_missing", slot_id=item.get("slot_id")))
    if background.get("static_decoration_records") != 0 or len(background.get("archetypes", [])) < background.get("minimum_count", 300):
        findings.append(finding("bg_inventory_or_static_records_invalid"))
    for archetype in background.get("archetypes", []):
        if archetype.get("status") != "RESERVED" or archetype.get("microchapter_ids") or archetype.get("extension_ids"):
            findings.append(finding("bg_bound_or_status_changed", archetype_id=archetype.get("id"), severity="MAJOR"))
    return {
        "u_slot_total": len(slots),
        "u_pov_candidate_total": len(pov),
        "u_natural_return_total": len(returns),
        "bg_archetype_total": len(background.get("archetypes", [])),
        "u_replaceable": not any(item["code"].startswith("u_") for item in findings),
        "bg_reserved": not any(item["code"].startswith("bg_") for item in findings),
    }, findings


def audit() -> dict:
    characters, relationships, locations = known_ids()
    ledger = load(SEASON_DIR / "season-causal-ledger.json")
    activity = load(SEASON_DIR / "song-life-activity-matrix.json")
    humor = load(SEASON_DIR / "humor-register-matrix.json")
    relation_result, relation_findings = audit_relationships(ledger, activity, humor)
    activity_result, activity_findings = audit_activities(activity, characters, relationships, locations)
    humor_result, humor_findings = audit_humor(humor, characters, relationships)
    boundary_result, boundary_findings = audit_u_bg()
    findings = relation_findings + activity_findings + humor_findings + boundary_findings
    report = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        "scope": "P2 SG-02 independent relationship, Song-life, humor and replacement-boundary Season Gate review",
        "relationship_total": relation_result["relationship_total"],
        "activity_entry_total": activity_result["activity_entry_total"],
        "humor_entry_total": humor_result["humor_entry_total"],
        "u_slot_total": boundary_result["u_slot_total"],
        "bg_archetype_total": boundary_result["bg_archetype_total"],
        "checks": {
            "relationship_slots_and_snapshots_complete": relation_result["relationship_total"] == 17 and relation_result["relationship_snapshot_total"] == 136,
            "relationship_choices_change_state": not any(item["code"].startswith("season_relationship_choice") for item in findings),
            "all_relationships_used": relation_result["all_relationships_used"],
            "emotional_spines_cover_relationships": not any(item["code"] == "emotional_spine_relationship_coverage_incomplete" for item in findings),
            "activities_change_relationship_or_clue": not any(item["code"] == "activity_has_no_relationship_or_clue_delta" for item in findings),
            "activities_cover_all_episodes": activity_result["activity_episode_coverage"],
            "activity_repeat_state_transfer_differs": activity_result["activity_state_transfers_differ"],
            "humor_covers_all_episodes": humor_result["humor_episode_coverage"],
            "humor_has_reaction_and_recovery": not any(item["code"] in {"humor_entry_missing_fields", "humor_reaction_order_incomplete"} for item in findings),
            "humor_has_tonal_safety_and_no_modern_terms": not any(item["code"] in {"humor_modern_term_found", "high_stakes_humor_safety_missing"} for item in findings),
            "u_candidates_replaceable": boundary_result["u_replaceable"],
            "bg_remains_reserved_and_unbound": boundary_result["bg_reserved"],
        },
        "findings": findings,
        "deferred_followup": [
            "SG-03 建立跨层例外账本，处理两份独立审读之间的冲突或明确延期项。",
            "Episode Gate 再把关系动作、活动状态转移和幽默反应顺序绑定到正式逐场剧本、表演、分镜与 AIGC 资产。",
            "本报告不锁定最终对白、shot ID、U 唯一身份或 BG 微章 ID；Season Gate 仍保持 OPEN。",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-SEASON-PASS" else 1)
