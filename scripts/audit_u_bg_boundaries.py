from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
UNIT = ROOT / "qa/unit-slots.json"
BACKGROUND = ROOT / "qa/background-usage.json"
RELATION_EVIDENCE = ROOT / "qa/relationship-evidence.json"
REPORT = ROOT / "qa/reviews/u-bg-boundary-audit.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue(bucket: list[str], message: str) -> None:
    bucket.append(message)


def audit_units(roster: dict, unit: dict, relation_ids: set[str]) -> dict:
    findings: list[str] = []
    slots = unit.get("slots", [])
    expected_ids = {f"CHR-U-{number:03d}" for number in range(1, 121)}
    actual_ids = [item.get("id") for item in slots]
    if len(slots) != 120:
        issue(findings, f"U 槽位数量应为 120，实际 {len(slots)}")
    if len(actual_ids) != len(set(actual_ids)):
        issue(findings, "U 槽位存在重复 ID")
    if set(actual_ids) != expected_ids:
        issue(findings, "U 槽位 ID 未覆盖 CHR-U-001..120")
    if unit.get("pov_slot_count") != 22 or sum(bool(item.get("pov_slot")) for item in slots) != 22:
        issue(findings, "U POV 槽位数量不是 22")
    if unit.get("pov_candidate_count") != 44 or sum(bool(item.get("pov_candidate")) for item in slots) != 44:
        issue(findings, "U POV 候选数量不是 44")
    if unit.get("natural_return_candidate_count") != 40 or sum(bool(item.get("natural_return_candidate")) for item in slots) != 40:
        issue(findings, "U 自然回访候选数量不是 40")
    named_text = json.dumps(roster.get("named_characters", []), ensure_ascii=False)
    for item in slots:
        item_id = item.get("id", "?")
        if item.get("status") != "RESERVED":
            issue(findings, f"{item_id} 未保持 RESERVED")
        if item.get("relation_slot") not in relation_ids:
            issue(findings, f"{item_id} 的 relation_slot 无效: {item.get('relation_slot')}")
        if not item.get("eligible_profession_families"):
            issue(findings, f"{item_id} 缺少职业族候选")
        serialized = json.dumps(item, ensure_ascii=False)
        if any(name and name in serialized for name in _named_names(roster)):
            issue(findings, f"{item_id} 提前包含具名人物身份")
        for forbidden in ("episode_id", "microchapter_id", "microchapter_ids", "scene_id", "shot_id"):
            if forbidden in item:
                issue(findings, f"{item_id} 提前写入下游绑定字段 {forbidden}")
    return {
        "status": "PASS" if not findings else "FAIL",
        "slot_count": len(slots),
        "pov_slot_count": sum(bool(item.get("pov_slot")) for item in slots),
        "pov_candidate_count": sum(bool(item.get("pov_candidate")) for item in slots),
        "natural_return_candidate_count": sum(bool(item.get("natural_return_candidate")) for item in slots),
        "all_reserved": all(item.get("status") == "RESERVED" for item in slots),
        "no_named_identity": not any("提前包含具名人物身份" in finding for finding in findings),
        "no_downstream_bindings": not any("提前写入下游绑定字段" in finding for finding in findings),
        "findings": findings,
        "gate_note": "U 仅通过 Foundation 边界审计；Season Gate 前仍保持可替换候选，不分配唯一主线身份。",
    }


def _named_names(roster: dict) -> list[str]:
    names: list[str] = []
    for record in roster.get("named_characters", []):
        for key in ("name", "alias"):
            value = record.get(key)
            if isinstance(value, str) and value:
                names.append(value)
    return names


def audit_background(roster: dict, background: dict) -> dict:
    findings: list[str] = []
    archetypes = background.get("archetypes", [])
    expected_minimum = roster.get("background_archetypes", {}).get("minimum_count", 300)
    actual_ids = [item.get("id") for item in archetypes]
    required = {
        "ecosystem",
        "age_band",
        "occupation_family",
        "class_band",
        "region",
        "family_state",
        "active_time",
        "materials",
        "eligible_location_ids",
        "eligible_time_windows",
        "eligible_work_states",
        "microchapter_ids",
        "extension_ids",
        "static_decoration_record",
        "status",
    }
    if len(archetypes) < expected_minimum:
        issue(findings, f"BG 原型数量至少 {expected_minimum}，实际 {len(archetypes)}")
    if len(actual_ids) != len(set(actual_ids)):
        issue(findings, "BG 原型存在重复 ID")
    if background.get("static_decoration_records") != 0:
        issue(findings, "BG 顶层 static_decoration_records 必须为 0")
    for item in archetypes:
        item_id = item.get("id", "?")
        missing = sorted(required - set(item))
        if missing:
            issue(findings, f"{item_id} 缺少字段: {', '.join(missing)}")
        if item.get("status") != "RESERVED":
            issue(findings, f"{item_id} 未保持 RESERVED")
        if item.get("static_decoration_record") is not False:
            issue(findings, f"{item_id} 被标记为静态装饰")
        if item.get("microchapter_ids") != [] or item.get("extension_ids") != []:
            issue(findings, f"{item_id} 在 Episode Gate 前已有具体下游绑定")
        for key in ("eligible_location_ids", "eligible_time_windows", "eligible_work_states", "materials"):
            if not item.get(key):
                issue(findings, f"{item_id} 缺少可追溯的 {key}")
    return {
        "status": "PASS" if not findings else "FAIL",
        "archetype_count": len(archetypes),
        "minimum_count": expected_minimum,
        "all_reserved": all(item.get("status") == "RESERVED" for item in archetypes),
        "static_decoration_records": background.get("static_decoration_records"),
        "all_downstream_arrays_empty": all(item.get("microchapter_ids") == [] and item.get("extension_ids") == [] for item in archetypes),
        "all_usage_bindings_traceable": all(
            item.get("eligible_location_ids") and item.get("eligible_time_windows") and item.get("eligible_work_states")
            for item in archetypes
        ),
        "findings": findings,
        "gate_note": "BG 仅通过 Foundation 边界审计；Episode Gate 前不写入具体 microchapter_ids 或 extension_ids。",
    }


def main() -> int:
    roster = read_json(ROSTER)
    unit = read_json(UNIT)
    background = read_json(BACKGROUND)
    evidence = read_json(RELATION_EVIDENCE)
    relation_ids = {item.get("relation_id") for item in evidence.get("relationships", [])}
    report = {
        "schema_version": 1,
        "status": "PASS",
        "scope": "P1 U/BG boundary audit",
        "U": audit_units(roster, unit, relation_ids),
        "BG": audit_background(roster, background),
        "downstream_binding_policy": {
            "U": "RESERVED-UNTIL-SEASON-GATE",
            "BG": "RESERVED-UNTIL-EPISODE-GATE",
            "no_early_identity_assignment": True,
            "no_early_microchapter_binding": True,
        },
    }
    findings = report["U"]["findings"] + report["BG"]["findings"]
    report["status"] = "PASS" if not findings else "FAIL"
    report["findings"] = findings
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
