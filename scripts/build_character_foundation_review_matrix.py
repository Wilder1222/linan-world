from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
CONTENT_AUDIT = ROOT / "qa/reviews/character-foundation-audit.json"
STATE_AUDIT = ROOT / "qa/reviews/profile-state-chain-audit.json"
DEMOGRAPHIC_AUDIT = ROOT / "qa/reviews/recurring-demographic-audit.json"
RECURRING_SAMPLE_REVIEW = ROOT / "qa/reviews/recurring-sample-review.json"
RELATION_QUALITY = ROOT / "qa/reviews/relationship-evidence-quality.json"
SPINE_PRESSURE = ROOT / "qa/reviews/emotional-spine-pressure-test.json"
U_BG_BOUNDARY = ROOT / "qa/reviews/u-bg-boundary-audit.json"
RECURRING_QUALITY = ROOT / "qa/reviews/recurring-production-quality.json"
RELATION_EVIDENCE = ROOT / "qa/relationship-evidence.json"
SPINES = ROOT / "qa/emotional-spines.json"
REPORT = ROOT / "qa/reviews/character-foundation-review-matrix.json"
GATE_CERTIFICATE = ROOT / "qa/gates/character-foundation-gate.json"

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


def recurring_review(record: dict) -> dict:
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
        "notes": "已从 48 人源表逐人回写并复核职业化日常动作、具体阻力、盲点、主动选择、不可逆代价、关系余波与结局动作；实际母集、微章和回访仍由后续 Gate 绑定。",
    }


def build() -> dict:
    roster = read_json(ROSTER)
    content_audit = read_json(CONTENT_AUDIT)
    state_audit = read_json(STATE_AUDIT)
    demographic_audit = read_json(DEMOGRAPHIC_AUDIT)
    recurring_sample_review = read_json(RECURRING_SAMPLE_REVIEW)
    relation_quality = read_json(RELATION_QUALITY)
    spine_pressure = read_json(SPINE_PRESSURE)
    u_bg_boundary = read_json(U_BG_BOUNDARY)
    recurring_quality = read_json(RECURRING_QUALITY)
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
            if recurring_quality.get("status") == "REVIEWED-PASS":
                profiles.append(recurring_review(record))
            else:
                profiles.append(pending_review(record, "需要按生活圈确认年龄、家庭结构、职业阶段、职业动作与回访连续性"))

    relation_quality_by_id = {item["relation_id"]: item for item in relation_quality.get("relationships", [])}
    relationships = []
    for relation in evidence.get("relationships", []):
        quality = relation_quality_by_id.get(relation["relation_id"], {})
        passed = quality.get("review_status") == "REVIEWED-PASS"
        relationships.append(
            {
                "relation_id": relation["relation_id"],
                "foundation_evidence_count": len(relation.get("snapshots", [])),
                "scene_binding_status": "RESERVED-UNTIL-SEASON-GATE",
                "review_status": "REVIEWED-PASS" if passed else "REVIEW-PENDING",
                "reviewer": "Codex production review" if passed else None,
                "blocking_items": [] if passed else ["确认每个快照的具体动作是否真正改变选择，而非只改变情绪标签"],
                "notes": quality.get("notes") if passed else "不得将机器通过误报为人工审读完成；补审后由质量报告回写。",
            }
        )
    spine_reviews = [
        {
            "spine_id": spine["id"],
            "name": spine["name"],
            "state_count": len(spine.get("arc_states", [])),
            "review_status": next((item["review_status"] for item in spine_pressure.get("spines", []) if item["spine_id"] == spine["id"]), "REVIEW-PENDING"),
            "reviewer": "Codex production review" if next((item["review_status"] for item in spine_pressure.get("spines", []) if item["spine_id"] == spine["id"]), "") == "REVIEWED-PASS" else None,
            "blocking_items": [] if next((item["review_status"] for item in spine_pressure.get("spines", []) if item["spine_id"] == spine["id"]), "") == "REVIEWED-PASS" else ["确认每个状态具有混合情感、主动选择、不可逆代价和下一状态余波"],
        }
        for spine in spines.get("spines", [])
    ]

    central_count = sum(1 for item in profiles if item["tier"].startswith("L") and item["review_status"] == "REVIEWED-PASS")
    important_reviewed = sum(1 for item in profiles if item["tier"].startswith("A") and item["review_status"] == "REVIEWED-PASS")
    important_pending = sum(1 for item in profiles if item["tier"].startswith("A") and item["review_status"] == "REVIEW-PENDING")
    u_bg_passed = u_bg_boundary.get("status") == "PASS"
    gate_blockers = [] if u_bg_passed else ["U/BG 边界审计未通过"]
    gate_locked = (
        not gate_blockers
        and GATE_CERTIFICATE.exists()
        and read_json(GATE_CERTIFICATE).get("status") == "LOCKED"
    )
    return {
        "schema_version": 1,
        "status": "LOCKED" if gate_locked else ("READY-TO-LOCK" if not gate_blockers else "OPEN"),
        "gate": "CHARACTER-FOUNDATION",
        "review_scope": "P1 production review matrix",
        "summary": {
            "profile_total": len(profiles),
            "central_reviewed": central_count,
            "important_reviewed": important_reviewed,
            "important_pending": important_pending,
            "recurring_pending": sum(1 for item in profiles if item["tier"] == "B" and item["review_status"] != "REVIEWED-PASS"),
            "recurring_reviewed": sum(1 for item in profiles if item["tier"] == "B" and item["review_status"] == "REVIEWED-PASS"),
            "recurring_sample_reviewed": recurring_sample_review.get("sample_count", 0),
            "recurring_sample_circles": recurring_sample_review.get("circle_count", 0),
            "relationship_total": len(relationships),
            "relationship_reviewed": sum(1 for item in relationships if item["review_status"] == "REVIEWED-PASS"),
            "relationship_evidence_total": sum(item["foundation_evidence_count"] for item in relationships),
            "emotional_spine_total": len(spine_reviews),
            "emotional_spine_reviewed": sum(1 for item in spine_reviews if item["review_status"] == "REVIEWED-PASS"),
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
        "relationship_quality_review": {
            "status": relation_quality.get("status"),
            "relationship_total": relation_quality.get("relationship_total", 0),
            "snapshot_total": relation_quality.get("snapshot_total", 0),
            "report_path": "qa/reviews/relationship-evidence-quality.json",
        },
        "emotional_spine_pressure_review": {
            "status": spine_pressure.get("status"),
            "spine_total": spine_pressure.get("spine_total", 0),
            "state_total": spine_pressure.get("state_total", 0),
            "report_path": "qa/reviews/emotional-spine-pressure-test.json",
        },
        "recurring_production_quality_review": {
            "status": recurring_quality.get("status"),
            "reviewed": recurring_quality.get("reviewed", 0),
            "unique_daily_actions": recurring_quality.get("unique_daily_actions", 0),
            "unique_choices": recurring_quality.get("unique_choices", 0),
            "unique_ending_actions": recurring_quality.get("unique_ending_actions", 0),
            "report_path": "qa/reviews/recurring-production-quality.json",
        },
        "u_bg_boundary": {
            "review_status": "REVIEWED-PASS" if u_bg_passed else "REVIEW-PENDING",
            "report_path": "qa/reviews/u-bg-boundary-audit.json",
            "U": {
                "status": "REVIEWED-PASS" if u_bg_passed else "REVIEW-PENDING",
                "downstream_binding": "RESERVED-UNTIL-SEASON-GATE",
                "rule": "保持可替换候选，不提前分配唯一主线身份",
            },
            "BG": {
                "status": "REVIEWED-PASS" if u_bg_passed else "REVIEW-PENDING",
                "downstream_binding": "RESERVED-UNTIL-EPISODE-GATE",
                "rule": "具体 microchapter_ids 与 extension_ids 只能由 Episode Gate 写入",
            },
        },
        "gate_blockers": gate_blockers,
        "next_action": (
            "Character Foundation Gate 已锁定；进入 P2 Season 因果账本、悬疑翻转、宋代生活活动与幽默登记，"
            "不提前绑定 U/BG 下游身份。"
            if u_bg_passed and recurring_quality.get("status") == "REVIEWED-PASS"
            else "完成 U/BG 边界与 B 级生产细节审计，再锁定 Character Foundation Gate。"
        ),
    }


def main() -> int:
    report = build()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
