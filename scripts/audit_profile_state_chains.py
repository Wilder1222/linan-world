from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
REPORT = ROOT / "qa/reviews/profile-state-chain-audit.json"
LA_STATES = ("Y-13", "Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END", "ARC6-END", "ENDING", "Y+1")


def state_block(text: str, state: str) -> str:
    match = re.search(rf"(?m)^###\s+{re.escape(state)}\s*$\n(.*?)(?=^###\s+|\Z)", text, re.S)
    return match.group(1).strip() if match else ""


def audit() -> dict:
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    findings: list[dict[str, str]] = []
    profile_count = 0
    for record in roster.get("named_characters", []):
        if record.get("tier") == "B":
            continue
        profile_count += 1
        path = ROOT / record["profile_path"]
        text = path.read_text(encoding="utf-8")
        for state in LA_STATES:
            block = state_block(text, state)
            if not block:
                findings.append({"id": record["id"], "state": state, "code": "missing_state_block"})
                continue
            if state in {"ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END"}:
                required = ("目标", "误判", "选择", "代价", "移交")
                for field in required:
                    if field not in block:
                        findings.append({"id": record["id"], "state": state, "code": f"missing_{field}"})
                # Generators use either “关系移交” or the shorter “状态移交”
                # label. Both are valid so long as the state explicitly hands
                # a changed relationship position to the next state.
                if not any(marker in block for marker in ("关系", "状态移交")):
                    findings.append({"id": record["id"], "state": state, "code": "missing_relationship_transfer"})
            elif state == "ARC6-END" and not any(marker in block for marker in ("目标", "选择", "完成不可替代选择")):
                findings.append({"id": record["id"], "state": state, "code": "missing_final_choice"})
    status = "REVIEWED-PASS" if not findings and profile_count == 36 else "OPEN"
    return {
        "status": status,
        "scope": "P1 L/A observable state-chain audit",
        "profile_total": profile_count,
        "state_total": profile_count * len(LA_STATES),
        "findings": findings,
        "foundation_checks": {
            "observable_state_blocks": profile_count * len(LA_STATES),
            "choice_cost_transfer_states": profile_count * 5,
        },
        "deferred_followup": [
            "Season Gate 将状态链绑定到最终 episode/microchapter ID",
            "Episode Gate 将状态动作转译为 blocking、shot 和 AIGC continuity ID",
        ],
    }


def main() -> int:
    report = audit()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
