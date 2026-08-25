from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "qa/character-roster.json"


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("+++\n"):
        return {}
    end = text.find("\n+++", 4)
    if end < 0:
        return {}
    values = {}
    for line in text[4:end].splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            values[key.strip()] = value.strip().strip('"')
    values["_text"] = text
    return values


def audit() -> dict:
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    findings = []
    profile_counts = Counter()
    unique_fingerprints = set()
    unique_choices = set()
    for record in roster["named_characters"]:
        path = ROOT / record["profile_path"]
        data = front_matter(path)
        text = data.get("_text", "")
        tier = record["tier"]
        required = ["## 坚守七问", "## 非中央关系"]
        if tier == "B":
            required += ["## 基础状态", "## 终局职业回响", "## 四个 Foundation 状态"]
        else:
            required += ["## 身份与外在", "## 内在与行为", "## 现实与关系", "## 状态与选择链", "## 待集成人同步"]
            phrases = ("行为指纹", "复杂关系", "必须舍弃") if tier.startswith("L") else ("公开面具", "未承认欲望", "行为指纹", "触发与可观察序列", "日常锚点", "幽默/错位入口")
            for phrase in phrases:
                if phrase not in text:
                    findings.append({"id": record["id"], "severity": "REVIEW", "code": f"missing_observable_{phrase}"})
            fingerprint = next((line.strip() for line in text.splitlines() if line.strip().startswith("- 行为指纹：")), "")
            match = re.search(r"### ARC6-END\n(.*?)(?=\n### |\Z)", text, re.S)
            choice = match.group(1).strip() if match else ""
            if fingerprint:
                unique_fingerprints.add(fingerprint)
            if choice:
                unique_choices.add(choice)
        for heading in required:
            if heading not in text:
                findings.append({"id": record["id"], "severity": "BLOCK", "code": "missing_section", "field": heading})
        profile_counts[tier] += 1

    relation_files = sorted((ROOT / "characters/relations/core").glob("rel-*.md"))
    relation_missing_layers = []
    for path in relation_files:
        text = path.read_text(encoding="utf-8")
        for label in ("表面行为", "自觉动机", "未承认动机", "情感债务", "## 七维状态", "## 八个快照"):
            if label not in text:
                relation_missing_layers.append({"path": path.relative_to(ROOT).as_posix(), "field": label})

    spines = json.loads((ROOT / "qa/emotional-spines.json").read_text(encoding="utf-8"))["spines"]
    spine_state_count = sum(len(spine.get("arc_states", [])) for spine in spines)
    return {
        "status": "OPEN",
        "scope": "P1 Character Foundation content audit",
        "profile_counts": dict(profile_counts),
        "named_profile_total": sum(profile_counts.values()),
        "unique_observable_fingerprints": len(unique_fingerprints),
        "unique_arc6_choice_markers": len(unique_choices),
        "relationship_profile_total": len(relation_files),
        "relationship_missing_layers": relation_missing_layers,
        "emotional_spine_total": len(spines),
        "emotional_spine_state_total": spine_state_count,
        "findings": findings,
        "manual_review_required": [
            "确认年龄推定与职业状态，尤其 B 级人物的年龄与家庭结构",
            "将关系七维与八快照绑定到具体场次、物件、台词和连续性账本",
            "为 U 槽位在 Season Gate 后分配唯一故事身份，不提前写入主线",
            "为 BG 原型在 Episode Gate 后写入具体 microchapter_ids 与 extension_ids",
        ],
    }


def main() -> int:
    report = audit()
    path = ROOT / "qa/reviews/character-foundation-audit.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
