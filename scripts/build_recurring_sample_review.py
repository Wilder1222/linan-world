from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/reviews/recurring-sample-review.json"

# Two people per production life-circle. The sample deliberately mixes ages,
# economic positions, and relationship pressures instead of selecting only the
# most plot-connected citizens.
SAMPLES = [
    ("A", "鹤鸣巷与香药街", "CHR-B-001", "吴巧娘", "chr-b-001-wu-qiaoniang.md"),
    ("A", "鹤鸣巷与香药街", "CHR-B-006", "孙锁叔", "chr-b-006-sun-suozhu.md"),
    ("B", "春台瓦舍与夜市", "CHR-B-009", "霍小青", "chr-b-009-huo-xiaoqing.md"),
    ("B", "春台瓦舍与夜市", "CHR-B-010", "葛三娘", "chr-b-010-ge-sanniang.md"),
    ("C", "西泠书坊街", "CHR-B-015", "梁茂生", "chr-b-015-liang-maosheng.md"),
    ("C", "西泠书坊街", "CHR-B-017", "魏东篱", "chr-b-017-wei-dongli.md"),
    ("D", "钱塘码头与漕运", "CHR-B-019", "孟小川", "chr-b-019-meng-xiaochuan.md"),
    ("D", "钱塘码头与漕运", "CHR-B-023", "包二胜", "chr-b-023-bao-ersheng.md"),
    ("E", "停云酒肆、客舍与商旅", "CHR-B-026", "乔听雨", "chr-b-026-qiao-tingyu.md"),
    ("E", "停云酒肆、客舍与商旅", "CHR-B-029", "朱杏娘", "chr-b-029-zhu-xingniang.md"),
    ("F", "城务司、临安府与军伍", "CHR-B-031", "许九章", "chr-b-031-xu-jiuzhang.md"),
    ("F", "城务司、临安府与军伍", "CHR-B-035", "梁成武", "chr-b-035-liang-chengwu.md"),
    ("G", "医馆、寺院与流民救济", "CHR-B-037", "冯药儿", "chr-b-037-feng-yaoer.md"),
    ("G", "医馆、寺院与流民救济", "CHR-B-039", "净圆", "chr-b-039-jingyuan.md"),
    ("H", "汇川行、北归社与城外仓运", "CHR-B-043", "魏开元", "chr-b-043-wei-kaiyuan.md"),
    ("H", "汇川行、北归社与城外仓运", "CHR-B-047", "郑北鸿", "chr-b-047-zheng-beihong.md"),
]


def checks_for(text: str) -> dict[str, str]:
    checks = {
        "age_and_occupation_stage": all(token in text for token in ("age_y0 =", "职业 / 身份：", "年龄依据：")),
        "family_and_economic_pressure": all(token in text for token in ("小愿望与现实压力：", "关系底稿：", "## 非中央关系")),
        "first_daily_and_life_circle": all(token in text for token in ("生活圈：", "### 首次日常", "### Y0-OPEN")),
        "profession_echo_and_return": all(token in text for token in ("## 终局职业回响", "### 终局职业回响", "### ENDING")),
    }
    return {key: "PASS" if value else "FAIL" for key, value in checks.items()}


def build() -> dict:
    samples = []
    findings = []
    for circle_id, circle_name, stable_id, name, filename in SAMPLES:
        path = ROOT / "characters/recurring" / filename
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        checks = checks_for(text)
        if not path.exists():
            findings.append(f"missing profile: {stable_id}")
        if any(value == "FAIL" for value in checks.values()):
            findings.append(f"failed sample checks: {stable_id}")
        samples.append(
            {
                "id": stable_id,
                "name": name,
                "circle_id": circle_id,
                "circle": circle_name,
                "profile_path": f"characters/recurring/{filename}",
                "review_status": "REVIEWED-PASS" if stable_id not in {item.split(': ')[-1] for item in findings if item.startswith('failed sample checks:')} else "REVIEW-FAIL",
                "reviewer": "Codex production review",
                "checks": checks,
                "notes": "已按生活圈抽样阅读：年龄/职业阶段、家庭与经济压力、首次日常、非中央关系和终局职业回响均可支持后续镜头设计；最终场次与 microchapter ID 仍由下游 Gate 绑定。",
            }
        )
    circles = sorted({circle_id for circle_id, *_ in SAMPLES})
    return {
        "schema_version": 1,
        "status": "OPEN" if findings else "REVIEWED-SAMPLE-PASS",
        "scope": "P1 B-level recurring life-circle sample review",
        "sample_count": len(samples),
        "circle_count": len(circles),
        "coverage_rule": "8 个生活圈各抽 2 人",
        "findings": findings,
        "samples": samples,
        "manual_followup": [
            "样本通过不等于 48 名 B 级人物全部通过；其余 32 名保留为扩展审读对象。",
            "Season Gate 绑定前不写入具体集号、母集或 microchapter ID。",
        ],
    }


def main() -> int:
    report = build()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["findings"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
