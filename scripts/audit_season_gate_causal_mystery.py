from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"
REVIEW = ROOT / "qa/reviews/season-gate-causal-mystery-review.json"
EPISODES = [f"S1-E{index:02d}" for index in range(1, 37)]
MYSTERY_PHASES = ("planted_episode", "recheck_episode", "reframe_episode", "arc_end_reveal_episode")
LEDGER_FIELDS = (
    "episode_id", "arc_id", "title", "status", "duration_minutes", "central_question",
    "opening_state", "city_evidence", "relationship_choice", "profession_action", "clue_seed",
    "misread", "recheck", "reframe", "irreversible_cost", "episode_choice", "tail_hook",
    "next_chase", "causal_chain", "continuity_refs", "pov_ids", "activity_ids", "humor_ids",
)
HOOK_FIELDS = (
    "chapter_id", "episode_id", "sequence", "duration_seconds", "pov_id", "pov_name", "function",
    "cold_hook", "goal_obstacle", "evidence_or_relationship_action", "choice_cost", "tail_hook_type",
    "tail_hook", "next_chase", "state_delta",
)
CHARACTERS = {
    item["id"]
    for item in json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))["named_characters"]
}
CHARACTER_NAMES_BY_ID = {
    item["id"]: item["name"]
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
EVENTS = {f"EVT-Y0-{index:03d}" for index in range(1, 11)}
OBSERVATIONS = {f"OBS-W-{index:03d}" for index in range(1, 11)}
FUNCTIONS = {
    "生活入口", "异常进入", "跨过门槛", "职业验证", "生活承载", "第一闭环", "换生活圈", "关系碰撞",
    "中点改义", "制度/利益反应", "落到具体人", "关系状态变化", "提出方案", "看见代价", "执行",
    "真相兑现", "伦理决定", "母集闭环",
}


def load_json(name: str) -> dict:
    return json.loads((SEASON_DIR / name).read_text(encoding="utf-8"))


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def episode_index(episode_id: str) -> int:
    return int(episode_id[-2:])


def finding(code: str, severity: str = "BLOCKING", **details: object) -> dict:
    return {"code": code, "severity": severity, **details}


def audit_episode_rows(ledger: dict, hooks: dict) -> tuple[dict, list[dict], dict[str, dict], dict[str, list[dict]]]:
    findings: list[dict] = []
    episodes = ledger.get("episodes", [])
    ids = [item.get("episode_id") for item in episodes]
    by_episode = {item.get("episode_id"): item for item in episodes}
    hooks_by_episode: dict[str, list[dict]] = defaultdict(list)

    if ledger.get("status") != "SEASON-DRAFT":
        findings.append(finding("ledger_status_not_season_draft", actual=ledger.get("status")))
    if len(episodes) != 36 or ids != EPISODES:
        findings.append(finding("episode_rows_not_ordered_or_complete", actual=len(episodes)))
    questions: list[str] = []
    for episode in episodes:
        episode_id = episode.get("episode_id")
        if episode.get("status") != "SEASON-DRAFT":
            findings.append(finding("episode_status_not_season_draft", episode_id=episode_id, actual=episode.get("status")))
        missing = [field for field in LEDGER_FIELDS if field not in episode or not nonempty(episode[field])]
        if missing:
            findings.append(finding("episode_missing_required_fields", episode_id=episode_id, fields=missing))
            continue
        questions.append(episode["central_question"])
        if episode["central_question"].count("？") + episode["central_question"].count("?") != 1:
            findings.append(finding("episode_central_question_not_single", episode_id=episode_id, severity="MAJOR"))
        city = episode["city_evidence"]
        if not any(city.get(key) for key in ("event_ids", "observation_ids", "object_ids", "clue_ids")):
            findings.append(finding("episode_has_no_city_evidence", episode_id=episode_id))
        if not city.get("location_ids") or not nonempty(city.get("description")) or not city.get("canon_refs"):
            findings.append(finding("episode_city_evidence_incomplete", episode_id=episode_id))
        unknown_events = [item for item in city.get("event_ids", []) if item not in EVENTS]
        unknown_observations = [item for item in city.get("observation_ids", []) if item not in OBSERVATIONS]
        unknown_locations = [item for item in city.get("location_ids", []) if item not in LOCATIONS]
        if unknown_events or unknown_observations or unknown_locations:
            findings.append(finding(
                "episode_city_reference_unknown", episode_id=episode_id, events=unknown_events,
                observations=unknown_observations, locations=unknown_locations,
            ))
        relation = episode["relationship_choice"]
        unknown_relations = [item for item in relation.get("relation_ids", []) if item not in RELATIONSHIPS]
        relation_characters = relation.get("character_ids", [])
        unknown_relation_characters = [item for item in relation_characters if item not in CHARACTERS]
        if unknown_relations or unknown_relation_characters:
            findings.append(finding(
                "episode_relationship_reference_unknown", episode_id=episode_id,
                relationships=unknown_relations, characters=unknown_relation_characters,
            ))
        profession = episode["profession_action"]
        if profession.get("character_id") not in CHARACTERS:
            findings.append(finding("episode_profession_character_unknown", episode_id=episode_id))
        capability = profession.get("capability_ref", "")
        if not isinstance(capability, str) or not (ROOT / capability).exists():
            findings.append(finding("episode_capability_ref_missing", episode_id=episode_id, path=capability))
        choice = episode["episode_choice"]
        if choice.get("actor") not in CHARACTERS:
            findings.append(finding("episode_choice_actor_unknown", episode_id=episode_id))
        elif choice["actor"] not in set(episode.get("pov_ids", [])) | set(relation_characters):
            findings.append(finding("episode_choice_actor_not_traceable", episode_id=episode_id, actor=choice["actor"], severity="MAJOR"))
        if profession.get("character_id") not in set(episode.get("pov_ids", [])) | set(relation_characters):
            findings.append(finding("episode_profession_action_not_traceable", episode_id=episode_id, severity="MAJOR"))
        unknown_pov = [item for item in episode.get("pov_ids", []) if item not in CHARACTERS]
        if unknown_pov:
            findings.append(finding("episode_pov_reference_unknown", episode_id=episode_id, characters=unknown_pov))
        if not episode.get("continuity_refs"):
            findings.append(finding("episode_continuity_refs_empty", episode_id=episode_id))
        hook = episode["tail_hook"]
        if not nonempty(hook.get("type")) or not nonempty(hook.get("text")):
            findings.append(finding("episode_tail_hook_incomplete", episode_id=episode_id))

    if len(questions) != len(set(questions)):
        findings.append(finding("central_questions_not_unique", severity="MAJOR"))
    hook_entries = hooks.get("entries", [])
    for item in hook_entries:
        hooks_by_episode[item.get("episode_id")].append(item)
    for episode_id in EPISODES:
        rows = hooks_by_episode.get(episode_id, [])
        if len(rows) != 18:
            findings.append(finding("episode_hook_count_invalid", episode_id=episode_id, actual=len(rows)))
            continue
        rows.sort(key=lambda row: row.get("sequence", 0))
        ledger_episode = by_episode.get(episode_id)
        if ledger_episode and rows[0].get("cold_hook") != ledger_episode.get("opening_state"):
            findings.append(finding("episode_opening_not_bound_to_first_hook", episode_id=episode_id, severity="MAJOR"))
        if ledger_episode and rows[-1].get("next_chase") != ledger_episode.get("next_chase"):
            findings.append(finding("episode_next_chase_not_bound_to_final_hook", episode_id=episode_id, severity="MAJOR"))
        if ledger_episode and rows[-1].get("tail_hook_type") != ledger_episode.get("tail_hook", {}).get("type"):
            findings.append(finding("episode_tail_hook_type_not_bound", episode_id=episode_id, severity="MAJOR"))
    return {
        "episode_total": len(episodes),
        "chapter_total": len(hook_entries),
        "questions_unique": len(questions) == len(set(questions)) == 36,
        "episode_statuses": Counter(item.get("status") for item in episodes),
    }, findings, by_episode, hooks_by_episode


def audit_mystery_chains(matrix: dict, episodes: dict[str, dict]) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = matrix.get("entries", [])
    bindings = matrix.get("episode_bindings", [])
    if matrix.get("status") != "SEASON-DRAFT":
        findings.append(finding("mystery_matrix_status_not_season_draft", actual=matrix.get("status")))
    if len(entries) != 18:
        findings.append(finding("mystery_chain_total_invalid", actual=len(entries)))
    binding_map = {item.get("episode_id"): item for item in bindings}
    if [item.get("episode_id") for item in bindings] != EPISODES:
        findings.append(finding("mystery_bindings_not_ordered_or_complete"))
    known_mystery_ids = {item.get("mystery_id") for item in entries}
    for binding in bindings:
        episode_id = binding.get("episode_id")
        unknown_ids = [item for item in binding.get("ids", []) if item not in known_mystery_ids]
        if not binding.get("ids") or not nonempty(binding.get("reversal_type")):
            findings.append(finding("mystery_binding_incomplete", episode_id=episode_id))
        if unknown_ids:
            findings.append(finding("mystery_binding_unknown_id", episode_id=episode_id, mystery_ids=unknown_ids))
        expected_arc = f"ARC-{((episode_index(episode_id) - 1) // 6) + 1:02d}" if episode_id in EPISODES else None
        if expected_arc and binding.get("arc_id") != expected_arc:
            findings.append(finding("mystery_binding_arc_mismatch", episode_id=episode_id, actual=binding.get("arc_id")))
    for entry in entries:
        mystery_id = entry.get("mystery_id")
        phases = [entry.get(field) for field in MYSTERY_PHASES]
        missing = [field for field in ("mystery_id", "arc_id", "question", *MYSTERY_PHASES, "true_reframe", "cost_of_knowing", "information_owner", "audience_knowledge", "character_misread", "reframe_type", "irreversible_reveal", "episode_refs") if not nonempty(entry.get(field))]
        if missing:
            findings.append(finding("mystery_chain_missing_fields", mystery_id=mystery_id, fields=missing))
            continue
        if any(phase not in EPISODES for phase in phases) or phases != sorted(phases, key=episode_index):
            findings.append(finding("mystery_phase_order_invalid", mystery_id=mystery_id, phases=phases))
        if any(character_id not in CHARACTERS for character_id in entry.get("information_owner", [])):
            findings.append(finding("mystery_information_owner_unknown", mystery_id=mystery_id))
        if any(episode_id not in EPISODES for episode_id in entry.get("episode_refs", [])):
            findings.append(finding("mystery_episode_ref_unknown", mystery_id=mystery_id))
        phase_set = set(phases)
        if not phase_set.issubset(set(entry.get("episode_refs", []))):
            findings.append(finding("mystery_phase_not_in_episode_refs", mystery_id=mystery_id))
        for phase in phase_set:
            if phase not in episodes:
                continue
            binding = binding_map.get(phase, {})
            if mystery_id not in binding.get("ids", []):
                findings.append(finding("mystery_phase_binding_missing", mystery_id=mystery_id, episode_id=phase))
        planted = episodes.get(entry["planted_episode"], {})
        recheck = episodes.get(entry["recheck_episode"], {})
        reframe = episodes.get(entry["reframe_episode"], {})
        reveal = episodes.get(entry["arc_end_reveal_episode"], {})
        if not planted.get("clue_seed", {}).get("source_ids"):
            findings.append(finding("mystery_planted_without_evidence", mystery_id=mystery_id, severity="MAJOR"))
        if not nonempty(recheck.get("recheck")) or not recheck.get("city_evidence", {}).get("canon_refs"):
            findings.append(finding("mystery_recheck_without_evidence", mystery_id=mystery_id, severity="MAJOR"))
        if not nonempty(reframe.get("reframe")) or not nonempty(entry.get("true_reframe")):
            findings.append(finding("mystery_reframe_without_changed_meaning", mystery_id=mystery_id, severity="MAJOR"))
        if not nonempty(reveal.get("irreversible_cost")) or not nonempty(entry.get("irreversible_reveal")):
            findings.append(finding("mystery_reveal_without_irreversible_cost", mystery_id=mystery_id, severity="MAJOR"))
        if not nonempty(reframe.get("relationship_choice", {}).get("delta")) or not nonempty(reframe.get("episode_choice", {}).get("state_change")):
            findings.append(finding("mystery_reframe_does_not_change_relationship_or_action", mystery_id=mystery_id, severity="MAJOR"))
    reversal_types = [item.get("reversal_type") for item in bindings]
    for index in range(1, len(reversal_types)):
        if reversal_types[index] == reversal_types[index - 1]:
            findings.append(finding("adjacent_mystery_reversal_types_repeat", episode_id=EPISODES[index], severity="MAJOR"))
    return {
        "mystery_total": len(entries),
        "episode_binding_total": len(bindings),
        "phase_traceable": not any(item["code"].startswith("mystery_") for item in findings),
    }, findings


def audit_hooks(hooks: dict, episodes: dict[str, dict], hooks_by_episode: dict[str, list[dict]]) -> tuple[dict, list[dict]]:
    findings: list[dict] = []
    entries = hooks.get("entries", [])
    if hooks.get("status") != "SEASON-DRAFT":
        findings.append(finding("hook_map_status_not_season_draft", actual=hooks.get("status")))
    expected_ids = [f"S1-E{episode:02d}-M{chapter:02d}" for episode in range(1, 37) for chapter in range(1, 19)]
    if len(entries) != 648 or [item.get("chapter_id") for item in entries] != expected_ids:
        findings.append(finding("hook_rows_not_ordered_or_complete", actual=len(entries)))
    for item in entries:
        chapter_id = item.get("chapter_id")
        missing = [field for field in HOOK_FIELDS if field not in item or not nonempty(item[field])]
        if missing:
            findings.append(finding("chapter_missing_playable_fields", chapter_id=chapter_id, fields=missing))
            continue
        if item.get("pov_id") not in CHARACTERS:
            findings.append(finding("chapter_pov_unknown", chapter_id=chapter_id))
        expected_pov_name = CHARACTER_NAMES_BY_ID.get(item.get("pov_id"))
        if expected_pov_name and item.get("pov_name") != expected_pov_name:
            findings.append(finding(
                "chapter_pov_name_mismatch",
                chapter_id=chapter_id,
                pov_id=item.get("pov_id"),
                actual=item.get("pov_name"),
                expected=expected_pov_name,
            ))
        if item.get("function") not in FUNCTIONS:
            findings.append(finding("chapter_function_unknown", chapter_id=chapter_id))
        if not 120 <= int(item.get("duration_seconds", 0)) <= 180:
            findings.append(finding("chapter_duration_out_of_range", chapter_id=chapter_id))
    for episode_id in EPISODES:
        rows = sorted(hooks_by_episode.get(episode_id, []), key=lambda row: row.get("sequence", 0))
        types = [row.get("tail_hook_type") for row in rows]
        for index in range(1, len(types)):
            if types[index] == types[index - 1]:
                findings.append(finding("adjacent_chapter_hook_types_repeat", episode_id=episode_id, sequence=index + 1, severity="MAJOR"))
        for index in range(2, len(types)):
            if types[index] == types[index - 1] == types[index - 2]:
                findings.append(finding("three_chapter_hook_types_repeat", episode_id=episode_id, sequence=index + 1, severity="MAJOR"))
        if rows and episodes.get(episode_id):
            final = rows[-1]
            ledger_episode = episodes[episode_id]
            if final.get("tail_hook_type") != ledger_episode.get("tail_hook", {}).get("type"):
                findings.append(finding("final_chapter_hook_type_not_episode_hook", episode_id=episode_id, severity="MAJOR"))
            if final.get("next_chase") != ledger_episode.get("next_chase"):
                findings.append(finding("final_chapter_next_chase_not_episode_chase", episode_id=episode_id, severity="MAJOR"))
    return {
        "chapter_total": len(entries),
        "chapters_per_episode": all(len(hooks_by_episode.get(episode_id, [])) == 18 for episode_id in EPISODES),
        "hook_types_adjacent_distinct": not any(item["code"].startswith("adjacent_chapter") for item in findings),
    }, findings


def audit() -> dict:
    ledger = load_json("season-causal-ledger.json")
    mystery = load_json("mystery-reversal-matrix.json")
    hooks = load_json("short-chapter-hook-map.json")
    episode_result, episode_findings, episodes, hooks_by_episode = audit_episode_rows(ledger, hooks)
    mystery_result, mystery_findings = audit_mystery_chains(mystery, episodes)
    hook_result, hook_findings = audit_hooks(hooks, episodes, hooks_by_episode)
    findings = episode_findings + mystery_findings + hook_findings
    report = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        "scope": "P2 SG-01 independent causal and mystery Season Gate review",
        "episode_total": episode_result["episode_total"],
        "mystery_total": mystery_result["mystery_total"],
        "chapter_total": hook_result["chapter_total"],
        "checks": {
            "episode_rows_complete": episode_result["episode_total"] == 36,
            "episode_statuses_season_draft": all(value == 36 if key == "SEASON-DRAFT" else value == 0 for key, value in episode_result["episode_statuses"].items()),
            "one_unique_central_question_per_episode": episode_result["questions_unique"],
            "city_profession_relationship_cost_present": not any(item["code"].startswith("episode_") and item["code"] not in {"episode_rows_not_ordered_or_complete", "episode_status_not_season_draft", "episode_continuity_refs_empty"} for item in findings),
            "mystery_phase_traceable": mystery_result["phase_traceable"],
            "mystery_reveals_change_state": not any(item["code"] == "mystery_reframe_does_not_change_relationship_or_action" for item in findings),
            "chapter_rows_complete": hook_result["chapter_total"] == 648 and hook_result["chapters_per_episode"],
            "chapter_pov_name_identity_consistent": not any(item["code"] == "chapter_pov_name_mismatch" for item in findings),
            "chapter_hook_chain_playable": not any(item["code"] == "chapter_missing_playable_fields" for item in findings),
            "adjacent_hook_types_distinct": hook_result["hook_types_adjacent_distinct"],
            "episode_tail_hooks_bound": not any(item["code"].startswith("final_chapter_") or item["code"].startswith("episode_") and "bound" in item["code"] for item in findings),
        },
        "findings": findings,
        "deferred_followup": [
            "SG-02 已独立完成；本报告不替代其关系、宋代活动、幽默与 U/BG 可替换边界结论。",
            "Episode Gate 再把每章目标/阻力/选择与正式逐场剧本、表演、分镜、AIGC 资产和连续性账本绑定。",
            "本报告不锁定最终对白、shot ID、U 唯一身份或 BG 微章 ID；Season Gate 决议由独立 Gate 证书维护。",
        ],
    }
    REVIEW.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-SEASON-PASS" else 1)
