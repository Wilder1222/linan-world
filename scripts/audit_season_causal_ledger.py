from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "story/season/season-causal-ledger.json"
REPORT = ROOT / "qa/reviews/season-causal-ledger-review.json"
REQUIRED = (
    "episode_id", "arc_id", "title", "status", "duration_minutes", "central_question",
    "opening_state", "city_evidence", "relationship_choice", "profession_action", "clue_seed",
    "misread", "recheck", "reframe", "irreversible_cost", "episode_choice", "tail_hook",
    "next_chase", "causal_chain", "continuity_refs", "pov_ids", "activity_ids", "humor_ids",
)
SAMPLE_IDS = [f"S1-E{index:02d}" for index in range(1, 7)]
ALL_IDS = [f"S1-E{index:02d}" for index in range(1, 37)]
EVENT_IDS = {f"EVT-Y0-{index:03d}" for index in range(1, 11)}
OBS_IDS = {f"OBS-W-{index:03d}" for index in range(1, 11)}
REL_IDS = {item["id"] for item in json.loads((ROOT / "qa/relationship-slots.json").read_text(encoding="utf-8")).get("relationships", [])}
CHAR_IDS = {item["id"] for item in json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8")).get("named_characters", [])}
LOC_IDS = set(re.findall(r"\|\s*(LOC-\d{3})\s*\|", (ROOT / "canon/city/00-city-index.md").read_text(encoding="utf-8")))


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value) and all(nonempty(item) for item in value.values())
    return value is not None


def audit() -> dict:
    findings: list[dict[str, object]] = []
    if not LEDGER.exists():
        findings.append({"code": "ledger_missing"})
        return {"status": "OPEN", "scope": "P2 Season causal ledger", "findings": findings}
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    ids = [item.get("episode_id") for item in episodes]
    if len(episodes) != 36:
        findings.append({"code": "episode_count", "actual": len(episodes), "expected": 36})
    if ids != ALL_IDS:
        findings.append({"code": "episode_ids_not_ordered_or_complete"})
    # S2-C promotes the same ledger from a six-episode sample to a season draft.
    # Keep the S2-A sample audit path intact for historical reruns, but apply a
    # complete-field audit when the root status is SEASON-DRAFT.
    if data.get("status") == "SEASON-DRAFT":
        complete = 0
        for item in episodes:
            episode_id = item.get("episode_id")
            for field in ("central_question", "opening_state", "misread", "recheck", "reframe", "irreversible_cost", "next_chase"):
                if not nonempty(item.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_empty_{field}"})
            city = item.get("city_evidence") or {}
            for field in ("description", "canon_refs", "location_ids"):
                if not nonempty(city.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_city_{field}"})
            relation = item.get("relationship_choice") or {}
            for field in ("relation_ids", "character_ids", "choice", "delta", "evidence_ids"):
                if not nonempty(relation.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_relation_{field}"})
            profession = item.get("profession_action") or {}
            for field in ("character_id", "action", "capability_ref"):
                if not nonempty(profession.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_profession_{field}"})
            choice = item.get("episode_choice") or {}
            for field in ("actor", "action", "cost", "state_change"):
                if not nonempty(choice.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_choice_{field}"})
            hook = item.get("tail_hook") or {}
            if not nonempty(hook.get("type")) or not nonempty(hook.get("text")):
                findings.append({"episode_id": episode_id, "code": "season_tail_hook_incomplete"})
            chain = item.get("causal_chain") or {}
            for field in ("seed", "misread", "recheck", "reframe"):
                if not nonempty(chain.get(field)):
                    findings.append({"episode_id": episode_id, "code": f"season_chain_{field}"})
            refs = city.get("event_ids", []) + city.get("observation_ids", []) + city.get("location_ids", [])
            unknown_events = [ref for ref in city.get("event_ids", []) if ref not in EVENT_IDS]
            unknown_obs = [ref for ref in city.get("observation_ids", []) if ref not in OBS_IDS]
            unknown_locs = [ref for ref in city.get("location_ids", []) if ref not in LOC_IDS]
            unknown_rels = [ref for ref in relation.get("relation_ids", []) if ref not in REL_IDS]
            unknown_chars = [ref for ref in relation.get("character_ids", []) + item.get("pov_ids", []) if ref not in CHAR_IDS]
            if unknown_events or unknown_obs or unknown_locs or unknown_rels or unknown_chars:
                findings.append({"episode_id": episode_id, "code": "unknown_reference", "events": unknown_events, "observations": unknown_obs, "locations": unknown_locs, "relations": unknown_rels, "characters": unknown_chars})
            if not refs:
                findings.append({"episode_id": episode_id, "code": "season_no_city_reference"})
            if not Path(profession.get("capability_ref", "")).exists():
                findings.append({"episode_id": episode_id, "code": "capability_ref_missing", "path": profession.get("capability_ref")})
            if nonempty(item.get("central_question")) and nonempty(item.get("episode_choice")):
                complete += 1
        hook_types = [item.get("tail_hook", {}).get("type") for item in episodes]
        for index in range(1, len(hook_types)):
            if hook_types[index] == hook_types[index - 1]:
                findings.append({"code": "adjacent_hook_type_repeated", "index": index})
        report = {
            "schema_version": 1,
            "status": "REVIEWED-SEASON-PASS" if not findings and complete == len(ALL_IDS) else "OPEN",
            "scope": "P2 Season causal ledger full season review",
            "episode_total": len(episodes),
            "season_complete": complete,
            "sample_window": SAMPLE_IDS,
            "draft_scaffold_total": 0,
            "required_fields_per_episode": list(REQUIRED),
            "checks": {
                "episode_rows": len(episodes) == 36,
                "season_rows_complete": complete == 36,
                "references_traceable": not any(item.get("code") == "unknown_reference" for item in findings),
                "capability_refs_traceable": not any(item.get("code") == "capability_ref_missing" for item in findings),
                "adjacent_hooks_distinct": not any(item.get("code") == "adjacent_hook_type_repeated" for item in findings),
            },
            "findings": findings,
            "deferred_followup": [
                "Episode Gate 将把逐章钩子映射绑定到逐场剧本、表演、分镜与 AIGC 资产。",
                "Season Gate 前不绑定最终对白、shot ID、U 唯一身份或 BG 微章 ID。",
            ],
        }
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    sample_complete = 0
    for item in episodes:
        episode_id = item.get("episode_id")
        for field in REQUIRED:
            if field not in item:
                findings.append({"episode_id": episode_id, "code": f"missing_{field}"})
        if episode_id not in SAMPLE_IDS:
            if item.get("status") != "DRAFT-SCAFFOLD":
                findings.append({"episode_id": episode_id, "code": "non_sample_not_scaffold"})
            continue
        sample_complete += 1
        for field in ("central_question", "opening_state", "misread", "recheck", "reframe", "irreversible_cost", "next_chase"):
            if not nonempty(item.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_empty_{field}"})
        city = item.get("city_evidence") or {}
        for field in ("description", "canon_refs", "location_ids"):
            if not nonempty(city.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_city_{field}"})
        relation = item.get("relationship_choice") or {}
        for field in ("relation_ids", "character_ids", "choice", "delta", "evidence_ids"):
            if not nonempty(relation.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_relation_{field}"})
        profession = item.get("profession_action") or {}
        for field in ("character_id", "action", "capability_ref"):
            if not nonempty(profession.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_profession_{field}"})
        choice = item.get("episode_choice") or {}
        for field in ("actor", "action", "cost", "state_change"):
            if not nonempty(choice.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_choice_{field}"})
        hook = item.get("tail_hook") or {}
        if not nonempty(hook.get("type")) or not nonempty(hook.get("text")):
            findings.append({"episode_id": episode_id, "code": "sample_tail_hook_incomplete"})
        chain = item.get("causal_chain") or {}
        for field in ("seed", "misread", "recheck", "reframe"):
            if not nonempty(chain.get(field)):
                findings.append({"episode_id": episode_id, "code": f"sample_chain_{field}"})
        refs = city.get("event_ids", []) + city.get("observation_ids", []) + city.get("location_ids", [])
        unknown_events = [ref for ref in city.get("event_ids", []) if ref not in EVENT_IDS]
        unknown_obs = [ref for ref in city.get("observation_ids", []) if ref not in OBS_IDS]
        unknown_locs = [ref for ref in city.get("location_ids", []) if ref not in LOC_IDS]
        unknown_rels = [ref for ref in relation.get("relation_ids", []) if ref not in REL_IDS]
        unknown_chars = [ref for ref in relation.get("character_ids", []) + item.get("pov_ids", []) if ref not in CHAR_IDS]
        if unknown_events or unknown_obs or unknown_locs or unknown_rels or unknown_chars:
            findings.append({"episode_id": episode_id, "code": "unknown_reference", "events": unknown_events, "observations": unknown_obs, "locations": unknown_locs, "relations": unknown_rels, "characters": unknown_chars})
        if not refs:
            findings.append({"episode_id": episode_id, "code": "sample_no_city_reference"})
    sample_hook_types = [
        next(item["tail_hook"]["type"] for item in episodes if item.get("episode_id") == episode_id)
        for episode_id in SAMPLE_IDS
    ]
    for index in range(1, len(sample_hook_types)):
        if sample_hook_types[index] == sample_hook_types[index - 1]:
            findings.append({"code": "adjacent_sample_hook_type_repeated", "index": index})
    status = "REVIEWED-SAMPLE-PASS" if not findings and sample_complete == len(SAMPLE_IDS) else "OPEN"
    report = {
        "schema_version": 1,
        "status": status,
        "scope": "P2 Season causal ledger sample review",
        "episode_total": len(episodes),
        "sample_window": SAMPLE_IDS,
        "sample_complete": sample_complete,
        "draft_scaffold_total": len(episodes) - sample_complete,
        "required_fields_per_episode": list(REQUIRED),
        "checks": {
            "episode_rows": len(episodes) == 36,
            "sample_rows_complete": sample_complete == 6,
            "sample_causal_chain": not any(item.get("code", "").startswith("sample_chain") for item in findings),
            "sample_references_traceable": not any(item.get("code") == "unknown_reference" for item in findings),
            "adjacent_sample_hooks_distinct": not any(item.get("code") == "adjacent_sample_hook_type_repeated" for item in findings),
        },
        "findings": findings,
        "deferred_followup": [
            "S2-B 将把悬疑翻转、宋代活动与幽默挂到具体集/章。",
            "S2-C 将把 36 集账本扩展为 648 个 2–3 分钟短章钩子。",
            "Season Gate 前不绑定最终对白、shot ID、U 唯一身份或 BG 微章 ID。",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "REVIEWED-SAMPLE-PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
