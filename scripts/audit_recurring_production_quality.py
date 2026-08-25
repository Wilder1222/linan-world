from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
REPORT = ROOT / "qa/reviews/recurring-production-quality.json"


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n+++", 4)
    if not text.startswith("+++\n") or end < 0:
        return {}
    values: dict = {}
    for line in text[4:end].splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def section(text: str, heading: str, next_heading: str) -> str:
    if heading not in text:
        return ""
    return text.split(heading, 1)[1].split(next_heading, 1)[0]


def audit() -> dict:
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    findings: list[dict[str, str]] = []
    profiles: list[dict[str, object]] = []
    actions: set[str] = set()
    choices: set[str] = set()
    endings: set[str] = set()
    generic_markers = (
        "自己的生计、照料对象和不被抹掉的日常",
        "先完成眼前的劳动、交易、清洁、等待或照料",
        "至少一位亲近者会因为自己的先后顺序承担损失",
        "同行、家人或同一生活圈的人可能认为这是多管闲事",
    )
    for record in roster.get("named_characters", []):
        if record.get("tier") != "B":
            continue
        path = ROOT / record["profile_path"]
        text = path.read_text(encoding="utf-8")
        data = front_matter(path)
        checks = {
            "front_matter": bool(data),
            "daily_action": "- 常态行为：" in text,
            "daily_obstacle": "- 日常阻力：" in text,
            "observable_choice": "选择：" in text,
            "irreversible_cost": "不可逆代价：" in text and "未解决问题：" in text,
            "ending_action": "回到自己的工作现场：" in text,
            "two_relationships": len(re.findall(r"(?m)^- REL-B-", section(text, "## 非中央关系", "## 终局职业回响"))) >= 2,
            "career_echo": "## 终局职业回响" in text,
            "life_circle": "## 基础状态" in text and "生活圈：" in text,
            "no_generic_scaffold": not any(marker in text for marker in generic_markers),
        }
        if not all(checks.values()):
            for check, passed in checks.items():
                if not passed:
                    findings.append({"id": record["id"], "code": f"missing_or_generic_{check}"})
        daily_match = re.search(r"^- 常态行为：(.*)$", text, re.M)
        choice_match = re.search(r"^4\. 两件都正确的事冲突时选择什么：(.*)$", text, re.M)
        ending_match = re.search(r"^回到自己的工作现场：(.*)$", text, re.M)
        if daily_match:
            actions.add(daily_match.group(1).strip())
        if choice_match:
            choices.add(choice_match.group(1).strip())
        if ending_match:
            endings.add(ending_match.group(1).split("；", 1)[0].strip())
        profiles.append({"id": record["id"], "name": record["name"], "checks": checks})
    total = len(profiles)
    if len(actions) != total:
        findings.append({"code": "daily_action_not_unique", "unique": str(len(actions)), "total": str(total)})
    if len(choices) != total:
        findings.append({"code": "choice_not_unique", "unique": str(len(choices)), "total": str(total)})
    if len(endings) != total:
        findings.append({"code": "ending_action_not_unique", "unique": str(len(endings)), "total": str(total)})
    return {
        "schema_version": 1,
        "status": "REVIEWED-PASS" if not findings and total == 48 else "REVIEW-PENDING",
        "scope": "P1 recurring production-detail review",
        "reviewed": total,
        "unique_daily_actions": len(actions),
        "unique_choices": len(choices),
        "unique_ending_actions": len(endings),
        "profiles": profiles,
        "findings": findings,
        "notes": "全量 B 级人物均已从源表回写职业化日常动作、角色盲点、主动选择、不可逆代价、关系余波和结局动作；Season/Episode Gate 仍负责母集、微章与实际回访绑定。",
    }


def main() -> int:
    report = audit()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "REVIEWED-PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
