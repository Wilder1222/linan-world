from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"
REVIEW_PATH = ROOT / "qa/reviews/season-u-boundary-review.json"
SELECTION_PATH = SEASON_DIR / "u-candidate-selection.json"
UNIT_PATH = ROOT / "qa/unit-slots.json"
HOOK_PATH = SEASON_DIR / "short-chapter-hook-map.json"
BG_PATH = ROOT / "qa/background-usage.json"
EPISODES = {f"S1-E{i:02d}" for i in range(1, 37)}
WINDOWS = {
    "ARC1-ARC2": (1, 12),
    "ARC2-ARC3": (7, 18),
    "ARC3-ARC5": (13, 30),
    "ARC4-ARC6": (19, 36),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def audit() -> dict:
    findings: list[dict] = []
    selection = load(SELECTION_PATH)
    source = load(UNIT_PATH)
    hooks = load(HOOK_PATH)
    bg = load(BG_PATH)
    source_slots = {item["id"]: item for item in source["slots"]}
    hook_by_id = {item["chapter_id"]: item for item in hooks["entries"]}

    if selection.get("status") != "SEASON-DRAFT":
        findings.append({"code": "selection_status_invalid"})
    if selection.get("slot_total") != 120 or len(selection.get("slots", [])) != 120:
        findings.append({"code": "slot_total_invalid", "actual": len(selection.get("slots", []))})
    selected_pov = selection.get("pov_selections", [])
    selected_returns = selection.get("natural_return_selections", [])
    if len(selected_pov) != 22:
        findings.append({"code": "pov_selection_count_invalid", "actual": len(selected_pov)})
    if len(selected_returns) < 40:
        findings.append({"code": "return_selection_count_invalid", "actual": len(selected_returns)})

    source_ids = set(source_slots)
    slot_rows = selection.get("slots", [])
    row_ids = [item.get("slot_id") for item in slot_rows]
    if set(row_ids) != source_ids or len(row_ids) != len(set(row_ids)):
        findings.append({"code": "slot_identity_or_uniqueness_invalid"})
    if any(item.get("source_status") != "RESERVED" for item in slot_rows):
        findings.append({"code": "source_reserved_status_changed"})
    if any(item.get("named_identity") is not None for item in slot_rows):
        findings.append({"code": "slot_named_identity_assigned"})
    if any(item.get("binding_status") != "RESERVED-UNTIL-SEASON-GATE" for item in slot_rows):
        findings.append({"code": "slot_binding_status_invalid"})

    pov_ids = [item.get("slot_id") for item in selected_pov]
    return_ids = [item.get("slot_id") for item in selected_returns]
    if len(set(pov_ids)) != len(pov_ids) or any(item not in source_ids for item in pov_ids):
        findings.append({"code": "pov_slot_refs_invalid"})
    if len(set(return_ids)) != len(return_ids) or any(item not in source_ids for item in return_ids):
        findings.append({"code": "return_slot_refs_invalid"})
    if any(not source_slots[item].get("pov_slot") for item in pov_ids if item in source_slots):
        findings.append({"code": "pov_selection_not_from_pov_slots"})
    if any(not source_slots[item].get("natural_return_candidate") for item in return_ids if item in source_slots):
        findings.append({"code": "return_selection_not_from_return_pool"})

    def check_context(context: dict, owner: str) -> None:
        chapter_id = context.get("chapter_id")
        episode_id = context.get("episode_id")
        if chapter_id not in hook_by_id or episode_id not in EPISODES:
            findings.append({"code": "context_ref_untraceable", "owner": owner, "chapter_id": chapter_id})
            return
        if hook_by_id[chapter_id].get("episode_id") != episode_id:
            findings.append({"code": "context_episode_mismatch", "owner": owner, "chapter_id": chapter_id})
        trace = context.get("traceability", {})
        if not nonempty(trace.get("ledger_ref")) or not nonempty(trace.get("hook_ref")):
            findings.append({"code": "context_traceability_missing", "owner": owner})

    def episode_number(episode_id: str) -> int:
        return int(episode_id[-2:])

    def check_window(slot_id: str, episode_id: str, owner: str) -> None:
        slot = source_slots.get(slot_id)
        if not slot or slot.get("window") not in WINDOWS:
            findings.append({"code": "source_window_invalid", "owner": owner})
            return
        low, high = WINDOWS[slot["window"]]
        if not low <= episode_number(episode_id) <= high:
            findings.append({"code": "context_outside_slot_window", "owner": owner, "episode_id": episode_id})

    for item in selected_pov:
        slot_id = item.get("slot_id")
        if item.get("named_identity") is not None or item.get("binding_status") != "RESERVED-UNTIL-SEASON-GATE":
            findings.append({"code": "pov_candidate_locked_too_early", "slot_id": slot_id})
        check_context(item.get("candidate_context", {}), slot_id)
        check_window(slot_id, item.get("candidate_context", {}).get("episode_id", ""), slot_id)
        if not nonempty(item.get("replacement_rule")):
            findings.append({"code": "pov_replacement_rule_missing", "slot_id": slot_id})

    for item in selected_returns:
        slot_id = item.get("slot_id")
        if item.get("named_identity") is not None or item.get("binding_status") != "RESERVED-UNTIL-SEASON-GATE":
            findings.append({"code": "return_candidate_locked_too_early", "slot_id": slot_id})
        first = item.get("first_appearance_context", {})
        returned = item.get("return_appearance_context", {})
        check_context(first, slot_id + ":first")
        check_context(returned, slot_id + ":return")
        check_window(slot_id, first.get("episode_id", ""), slot_id + ":first")
        check_window(slot_id, returned.get("episode_id", ""), slot_id + ":return")
        if first.get("episode_id") == returned.get("episode_id"):
            findings.append({"code": "return_not_later_than_first", "slot_id": slot_id})
        elif first.get("episode_id") and returned.get("episode_id") and episode_number(returned["episode_id"]) <= episode_number(first["episode_id"]):
            findings.append({"code": "return_not_after_first", "slot_id": slot_id})
        if not nonempty(item.get("return_reason")) or not nonempty(item.get("state_transfer")):
            findings.append({"code": "return_boundary_fields_missing", "slot_id": slot_id})
        if not nonempty(item.get("replacement_rule")):
            findings.append({"code": "return_replacement_rule_missing", "slot_id": slot_id})

    alternate_ids = {item["id"] for item in source["slots"] if item.get("pov_candidate") and not item.get("pov_slot")}
    reported_alternates = {
        item["slot_id"] for item in slot_rows if "POV-ALTERNATE" in item.get("selection_roles", [])
    }
    if alternate_ids != reported_alternates:
        findings.append({"code": "alternate_pov_pool_mismatch"})

    if bg.get("static_decoration_records") != 0:
        findings.append({"code": "bg_static_decoration_records_nonzero"})
    if any(item.get("status") != "RESERVED" for item in bg.get("archetypes", [])):
        findings.append({"code": "bg_status_changed"})
    if any(item.get("microchapter_ids") or item.get("extension_ids") for item in bg.get("archetypes", [])):
        findings.append({"code": "bg_downstream_binding_present"})

    selected_union = set(pov_ids) | set(return_ids)
    reserved_unselected = [item for item in slot_rows if item["slot_id"] not in selected_union]
    if any(item.get("selection_status") not in {"RESERVED", "RESERVED-ALTERNATE-POV"} for item in reserved_unselected):
        findings.append({"code": "unselected_u_not_reserved"})

    result = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        "scope": "P2 S2-06 U candidate and natural return boundary review",
        "slot_total": len(slot_rows),
        "pov_slot_total": len(selected_pov),
        "natural_return_candidate_total": len(selected_returns),
        "selected_slot_total": len(selected_union),
        "alternate_pov_total": len(reported_alternates),
        "reserved_unselected_total": len(reserved_unselected),
        "checks": {
            "all_120_slots_preserve_reserved_source": not any(item.get("code") == "source_reserved_status_changed" for item in findings),
            "22_pov_slots_selected_and_traceable": len(selected_pov) == 22 and not any(item.get("code", "").startswith("pov_") or item.get("code") == "context_ref_untraceable" for item in findings),
            "40_natural_returns_selected_and_traceable": len(selected_returns) >= 40 and not any(item.get("code", "").startswith("return_") or item.get("code") == "context_ref_untraceable" for item in findings),
            "unselected_u_reserved": not any(item.get("code") == "unselected_u_not_reserved" for item in findings),
            "no_named_identity_assigned": not any(item.get("code") == "slot_named_identity_assigned" or item.get("code", "").endswith("locked_too_early") for item in findings),
            "bg_not_bound": not any(item.get("code") in {"bg_static_decoration_records_nonzero", "bg_status_changed", "bg_downstream_binding_present"} for item in findings),
            "replacement_rules_present": not any(item.get("code", "").endswith("replacement_rule_missing") for item in findings),
        },
        "findings": findings,
        "deferred_followup": [
            "Season Gate 通过后才可把候选 U 槽位写入唯一姓名与最终关系/场次。",
            "Episode Gate 通过后才可为 BG 原型写入具体 microchapter_ids 与 extension_ids。",
        ],
    }
    REVIEW_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    report = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "REVIEWED-SEASON-PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
