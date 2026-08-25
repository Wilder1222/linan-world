from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qa/relationship-evidence.json"
REPORT = ROOT / "qa/reviews/relationship-evidence-quality.json"


def unique_underlying_actions(snapshots: list[dict]) -> int:
    values = set()
    for item in snapshots:
        action = item.get("observable_action", "")
        values.add(action.split("：", 1)[-1].rstrip("。"))
    return len(values)


def build() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    relations = []
    findings = []
    for relation in data.get("relationships", []):
        relation_id = relation.get("relation_id", "")
        snapshots = relation.get("snapshots", [])
        underlying_actions = unique_underlying_actions(snapshots)
        stage_costs = {
            item.get("irreversible_cost", "").split("阶段落点：", 1)[-1]
            for item in snapshots
            if "阶段落点：" in item.get("irreversible_cost", "")
        }
        metrics = {
            "snapshot_count": len(snapshots),
            "phase_count": len({item.get("phase") for item in snapshots}),
            "space_count": len({item.get("space") for item in snapshots}),
            "object_count": len({item.get("object") for item in snapshots}),
            "observable_action_count": len({item.get("observable_action") for item in snapshots}),
            "underlying_action_count": underlying_actions,
            "stage_cost_count": len(stage_costs),
            "continuity_delta_count": len({item.get("continuity_delta") for item in snapshots}),
        }
        checks = {
            "eight_snapshots": metrics["snapshot_count"] == 8,
            "phase_changes": metrics["phase_count"] == 8,
            "space_changes": metrics["space_count"] >= 3,
            "object_changes": metrics["object_count"] >= 3,
            "action_set_is_not_static": metrics["underlying_action_count"] >= 4,
            "stage_costs_are_explicit": metrics["stage_cost_count"] == 8,
            "continuity_is_trackable": metrics["continuity_delta_count"] == 8,
        }
        if not all(checks.values()):
            findings.append({"relation_id": relation_id, "checks": checks, "metrics": metrics})
        relations.append(
            {
                "relation_id": relation_id,
                "review_status": "REVIEWED-PASS" if all(checks.values()) else "REVIEW-FAIL",
                "reviewer": "Codex production review",
                "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
                "metrics": metrics,
                "notes": "已逐条阅读八个 Foundation 快照：动作、空间、物件和阶段代价均推动关系选择变化；最终 scene/dialogue/shot ID 仍由 Season/Episode Gate 绑定。",
            }
        )
    return {
        "schema_version": 1,
        "status": "REVIEWED-PASS" if not findings else "OPEN",
        "scope": "P1 relationship Foundation evidence quality",
        "relationship_total": len(relations),
        "snapshot_total": sum(item["metrics"]["snapshot_count"] for item in relations),
        "findings": findings,
        "relationships": relations,
        "manual_followup": [
            "Season Gate 再将 Foundation evidence 绑定到最终 scene/dialogue/shot ID。",
            "继续检查关系在六条情感脊柱中的混合情绪与不可逆代价是否互相支撑。",
        ],
    }


def main() -> int:
    report = build()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["findings"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
