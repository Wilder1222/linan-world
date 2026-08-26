from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORECARD_PATH = ROOT / "qa/reviews/p3-e01-episode-gate-review.json"
AUDIT_PATH = ROOT / "qa/reviews/p3-e01-episode-gate-audit.json"
FORMAL_PATH = ROOT / "production/episodes/S1-E01/episode-formal-delivery.json"
DIMENSIONS = {
    "character_consistency",
    "expression_continuity",
    "action_logic",
    "behavior_logic",
    "relationship_continuity",
    "costume_continuity",
    "prop_continuity",
    "camera_performance",
    "aigc_stability",
    "story_logic",
}


def finding(code: str, severity: str = "BLOCKING", **details: object) -> dict:
    return {"code": code, "severity": severity, **details}


def audit() -> dict:
    findings: list[dict] = []
    if not SCORECARD_PATH.exists() or not FORMAL_PATH.exists():
        findings.append(finding("episode_gate_artifact_missing"))
        report = {"schema_version": 1, "status": "OPEN", "findings": findings}
        AUDIT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report
    gate = json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_PATH.read_text(encoding="utf-8"))
    if gate.get("status") != "REVIEWED-P3-DESIGN-GATE-PASS":
        findings.append(finding("design_gate_status_invalid", actual=gate.get("status")))
    if gate.get("decision") != "HOLD-OPEN-DEFERRED" or gate.get("eligible_for_episode_gate_pass") is not False:
        findings.append(finding("design_gate_decision_must_remain_open"))
    if gate.get("episode_gate_status") != "OPEN":
        findings.append(finding("episode_gate_status_not_open", actual=gate.get("episode_gate_status")))
    if gate.get("threshold") != 90 or gate.get("dimension_total") != 10:
        findings.append(finding("episode_gate_threshold_or_dimension_total_invalid"))
    dimensions = gate.get("dimensions", {})
    if set(dimensions) != DIMENSIONS:
        findings.append(finding("episode_gate_dimensions_invalid", actual=sorted(dimensions)))
    scored = []
    deferred = []
    for dimension, item in dimensions.items():
        score = item.get("score")
        status = item.get("status")
        if score is None:
            deferred.append(dimension)
            if status != "DEFERRED-EVIDENCE-REQUIRED" or not item.get("basis") or not item.get("evidence"):
                findings.append(finding("deferred_dimension_missing_reason", dimension=dimension))
        else:
            scored.append(dimension)
            if not isinstance(score, int) or score < 0 or score > 100:
                findings.append(finding("dimension_score_invalid", dimension=dimension, score=score))
            if score < gate["threshold"]:
                findings.append(finding("dimension_below_threshold", dimension=dimension, score=score))
            if status != "SCORED-DESIGN-REVIEW" or not item.get("basis") or not item.get("evidence"):
                findings.append(finding("scored_dimension_missing_basis", dimension=dimension))
    if set(deferred) != {"aigc_stability"}:
        findings.append(finding("unexpected_deferred_dimensions", actual=deferred))
    if gate.get("scored_dimension_total") != len(scored) or gate.get("deferred_dimension_total") != len(deferred):
        findings.append(finding("dimension_rollup_invalid"))
    if gate.get("minimum_scored_score") != min(dimensions[item]["score"] for item in scored):
        findings.append(finding("minimum_score_rollup_invalid"))
    if gate.get("human_signoff", {}).get("status") != "REQUIRED" or gate.get("human_signoff", {}).get("reviewer") is not None:
        findings.append(finding("human_signoff_boundary_invalid"))
    execution = gate.get("execution", {})
    if execution.get("provider_calls") != 0 or execution.get("external_execution") is not False or execution.get("media_evidence") != "NOT_PROVIDED" or execution.get("execution_receipts"):
        findings.append(finding("execution_boundary_invalid"))
    scenes = formal.get("script_scenes", [])
    storyboards = formal.get("storyboard", [])
    if len(scenes) != 18 or len(storyboards) != 18 or gate.get("scene_rollup", []) == []:
        findings.append(finding("scene_rollup_incomplete"))
    expected_ids = [f"S1-E01-M{index:02d}" for index in range(1, 19)]
    if [item.get("chapter_id") for item in gate.get("scene_rollup", [])] != expected_ids:
        findings.append(finding("scene_rollup_order_invalid"))
    for item in gate.get("scene_rollup", []):
        if item.get("structural_status") != "PASS" or item.get("shot_count") != 3 or item.get("continuity_present") is not True or item.get("human_scene_score_status") != "PENDING":
            findings.append(finding("scene_rollup_item_invalid", chapter_id=item.get("chapter_id")))
    report = {
        "schema_version": 1,
        "status": "REVIEWED-P3-DESIGN-GATE-PASS" if not findings else "OPEN",
        "scope": "P3-04 S1-E01 Episode Gate design review audit",
        "episode_id": "S1-E01",
        "checks": {
            "ten_dimensions_present": set(dimensions) == DIMENSIONS,
            "nine_design_dimensions_above_threshold": not any(item["code"] == "dimension_below_threshold" for item in findings),
            "aigc_evidence_explicitly_deferred": set(deferred) == {"aigc_stability"},
            "human_signoff_required": gate.get("human_signoff", {}).get("status") == "REQUIRED",
            "execution_blocked_and_receipt_free": not any(item["code"] == "execution_boundary_invalid" for item in findings),
            "scene_rollup_complete": not any(item["code"].startswith("scene_rollup") for item in findings),
        },
        "findings": findings,
        "deferred_followup": [
            "AIGC 稳定性不是设计分数；必须在明确授权后取得 fixture/dry-run 或验证输出证据。",
            "Episode Gate 的最终通过需要人工逐章签字，不得由本结构化报告代替。",
            "在上述两项完成前，不推进 E02/E03 的正式资产生成。",
        ],
    }
    AUDIT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-P3-DESIGN-GATE-PASS" else 1)
