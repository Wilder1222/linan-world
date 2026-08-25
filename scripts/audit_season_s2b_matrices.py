from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"
REVIEW_DIR = ROOT / "qa/reviews"
EPISODES = [f"S1-E{i:02d}" for i in range(1, 37)]
ARC_ENDS = {f"ARC-{i:02d}": f"S1-E{i * 6:02d}" for i in range(1, 7)}
ARC_STARTS = {f"ARC-{i:02d}": f"S1-E{(i - 1) * 6 + 1:02d}" for i in range(1, 7)}
CHARACTERS = {
    item["id"]
    for item in json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))["named_characters"]
}
RELATIONSHIPS = {
    item["id"]
    for item in json.loads((ROOT / "qa/relationship-slots.json").read_text(encoding="utf-8"))["relationships"]
}
LOCATIONS = {
    line.split("|")[1].strip()
    for line in (ROOT / "canon/city/00-city-index.md").read_text(encoding="utf-8").splitlines()
    if line.startswith("|") and "LOC-" in line
}
ACTIVITY_IDS = {f"EVT-{i:03d}" for i in range(1, 25)}
BANNED_MODERN_TERMS = ["内卷", "破防", "CPU", "老六", "社死", "你礼貌吗", "外卖", "手机", "互联网", "平台"]
REQUIRED_MYSTERY = [
    "mystery_id", "arc_id", "question", "planted_episode", "apparent_answer", "recheck_episode",
    "true_reframe", "cost_of_knowing", "information_owner", "audience_knowledge", "character_misread",
    "reframe_type", "reframe_episode", "arc_end_reveal_episode", "irreversible_reveal", "episode_refs",
]
REQUIRED_ACTIVITY = [
    "binding_id", "activity_id", "episode_id", "arc_id", "activity", "historical_anchor",
    "interpretation_note", "season_and_location", "modern_emotional_entry", "lead_characters", "surface_goal",
    "obstacle", "relationship_ids", "relationship_delta", "clue_delta", "choice", "state_transfer", "continuity_cost",
    "opening_hook", "ending_button",
]
REQUIRED_HUMOR = [
    "humor_id", "episode_id", "arc_id", "speaker", "humor_type", "scene_context", "surface_line",
    "relationship_ids", "speaker_intent", "subtext", "listener_reaction", "reaction_order", "laugh_release", "emotional_recovery",
    "forbidden_target", "tonal_safety", "era_translation", "no_modern_terms",
]


def read_json(name: str) -> dict:
    return json.loads((SEASON_DIR / name).read_text(encoding="utf-8"))


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def episode_index(episode_id: str) -> int:
    return int(episode_id[-2:])


def audit_mystery(data: dict) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = data.get("entries", [])
    bindings = data.get("episode_bindings", [])
    ids = [entry.get("mystery_id") for entry in entries]
    if len(entries) != 18:
        findings.append({"code": "mystery_entry_total", "actual": len(entries), "expected": 18})
    if len(set(ids)) != len(ids):
        findings.append({"code": "mystery_ids_not_unique"})
    for entry in entries:
        missing = [key for key in REQUIRED_MYSTERY if key not in entry or entry[key] in (None, [], "")]
        if missing:
            findings.append({"mystery_id": entry.get("mystery_id"), "code": "missing_fields", "fields": missing})
            continue
        refs = entry["episode_refs"]
        if any(ref not in EPISODES for ref in refs):
            findings.append({"mystery_id": entry["mystery_id"], "code": "unknown_episode_ref"})
        if any(char_id not in CHARACTERS for char_id in entry["information_owner"]):
            findings.append({"mystery_id": entry["mystery_id"], "code": "unknown_character_ref"})
        ordered = [entry["planted_episode"], entry["recheck_episode"], entry["reframe_episode"], entry["arc_end_reveal_episode"]]
        if any(item not in EPISODES for item in ordered) or ordered != sorted(ordered, key=episode_index):
            findings.append({"mystery_id": entry["mystery_id"], "code": "causal_phase_order_invalid", "phases": ordered})
        if entry["arc_id"] != f"ARC-{((episode_index(entry["planted_episode"]) - 1) // 6) + 1:02d}":
            findings.append({"mystery_id": entry["mystery_id"], "code": "arc_mismatch"})
    binding_episode_ids = [item.get("episode_id") for item in bindings]
    if binding_episode_ids != EPISODES:
        findings.append({"code": "mystery_binding_episode_order_invalid"})
    covered = set()
    reversal_types = []
    for item in bindings:
        ids_for_episode = item.get("ids", [])
        covered.add(item.get("episode_id"))
        if not ids_for_episode:
            findings.append({"episode_id": item.get("episode_id"), "code": "episode_has_no_mystery"})
        if item.get("reversal_type") in (None, ""):
            findings.append({"episode_id": item.get("episode_id"), "code": "episode_missing_reversal_type"})
        reversal_types.append(item.get("reversal_type"))
    if covered != set(EPISODES):
        findings.append({"code": "mystery_episode_coverage_incomplete"})
    for index in range(1, len(reversal_types)):
        if reversal_types[index] == reversal_types[index - 1]:
            findings.append({"code": "adjacent_reversal_type_repeated", "episode_index": index + 1})
    by_arc = defaultdict(list)
    for entry in entries:
        by_arc[entry["arc_id"]].append(entry)
    for arc_id in ARC_ENDS:
        arc_entries = by_arc[arc_id]
        if not any(entry["reframe_episode"] != ARC_STARTS[arc_id] for entry in arc_entries):
            findings.append({"arc_id": arc_id, "code": "no_mid_arc_reframe"})
        if not any(entry["arc_end_reveal_episode"] == ARC_ENDS[arc_id] for entry in arc_entries):
            findings.append({"arc_id": arc_id, "code": "no_arc_end_irreversible_reveal"})
    return {
        "scope": "P2 Season mystery and reversal matrix review",
        "entry_total": len(entries), "episode_binding_total": len(bindings), "arc_total": len(by_arc),
        "checks": {
            "all_episode_bindings": not any(item.get("episode_id") not in EPISODES for item in bindings) and len(bindings) == 36,
            "fair_clue_fields": not any(item.get("code") == "missing_fields" for item in findings),
            "mid_reframe_per_arc": not any(item.get("code") == "no_mid_arc_reframe" for item in findings),
            "arc_end_reveal_per_arc": not any(item.get("code") == "no_arc_end_irreversible_reveal" for item in findings),
            "adjacent_reversal_types_distinct": not any(item.get("code") == "adjacent_reversal_type_repeated" for item in findings),
            "references_traceable": not any(item.get("code") in {"unknown_episode_ref", "unknown_character_ref", "arc_mismatch"} for item in findings),
        },
    }, findings


def audit_activity(data: dict) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = data.get("entries", [])
    bindings = data.get("episode_bindings", [])
    if len(entries) != 36 or len(bindings) != 36:
        findings.append({"code": "activity_episode_total", "entries": len(entries), "bindings": len(bindings)})
    seen_episodes = set()
    by_activity = defaultdict(list)
    for entry in entries:
        missing = [key for key in REQUIRED_ACTIVITY if key not in entry or entry[key] in (None, [], "")]
        if missing:
            findings.append({"binding_id": entry.get("binding_id"), "code": "missing_fields", "fields": missing})
            continue
        episode_id = entry["episode_id"]
        seen_episodes.add(episode_id)
        by_activity[entry["activity_id"]].append(entry["state_transfer"])
        if episode_id not in EPISODES or entry["activity_id"] not in ACTIVITY_IDS:
            findings.append({"binding_id": entry["binding_id"], "code": "unknown_episode_or_activity"})
        location_ids = entry["season_and_location"].get("location_ids", [])
        if any(location_id not in LOCATIONS for location_id in location_ids):
            findings.append({"binding_id": entry["binding_id"], "code": "unknown_location_ref"})
        if any(char_id not in CHARACTERS for char_id in entry["lead_characters"]):
            findings.append({"binding_id": entry["binding_id"], "code": "unknown_character_ref"})
        if any(relation_id not in RELATIONSHIPS for relation_id in entry["relationship_ids"]):
            findings.append({"binding_id": entry["binding_id"], "code": "unknown_relationship_ref"})
        if not nonempty(entry["relationship_delta"]) and not nonempty(entry["clue_delta"]):
            findings.append({"binding_id": entry["binding_id"], "code": "activity_has_no_story_delta"})
    if seen_episodes != set(EPISODES):
        findings.append({"code": "activity_episode_coverage_incomplete"})
    for activity_id, transfers in by_activity.items():
        if len(transfers) != len(set(transfers)):
            findings.append({"activity_id": activity_id, "code": "repeat_activity_state_transfer_unchanged"})
    return {
        "scope": "P2 Song-life activity matrix review", "entry_total": len(entries), "episode_binding_total": len(bindings),
        "checks": {
            "all_episode_bindings": seen_episodes == set(EPISODES) and len(bindings) == 36,
            "historical_anchor_and_interpretation_present": not any(item.get("code") == "missing_fields" for item in findings),
            "activity_changes_relationship_or_clue": not any(item.get("code") == "activity_has_no_story_delta" for item in findings),
            "location_references_traceable": not any(item.get("code") == "unknown_location_ref" for item in findings),
            "participants_traceable": not any(item.get("code") == "unknown_character_ref" for item in findings),
            "relationship_references_traceable": not any(item.get("code") == "unknown_relationship_ref" for item in findings),
            "repeat_activity_state_transfer_differs": not any(item.get("code") == "repeat_activity_state_transfer_unchanged" for item in findings),
        },
    }, findings


def audit_humor(data: dict) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = data.get("entries", [])
    bindings = data.get("episode_bindings", [])
    if len(entries) != 36 or len(bindings) != 36:
        findings.append({"code": "humor_episode_total", "entries": len(entries), "bindings": len(bindings)})
    seen_episodes = set()
    types = []
    for entry in entries:
        missing = [key for key in REQUIRED_HUMOR if key not in entry or entry[key] in (None, [], "")]
        if missing:
            findings.append({"humor_id": entry.get("humor_id"), "code": "missing_fields", "fields": missing})
            continue
        episode_id = entry["episode_id"]
        seen_episodes.add(episode_id)
        types.append(entry["humor_type"])
        if episode_id not in EPISODES or entry["speaker"] not in CHARACTERS:
            findings.append({"humor_id": entry["humor_id"], "code": "unknown_episode_or_speaker"})
        if any(relation_id not in RELATIONSHIPS for relation_id in entry["relationship_ids"]):
            findings.append({"humor_id": entry["humor_id"], "code": "unknown_relationship_ref"})
        searchable = " ".join([entry["scene_context"], entry["surface_line"], entry["speaker_intent"], entry["subtext"]])
        found_terms = [term for term in BANNED_MODERN_TERMS if term in searchable]
        if found_terms:
            findings.append({"humor_id": entry["humor_id"], "code": "modern_term_found", "terms": found_terms})
        if episode_index(episode_id) >= 25 and not nonempty(entry["tonal_safety"]):
            findings.append({"humor_id": entry["humor_id"], "code": "high_stakes_tonal_safety_missing"})
    if len({entry.get("humor_id") for entry in entries}) != len(entries):
        findings.append({"code": "humor_ids_not_unique"})
    if seen_episodes != set(EPISODES):
        findings.append({"code": "humor_episode_coverage_incomplete"})
    for index in range(2, len(types)):
        if types[index] == types[index - 1] == types[index - 2]:
            findings.append({"code": "three_adjacent_same_humor_type", "index": index + 1})
    return {
        "scope": "P2 Humor and register matrix review", "entry_total": len(entries), "episode_binding_total": len(bindings),
        "checks": {
            "all_episode_bindings": seen_episodes == set(EPISODES) and len(bindings) == 36,
            "speaker_references_traceable": not any(item.get("code") == "unknown_episode_or_speaker" for item in findings),
            "relationship_references_traceable": not any(item.get("code") == "unknown_relationship_ref" for item in findings),
            "no_modern_terms": not any(item.get("code") == "modern_term_found" for item in findings),
            "forbidden_targets_declared": all(nonempty(entry.get("forbidden_target")) for entry in entries),
            "reaction_and_recovery_present": all(nonempty(entry.get("listener_reaction")) and nonempty(entry.get("emotional_recovery")) for entry in entries),
            "high_stakes_tonal_safety": not any(item.get("code") == "high_stakes_tonal_safety_missing" for item in findings),
        },
    }, findings


def audit_ledger_bindings() -> list[dict]:
    findings: list[dict] = []
    ledger = json.loads((SEASON_DIR / "season-causal-ledger.json").read_text(encoding="utf-8"))
    activities = read_json("song-life-activity-matrix.json")
    humor = read_json("humor-register-matrix.json")
    activity_map = {item["episode_id"]: item.get("activity_ids", []) for item in activities.get("episode_bindings", [])}
    humor_map = {item["episode_id"]: item.get("humor_ids", []) for item in humor.get("episode_bindings", [])}
    for episode in ledger.get("episodes", []):
        episode_id = episode["episode_id"]
        if episode.get("activity_ids") != activity_map.get(episode_id, []):
            findings.append({"episode_id": episode_id, "code": "ledger_activity_binding_mismatch"})
        if episode.get("humor_ids") != humor_map.get(episode_id, []):
            findings.append({"episode_id": episode_id, "code": "ledger_humor_binding_mismatch"})
    return findings


def update_report(path: Path, result: dict, findings: list[dict]) -> None:
    report = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        **result,
        "findings": findings,
        "deferred_followup": [
            "Season Gate 审读仍不绑定最终对白、shot ID、U 唯一身份或 BG 微章 ID。",
            "Episode Gate 将把活动、幽默与关系动作进一步绑定到逐场剧本和连续性账本。",
        ],
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    mystery_result, mystery_findings = audit_mystery(read_json("mystery-reversal-matrix.json"))
    activity_result, activity_findings = audit_activity(read_json("song-life-activity-matrix.json"))
    humor_result, humor_findings = audit_humor(read_json("humor-register-matrix.json"))
    ledger_findings = audit_ledger_bindings()
    if ledger_findings:
        mystery_findings.extend(ledger_findings)
        activity_findings.extend(ledger_findings)
        humor_findings.extend(ledger_findings)
    update_report(REVIEW_DIR / "season-mystery-review.json", mystery_result, mystery_findings)
    update_report(REVIEW_DIR / "season-activity-review.json", activity_result, activity_findings)
    update_report(REVIEW_DIR / "season-humor-review.json", humor_result, humor_findings)
    all_findings = mystery_findings + activity_findings + humor_findings
    print(json.dumps({"status": "REVIEWED-SEASON-PASS" if not all_findings else "OPEN", "findings": all_findings}, ensure_ascii=False, indent=2))
    return 0 if not all_findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
