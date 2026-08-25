from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from scripts.audit_season_causal_ledger import audit as audit_ledger
except ModuleNotFoundError:  # direct execution: Python places scripts/ on sys.path
    from audit_season_causal_ledger import audit as audit_ledger


ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "story/season/short-chapter-hook-map.json"
HOOK_SCHEMA = ROOT / "story/season/short-chapter-hook-map.schema.json"
REPORT = ROOT / "qa/reviews/season-s2c-review.json"
HOOK_REPORT = ROOT / "qa/reviews/season-hook-review.json"
ALL_EPISODES = [f"S1-E{i:02d}" for i in range(1, 37)]
FUNCTIONS = {"生活入口", "异常进入", "跨过门槛", "职业验证", "生活承载", "第一闭环", "换生活圈", "关系碰撞", "中点改义", "制度/利益反应", "落到具体人", "关系状态变化", "提出方案", "看见代价", "执行", "真相兑现", "伦理决定", "母集闭环"}
CHAR_IDS = {item["id"] for item in json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))["named_characters"]}


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def audit() -> dict:
    findings: list[dict[str, object]] = []
    ledger_report = audit_ledger()
    if ledger_report["status"] != "REVIEWED-SEASON-PASS":
        findings.append({"code": "ledger_not_season_pass", "status": ledger_report["status"]})
    if not HOOK_PATH.exists():
        findings.append({"code": "hook_map_missing"})
        report = {"schema_version": 1, "status": "OPEN", "scope": "P2 S2-C review", "findings": findings}
        serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        REPORT.write_text(serialized, encoding="utf-8")
        HOOK_REPORT.write_text(serialized, encoding="utf-8")
        return report
    data = json.loads(HOOK_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if data.get("status") != "SEASON-DRAFT":
        findings.append({"code": "hook_map_status", "actual": data.get("status")})
    if len(entries) != 648:
        findings.append({"code": "chapter_total", "actual": len(entries), "expected": 648})
    ids = [item.get("chapter_id") for item in entries]
    expected_ids = [f"S1-E{episode:02d}-M{chapter:02d}" for episode in range(1, 37) for chapter in range(1, 19)]
    if ids != expected_ids:
        findings.append({"code": "chapter_ids_not_ordered_or_complete"})
    by_episode: dict[str, list[dict]] = {episode_id: [] for episode_id in ALL_EPISODES}
    for item in entries:
        episode_id = item.get("episode_id")
        if episode_id not in by_episode:
            findings.append({"code": "unknown_episode", "episode_id": episode_id})
            continue
        by_episode[episode_id].append(item)
        if item.get("pov_id") not in CHAR_IDS:
            findings.append({"code": "unknown_pov", "chapter_id": item.get("chapter_id"), "pov_id": item.get("pov_id")})
        if item.get("function") not in FUNCTIONS:
            findings.append({"code": "unknown_function", "chapter_id": item.get("chapter_id"), "function": item.get("function")})
        for field in ("cold_hook", "goal_obstacle", "evidence_or_relationship_action", "choice_cost", "tail_hook_type", "tail_hook", "next_chase", "state_delta"):
            if not nonempty(item.get(field)):
                findings.append({"code": f"empty_{field}", "chapter_id": item.get("chapter_id")})
        if not 120 <= int(item.get("duration_seconds", 0)) <= 180:
            findings.append({"code": "duration_out_of_range", "chapter_id": item.get("chapter_id")})
    for episode_id in ALL_EPISODES:
        chapter_rows = by_episode[episode_id]
        if len(chapter_rows) != 18:
            findings.append({"code": "episode_chapter_count", "episode_id": episode_id, "actual": len(chapter_rows)})
        types = [item.get("tail_hook_type") for item in chapter_rows]
        for index in range(1, len(types)):
            if types[index] == types[index - 1]:
                findings.append({"code": "adjacent_chapter_hook_type_repeated", "episode_id": episode_id, "sequence": index + 1})
        if chapter_rows and chapter_rows[-1].get("tail_hook_type") != json.loads((ROOT / "story/season/season-causal-ledger.json").read_text(encoding="utf-8"))["episodes"][int(episode_id[-2:]) - 1]["tail_hook"]["type"]:
            findings.append({"code": "episode_tail_hook_not_bound", "episode_id": episode_id})
    report = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        "scope": "P2 S2-C causal ledger and 648 short chapter hook review",
        "episode_total": 36,
        "chapter_total": len(entries),
        "checks": {
            "ledger_complete": ledger_report["status"] == "REVIEWED-SEASON-PASS",
            "chapter_rows": len(entries) == 648,
            "ordered_ids": ids == expected_ids,
            "eighteen_per_episode": all(len(by_episode[e]) == 18 for e in ALL_EPISODES),
            "playable_fields": not any(item.get("code", "").startswith("empty_") for item in findings),
            "pov_refs_traceable": not any(item.get("code") == "unknown_pov" for item in findings),
            "adjacent_hooks_distinct": not any(item.get("code") == "adjacent_chapter_hook_type_repeated" for item in findings),
            "episode_tail_hooks_bound": not any(item.get("code") == "episode_tail_hook_not_bound" for item in findings),
        },
        "findings": findings,
        "deferred_followup": [
            "Episode Gate 将把每章 objective/obstacle/choice/state_delta 与逐场剧本、关系快照和资产账本绑定。",
            "在完成 Episode Gate 前不锁定最终对白、shot ID、U 唯一身份或 BG 微章 ID。",
        ],
    }
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    REPORT.write_text(serialized, encoding="utf-8")
    HOOK_REPORT.write_text(serialized, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
    raise SystemExit(0 if json.loads(REPORT.read_text(encoding="utf-8"))["status"] == "REVIEWED-SEASON-PASS" else 1)
