from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "qa/reviews"
REPORT = REVIEW_DIR / "season-gate-exception-ledger.json"
SOURCE_REPORTS = [
    REVIEW_DIR / "season-gate-causal-mystery-review.json",
    REVIEW_DIR / "season-gate-relationship-life-humor-review.json",
]


EXCEPTIONS = [
    {
        "exception_id": "EXC-SG-01-01",
        "severity": "DEFERRED",
        "source": "qa/reviews/season-gate-causal-mystery-review.json",
        "description": "最终对白、shot ID、U 唯一身份和 BG 微章 ID 不在 SG-01 季级因果审读范围内。",
        "owner": "Episode Gate / AIGC 生产",
        "disposition": "DEFERRED-UNTIL-EPISODE-GATE",
        "next_gate": "Episode Gate",
        "preserved_boundary": "保持 U 槽位可替换、BG 的 microchapter_ids 与 extension_ids 为空。",
        "acceptance_criteria": "逐场剧本、表演、分镜、连续性账本和资产清单完成绑定后再审。",
    },
    {
        "exception_id": "EXC-SG-01-02",
        "severity": "DEFERRED",
        "source": "qa/reviews/season-gate-causal-mystery-review.json",
        "description": "章级目标/阻力/选择的最终对白节奏、镜头语义和 AIGC 表演可执行性尚未锁定。",
        "owner": "Episode Gate / 导演与表演审读",
        "disposition": "DEFERRED-UNTIL-EPISODE-GATE",
        "next_gate": "Episode Gate",
        "preserved_boundary": "Season 层只锁定因果节拍与状态转移，不将节拍误读为成片脚本。",
        "acceptance_criteria": "每章完成 Character State、Relationship Delta、Blocking/Storyboard 与九项 QA。",
    },
    {
        "exception_id": "EXC-SG-02-01",
        "severity": "DEFERRED",
        "source": "qa/reviews/season-gate-relationship-life-humor-review.json",
        "description": "关系动作、宋代活动的具体走位和幽默反应顺序尚未绑定到正式逐场剧本。",
        "owner": "Episode Gate / 剧本与表演组",
        "disposition": "DEFERRED-UNTIL-EPISODE-GATE",
        "next_gate": "Episode Gate",
        "preserved_boundary": "保留关系证据快照、活动状态转移和幽默语域字段，不提前写死 scene/dialogue/shot。",
        "acceptance_criteria": "逐场稿明确动作、潜台词、听者反应、活动选择和连续性代价。",
    },
    {
        "exception_id": "EXC-SG-02-02",
        "severity": "DEFERRED",
        "source": "qa/reviews/season-gate-relationship-life-humor-review.json",
        "description": "U 候选仍未分配唯一姓名与最终场次；可替换规则必须在 Episode Gate 继续成立。",
        "owner": "Episode Gate / 角色与连续性组",
        "disposition": "DEFERRED-UNTIL-EPISODE-GATE",
        "next_gate": "Episode Gate",
        "preserved_boundary": "120 个 U 槽位保持 RESERVED，候选仅代表功能位置。",
        "acceptance_criteria": "若写入唯一身份，必须保留同类槽位替换路径并通过连续性审计。",
    },
    {
        "exception_id": "EXC-SG-02-03",
        "severity": "DEFERRED",
        "source": "qa/reviews/season-gate-relationship-life-humor-review.json",
        "description": "BG 原型尚未写入具体微章或扩展绑定，不能在 Season Gate 之后静默补写。",
        "owner": "Episode Gate / 场景与群演资产组",
        "disposition": "DEFERRED-UNTIL-EPISODE-GATE",
        "next_gate": "Episode Gate",
        "preserved_boundary": "300 个 BG 原型保持 RESERVED，microchapter_ids 与 extension_ids 为空。",
        "acceptance_criteria": "绑定必须同时满足地点、时段、工作状态和群像功能的连续性检查。",
    },
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict:
    findings: list[dict] = []
    source_statuses: dict[str, str] = {}
    for path in SOURCE_REPORTS:
        key = path.relative_to(ROOT).as_posix()
        if not path.exists():
            findings.append({"code": "source_report_missing", "source": key, "severity": "BLOCKING"})
            continue
        data = load(path)
        source_statuses[key] = data.get("status", "MISSING")
        if data.get("status") != "REVIEWED-SEASON-PASS":
            findings.append({"code": "source_report_not_pass", "source": key, "status": data.get("status"), "severity": "BLOCKING"})
        if data.get("findings"):
            findings.append({"code": "source_report_has_open_findings", "source": key, "count": len(data["findings"]), "severity": "BLOCKING"})

    ids = [item["exception_id"] for item in EXCEPTIONS]
    if len(ids) != len(set(ids)):
        findings.append({"code": "exception_ids_not_unique", "severity": "BLOCKING"})
    allowed_severities = {"BLOCKING", "MAJOR", "MINOR", "DEFERRED"}
    for item in EXCEPTIONS:
        missing = [field for field in ("exception_id", "severity", "source", "description", "owner", "disposition", "next_gate", "preserved_boundary", "acceptance_criteria") if not item.get(field)]
        if missing:
            findings.append({"code": "exception_fields_missing", "exception_id": item.get("exception_id"), "fields": missing, "severity": "BLOCKING"})
        if item.get("severity") not in allowed_severities:
            findings.append({"code": "exception_severity_invalid", "exception_id": item.get("exception_id"), "severity": "BLOCKING"})
        if item.get("severity") != "DEFERRED":
            findings.append({"code": "unexpected_open_exception", "exception_id": item.get("exception_id"), "severity": item.get("severity")})
        if item.get("source") not in source_statuses:
            findings.append({"code": "exception_source_not_a_review", "exception_id": item.get("exception_id"), "source": item.get("source"), "severity": "BLOCKING"})
        if item.get("disposition") == "DEFERRED-UNTIL-EPISODE-GATE" and item.get("next_gate") != "Episode Gate":
            findings.append({"code": "exception_next_gate_mismatch", "exception_id": item.get("exception_id"), "severity": "BLOCKING"})

    report = {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not findings else "OPEN",
        "scope": "P2 SG-03 independent Season Gate exception and deferred-boundary ledger",
        "source_reports": [path.relative_to(ROOT).as_posix() for path in SOURCE_REPORTS],
        "source_statuses": source_statuses,
        "blocking_open": sum(1 for item in findings if item.get("severity") == "BLOCKING"),
        "major_open": sum(1 for item in findings if item.get("severity") == "MAJOR"),
        "minor_open": sum(1 for item in findings if item.get("severity") == "MINOR"),
        "deferred_total": len(EXCEPTIONS),
        "exceptions": EXCEPTIONS,
        "checks": {
            "two_independent_reviews_pass": len(SOURCE_REPORTS) == 2 and all(value == "REVIEWED-SEASON-PASS" for value in source_statuses.values()) and not any(item.get("code") == "source_report_has_open_findings" for item in findings),
            "every_exception_classified": all(item.get("severity") in allowed_severities for item in EXCEPTIONS),
            "no_blocking_or_major_open": not any(item.get("severity") in {"BLOCKING", "MAJOR"} for item in findings),
            "deferred_next_gate_declared": all(item.get("next_gate") == "Episode Gate" for item in EXCEPTIONS),
            "boundaries_preserved": all(item.get("preserved_boundary") for item in EXCEPTIONS),
        },
        "findings": findings,
        "next_gate": "SG-04 Season Gate decision",
        "deferred_followup": [
            "SG-04 才能依据本账本生成 Season Gate 决议、输入 manifest 与 scope definition。",
            "Season Gate 关闭后仍不得把 DEFERRED 项静默视为已完成；它们必须在 Episode Gate 重新审读。",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-SEASON-PASS" else 1)
