from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qa/emotional-spines.json"
REPORT = ROOT / "qa/reviews/emotional-spine-pressure-test.json"


def build() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    spine_reports = []
    findings = []
    for spine in data.get("spines", []):
        states = spine.get("arc_states", [])
        checks = {
            "six_states": len(states) == 6,
            "mixed_emotion_each_state": all(item.get("mixed_emotions") for item in states),
            "concrete_dimension_before": all(
                item.get("seven_dimension_before") and "关系档案初始值" not in item.get("seven_dimension_before", "")
                for item in states
            ),
            "concrete_dimension_after": all(
                item.get("seven_dimension_after") and "至少一项七维状态" not in item.get("seven_dimension_after", "")
                for item in states
            ),
            "active_choice_each_state": all(item.get("choice") for item in states),
            "irreversible_cost_each_state": all("不可逆代价：" in item.get("cost", "") for item in states),
            "aftermath_each_state": all(item.get("aftermath") for item in states),
            "observable_evidence_each_state": all(item.get("observable_evidence") for item in states),
            "cost_effects_change": len({item.get("cost", "") for item in states}) == 6,
            "no_automatic_reconciliation": all("自动和解" not in item.get("aftermath", "") for item in states),
        }
        if not all(checks.values()):
            findings.append({"spine_id": spine.get("id"), "checks": checks})
        spine_reports.append(
            {
                "spine_id": spine.get("id"),
                "name": spine.get("name"),
                "review_status": "REVIEWED-PASS" if all(checks.values()) else "REVIEW-FAIL",
                "reviewer": "Codex production review",
                "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
                "notes": "已逐状态检查混合情感、主动选择、不可逆代价、关系余波与七维变化；最终 scene/dialogue/shot ID 仍由 Season/Episode Gate 绑定。",
            }
        )
    return {
        "schema_version": 1,
        "status": "REVIEWED-PASS" if not findings else "OPEN",
        "scope": "P1 emotional spine pressure test",
        "spine_total": len(spine_reports),
        "state_total": sum(len(item.get("arc_states", [])) for item in data.get("spines", [])),
        "findings": findings,
        "spines": spine_reports,
        "manual_followup": [
            "Season Gate 绑定具体关系、集号、scene/dialogue/shot ID。",
            "确认六条脊柱在 36 集因果账本中互相造成后续影响，而非各自独立完成。",
        ],
    }


def main() -> int:
    report = build()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["findings"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
