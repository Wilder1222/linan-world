from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"
REPORT = ROOT / "qa/reviews/recurring-demographic-audit.json"


def front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n+++", 4)
    values: dict[str, str] = {}
    if not text.startswith("+++\n") or end < 0:
        return values
    for line in text[4:end].splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def audit() -> dict:
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    findings: list[dict[str, str]] = []
    reviewed = 0
    explicit_youth = {"CHR-B-004": (0, 16), "CHR-B-025": (0, 16), "CHR-B-034": (0, 16), "CHR-B-042": (0, 16)}
    elder_cues = ("婆", "伯", "叔", "老人", "老吏", "老妇")
    youth_cues = ("少年", "孤女", "10 岁", "13 岁", "15 岁")
    for record in roster.get("named_characters", []):
        if record.get("tier") != "B":
            continue
        reviewed += 1
        path = ROOT / record["profile_path"]
        data = front_matter(path)
        text = path.read_text(encoding="utf-8")
        age = int(data.get("age_y0", "0"))
        occupation = data.get("occupation", "")
        residence = data.get("residence", "")
        if "由所在生活圈与工作时辰决定" in residence:
            findings.append({"id": record["id"], "severity": "BLOCK", "code": "generic_residence"})
        if record["id"] in explicit_youth and not (explicit_youth[record["id"]][0] <= age <= explicit_youth[record["id"]][1]):
            findings.append({"id": record["id"], "severity": "BLOCK", "code": "explicit_youth_age_mismatch", "age": str(age)})
        if any(cue in record["name"] + occupation for cue in elder_cues) and age < 45:
            findings.append({"id": record["id"], "severity": "REVIEW", "code": "elder_cue_age_review", "age": str(age)})
        if any(cue in record["name"] + occupation for cue in youth_cues) and age > 25:
            findings.append({"id": record["id"], "severity": "REVIEW", "code": "youth_cue_age_review", "age": str(age)})
        if "- 年龄依据：" not in text:
            findings.append({"id": record["id"], "severity": "BLOCK", "code": "missing_age_basis"})
    return {
        "status": "OPEN",
        "scope": "P1 recurring demographic and occupation audit",
        "reviewed": reviewed,
        "findings": findings,
        "manual_review_required": [
            "逐人确认年龄、家庭结构与职业阶段的南宋生活常识",
            "确认生活圈地址可支持首次日常、职业动作和回访连续性",
        ],
    }


def main() -> int:
    report = audit()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
