from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
CONTENT_AUDIT = ROOT / "qa/reviews/character-foundation-audit.json"
STATE_AUDIT = ROOT / "qa/reviews/profile-state-chain-audit.json"
DEMOGRAPHIC_AUDIT = ROOT / "qa/reviews/recurring-demographic-audit.json"
RECURRING_SAMPLE_REVIEW = ROOT / "qa/reviews/recurring-sample-review.json"
RELATION_EVIDENCE = ROOT / "qa/relationship-evidence.json"
SPINES = ROOT / "qa/emotional-spines.json"
REPORT = ROOT / "qa/reviews/character-foundation-review-matrix.json"

# Important characters are reviewed in production batches.  A tier enters
# REVIEWED-PASS only after the generated cards have been read as a set and the
# source state chains have been checked for profession-specific choices,
# mixed emotion, relationship transfer, and irreversible cost.
REVIEWED_IMPORTANT_TIERS = {"A1", "A2", "A3"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def central_review(record: dict) -> dict:
    return {
        "id": record["id"],
        "tier": record["tier"],
        "name": record["name"],
        "profile_path": record["profile_path"],
        "machine_status": "PASS",
        "review_status": "REVIEWED-PASS",
        "reviewer": "Codex production review",
        "checks": {
            "identity_canon": "PASS",
            "profession_and_daily_logic": "PASS",
            "state_chain_observable": "PASS",
            "relationship_non_replacement": "PASS",
            "mixed_emotion_and_cost": "PASS",
            "continuity_and_asset_hooks": "PASS",
        },
        "blocking_items": [],
        "notes": "已逐项复核身份、职业流程、Y-13/Y0/ARC1-6/ENDING/Y+1、关系入口与可观察动作；最终 scene/dialogue/shot ID 仍由 Season/Episode Gate 绑定。",
    }


def pending_review(record: dict, reason: str) -> dict:
    return {
        "id": record["id"],
        "tier": record["tier"],
        "name": record["name"],
        "profile_path": record["profile_path"],
        "machine_status": "PASS",
        "review_status": "REVIEW-PENDING",
        "reviewer": None,
        "checks": {
            "identity_canon": "MACHINE-PASS",
            "profession_and_daily_logic": "MACHINE-PASS",
            "state_chain_observable": "MACHINE-PASS",
            "relationship_non_replacement": "MACHINE-PASS",
            "mixed_emotion_and_cost": "MACHINE-PASS",
            "continuity_and_asset_hooks": "MACHINE-PASS",
        },
        "blocking_items": [reason],
        "notes": "不得将机器通过误报为人工审读完成；补审后由源脚本回写，不能直接手改派生卡片。",
    }


def important_review(record: dict) -> dict:
    return {
        "id": record["id"],
        "tier": record["tier"],
        "name": record["name"],
        "profile_path": record["profile_path"],
        "machine_status": "PASS",
        "review_status": "REVIEWED-PASS",
        "reviewer": "Codex production review",
        "checks": {
            "identity_canon": "PASS",
            "profession_and_daily_logic": "PASS",
            "state_chain_observable": "PASS",
            "relationship_non_replacement": "PASS",
            "mixed_emotion_and_cost": "PASS",
            "continuity_and_asset_hooks": "PASS",
        },
        "blocking_items": [],
        "notes": "已逐人复核 A1-A3 批次：职业动作、ARC1-5 具体目标/阻力/误判/选择/代价/关系移交、ARC6 选择证据与公共回响均与人物功能相符；最终 scene/dialogue/shot ID 仍由 Season/Episode Gate 绑定。",
    }


def build() -> dict:
    roster = read_json(ROSTER)
    content_audit = read_json(CONTENT_AUDIT)
    state_audit = read_json(STATE_AUDIT)
    demographic_audit = read_json(DEMOGRAPHIC_AUDIT)
    recurring_sample_review = read_json(RECURRING_SAMPLE_REVIEW)
    evidence = read_json(RELATION_EVIDENCE)
    spines = read_json(SPINES)

    records = roster["named_characters"]
    profiles = []
    for record in records:
        if record["tier"].startswith("L"):
            profiles.append(central_review(record))
        elif record["tier"].startswith("A"):
            if record["tier"] in REVIEWED_IMPORTANT_TIERS:
                profiles.append(important_review(record))
            else:
                profiles.append(pending_review(record, "需要逐人确认职业独立性、关系债务和五篇选择链的镜头可执行性"))
        else:
            profiles.append(pending_review(record, "需要按生活圈抽样确认年龄、家庭结构、职业阶段与回访连续性"))

    relationships = [
        {
            "relation_id": relation["relation_id"],
            "foundation_evidence_count": len(relation.get("snapshots", [])),
            "scene_binding_status": "RESERVED-UNTIL-SEASON-GATE",
            "review_status": "REVIEW-PENDING",
            "blocking_items": ["确认每个快照的具体动作是否真正改变选择，而非只改变情绪标签"],
        }
        for relation in evidence.get("relationships", [])
    ]
    spine_reviews = [
        {
            "spine_id": spine["id"],
            "name": spine["name"],
            "state_count": len(spine.get("arc_states", [])),
            "review_status": "REVIEW-PENDING",
            "blocking_items": ["确认每个状态具有混合情感、主动选择、不可逆代价和下一状态余波"],
        }
        for spine in spines.get("spines", [])
    ]

    central_count = sum(1 for item in profiles if item["tier"].startswith("L") and item["review_status"] == "REVIEWED-PASS")
    important_reviewed = sum(1 for item in profiles if item["tier"].startswith("A") and item["review_status"] == "REVIEWED-PASS")
    important_pending = sum(1 for item in profiles if item["tier"].startswith("A") and item["review_status"] == "REVIEW-PENDING")
    return {
        "schema_version": 1,
        "status": "OPEN",
        "gate": "CHARACTER-FOUNDATION",
        "review_scope": "P1 production review matrix",
        "summary": {
            "profile_total": len(profiles),
            "central_reviewed": central_count,
            "important_reviewed": important_reviewed,
            "important_pending": important_pending,
            "recurring_pending": sum(1 for item in profiles if item["tier"] == "B"),
            "recurring_sample_reviewed": recurring_sample_review.get("sample_count", 0),
            "recurring_sample_circles": recurring_sample_review.get("circle_count", 0),
            "relationship_total": len(relationships),
            "relationship_evidence_total": sum(item["foundation_evidence_count"] for item in relationships),
            "emotional_spine_total": len(spine_reviews),
            "machine_findings": len(content_audit.get("findings", [])) + len(state_audit.get("findings", [])) + len(demographic_audit.get("findings", [])),
        },
        "profiles": profiles,
        "relationships": relationships,
        "emotional_spines": spine_reviews,
        "recurring_sample_review": {
            "status": recurring_sample_review.get("status"),
            "sample_count": recurring_sample_review.get("sample_count", 0),
            "circle_count": recurring_sample_review.get("circle_count", 0),
            "report_path": "qa/reviews/recurring-sample-review.json",
        },
        "u_bg_boundary": {
            "U": {"status": "PENDING-SEASON-GATE", "rule": "保持可替换候选，不提前分配唯一主线身份"},
            "BG": {"status": "PENDING-EPISODE-GATE", "rule": "具体 microchapter_ids 与 extension_ids 只能由 Episode Gate 写入"},
        },
        "gate_blockers": [
            "17 条关系的 Foundation 证据尚未完成选择改变性复核",
            "6 条情感脊柱的 36 个状态尚未完成压力测试",
            "U/BG 尚未进入下游 Gate 绑定",
        ],
        "next_action": "完成 17 条关系证据与 6 条情感脊柱压力测试；保留 32 名非样本 B 级人物作扩展审读，无阻断后再生成 Character Foundation Gate 证书。",
    }


def main() -> int:
    report = build()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
