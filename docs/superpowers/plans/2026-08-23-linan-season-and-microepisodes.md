# 《临安春信》36 集母版与 648 微短章 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成一季 6 篇、36 集母版和 648 个可独立发布的 2—3 分钟微短章，使 12 名中央人物、24 名重要人物、48 名常驻人物及 22 名 U 级视角真正进入因果，同时精确满足主线 312、关系 204、日常 132 的内容预算。

**Architecture:** 先锁“谁在看”再写“看见什么”。每章只有一个首要 POV，并另有一个首要叙事功能；档位与功能是两套独立预算。生产顺序固定为编号骨架 → 个人 POV 卡位 → 72 个中央责任格与 36 个情感锚点 → 36 集因果 → 六篇季纲 → 每集三批六章 → 篇章与全季审读。任何 POV 变更都会让责任、覆盖、关系和连续性账本退回复核。

**Tech Stack:** Markdown、JSON、Python 3 标准库、`unittest`、PowerShell、Git。

---

## 1. 正式源文件

```text
story/
  00-series-outline.md
  01-arc-he-ming-lane.md
  02-arc-west-lake-rain.md
  03-arc-qiantang-undercurrent.md
  04-arc-osmanthus-human-world.md
  05-arc-linan-lockdown.md
  06-arc-ten-thousand-lanterns.md
  07-clue-and-payoff-ledger.md

episodes/
  arc-01-m001-m108.md
  arc-02-m109-m216.md
  arc-03-m217-m324.md
  arc-04-m325-m432.md
  arc-05-m433-m540.md
  arc-06-m541-m648.md

qa/
  story-production-schema.md
  pov-allocation.json
  pov-budget-matrix.md
  function-allocation.json
  emotional-anchor-bindings.json
  emotional-spine-matrix.md
  episode-coverage-matrix.json
  episode-coverage-matrix.md
  background-usage.json
  unit-selection.json
  state/microchapter-state-events.jsonl
  state/relationship-events.jsonl
  state/clue-events.jsonl
  continuity-ledger.md
  clue-ledger.json
  production-status-ledger.md
```

六个 `episodes/arc-*.md` 是微短章正文唯一来源；季纲只引用微章 ID，不复制正文。Gate 状态只以 `qa/production-status.json` 为机器权威，`qa/production-status-ledger.md` 由它生成；人物覆盖只以 JSON 为权威，Markdown 为生成视图；17 个 REL 与六条情感脊柱保存关系语义，Season QA 只保存集章绑定。

## Task 1: 建立故事 Schema、骨架器与 19 类失败测试

**Files:**
- Create: `qa/story-production-schema.md`
- Create: `qa/production-status-ledger.md`
- Create: `qa/state/microchapter-state-events.jsonl`
- Create: `qa/state/relationship-events.jsonl`
- Create: `qa/state/clue-events.jsonl`
- Create: `scripts/scaffold_story.py`
- Create: `scripts/validate_story.py`
- Create: `scripts/accept_episode_task.ps1`
- Create: `tests/story_fixture.py`
- Create: `tests/test_story_validator.py`
- Create: `tests/test_accept_episode_task.ps1`
- Modify: `scripts/validate_project.py`

- [ ] **Step 1: 先写以下失败测试**

```text
duplicate_formal_id
global_id_gap
episode_not_18_cards
tier_total_mismatch
individual_pov_mismatch
arc_pov_mismatch
episode_tier_or_function_vector_mismatch
duration_or_compilation_window_failure
state_event_schema_or_chain_failure
important_cast_coverage_shortfall
central_four_episode_state_gap
recurring_first_second_pov_mismatch
unit_pov_duplicate
unit_event_or_return_shortfall
background_usage_invalid_or_shortfall
missing_responsibility_cell
missing_emotional_anchor
function_labor_closure_or_ending_failure
placeholder_or_required_clue_unresolved
```

测试不能只保留上面的名字。先创建以下完整、确定性的测试夹具；它不读取正式项目文件，因而任何失败都只归因于被测规则。将以下内容原样写入 `tests/story_fixture.py`：

```python
from __future__ import annotations

from collections import Counter, deque
from typing import Any


TIERS = ("L1", "L2", "L3", "A1", "A2", "A3", "B", "U")
FUNCTIONS = ("main", "relationship", "daily")
TIER_VECTORS = (
    (8, 4, 1, 1, 1, 0, 2, 1), (7, 4, 1, 2, 1, 1, 1, 1),
    (7, 3, 2, 2, 2, 0, 2, 0), (7, 3, 2, 2, 1, 1, 2, 0),
    (7, 3, 1, 2, 1, 0, 3, 1), (6, 4, 2, 2, 2, 1, 0, 1),
    (7, 3, 2, 2, 1, 0, 2, 1), (7, 3, 2, 2, 1, 1, 2, 0),
    (6, 3, 2, 2, 2, 0, 2, 1), (6, 3, 2, 2, 1, 1, 2, 1),
    (6, 3, 2, 3, 1, 0, 3, 0), (6, 3, 2, 2, 2, 1, 1, 1),
    (7, 3, 2, 2, 1, 0, 2, 1), (7, 3, 2, 2, 1, 1, 2, 0),
    (7, 3, 2, 2, 2, 0, 2, 0), (7, 3, 2, 2, 1, 0, 2, 1),
    (7, 3, 2, 2, 1, 1, 2, 0), (6, 3, 2, 2, 2, 0, 2, 1),
    (6, 3, 1, 2, 1, 1, 3, 1), (6, 3, 2, 2, 1, 0, 3, 1),
    (6, 3, 1, 2, 2, 1, 2, 1), (5, 3, 2, 3, 1, 0, 3, 1),
    (6, 3, 2, 2, 1, 1, 3, 0), (5, 3, 2, 3, 2, 0, 2, 1),
    (7, 3, 2, 2, 1, 0, 2, 1), (7, 3, 2, 3, 1, 1, 1, 0),
    (7, 3, 2, 2, 2, 0, 2, 0), (6, 3, 3, 3, 1, 0, 1, 1),
    (6, 3, 3, 3, 1, 1, 1, 0), (6, 2, 2, 2, 2, 0, 3, 1),
    (6, 3, 2, 2, 1, 0, 3, 1), (6, 3, 2, 3, 1, 1, 2, 0),
    (6, 3, 3, 2, 2, 0, 2, 0), (6, 2, 3, 3, 1, 1, 2, 0),
    (6, 2, 3, 3, 1, 0, 2, 1), (6, 3, 2, 2, 2, 1, 1, 1),
)
FUNCTION_VECTORS = (
    (9, 5, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4), (7, 7, 4),
    (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4), (8, 6, 4),
    (9, 6, 3), (10, 5, 3), (10, 5, 3), (10, 5, 3), (11, 4, 3), (10, 5, 3),
    (5, 7, 6), (5, 7, 6), (5, 7, 6), (5, 7, 6), (5, 7, 6), (5, 7, 6),
    (9, 7, 2), (10, 6, 2), (10, 6, 2), (10, 6, 2), (11, 5, 2), (10, 6, 2),
    (10, 5, 3), (11, 4, 3), (11, 4, 3), (12, 3, 3), (12, 3, 3), (10, 5, 3),
)
CHARACTER_QUOTAS = {
    "L1": (("CHR-L1-01", 52), ("CHR-L1-02", 44), ("CHR-L1-03", 42), ("CHR-L1-04", 46), ("CHR-L1-05", 46)),
    "L2": (("CHR-L2-01", 30), ("CHR-L2-02", 28), ("CHR-L2-03", 26), ("CHR-L2-04", 24)),
    "L3": (("CHR-L3-01", 28), ("CHR-L3-02", 24), ("CHR-L3-03", 20)),
    "A1": tuple((f"CHR-A1-{index:02}", 10) for index in range(1, 9)),
    "A2": tuple((f"CHR-A2-{index:02}", 6) for index in range(1, 9)),
    "A3": tuple((f"CHR-A3-{index:02}", 2) for index in range(1, 9)),
    "B": tuple((f"CHR-B-{index:03}", 2 if index <= 24 else 1) for index in range(1, 49)),
    "U": tuple((f"CHR-U-{index:03}", 1) for index in range(1, 23)),
}


def _expanded_queues() -> dict[str, deque[str]]:
    return {
        tier: deque(character_id for character_id, quota in entries for _ in range(quota))
        for tier, entries in CHARACTER_QUOTAS.items()
    }


def _coverage_event(episode: int, role: str = "A", *, state_update: bool = False) -> dict[str, Any]:
    return {
        "episode_id": f"S1-E{episode:02}",
        "global_id": f"M{((episode - 1) * 18) + 1:03}",
        "role": role,
        "state_update": state_update,
    }


def make_valid_dataset() -> dict[str, Any]:
    queues = _expanded_queues()
    cards: list[dict[str, Any]] = []
    tier_by_episode: dict[str, dict[str, int]] = {}
    function_by_episode: dict[str, dict[str, int]] = {}
    assignments: dict[str, dict[str, str]] = {}
    function_assignments: dict[str, str] = {}
    global_number = 0

    for episode_index, (tier_vector, function_vector) in enumerate(zip(TIER_VECTORS, FUNCTION_VECTORS), start=1):
        episode_id = f"S1-E{episode_index:02}"
        tier_sequence = [tier for tier, count in zip(TIERS, tier_vector) for _ in range(count)]
        function_sequence = [name for name, count in zip(FUNCTIONS, function_vector) for _ in range(count)]
        tier_by_episode[episode_id] = dict(zip(TIERS, tier_vector))
        function_by_episode[episode_id] = dict(zip(FUNCTIONS, function_vector))
        for position, (tier, primary_function) in enumerate(zip(tier_sequence, function_sequence), start=1):
            global_number += 1
            global_id = f"M{global_number:03}"
            character_id = queues[tier].popleft()
            responsibility_ids = [f"RESP-{index:03}" for index in range(global_number, global_number + 1)] if global_number <= 72 else []
            emotional_anchor_ids = [f"EM-{episode_index:03}"] if position == 1 else []
            card = {
                "formal_id": f"S1-E{episode_index:02}-M{position:02}",
                "global_id": global_id,
                "episode_id": episode_id,
                "arc_id": f"{((episode_index - 1) // 6) + 1:02}",
                "position": position,
                "pov_character_id": character_id,
                "pov_tier": tier,
                "primary_function": primary_function,
                "target_seconds": 150,
                "hook_seconds": 10,
                "desire_seconds": 25,
                "resistance_seconds": 80,
                "choice_seconds": 25,
                "ending_seconds": 10,
                "seam_trim_seconds": 5,
                "duration_exception_reason": "",
                "labor": position <= 9,
                "closure": position in {6, 12, 18},
                "ending_kind": "hard" if position in {6, 12, 18} else "soft",
                "choice": "作出不可撤销的当下选择",
                "cost": "失去时间、收入或关系信用",
                "entry_state_ref": f"ENTRY-{global_id}",
                "exit_state_ref": f"EXIT-{global_id}",
                "responsibility_ids": responsibility_ids,
                "emotional_anchor_ids": emotional_anchor_ids,
                "state_event_ids": [],
                "clue_event_ids": [],
                "text": "人物以本职行动，状态发生可见变化。",
            }
            cards.append(card)
            assignments[global_id] = {"pov_character_id": character_id, "pov_tier": tier}
            function_assignments[global_id] = primary_function

    assert global_number == 648
    assert all(not queue for queue in queues.values())
    individual_totals = Counter(card["pov_character_id"] for card in cards)
    arc_tier_vectors: dict[str, dict[str, int]] = {}
    for arc_number in range(1, 7):
        arc_id = f"{arc_number:02}"
        arc_cards = [card for card in cards if card["arc_id"] == arc_id]
        arc_tier_vectors[arc_id] = {tier: sum(card["pov_tier"] == tier for card in arc_cards) for tier in TIERS}

    coverage: dict[str, dict[str, Any]] = {}
    for tier, entries in CHARACTER_QUOTAS.items():
        for character_id, _ in entries:
            if tier in {"L1", "L2", "L3"}:
                events = [_coverage_event(episode, state_update=True) for episode in range(1, 37)]
            elif tier == "A1":
                events = [_coverage_event(episode) for episode in range(1, 13)]
            elif tier == "A2":
                events = [_coverage_event(episode) for episode in range(1, 9)]
            elif tier == "A3":
                events = [_coverage_event(episode) for episode in range(1, 5)]
            elif tier == "B":
                events = [_coverage_event(1), _coverage_event(31)]
            else:
                number = int(character_id.rsplit("-", 1)[1])
                first_episode = 1 + ((number - 1) % 30)
                events = [_coverage_event(first_episode, "A")]
                if number <= 40:
                    events.append(_coverage_event(31 + ((number - 1) % 6), "R"))
            coverage[character_id] = {"tier": tier, "events": events}

    prototypes = {
        f"CHR-BG-{index:03}": {
            "eligible_location_ids": ["LOC-01"],
            "eligible_time_windows": ["DAY"],
            "eligible_work_states": ["WORK"],
        }
        for index in range(1, 301)
    }
    background_uses = [
        {
            "prototype_id": f"CHR-BG-{index:03}",
            "global_id": f"M{index:03}",
            "location_id": "LOC-01",
            "time_window": "DAY",
            "work_state": "WORK",
        }
        for index in range(1, 181)
    ]
    responsibilities = [
        {"id": f"RESP-{index:03}", "episode_id": cards[index - 1]["episode_id"], "global_id": f"M{index:03}"}
        for index in range(1, 73)
    ]
    emotions = [
        {"id": f"EM-{episode:03}", "episode_id": f"S1-E{episode:02}", "global_id": f"M{((episode - 1) * 18) + 1:03}"}
        for episode in range(1, 37)
    ]
    state_events = [
        {"event_id": "ST-M001-01", "global_id": "M001", "subject_id": "CHR-L1-01", "dimension": "money", "before": 0, "after": 1},
        {"event_id": "ST-M002-01", "global_id": "M002", "subject_id": "CHR-L1-01", "dimension": "money", "before": 1, "after": 2},
    ]
    clues = [{"id": "CLU-001", "required": True, "stages": ["seed", "misread", "verify", "payoff"]}]
    outlines = [
        {"episode_id": f"S1-E{episode:02}", "irreversible_change": "状态改变", "next_question": "相邻问题"}
        for episode in range(1, 37)
    ]
    return {
        "cards": cards,
        "expected": {
            "assignments": assignments,
            "function_assignments": function_assignments,
            "individual_totals": dict(individual_totals),
            "arc_tier_vectors": arc_tier_vectors,
            "episode_tier_vectors": tier_by_episode,
            "episode_function_vectors": function_by_episode,
        },
        "coverage": coverage,
        "background": {"prototypes": prototypes, "uses": background_uses},
        "responsibilities": responsibilities,
        "emotions": emotions,
        "state_events": state_events,
        "relationship_events": [],
        "clue_events": [],
        "clues": clues,
        "outlines": outlines,
        "source_texts": {"episodes/arc-01-m001-m108.md": "成品正文，无占位文本。"},
    }
```

再将以下完整测试写入 `tests/test_story_validator.py`。每个测试只破坏一个最小事实，并断言稳定错误码；最后三个测试覆盖脚手架和 CLI 的 0/1/2 退出码：

```python
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.scaffold_story import build_documents, inspect_documents
from scripts.validate_story import validate_dataset
from tests.story_fixture import make_valid_dataset


ROOT = Path(__file__).resolve().parents[1]


class StoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = make_valid_dataset()

    def codes(self, data=None) -> set[str]:
        errors = validate_dataset(data or self.data, stage="all", strict=True)
        return {error.split("|", 1)[0] for error in errors}

    def assert_code(self, code: str, data=None) -> None:
        self.assertIn(code, self.codes(data), f"missing {code}")

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], validate_dataset(self.data, stage="all", strict=True))

    def test_duplicate_formal_id(self) -> None:
        self.data["cards"][1]["formal_id"] = self.data["cards"][0]["formal_id"]
        self.assert_code("duplicate_formal_id")

    def test_global_id_gap(self) -> None:
        self.data["cards"][1]["global_id"] = "M999"
        self.assert_code("global_id_gap")

    def test_episode_not_18_cards(self) -> None:
        self.data["cards"].pop()
        self.assert_code("episode_not_18_cards")

    def test_tier_total_mismatch(self) -> None:
        self.data["cards"][0]["pov_tier"] = "L2"
        self.assert_code("tier_total_mismatch")

    def test_individual_pov_mismatch(self) -> None:
        self.data["expected"]["assignments"]["M001"]["pov_character_id"] = "CHR-L1-02"
        self.assert_code("individual_pov_mismatch")

    def test_arc_pov_mismatch(self) -> None:
        self.data["expected"]["arc_tier_vectors"]["01"]["L1"] += 1
        self.assert_code("arc_pov_mismatch")

    def test_episode_tier_or_function_vector_mismatch(self) -> None:
        self.data["expected"]["episode_function_vectors"]["S1-E01"]["daily"] += 1
        self.assert_code("episode_tier_or_function_vector_mismatch")

    def test_duration_or_compilation_window_failure(self) -> None:
        self.data["cards"][0]["target_seconds"] = 181
        self.assert_code("duration_or_compilation_window_failure")

    def test_state_event_schema_or_chain_failure(self) -> None:
        self.data["state_events"][1]["before"] = 99
        self.assert_code("state_event_schema_or_chain_failure")

    def test_important_cast_coverage_shortfall(self) -> None:
        self.data["coverage"]["CHR-A1-01"]["events"] = []
        self.assert_code("important_cast_coverage_shortfall")

    def test_central_four_episode_state_gap(self) -> None:
        for event in self.data["coverage"]["CHR-L1-01"]["events"][:4]:
            event["state_update"] = False
        self.assert_code("central_four_episode_state_gap")

    def test_recurring_first_second_pov_mismatch(self) -> None:
        self.data["expected"]["individual_totals"]["CHR-B-001"] = 1
        self.assert_code("recurring_first_second_pov_mismatch")

    def test_unit_pov_duplicate(self) -> None:
        unit_cards = [card for card in self.data["cards"] if card["pov_tier"] == "U"]
        unit_cards[1]["pov_character_id"] = unit_cards[0]["pov_character_id"]
        self.assert_code("unit_pov_duplicate")

    def test_unit_event_or_return_shortfall(self) -> None:
        self.data["coverage"]["CHR-U-120"]["events"] = []
        self.assert_code("unit_event_or_return_shortfall")

    def test_background_usage_invalid_or_shortfall(self) -> None:
        self.data["background"]["uses"] = self.data["background"]["uses"][:179]
        self.assert_code("background_usage_invalid_or_shortfall")

    def test_missing_responsibility_cell(self) -> None:
        self.data["responsibilities"].pop()
        self.assert_code("missing_responsibility_cell")

    def test_missing_emotional_anchor(self) -> None:
        self.data["emotions"].pop()
        self.assert_code("missing_emotional_anchor")

    def test_function_labor_closure_or_ending_failure(self) -> None:
        for card in self.data["cards"][:18]:
            card["labor"] = False
        self.assert_code("function_labor_closure_or_ending_failure")

    def test_placeholder_or_required_clue_unresolved(self) -> None:
        self.data["source_texts"]["episodes/arc-01-m001-m108.md"] = "TBD"
        self.assert_code("placeholder_or_required_clue_unresolved")

    def test_scaffold_is_exact_and_contiguous(self) -> None:
        documents = build_documents()
        self.assertEqual([], inspect_documents(documents))
        self.assertEqual(6, len(documents["episodes"]))
        self.assertEqual(648, sum(text.count("+++microcard") for text in documents["episodes"].values()))

    def test_cli_returns_zero_for_valid_and_one_for_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "fixture.json"
            fixture.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
            valid = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_story.py"), "--fixture", str(fixture), "--stage", "all", "--strict"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)
            broken = copy.deepcopy(self.data)
            broken["cards"][0]["formal_id"] = broken["cards"][1]["formal_id"]
            fixture.write_text(json.dumps(broken, ensure_ascii=False), encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_story.py"), "--fixture", str(fixture), "--stage", "all", "--strict"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(1, invalid.returncode)
            self.assertIn("FAIL duplicate_formal_id", invalid.stdout)

    def test_cli_usage_error_returns_two(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_story.py"), "--stage", "not-a-stage"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()
```

Run:

```powershell
python -m unittest tests.test_story_validator -v
```

Expected: 因实现尚不存在而失败。

- [ ] **Step 2: 定义微章完整字段**

`qa/story-production-schema.md` 必须要求：

```markdown
- 正式 ID：S1-E##-M##
- 全局 ID：M###
- 篇章／母集／章位：
- 目标时长：`target_seconds`，硬范围 120—180 秒，生产目标 145—165 秒
- 分段时长：`hook_seconds`、`desire_seconds`、`resistance_seconds`、`choice_seconds`、`ending_seconds`，五项之和必须等于目标时长
- 母集拼接裁缝：`seam_trim_seconds` 为 0—15 秒，只可删除重复承接，不得删选择或代价
- 主视角角色 ID：
- 主视角档位：
- 主视角预算槽：
- 覆盖角色：ID:P/A/R/D
- 背景人口原型：CHR-BG-### 列表；仅在画面中实际从事其允许劳动、消费、等待、照料或争执时填写
- 首要叙事功能：主线行动／人物关系／纯日常
- 副标签：职业、生活、节气、风物、声音、主题回声
- 时间与地点：
- POV 内可知事实：
- POV 错误认知：
- 禁止越界信息：
- 当下目标：
- 阻力或关系差：
- 状态变化：
- 选择与代价：
- 可见职业／日常行动：
- 入场硬状态／离场硬状态：
- 状态事件 ID：按 `ST-M001-01`、`RSE-M001-01`、`CSE-M001-01` 格式引用机器事件，不在 Markdown 内另写不可解析真值
- 线索事件：播种／误读／发酵／验证／回收
- 中央责任 ID：
- 情感锚点 ID：
- 结束按钮：
- 独立发布入口：
- 可剪承接缝：
- 外传插槽：
```

时长门禁同时验证：每章 120—180 秒且目标落在 145—165 秒；每母集 18 章去除 `seam_trim_seconds` 后为 2580—2760 秒，即 43—46 分钟。五段建议范围为入口 5—12 秒、愿望 20—35 秒、阻力 65—95 秒、选择 20—35 秒、结束按钮 8—18 秒；超出建议范围必须有 `duration_exception_reason`，但总时长硬范围不可豁免。

三份 JSONL 是连续性状态的机器权威：`microchapter-state-events` 每条含事件 ID、微章 ID、角色/物件 ID、维度、`before`、`after`、生效区间与来源；`relationship-events` 含 REL、七维之一、双向前后值与证据微章；`clue-events` 含 CLU、播种/误读/发酵/验证/回收阶段及知情角色。Markdown 卡只引用事件 ID，验证器逐条核对入场值等于上一有效离场值。

- [ ] **Step 3: 实现状态机**

```text
UNALLOCATED → ALLOCATED_TIER → ALLOCATED_CHARACTER → OUTLINED → DRAFTED
→ CARD_QA → EPISODE_QA → ARC_QA → CONTINUITY_QA → LOCKED
```

任一步失败转 `NEEDS_REVISION`；作者不得自行标记 `LOCKED`。

- [ ] **Step 3A: 写入完整故事验证器实现**

将以下整段原样写入 `scripts/validate_story.py`。这是唯一实现段，不允许执行者自行补写未定义函数：

```python
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
TIERS = ("L1", "L2", "L3", "A1", "A2", "A3", "B", "U")
FUNCTIONS = ("main", "relationship", "daily")
LOCKED_TIER_TOTALS = dict(zip(TIERS, (230, 108, 72, 80, 48, 16, 72, 22)))
LOCKED_FUNCTION_TOTALS = dict(zip(FUNCTIONS, (312, 204, 132)))
COVERAGE_MINIMUMS = {"L1": 24, "L2": 16, "L3": 12, "A1": 12, "A2": 8, "A3": 4, "B": 2, "U": 1}
VALID_COVERAGE_ROLES = {"P", "A", "R", "D"}
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|FIXME|XXX|PLACEHOLDER)\b|待定|以后再说|某角色|暂略|同上|\?{3,}", re.IGNORECASE)
MICROCARD_RE = re.compile(
    r"(?ms)^###\s+(?P<formal>S1-E\d{2}-M\d{2})\s*/\s*(?P<global>M\d{3})\s*$\s*"
    r"^\+\+\+microcard\s*$\n(?P<toml>.*?)^\+\+\+\s*$"
)
STATE_REQUIRED = {"event_id", "global_id", "subject_id", "dimension", "before", "after"}
STAGES = {"allocation", "outline", "coverage", "responsibility", "emotions", "continuity", "all"}


def issue(code: str, stable_id: str, detail: str) -> str:
    return f"{code}|{stable_id}|{detail}"


def numeric_id(value: str, prefix: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(rf"{re.escape(prefix)}\d{{3}}", value):
        return -1
    return int(value[len(prefix):])


def _json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        record.setdefault("_source_line", line_number)
        records.append(record)
    return records


def parse_microcards(episode_root: Path) -> tuple[list[dict[str, Any]], dict[str, str], list[str]]:
    cards: list[dict[str, Any]] = []
    texts: dict[str, str] = {}
    errors: list[str] = []
    if not episode_root.exists():
        return cards, texts, [issue("input_schema_error", "episodes", "missing_directory")]
    for path in sorted(episode_root.glob("arc-??-m???.md")):
        relative = path.as_posix()
        text = path.read_text(encoding="utf-8")
        texts[relative] = text
        for match in MICROCARD_RE.finditer(text):
            try:
                card = tomllib.loads(match.group("toml"))
            except tomllib.TOMLDecodeError as exc:
                errors.append(issue("input_schema_error", relative, f"invalid_microcard_toml={exc}"))
                continue
            card["_header_formal_id"] = match.group("formal")
            card["_header_global_id"] = match.group("global")
            card.setdefault("text", text[match.end(): text.find("\n### ", match.end()) if text.find("\n### ", match.end()) >= 0 else len(text)])
            cards.append(card)
    return cards, texts, errors


def load_root_dataset(root: Path = ROOT) -> dict[str, Any]:
    cards, episode_texts, load_errors = parse_microcards(root / "episodes")
    pov = _json(root / "qa/pov-allocation.json", {})
    functions = _json(root / "qa/function-allocation.json", {})
    coverage_raw = _json(root / "qa/episode-coverage-matrix.json", {})
    background = _json(root / "qa/background-usage.json", {"prototypes": {}, "uses": []})
    emotions_raw = _json(root / "qa/emotional-anchor-bindings.json", {})
    clues_raw = _json(root / "qa/clue-ledger.json", {})
    source_texts = dict(episode_texts)
    for directory in (root / "story",):
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                source_texts[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")

    responsibilities: list[dict[str, str]] = []
    for card in cards:
        for responsibility_id in card.get("responsibility_ids", []):
            responsibilities.append({"id": responsibility_id, "episode_id": card.get("episode_id", ""), "global_id": card.get("global_id", "")})
    emotions = emotions_raw.get("bindings", emotions_raw if isinstance(emotions_raw, list) else [])
    clues = clues_raw.get("clues", clues_raw if isinstance(clues_raw, list) else [])
    coverage = coverage_raw.get("characters", coverage_raw if isinstance(coverage_raw, dict) else {})
    outlines = [
        {
            "episode_id": f"S1-E{episode:02}",
            "irreversible_change": "BOUND_IN_STORY_SOURCE" if f"S1-E{episode:02}" in "\n".join(source_texts.values()) else "",
            "next_question": "BOUND_IN_STORY_SOURCE" if f"S1-E{episode:02}" in "\n".join(source_texts.values()) else "",
        }
        for episode in range(1, 37)
    ]
    return {
        "cards": cards,
        "expected": {
            "assignments": pov.get("assignments", {}),
            "individual_totals": pov.get("individual_totals", {}),
            "arc_tier_vectors": pov.get("arc_tier_vectors", {}),
            "episode_tier_vectors": pov.get("episode_tier_vectors", {}),
            "function_assignments": functions.get("assignments", {}),
            "episode_function_vectors": functions.get("episode_vectors", {}),
        },
        "coverage": coverage,
        "background": background,
        "responsibilities": responsibilities,
        "emotions": emotions,
        "state_events": _jsonl(root / "qa/state/microchapter-state-events.jsonl"),
        "relationship_events": _jsonl(root / "qa/state/relationship-events.jsonl"),
        "clue_events": _jsonl(root / "qa/state/clue-events.jsonl"),
        "clues": clues,
        "outlines": outlines,
        "source_texts": source_texts,
        "_load_errors": load_errors,
    }


def validate_identifiers(cards: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    formal_ids = [card.get("formal_id", "") for card in cards]
    global_ids = [card.get("global_id", "") for card in cards]
    for value, count in Counter(formal_ids).items():
        if count > 1:
            errors.append(issue("duplicate_formal_id", value or "missing", f"count={count}"))
    for card in cards:
        if card.get("formal_id") != card.get("_header_formal_id", card.get("formal_id")):
            errors.append(issue("duplicate_formal_id", str(card.get("formal_id", "missing")), "header_body_mismatch"))
        if card.get("global_id") != card.get("_header_global_id", card.get("global_id")):
            errors.append(issue("global_id_gap", str(card.get("global_id", "missing")), "header_body_mismatch"))
    numbers = sorted(numeric_id(value, "M") for value in global_ids)
    if numbers != list(range(1, 649)):
        errors.append(issue("global_id_gap", "M001..M648", f"actual_count={len(numbers)}"))
    episode_counts = Counter(card.get("episode_id", "") for card in cards)
    for episode in range(1, 37):
        episode_id = f"S1-E{episode:02}"
        if episode_counts[episode_id] != 18:
            errors.append(issue("episode_not_18_cards", episode_id, f"actual={episode_counts[episode_id]}"))
    return errors


def _counter_dict(cards: Iterable[dict[str, Any]], key: str, values: Iterable[str]) -> dict[str, int]:
    counter = Counter(card.get(key) for card in cards)
    return {value: counter[value] for value in values}


def validate_allocation(data: dict[str, Any], allow_reserved_unit_slots: bool) -> list[str]:
    cards = data["cards"]
    expected = data.get("expected", {})
    errors: list[str] = []
    actual_tiers = _counter_dict(cards, "pov_tier", TIERS)
    if actual_tiers != LOCKED_TIER_TOTALS:
        errors.append(issue("tier_total_mismatch", "S1", f"actual={actual_tiers}"))
    actual_functions = _counter_dict(cards, "primary_function", FUNCTIONS)
    if actual_functions != LOCKED_FUNCTION_TOTALS:
        errors.append(issue("function_labor_closure_or_ending_failure", "S1", f"functions={actual_functions}"))

    assignments = expected.get("assignments", {})
    function_assignments = expected.get("function_assignments", {})
    for card in cards:
        global_id = card.get("global_id", "missing")
        allocation = assignments.get(global_id)
        if allocation is None or allocation.get("pov_character_id") != card.get("pov_character_id") or allocation.get("pov_tier") != card.get("pov_tier"):
            errors.append(issue("individual_pov_mismatch", global_id, "card_does_not_match_pov_allocation"))
        if function_assignments.get(global_id) != card.get("primary_function"):
            errors.append(issue("episode_tier_or_function_vector_mismatch", global_id, "card_does_not_match_function_allocation"))

    actual_individual = Counter(card.get("pov_character_id") for card in cards)
    for character_id, quota in expected.get("individual_totals", {}).items():
        if actual_individual[character_id] != quota:
            code = "recurring_first_second_pov_mismatch" if character_id.startswith("CHR-B-") else "individual_pov_mismatch"
            errors.append(issue(code, character_id, f"actual={actual_individual[character_id]} expected={quota}"))

    for arc_id, vector in expected.get("arc_tier_vectors", {}).items():
        arc_cards = [card for card in cards if card.get("arc_id") == arc_id]
        actual = _counter_dict(arc_cards, "pov_tier", TIERS)
        if actual != vector:
            errors.append(issue("arc_pov_mismatch", arc_id, f"actual={actual} expected={vector}"))
    for episode_id, vector in expected.get("episode_tier_vectors", {}).items():
        episode_cards = [card for card in cards if card.get("episode_id") == episode_id]
        actual = _counter_dict(episode_cards, "pov_tier", TIERS)
        if actual != vector:
            errors.append(issue("episode_tier_or_function_vector_mismatch", episode_id, f"tier_actual={actual} expected={vector}"))
    for episode_id, vector in expected.get("episode_function_vectors", {}).items():
        episode_cards = [card for card in cards if card.get("episode_id") == episode_id]
        actual = _counter_dict(episode_cards, "primary_function", FUNCTIONS)
        if actual != vector:
            errors.append(issue("episode_tier_or_function_vector_mismatch", episode_id, f"function_actual={actual} expected={vector}"))

    unit_ids = [card.get("pov_character_id", "") for card in cards if card.get("pov_tier") == "U"]
    if allow_reserved_unit_slots:
        valid = len(unit_ids) == 22 and len(set(unit_ids)) == 22 and all(re.fullmatch(r"U-POV-SLOT-\d{2}", value) for value in unit_ids)
    else:
        valid = len(unit_ids) == 22 and len(set(unit_ids)) == 22 and all(re.fullmatch(r"CHR-U-\d{3}", value) for value in unit_ids)
    if not valid:
        errors.append(issue("unit_pov_duplicate", "U", f"values={unit_ids}"))
    return errors


def validate_outline(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    outlines = data.get("outlines", [])
    by_id = {item.get("episode_id"): item for item in outlines}
    for episode in range(1, 37):
        episode_id = f"S1-E{episode:02}"
        item = by_id.get(episode_id, {})
        if not item.get("irreversible_change") or not item.get("next_question"):
            errors.append(issue("outline_episode_incomplete", episode_id, "missing_irreversible_change_or_next_question"))
    return errors


def validate_coverage(data: dict[str, Any]) -> list[str]:
    coverage = data.get("coverage", {})
    errors: list[str] = []
    for character_id, record in coverage.items():
        tier = record.get("tier", "")
        events = record.get("events", [])
        valid_events = [event for event in events if event.get("role") in VALID_COVERAGE_ROLES]
        unique_episodes = {event.get("episode_id") for event in valid_events}
        required = COVERAGE_MINIMUMS.get(tier, math.inf)
        if len(unique_episodes) < required:
            errors.append(issue("important_cast_coverage_shortfall", character_id, f"actual={len(unique_episodes)} expected>={required}"))
        if tier in {"L1", "L2", "L3"}:
            updated = {int(event["episode_id"][-2:]) for event in valid_events if event.get("state_update")}
            for start in range(1, 34):
                if not updated.intersection(range(start, start + 4)):
                    errors.append(issue("central_four_episode_state_gap", character_id, f"window=E{start:02}-E{start + 3:02}"))
                    break

    unit_records = {character_id: record for character_id, record in coverage.items() if character_id.startswith("CHR-U-")}
    returners = 0
    for index in range(1, 121):
        character_id = f"CHR-U-{index:03}"
        events = [event for event in unit_records.get(character_id, {}).get("events", []) if event.get("role") in VALID_COVERAGE_ROLES]
        episodes = sorted({event.get("episode_id") for event in events})
        if not episodes:
            errors.append(issue("unit_event_or_return_shortfall", character_id, "missing_first_event"))
        if len(episodes) >= 2:
            returners += 1
    if returners < 40:
        errors.append(issue("unit_event_or_return_shortfall", "U-RETURNS", f"actual={returners} expected>=40"))

    background = data.get("background", {})
    prototypes = background.get("prototypes", {})
    uses = background.get("uses", [])
    distinct = {use.get("prototype_id") for use in uses}
    if len(prototypes) < 300 or len(distinct) < 180:
        errors.append(issue("background_usage_invalid_or_shortfall", "BG", f"prototypes={len(prototypes)} distinct_used={len(distinct)}"))
    for use in uses:
        prototype_id = use.get("prototype_id", "missing")
        prototype = prototypes.get(prototype_id)
        if prototype is None or use.get("location_id") not in prototype.get("eligible_location_ids", []) or use.get("time_window") not in prototype.get("eligible_time_windows", []) or use.get("work_state") not in prototype.get("eligible_work_states", []):
            errors.append(issue("background_usage_invalid_or_shortfall", prototype_id, "ineligible_use"))
    return errors


def validate_responsibilities(data: dict[str, Any]) -> list[str]:
    bindings = data.get("responsibilities", [])
    ids = [binding.get("id", "") for binding in bindings]
    valid_globals = {card.get("global_id") for card in data["cards"]}
    if len(bindings) != 72 or len(set(ids)) != 72 or any(binding.get("global_id") not in valid_globals for binding in bindings):
        return [issue("missing_responsibility_cell", "RESP", f"bindings={len(bindings)} unique={len(set(ids))}")]
    return []


def validate_emotions(data: dict[str, Any]) -> list[str]:
    bindings = data.get("emotions", [])
    ids = [binding.get("id", "") for binding in bindings]
    episodes = Counter(binding.get("episode_id") for binding in bindings)
    valid_globals = {card.get("global_id") for card in data["cards"]}
    if len(bindings) != 36 or len(set(ids)) != 36 or any(episodes[f"S1-E{episode:02}"] != 1 for episode in range(1, 37)) or any(binding.get("global_id") not in valid_globals for binding in bindings):
        return [issue("missing_emotional_anchor", "EM", f"bindings={len(bindings)} unique={len(set(ids))}")]
    return []


def _selected_cards(cards: list[dict[str, Any]], episode: str | None, arc: str | None) -> list[dict[str, Any]]:
    if episode:
        return [card for card in cards if card.get("episode_id") == episode]
    if arc:
        return [card for card in cards if card.get("arc_id") == arc]
    return cards


def validate_content(data: dict[str, Any], *, episode: str | None, arc: str | None, strict: bool) -> list[str]:
    cards = _selected_cards(data["cards"], episode, arc)
    errors: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        grouped[card.get("episode_id", "missing")].append(card)
        global_id = card.get("global_id", "missing")
        target = card.get("target_seconds")
        beats = [card.get(name) for name in ("hook_seconds", "desire_seconds", "resistance_seconds", "choice_seconds", "ending_seconds")]
        hard_ok = isinstance(target, int) and 120 <= target <= 180
        target_ok = isinstance(target, int) and 145 <= target <= 165
        sum_ok = all(isinstance(value, int) for value in beats) and sum(beats) == target
        trim = card.get("seam_trim_seconds")
        trim_ok = isinstance(trim, int) and 0 <= trim <= 15
        suggestions = ((5, 12), (20, 35), (65, 95), (20, 35), (8, 18))
        suggestions_ok = all(low <= value <= high for value, (low, high) in zip(beats, suggestions)) if all(isinstance(value, int) for value in beats) else False
        if not hard_ok or not target_ok or not sum_ok or not trim_ok or (not suggestions_ok and not card.get("duration_exception_reason")):
            errors.append(issue("duration_or_compilation_window_failure", global_id, "invalid_microchapter_duration"))
        if not card.get("choice") or not card.get("cost"):
            errors.append(issue("function_labor_closure_or_ending_failure", global_id, "missing_choice_or_cost"))

    for episode_id, episode_cards in grouped.items():
        if len(episode_cards) != 18:
            continue
        episode_cards.sort(key=lambda card: card.get("position", 0))
        compiled = sum(card["target_seconds"] - card["seam_trim_seconds"] for card in episode_cards)
        hard = sum(card.get("ending_kind") == "hard" for card in episode_cards)
        soft = sum(card.get("ending_kind") == "soft" for card in episode_cards)
        closures = {card.get("position") for card in episode_cards if card.get("closure")}
        labor = sum(bool(card.get("labor")) for card in episode_cards)
        if not 2580 <= compiled <= 2760:
            errors.append(issue("duration_or_compilation_window_failure", episode_id, f"compiled={compiled}"))
        if labor < 9 or not 3 <= hard <= 5 or soft < 9 or closures != {6, 12, 18}:
            errors.append(issue("function_labor_closure_or_ending_failure", episode_id, f"labor={labor} hard={hard} soft={soft} closures={sorted(closures)}"))

    if strict:
        for path, text in data.get("source_texts", {}).items():
            match = PLACEHOLDER_RE.search(text)
            if match:
                errors.append(issue("placeholder_or_required_clue_unresolved", path, f"placeholder={match.group(0)}"))
    return errors


def validate_state_events(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    chains: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in data.get("state_events", []):
        missing = STATE_REQUIRED.difference(event)
        if missing or numeric_id(str(event.get("global_id", "")), "M") < 1:
            errors.append(issue("state_event_schema_or_chain_failure", str(event.get("event_id", "missing")), f"missing={sorted(missing)}"))
            continue
        chains[(event["subject_id"], event["dimension"])].append(event)
    for key, events in chains.items():
        events.sort(key=lambda event: numeric_id(event["global_id"], "M"))
        for previous, current in zip(events, events[1:]):
            if previous["after"] != current["before"]:
                errors.append(issue("state_event_schema_or_chain_failure", "/".join(key), f"{previous['event_id']}->{current['event_id']}"))
    return errors


def validate_clues(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_stages = {"seed", "verify", "payoff"}
    for clue in data.get("clues", []):
        stages = set(clue.get("stages", []))
        has_middle = bool(stages.intersection({"misread", "ferment"}))
        if clue.get("required") and (not required_stages.issubset(stages) or not has_middle):
            errors.append(issue("placeholder_or_required_clue_unresolved", clue.get("id", "missing"), f"stages={sorted(stages)}"))
    return errors


def validate_dataset(
    data: dict[str, Any],
    *,
    stage: str = "all",
    strict: bool = False,
    episode: str | None = None,
    arc: str | None = None,
    allow_reserved_unit_slots: bool = False,
) -> list[str]:
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    errors = list(data.get("_load_errors", []))
    errors.extend(validate_identifiers(data.get("cards", [])))
    if stage in {"allocation", "outline", "continuity", "all"}:
        errors.extend(validate_allocation(data, allow_reserved_unit_slots))
    if stage in {"outline", "all"}:
        errors.extend(validate_outline(data))
    if stage in {"coverage", "continuity", "all"}:
        errors.extend(validate_coverage(data))
    if stage in {"responsibility", "continuity", "all"}:
        errors.extend(validate_responsibilities(data))
    if stage in {"emotions", "continuity", "all"}:
        errors.extend(validate_emotions(data))
    if stage in {"continuity", "all"}:
        errors.extend(validate_content(data, episode=episode, arc=arc, strict=strict))
        errors.extend(validate_state_events(data))
        errors.extend(validate_clues(data))
    return sorted(set(errors))


def validate_root(
    root: Path = ROOT,
    *,
    stage: str = "all",
    strict: bool = False,
    episode: str | None = None,
    arc: str | None = None,
    allow_reserved_unit_slots: bool = False,
) -> list[str]:
    try:
        data = load_root_dataset(root)
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return [issue("input_schema_error", str(root), str(exc))]
    return validate_dataset(
        data,
        stage=stage,
        strict=strict,
        episode=episode,
        arc=arc,
        allow_reserved_unit_slots=allow_reserved_unit_slots,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Linan season and microchapter production data")
    parser.add_argument("--stage", choices=sorted(STAGES), default="all")
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument("--episode", choices=[f"S1-E{number:02}" for number in range(1, 37)])
    selectors.add_argument("--arc", choices=[f"{number:02}" for number in range(1, 7)])
    selectors.add_argument("--season", choices=["S1"])
    parser.add_argument("--allow-reserved-unit-slots", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--fixture", type=Path, help="test-only normalized JSON fixture")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture else load_root_dataset(args.root.resolve())
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"FAIL input_schema_error|cli|{exc}")
        return 1
    errors = validate_dataset(
        data,
        stage=args.stage,
        strict=args.strict,
        episode=args.episode,
        arc=args.arc,
        allow_reserved_unit_slots=args.allow_reserved_unit_slots,
    )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"FAIL stage={args.stage} errors={len(errors)}")
        return 1
    selected = args.episode or (f"arc-{args.arc}" if args.arc else args.season or "S1")
    print(f"PASS stage={args.stage} scope={selected} errors=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

验证器退出码固定为：`0` 验证通过；`1` 内容、状态链、输入文件或 Schema 失败；`2` `argparse` 用法或非法枚举失败。错误行固定为 `FAIL error_code|stable_id|detail`，并按完整字符串排序；成功行固定以 `PASS` 开头。

- [ ] **Step 4: 实现 CLI**

`scripts/validate_story.py` 必须支持：

```text
--stage allocation|outline|coverage|responsibility|emotions|continuity
--episode S1-E##
--arc 01..06
--season S1
--allow-reserved-unit-slots
--strict
```

- [ ] **Step 4A: 实现逐母集验收辅助脚本**

`scripts/accept_episode_task.ps1` 只接受 `-Task 13` 至 `-Task 48`，由任务号严格计算 `S1-E01` 至 `S1-E36` 并映射到六个明确的 `episodes/arc-*.md` 文件。它采用两阶段协议：`-Begin` 仅在工作树和暂存区都干净、上一任务提交存在且当前任务正是下一个任务时，以独占创建方式取得 `.git/linan-episode-integration.lock`，记录任务号、基线 HEAD、允许修改路径与取得时间；作者持锁写作。无模式参数等同 `-Finish`：要求锁中任务与参数一致、HEAD 仍等于基线、暂存区为空、所有 dirty 路径严格属于本任务 allowlist，然后运行本集验证与 `git diff --check`，只暂存该篇正文文件及 POV、功能、覆盖、人物状态、关系、BG、线索、连续性账本和三份状态事件 JSONL，使用 `episodes: complete S1-E## microchapter cards` 提交并释放锁。验证失败时保留锁供同一任务修正；`-Abort` 只在 HEAD 未变且工作树/暂存区重新干净后释放本任务锁。`-DryRun` 输出映射、前序条件、allowlist 和锁状态而不写入或提交；越界、乱序、已有锁、锁不匹配、越权脏路径或前序缺失均立即非零退出。

- [ ] **Step 4A.1: 先写两阶段锁的失败测试**

将以下完整脚本写入 `tests/test_accept_episode_task.ps1`。它在系统临时目录建立独立 Git fixture，验证映射、退出码、原子排他、脏路径白名单、失败保锁、成功提交与安全中止：

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SourceHelper = Join-Path $ProjectRoot 'scripts/accept_episode_task.ps1'
$Assertions = 0

function Assert-True {
    param([bool]$Condition, [string]$Message)
    $script:Assertions += 1
    if (-not $Condition) { throw "ASSERT_TRUE failed: $Message" }
}

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    $script:Assertions += 1
    if ($Expected -ne $Actual) { throw "ASSERT_EQUAL failed: $Message expected=[$Expected] actual=[$Actual]" }
}

function Invoke-Helper {
    param([string[]]$Arguments)
    $output = @(& pwsh -NoProfile -File 'scripts/accept_episode_task.ps1' @Arguments 2>&1)
    $code = $LASTEXITCODE
    return [pscustomobject]@{ Code = $code; Text = ($output -join "`n") }
}

if (-not (Test-Path -LiteralPath $SourceHelper)) {
    [Console]::Error.WriteLine('FAIL helper_missing_before_implementation')
    exit 1
}

$FixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("linan-helper-test-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $FixtureRoot | Out-Null

try {
    Push-Location $FixtureRoot
    & git init --quiet
    & git config user.name 'Linan Test'
    & git config user.email 'linan-test@example.invalid'
    New-Item -ItemType Directory -Path 'scripts', 'episodes' | Out-Null
    Copy-Item -LiteralPath $SourceHelper -Destination 'scripts/accept_episode_task.ps1'
    @'
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--episode", required=True)
parser.add_argument("--strict", action="store_true")
args = parser.parse_args()
print(f"PASS episode={args.episode}")
'@ | Set-Content -LiteralPath 'scripts/validate_story.py' -Encoding utf8NoBOM
    'arc-one baseline' | Set-Content -LiteralPath 'episodes/arc-01-m001-m108.md' -Encoding utf8NoBOM
    & git add -- scripts episodes
    & git commit --quiet -m 'qa: lock Linan season one outline'

    $dry = Invoke-Helper @('-Task', '13', '-DryRun')
    Assert-Equal 0 $dry.Code 'DryRun must succeed without creating a lock'
    Assert-True ($dry.Text -match '"episode_id"\s*:\s*"S1-E01"') 'DryRun prints exact episode mapping'
    Assert-True ($dry.Text -match '"arc_file"\s*:\s*"episodes/arc-01-m001-m108.md"') 'DryRun prints exact arc file'

    $outOfRange = Invoke-Helper @('-Task', '12', '-DryRun')
    Assert-Equal 1 $outOfRange.Code 'ValidateRange failure exits one under pwsh'

    Add-Content -LiteralPath 'episodes/arc-01-m001-m108.md' -Value 'dirty before begin'
    $dirtyBegin = Invoke-Helper @('-Task', '13', '-Begin')
    Assert-Equal 1 $dirtyBegin.Code 'Begin rejects a dirty tree'
    Assert-True ($dirtyBegin.Text -match 'working_tree_not_clean') 'dirty-tree error is stable'
    & git restore --worktree -- 'episodes/arc-01-m001-m108.md'

    $begin = Invoke-Helper @('-Task', '13', '-Begin')
    Assert-Equal 0 $begin.Code 'Begin acquires the lock'
    $gitCommon = (& git rev-parse --git-common-dir).Trim()
    if (-not [System.IO.Path]::IsPathRooted($gitCommon)) { $gitCommon = Join-Path $FixtureRoot $gitCommon }
    $lockPath = Join-Path ([System.IO.Path]::GetFullPath($gitCommon)) 'linan-episode-integration.lock'
    Assert-True (Test-Path -LiteralPath $lockPath) 'lock lives in git common dir'

    $secondBegin = Invoke-Helper @('-Task', '13', '-Begin')
    Assert-Equal 1 $secondBegin.Code 'second Begin is excluded atomically'
    Assert-True ($secondBegin.Text -match 'lock_exists') 'lock collision has stable error'

    Add-Content -LiteralPath 'episodes/arc-01-m001-m108.md' -Value 'episode one completed'
    $finish = Invoke-Helper @('-Task', '13')
    Assert-Equal 0 $finish.Code 'default mode is Finish and commits allowlisted changes'
    Assert-True ($finish.Text -match 'PASS finish task=13 episode=S1-E01') 'Finish prints stable success line'
    Assert-True (-not (Test-Path -LiteralPath $lockPath)) 'successful Finish releases lock'
    Assert-Equal 'episodes: complete S1-E01 microchapter cards' ((& git log -1 --format=%s).Trim()) 'commit subject is exact'

    $begin14 = Invoke-Helper @('-Task', '14', '-Begin')
    Assert-Equal 0 $begin14.Code 'next sequential task can begin'
    'not allowed' | Set-Content -LiteralPath 'forbidden.txt' -Encoding utf8NoBOM
    $forbiddenFinish = Invoke-Helper @('-Task', '14', '-Finish')
    Assert-Equal 1 $forbiddenFinish.Code 'Finish rejects non-allowlisted paths'
    Assert-True ($forbiddenFinish.Text -match 'dirty_path_not_allowed\|forbidden.txt') 'forbidden path is named'
    Assert-True (Test-Path -LiteralPath $lockPath) 'failed Finish retains lock for correction'
    Remove-Item -LiteralPath 'forbidden.txt'

    $abort = Invoke-Helper @('-Task', '14', '-Abort')
    Assert-Equal 0 $abort.Code 'clean unchanged task can abort'
    Assert-True (-not (Test-Path -LiteralPath $lockPath)) 'Abort releases its own lock'

    $finishWithoutLock = Invoke-Helper @('-Task', '14', '-Finish')
    Assert-Equal 1 $finishWithoutLock.Code 'Finish without Begin fails'
    Assert-True ($finishWithoutLock.Text -match 'lock_missing') 'missing lock has stable error'

    Write-Output "PASS helper_tests=$Assertions"
    exit 0
}
catch {
    [Console]::Error.WriteLine("FAIL helper_test_exception=$($_.Exception.Message)")
    exit 1
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $FixtureRoot) {
        Remove-Item -LiteralPath $FixtureRoot -Recurse -Force
    }
}
```

Run:

```powershell
pwsh -NoProfile -File tests/test_accept_episode_task.ps1
```

Expected: 退出码 `1`，stderr 含 `FAIL helper_missing_before_implementation`。

- [ ] **Step 4A.2: 写入完整两阶段 helper**

将以下整段原样写入 `scripts/accept_episode_task.ps1`：

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(13, 48)]
    [int]$Task,
    [switch]$Begin,
    [switch]$Finish,
    [switch]$Abort,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Stop-Task {
    param([string]$Code, [string]$Detail = '')
    $suffix = if ($Detail) { "|$Detail" } else { '' }
    [Console]::Error.WriteLine("FAIL $Code$suffix")
    exit 1
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $output = @(& git @Arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Stop-Task 'git_command_failed' (($Arguments -join ' ') + '|' + ($output -join ' '))
    }
    return $output
}

function Normalize-RepoPath {
    param([string]$Path)
    return ($Path -replace '\\', '/').Trim()
}

function Get-HeadSha {
    return ((Invoke-Git 'rev-parse' 'HEAD') -join '').Trim()
}

function Get-HeadSubject {
    return ((Invoke-Git 'log' '-1' '--format=%s') -join '').Trim()
}

function Test-IndexClean {
    & git diff --cached --quiet --
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq 1) { return $false }
    Stop-Task 'git_command_failed' 'git diff --cached --quiet'
}

function Get-DirtyPaths {
    $tracked = @(Invoke-Git 'diff' '--name-only' '--')
    $untracked = @(Invoke-Git 'ls-files' '--others' '--exclude-standard')
    return @($tracked + $untracked | ForEach-Object { Normalize-RepoPath $_ } | Where-Object { $_ } | Sort-Object -Unique)
}

function Test-TreeClean {
    return (Test-IndexClean) -and ((Get-DirtyPaths).Count -eq 0)
}

function Read-TaskLock {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { Stop-Task 'lock_missing' $Path }
    try {
        return (Get-Content -LiteralPath $Path -Raw -Encoding utf8 | ConvertFrom-Json)
    }
    catch {
        Stop-Task 'lock_corrupt' $_.Exception.Message
    }
}

function New-AtomicTaskLock {
    param([string]$Path, [hashtable]$Record)
    $json = $Record | ConvertTo-Json -Depth 5 -Compress
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($json)
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $stream.Write($bytes, 0, $bytes.Length) }
        finally { $stream.Dispose() }
    }
    catch [System.IO.IOException] {
        Stop-Task 'lock_exists' $Path
    }
}

$modeCount = @($Begin.IsPresent, $Finish.IsPresent, $Abort.IsPresent, $DryRun.IsPresent | Where-Object { $_ }).Count
if ($modeCount -gt 1) { Stop-Task 'mode_conflict' 'choose exactly one of Begin/Finish/Abort/DryRun' }
$Mode = if ($Begin) { 'Begin' } elseif ($Abort) { 'Abort' } elseif ($DryRun) { 'DryRun' } else { 'Finish' }

$RepoRootText = @(& git rev-parse --show-toplevel 2>&1)
if ($LASTEXITCODE -ne 0) { Stop-Task 'not_a_git_repository' ($RepoRootText -join ' ') }
$RepoRoot = [System.IO.Path]::GetFullPath(($RepoRootText -join '').Trim())
Set-Location -LiteralPath $RepoRoot

$EpisodeNumber = $Task - 12
$EpisodeId = "S1-E{0:D2}" -f $EpisodeNumber
$ArcNumber = [int][Math]::Ceiling($EpisodeNumber / 6.0)
$ArcStart = (($ArcNumber - 1) * 108) + 1
$ArcEnd = $ArcNumber * 108
$ArcFile = "episodes/arc-{0:D2}-m{1:D3}-m{2:D3}.md" -f $ArcNumber, $ArcStart, $ArcEnd
$PreviousSubject = if ($Task -eq 13) {
    'qa: lock Linan season one outline'
} else {
    "episodes: complete S1-E{0:D2} microchapter cards" -f ($EpisodeNumber - 1)
}
$CommitSubject = "episodes: complete $EpisodeId microchapter cards"
$AllowList = @(
    $ArcFile,
    'qa/pov-allocation.json',
    'qa/function-allocation.json',
    'qa/episode-coverage-matrix.json',
    'qa/episode-coverage-matrix.md',
    'qa/character-state-matrix.md',
    'qa/relationship-seven-dimension-matrix.md',
    'qa/background-usage.json',
    'qa/clue-ledger.json',
    'qa/continuity-ledger.md',
    'qa/production-status-ledger.md',
    'qa/state/microchapter-state-events.jsonl',
    'qa/state/relationship-events.jsonl',
    'qa/state/clue-events.jsonl'
) | ForEach-Object { Normalize-RepoPath $_ }

$GitCommonText = ((Invoke-Git 'rev-parse' '--git-common-dir') -join '').Trim()
$GitCommon = if ([System.IO.Path]::IsPathRooted($GitCommonText)) {
    [System.IO.Path]::GetFullPath($GitCommonText)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $GitCommonText))
}
$LockPath = Join-Path $GitCommon 'linan-episode-integration.lock'
$Head = Get-HeadSha
$HeadSubject = Get-HeadSubject
$PredecessorOk = $HeadSubject -eq $PreviousSubject

if ($Mode -eq 'DryRun') {
    [ordered]@{
        task = $Task
        episode_id = $EpisodeId
        arc_file = $ArcFile
        previous_subject = $PreviousSubject
        predecessor_ok = $PredecessorOk
        head = $Head
        tree_clean = (Test-TreeClean)
        lock_path = $LockPath
        lock_exists = (Test-Path -LiteralPath $LockPath)
        allowlist = $AllowList
    } | ConvertTo-Json -Depth 5
    exit 0
}

if ($Mode -eq 'Begin') {
    if (Test-Path -LiteralPath $LockPath) { Stop-Task 'lock_exists' $LockPath }
    if (-not (Test-TreeClean)) { Stop-Task 'working_tree_not_clean' 'Begin requires clean index, tracked files, and untracked files' }
    if (-not $PredecessorOk) { Stop-Task 'predecessor_missing' "expected_head_subject=$PreviousSubject actual=$HeadSubject" }
    $record = [ordered]@{
        schema_version = 1
        task = $Task
        episode_id = $EpisodeId
        baseline_head = $Head
        previous_subject = $PreviousSubject
        allowlist = $AllowList
        acquired_at_utc = [DateTime]::UtcNow.ToString('o')
    }
    New-AtomicTaskLock -Path $LockPath -Record $record
    Write-Output "PASS begin task=$Task episode=$EpisodeId lock=$LockPath"
    exit 0
}

$Lock = Read-TaskLock -Path $LockPath
if ([int]$Lock.task -ne $Task -or [string]$Lock.episode_id -ne $EpisodeId) {
    Stop-Task 'lock_task_mismatch' "lock_task=$($Lock.task) requested=$Task"
}
if ((Get-HeadSha) -ne [string]$Lock.baseline_head) {
    Stop-Task 'head_changed_while_locked' "baseline=$($Lock.baseline_head) actual=$(Get-HeadSha)"
}

if ($Mode -eq 'Abort') {
    if (-not (Test-TreeClean)) { Stop-Task 'abort_requires_clean_tree' 'restore or commit no files; do not delete lock manually' }
    Remove-Item -LiteralPath $LockPath -Force
    Write-Output "PASS abort task=$Task episode=$EpisodeId"
    exit 0
}

if (-not (Test-IndexClean)) { Stop-Task 'index_not_empty' 'Finish never accepts pre-staged changes' }
$DirtyPaths = @(Get-DirtyPaths)
if ($DirtyPaths.Count -eq 0) { Stop-Task 'no_task_changes' $EpisodeId }
$AllowedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($path in @($Lock.allowlist)) { [void]$AllowedSet.Add((Normalize-RepoPath ([string]$path))) }
foreach ($path in $DirtyPaths) {
    if (-not $AllowedSet.Contains($path)) { Stop-Task 'dirty_path_not_allowed' $path }
}

& python 'scripts/validate_story.py' '--episode' $EpisodeId '--stage' 'continuity' '--strict'
if ($LASTEXITCODE -ne 0) { Stop-Task 'episode_validation_failed' $EpisodeId }
& git diff --check -- $DirtyPaths
if ($LASTEXITCODE -ne 0) { Stop-Task 'git_diff_check_failed' $EpisodeId }
& git add -- $DirtyPaths
if ($LASTEXITCODE -ne 0) { Stop-Task 'git_add_failed' ($DirtyPaths -join ',') }
if (Test-IndexClean) { Stop-Task 'nothing_staged_after_allowlist' $EpisodeId }
& git commit -m $CommitSubject
if ($LASTEXITCODE -ne 0) { Stop-Task 'git_commit_failed' $EpisodeId }
if ((Get-HeadSubject) -ne $CommitSubject) { Stop-Task 'commit_subject_mismatch' (Get-HeadSubject) }
Remove-Item -LiteralPath $LockPath -Force
Write-Output "PASS finish task=$Task episode=$EpisodeId commit=$(Get-HeadSha)"
exit 0
```

模式与退出码固定如下：

| 调用 | 成功效果 | 成功码 | 任何拒绝/验证失败 |
|---|---|---:|---:|
| `-Task N -Begin` | 原子建锁并记录基线 | 0 | 1，且不写正文 |
| `-Task N` 或 `-Finish` | 白名单验证、提交、解锁 | 0 | 1，保留锁 |
| `-Task N -Abort` | 仅在 HEAD 未变且树干净时解锁 | 0 | 1，保留锁 |
| `-Task N -DryRun` | 只打印 JSON 映射与条件 | 0 | 参数非法由 PowerShell 返回 1 |

- [ ] **Step 4A.3: 运行 helper 集成测试并确认通过**

Run:

```powershell
pwsh -NoProfile -File tests/test_accept_episode_task.ps1
```

Expected: 退出码 `0`，stdout 精确以 `PASS helper_tests=` 开头；测试临时仓库被删除，当前仓库没有新锁文件、提交或暂存改动。

- [ ] **Step 5: 接入总验证器并提交**

```powershell
python -m unittest tests.test_story_validator -v
pwsh -File scripts/accept_episode_task.ps1 -Task 13 -DryRun
git diff --check
git add qa/story-production-schema.md qa/production-status-ledger.md qa/state scripts/scaffold_story.py scripts/validate_story.py scripts/accept_episode_task.ps1 scripts/validate_project.py tests/test_story_validator.py
git commit -m "build: add narrative allocation validator"
```

Expected: 19 类测试全部通过。

## Task 2: 生成 36 集和 648 章空骨架

**Files:**
- Create: `story/00-series-outline.md`
- Create: `episodes/arc-01-m001-m108.md`
- Create: `episodes/arc-02-m109-m216.md`
- Create: `episodes/arc-03-m217-m324.md`
- Create: `episodes/arc-04-m325-m432.md`
- Create: `episodes/arc-05-m433-m540.md`
- Create: `episodes/arc-06-m541-m648.md`

- [ ] **Step 1: 由骨架器生成唯一正式 ID 和全局 ID**

```powershell
python scripts/scaffold_story.py --write
python scripts/scaffold_story.py --check
```

Expected:

```text
PASS episodes=36
PASS microchapters=648
PASS formal_ids=648 unique
PASS global_ids=M001..M648 contiguous
```

- [ ] **Step 2: 每集建立三个六章工作区和一个母集状态块**
- [ ] **Step 3: 每篇建立入口状态、出口状态、篇章问题和 108 章配额块**
- [ ] **Step 4: 提交骨架**

```powershell
git add story episodes
git commit -m "story: scaffold 36 episodes and 648 microchapters"
```

## Task 3: 锁定档位、个人及篇章 POV 预算

**Files:**
- Create: `qa/pov-allocation.json`
- Create: `qa/pov-budget-matrix.md`
- Create: `qa/function-allocation.json`
- Modify: `episodes/arc-01-m001-m108.md`
- Modify: `episodes/arc-02-m109-m216.md`
- Modify: `episodes/arc-03-m217-m324.md`
- Modify: `episodes/arc-04-m325-m432.md`
- Modify: `episodes/arc-05-m433-m540.md`
- Modify: `episodes/arc-06-m541-m648.md`

- [ ] **Step 1: 写入六篇档位预算**

| 篇章 | L1 | L2 | L3 | A1 | A2 | A3 | B | U | 合计 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | 42 | 21 | 9 | 11 | 8 | 3 | 10 | 4 | 108 |
| 02 | 38 | 18 | 12 | 13 | 8 | 3 | 12 | 4 | 108 |
| 03 | 41 | 18 | 12 | 12 | 8 | 2 | 12 | 3 | 108 |
| 04 | 34 | 18 | 10 | 14 | 8 | 3 | 16 | 5 | 108 |
| 05 | 39 | 17 | 14 | 15 | 8 | 2 | 10 | 3 | 108 |
| 06 | 36 | 16 | 15 | 15 | 8 | 3 | 12 | 3 | 108 |
| 合计 | 230 | 108 | 72 | 80 | 48 | 16 | 72 | 22 | 648 |

- [ ] **Step 2: 锁定 12 名中央人物六篇 POV**

| 人物 | 篇1 | 篇2 | 篇3 | 篇4 | 篇5 | 篇6 | 合计 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 沈蘅 | 10 | 8 | 9 | 8 | 9 | 8 | 52 |
| 柳十四 | 8 | 9 | 7 | 8 | 6 | 6 | 44 |
| 周砚之 | 7 | 8 | 8 | 8 | 6 | 5 | 42 |
| 裴九娘 | 9 | 6 | 9 | 5 | 9 | 8 | 46 |
| 顾行舟 | 8 | 7 | 8 | 5 | 9 | 9 | 46 |
| 陆清和 | 6 | 5 | 4 | 6 | 4 | 5 | 30 |
| 林阿沅 | 6 | 5 | 4 | 5 | 4 | 4 | 28 |
| 余青禾 | 5 | 4 | 5 | 4 | 5 | 3 | 26 |
| 高问 | 4 | 4 | 5 | 3 | 4 | 4 | 24 |
| 宋惟敬 | 3 | 5 | 5 | 4 | 5 | 6 | 28 |
| 黎见山 | 3 | 4 | 4 | 3 | 5 | 5 | 24 |
| 贺兰度 | 3 | 3 | 3 | 3 | 4 | 4 | 20 |

- [ ] **Step 3: 锁定 A1 六篇 POV**

| 人物 | 篇1 | 篇2 | 篇3 | 篇4 | 篇5 | 篇6 |
|---|---:|---:|---:|---:|---:|---:|
| 沈三娘 | 3 | 1 | 1 | 2 | 1 | 2 |
| 周伯安 | 3 | 2 | 1 | 1 | 1 | 2 |
| 余仲仁 | 1 | 1 | 2 | 2 | 2 | 2 |
| 顾念娘 | 1 | 3 | 1 | 2 | 1 | 2 |
| 许含章 | 1 | 2 | 1 | 2 | 2 | 2 |
| 章允中 | 0 | 2 | 2 | 1 | 3 | 2 |
| 黎令仪 | 1 | 1 | 2 | 2 | 2 | 2 |
| 曹肃 | 1 | 1 | 2 | 2 | 3 | 1 |

每人合计 10。

- [ ] **Step 4: 锁定 A2 与 A3 六篇 POV**

| A2 人物 | 篇1 | 篇2 | 篇3 | 篇4 | 篇5 | 篇6 |
|---|---:|---:|---:|---:|---:|---:|
| 陈桂婆 | 2 | 0 | 1 | 1 | 1 | 1 |
| 宋十九 | 2 | 1 | 1 | 1 | 0 | 1 |
| 沈怀川 | 0 | 1 | 1 | 2 | 1 | 1 |
| 贺九 | 1 | 1 | 2 | 0 | 1 | 1 |
| 石六 | 1 | 1 | 2 | 0 | 1 | 1 |
| 罗见潮 | 1 | 1 | 1 | 1 | 1 | 1 |
| 程野老 | 0 | 2 | 0 | 2 | 1 | 1 |
| 方书娘 | 1 | 1 | 0 | 1 | 2 | 1 |

每名 A2 合计 6。沈怀川所有 POV 均标注证据来源与“确定事实／人物理解”边界。

| A3 人物 | 篇1 | 篇2 | 篇3 | 篇4 | 篇5 | 篇6 |
|---|---:|---:|---:|---:|---:|---:|
| 祝小满 | 1 | 0 | 0 | 1 | 0 | 0 |
| 李观澜 | 0 | 1 | 0 | 0 | 0 | 1 |
| 江酌月 | 0 | 1 | 0 | 0 | 1 | 0 |
| 唐绮 | 1 | 0 | 0 | 1 | 0 | 0 |
| 段星河 | 0 | 1 | 0 | 1 | 0 | 0 |
| 丁小七 | 1 | 0 | 1 | 0 | 0 | 0 |
| 赵十一娘 | 0 | 0 | 0 | 0 | 1 | 1 |
| 慧明 | 0 | 0 | 1 | 0 | 0 | 1 |

- [ ] **Step 5: 锁定 B 首次／二次 POV 与 U 独占 POV**

```text
B 首次 POV：篇1 CHR-B-001—CHR-B-009；篇2 CHR-B-010—CHR-B-019；篇3 CHR-B-020—CHR-B-029；
篇4 CHR-B-030—CHR-B-039；篇5 CHR-B-040—CHR-B-048；篇6无首次。

B 二次 POV：
篇1 CHR-B-001
篇2 CHR-B-002、CHR-B-008
篇3 CHR-B-014、CHR-B-019
篇4 CHR-B-003、CHR-B-009、CHR-B-020、CHR-B-026、CHR-B-031、CHR-B-037
篇5 CHR-B-025
篇6 CHR-B-004、CHR-B-010、CHR-B-015、CHR-B-021、CHR-B-027、CHR-B-032、CHR-B-038、CHR-B-040、CHR-B-043、CHR-B-044、CHR-B-045、CHR-B-046

U 独占 POV 预算槽（此时不绑定人物）：
篇1 U-POV-SLOT-01—04；篇2 U-POV-SLOT-05—08；篇3 U-POV-SLOT-09—11；
篇4 U-POV-SLOT-12—16；篇5 U-POV-SLOT-17—19；篇6 U-POV-SLOT-20—22。
```

- [ ] **Step 6: 在 `qa/pov-allocation.json` 为 626 个非 U 章位写入具体 `pov_character_id`，为 22 个 U 章位写入稳定预算槽；再依照 Tasks 13—48 的母集功能表，在 `qa/function-allocation.json` 为 648 章写入唯一首要功能**

- [ ] **Step 6A: 从两个 JSON 生成只读 `qa/pov-budget-matrix.md`，通过前置 Allocation Gate**

```powershell
python scripts/validate_story.py --stage allocation --allow-reserved-unit-slots --strict
```

Expected:

```text
PASS tier_totals=230/108/72/80/48/16/72/22
PASS central_individual_totals=12/12
PASS A1=8x10 A2=8x6 A3=8x2
PASS B=48x1+24x1-extra U_reserved_slots=22
PASS arc_totals=6x108 episode_totals=36x18
PASS episode_tier_vectors=36/36 episode_function_vectors=36/36
PASS functions=312/204/132
```

- [ ] **Step 7: 提交分配**

```powershell
git add qa/pov-allocation.json qa/pov-budget-matrix.md qa/function-allocation.json episodes
git commit -m "story: lock 626 viewpoints and reserve 22 unit slots"
```

## Task 4: 锁定 72 个中央责任格、36 个情感锚点和覆盖席位

**Files:**
- Modify: `story/00-series-outline.md`
- Create: `qa/emotional-anchor-bindings.json`
- Create: `qa/emotional-spine-matrix.md`
- Modify: `qa/episode-coverage-matrix.json`
- Modify: `qa/episode-coverage-matrix.md`
- Modify: `qa/background-usage.json`
- Modify: `qa/character-state-matrix.md`

- [ ] **Step 1: 建立 `RESP-{CHARACTER_ID}-A01` 至 `A06` 共 72 格**

每格必须填写：规格责任原文、承载母集、承载微章、主动选择、不可替代资源/权限/关系、状态变化、代价、下一篇后果。

- [ ] **Step 2: 为六条情感脊柱建立以下 36 个母集锚点**

| 篇章 | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|
| 01 | 亲情 | 师徒 | 友情 | 同袍制度 | 理想共同体 | 爱情 |
| 02 | 友情 | 爱情 | 师徒 | 同袍制度 | 理想共同体 | 亲情 |
| 03 | 师徒 | 同袍制度 | 理想共同体 | 友情 | 爱情 | 亲情 |
| 04 | 亲情 | 友情 | 师徒 | 同袍制度 | 理想共同体 | 爱情 |
| 05 | 师徒 | 理想共同体 | 同袍制度 | 友情 | 爱情 | 亲情 |
| 06 | 理想共同体 | 同袍制度 | 师徒 | 友情 | 爱情 | 亲情 |

人物计划 `characters/emotional-spines/` 中的 `EM-A##-{SPINE}` 是情感语义权威，保存关系 ID、双重情感、七维前后目标、选择、代价和余波；本任务不得重写其语义。`qa/emotional-anchor-bindings.json` 只绑定母集与微章，`qa/emotional-spine-matrix.md` 必须由人物语义文件与绑定 JSON 合并生成，不能成为第三套可独立编辑的事实。

- [ ] **Step 3: 预留母集覆盖**

- L1 每人至少 24 集；L2 每人至少 16 集；L3 每人至少 12 集；
- A1 每人至少 12 集且跨四篇；A2 每人至少 8 集且跨两篇；A3 每人至少 4 集，两个 POV 不在同一母集；
- B 每人至少两集：E01—E18 一次独立日常状态，E31—E36 一次职业危机回响；至少一次不是递线索或替中央人物办事；
- U 120 人每人预留至少一个实际 `P/A/R/D` 事件锚点；其中至少 40 人预留在首次事件之后另一母集的自然回场，且回场仍须为 `P/A/R/D`，不能只是名字被提到；
- 覆盖格只允许 `P` 主视角、`A` 重要行动者、`R` 关键关系对象、`D` 决策承受者；提名、路过、转述不计。`qa/episode-coverage-matrix.json` 是机器可读权威，Markdown 只由它生成。

- [ ] **Step 4: 验证并提交**

```powershell
python scripts/validate_story.py --stage responsibility --strict
python scripts/validate_story.py --stage emotions --strict
python scripts/validate_story.py --stage coverage --strict
git add story/00-series-outline.md qa/emotional-anchor-bindings.json qa/emotional-spine-matrix.md qa/episode-coverage-matrix.json qa/episode-coverage-matrix.md qa/background-usage.json qa/character-state-matrix.md
git commit -m "story: lock responsibilities emotions and coverage"
```

Expected: `responsibility_cells=72`、`emotional_anchors=36`、所有最低覆盖席位已分配，且 `unit_event_slots=120/120 unit_return_slots>=40`。

## Task 5: 锁定 36 集全季因果矩阵

**Files:**
- Modify: `story/00-series-outline.md`
- Create: `story/07-clue-and-payoff-ledger.md`
- Modify: `qa/pov-allocation.json`
- Modify: `qa/episode-coverage-matrix.json`
- Modify: `qa/episode-coverage-matrix.md`
- Create: `qa/unit-selection.json`
- Create: `qa/continuity-ledger.md`
- Create: `qa/clue-ledger.json`

- [ ] **Step 1: 每集写城市事件、首要问题、18 个 POV 结构、核心选择、不可逆变化和片尾相邻问题**
- [ ] **Step 2: 每集挂接十步当代危机责任链、中央责任格、情感锚点和本篇牺牲**
- [ ] **Step 3: 每集写入场/离场硬状态：时间、地点、伤病、知识、物件、职业、钱财、债务、公开身份**
- [ ] **Step 4: 在 `story/07-clue-and-payoff-ledger.md` 为每条关键线索规划播种、误读/发酵、验证、回收；未在第一季回收者标明后续部移交；`qa/clue-ledger.json` 只能由该文件生成，不得另写第二套线索事实**
- [ ] **Step 5: 确保 E31—E36 使用的角色、路、船、灯号、医棚、印刷、粮食和权限均在 E01—E30 建立**
- [ ] **Step 6: 在 36 集因果明确后，依据实际单元事件为 120 个 U ID 分配唯一姓名、职业、住处、生活圈与一条不经过中央人物的关系，并写入 `qa/unit-selection.json`；再按“选择是否主动、风险是否真实、后果是否不可逆、是否带来独特伦理视角”评分，选出恰好 22 人，四类用途每类至少三人，不得按身份显赫程度选**
- [ ] **Step 7: 将 22 个实际 CHR-U ID 一一映射到 `U-POV-SLOT-01—22`，只写回 `qa/pov-allocation.json` 和 `qa/unit-selection.json`，不得修改 Character Foundation 已锁的 U 席位文件；随后运行不允许空槽的严格分配验证**
- [ ] **Step 8: 把 120 名 U 的实际首个母集、微章、`P/A/R/D`、主动选择、代价与余波逐人写入覆盖 JSON；22 名为 `P`，其余 98 名至少为 `A/R/D`；至少 40 名另写一个时间更晚、母集不同的 `P/A/R/D` 回场，身份、职业与关系状态连续**
- [ ] **Step 9: 运行因果与连续性预检并提交**

```powershell
python scripts/validate_story.py --stage continuity --strict
python scripts/validate_story.py --stage allocation --strict
python scripts/validate_story.py --stage coverage --strict
git add story/00-series-outline.md story/07-clue-and-payoff-ledger.md qa/pov-allocation.json qa/episode-coverage-matrix.json qa/episode-coverage-matrix.md qa/unit-selection.json qa/continuity-ledger.md qa/clue-ledger.json
git commit -m "story: lock season one causal matrix"
```

## Tasks 6–11: 完成六篇详细季纲

每一行是独立任务；每篇必须写满六集，完成数字/Canon、人物/情感、相邻篇章交接三次审读。

| Task | 文件 | 集数 | 时间 | 必须完成的篇章问题与牺牲 | Commit |
|---:|---|---|---|---|---|
| 6 | `story/01-arc-he-ming-lane.md` | E01–E06 | 惊蛰—清明 | 当代“无春”疑报、香箱藏粮、五线汇合、地下信房；沈蘅毁掉最大货契 | `story: outline arc one Heming Lane` |
| 7 | `story/02-arc-west-lake-rain.md` | E07–E12 | 谷雨—芒种 | 失窃春游图、水网、上层宴席、宋惟敬提出集中统筹；柳十四换曲失去台柱契约 | `story: outline arc two West Lake Rain` |
| 8 | `story/03-arc-qiantang-undercurrent.md` | E13–E18 | 梅雨—大暑 | 粮水药合流、旧信被截、三仓与假船、钱塘夜战；裴九娘救人失账匣与青鹞 | `story: outline arc three Qiantang Undercurrent` |
| 9 | `story/04-arc-osmanthus-human-world.md` | E19–E24 | 立秋—霜降 | 相亲、买簪、今日无事、桂花夜、北客与完整旧稿；陆清和公开丈夫错误 | `story: outline arc four Osmanthus Human World` |
| 10 | `story/05-arc-linan-lockdown.md` | E25–E30 | 立冬—大寒 | 北战、流民、疫病、非常令、五人决裂、截粮与烧账；顾以疫图换医棚 | `story: outline arc five Linan Lockdown` |
| 11 | `story/06-arc-ten-thousand-lanterns.md` | E31–E36 | 立春—春分 | 洪水、仓火、疫病、横向互助、含 E33“错灯”在内的四次纠错、制度转向与余生；所有牺牲兑现 | `story: outline arc six Ten Thousand Lanterns` |

每篇固定步骤：

- [ ] **Step 1: 写六集各自闭环，不把一篇只切成六段**
- [ ] **Step 2: 为六集分别锁 18 章的 POV 和功能预算**
- [ ] **Step 3: 写 12 名中央人物本篇责任及 A/B/U 自主选择**
- [ ] **Step 4: 写六条情感轴的本篇变化和持续误解**
- [ ] **Step 5: 写至少一个会跨集持续的真实牺牲后果**
- [ ] **Step 6: 运行篇章验证、相邻篇章反向检查并单独提交**

精确验证命令依次为：Task 6 `python scripts/validate_story.py --stage outline --arc 01 --strict`；Task 7 使用 `--arc 02`；Task 8 使用 `--arc 03`；Task 9 使用 `--arc 04`；Task 10 使用 `--arc 05`；Task 11 使用 `--arc 06`。

Expected: 每篇 `outline_episodes=6`、`allocated_card_slots=108`、档位与功能配额精确、`responsibility_cells=12`、`emotional_spines=6`、入口/出口一致；此阶段不要求 108 张正文卡处于 DRAFTED。

## Task 12: 锁定 Season Gate

**Files:**
- Modify: `qa/production-status.json`
- Create: `qa/gates/scope-definitions/season.json`
- Create: `qa/gates/input-manifests/season.json`
- Create: `qa/gates/season-gate.json`
- Create: `qa/reviews/season-canon-review.md`
- Create: `qa/reviews/season-character-review.md`
- Create: `qa/reviews/season-causality-review.md`

- [ ] **Step 1: 验证 36 个母集均有独立闭环和不可逆变化**
- [ ] **Step 2: 验证 72 责任格、36 情感锚点、六篇牺牲、十步危机链、终局四次纠错（其中至少一次为 E33“错灯”级联错配后由普通人发现并更正），以及 120 名 U 的唯一姓名与实际事件身份**
- [ ] **Step 2A: 在 `qa/gates/scope-definitions/season.json` 冻结六篇季纲、36 集因果、POV/功能向量、责任与情感绑定及 120 名 U 的故事身份；648 个正文卡槽只冻结 ID/预算投影，正文状态仍为 `RESERVED`**
- [ ] **Step 3: 运行 `python scripts/lock_gate.py --gate season --scope season --prepare`，生成本轮输入清单哈希**
- [ ] **Step 4: Canon、人物、因果三名不同审读者分别在 TOML 头签署同一哈希；修正任何问题后重新准备并重新签署**
- [ ] **Step 5: 只通过 Gate 工具锁定并提交**

```powershell
python scripts/validate_project.py --scope season --strict
python scripts/lock_gate.py --gate season --scope season --lock --review qa/reviews/season-canon-review.md --review qa/reviews/season-character-review.md --review qa/reviews/season-causality-review.md
python scripts/validate_project.py --scope season --strict
git add story qa
git commit -m "qa: lock Linan season one outline"
```

Expected: `PASS scope=season episodes=36 responsibilities=72 emotional_anchors=36 unit_named_for_story=120/120`。

## Tasks 13–48: 逐母集完成 648 张微短章卡

下表每行是一个独立任务，不得合并提交。视角顺序为 `L1/L2/L3/A1/A2/A3/B/U`；功能顺序为 `主线/关系/日常`。

| Task | 母集／全局章 | 视角预算 | 功能预算 | 主要情感锚点 | 精确验收命令 |
|---:|---|---|---|---|---|
| 13 | E01 / M001–018 | 8/4/1/1/1/0/2/1 | 9/5/4 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 13` |
| 14 | E02 / M019–036 | 7/4/1/2/1/1/1/1 | 8/6/4 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 14` |
| 15 | E03 / M037–054 | 7/3/2/2/2/0/2/0 | 8/6/4 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 15` |
| 16 | E04 / M055–072 | 7/3/2/2/1/1/2/0 | 8/6/4 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 16` |
| 17 | E05 / M073–090 | 7/3/1/2/1/0/3/1 | 8/6/4 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 17` |
| 18 | E06 / M091–108 | 6/4/2/2/2/1/0/1 | 7/7/4 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 18` |
| 19 | E07 / M109–126 | 7/3/2/2/1/0/2/1 | 8/6/4 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 19` |
| 20 | E08 / M127–144 | 7/3/2/2/1/1/2/0 | 8/6/4 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 20` |
| 21 | E09 / M145–162 | 6/3/2/2/2/0/2/1 | 8/6/4 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 21` |
| 22 | E10 / M163–180 | 6/3/2/2/1/1/2/1 | 8/6/4 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 22` |
| 23 | E11 / M181–198 | 6/3/2/3/1/0/3/0 | 8/6/4 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 23` |
| 24 | E12 / M199–216 | 6/3/2/2/2/1/1/1 | 8/6/4 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 24` |
| 25 | E13 / M217–234 | 7/3/2/2/1/0/2/1 | 9/6/3 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 25` |
| 26 | E14 / M235–252 | 7/3/2/2/1/1/2/0 | 10/5/3 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 26` |
| 27 | E15 / M253–270 | 7/3/2/2/2/0/2/0 | 10/5/3 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 27` |
| 28 | E16 / M271–288 | 7/3/2/2/1/0/2/1 | 10/5/3 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 28` |
| 29 | E17 / M289–306 | 7/3/2/2/1/1/2/0 | 11/4/3 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 29` |
| 30 | E18 / M307–324 | 6/3/2/2/2/0/2/1 | 10/5/3 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 30` |
| 31 | E19 / M325–342 | 6/3/1/2/1/1/3/1 | 5/7/6 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 31` |
| 32 | E20 / M343–360 | 6/3/2/2/1/0/3/1 | 5/7/6 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 32` |
| 33 | E21 / M361–378 | 6/3/1/2/2/1/2/1 | 5/7/6 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 33` |
| 34 | E22 / M379–396 | 5/3/2/3/1/0/3/1 | 5/7/6 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 34` |
| 35 | E23 / M397–414 | 6/3/2/2/1/1/3/0 | 5/7/6 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 35` |
| 36 | E24 / M415–432 | 5/3/2/3/2/0/2/1 | 5/7/6 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 36` |
| 37 | E25 / M433–450 | 7/3/2/2/1/0/2/1 | 9/7/2 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 37` |
| 38 | E26 / M451–468 | 7/3/2/3/1/1/1/0 | 10/6/2 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 38` |
| 39 | E27 / M469–486 | 7/3/2/2/2/0/2/0 | 10/6/2 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 39` |
| 40 | E28 / M487–504 | 6/3/3/3/1/0/1/1 | 10/6/2 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 40` |
| 41 | E29 / M505–522 | 6/3/3/3/1/1/1/0 | 11/5/2 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 41` |
| 42 | E30 / M523–540 | 6/2/2/2/2/0/3/1 | 10/6/2 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 42` |
| 43 | E31 / M541–558 | 6/3/2/2/1/0/3/1 | 10/5/3 | 理想共同体 | `pwsh -File scripts/accept_episode_task.ps1 -Task 43` |
| 44 | E32 / M559–576 | 6/3/2/3/1/1/2/0 | 11/4/3 | 同袍制度 | `pwsh -File scripts/accept_episode_task.ps1 -Task 44` |
| 45 | E33 / M577–594 | 6/3/3/2/2/0/2/0 | 11/4/3 | 师徒 | `pwsh -File scripts/accept_episode_task.ps1 -Task 45` |
| 46 | E34 / M595–612 | 6/2/3/3/1/1/2/0 | 12/3/3 | 友情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 46` |
| 47 | E35 / M613–630 | 6/2/3/3/1/0/2/1 | 12/3/3 | 爱情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 47` |
| 48 | E36 / M631–648 | 6/3/2/2/2/1/1/1 | 10/5/3 | 亲情 | `pwsh -File scripts/accept_episode_task.ps1 -Task 48` |

每个母集任务必须逐项完成：

- [ ] **Step 0: 在任何正式正文或共享账本写入前运行 `pwsh -File scripts/accept_episode_task.ps1 -Task <当前表中任务号> -Begin`；只有成功取得锁才继续**
- [ ] **Step 1: 读取本集入口状态、18 个具体 POV、功能预算、责任格和情感锚点**
- [ ] **Step 2: 写 M01—M06；第 06 章完成首个局部闭环**
- [ ] **Step 3: 执行本集第一批六章验证并修正**
- [ ] **Step 4: 写 M07—M12；第 12 章完成第二个局部闭环**
- [ ] **Step 5: 执行本集第二批六章验证并修正**
- [ ] **Step 6: 写 M13—M18；第 18 章闭合母集问题，只开启相邻问题**
- [ ] **Step 7: 执行第三批六章与母集验证**
- [ ] **Step 8: 更新 POV、覆盖、人物状态、七维关系、物件、钱财、知识、线索账本、三份 `qa/state/*.jsonl` 与 `qa/background-usage.json`；背景原型只有实际可见且符合地点、时辰、劳动状态时才计一次使用**
- [ ] **Step 9: Canon 审读并修正时间、地理、职业、制度和宋韵问题**
- [ ] **Step 10: 人物审读并修正被动角色、无代价选择、单一情绪与廉价和解**
- [ ] **Step 11: 连续性审读并反查下一集入口状态**
- [ ] **Step 12: 运行本任务行“精确验收命令”（无模式即 `-Finish`）；辅助脚本核对基线与 allowlist、完成本集验证、受限暂存、精确提交并释放锁**

每集 Expected：

```text
PASS cards=18
PASS pov_tiers 与当前母集表格中的八项预算完全相同
PASS function_tags 与当前母集表格中的三项预算完全相同
PASS labor>=9
PASS hard_cliffs=3..5 soft_endings>=9
PASS closures=M06,M12,M18
PASS duration=120..180 target=145..165 compiled_episode=2580..2760
PASS entry_exit_chain required_fields unique_primary_pov_per_card
```

## Tasks 49–54: 六篇 108 章验收

| Task | 篇章 | 验收重点 | Commit |
|---:|---|---|---|
| 49 | 01 | 当代疑报、五线汇合、沈蘅货契后果延续至篇二 | `qa: accept arc one microchapters` |
| 50 | 02 | 宋惟敬价值成立、柳十四失契不被迅速补偿 | `qa: accept arc two microchapters` |
| 51 | 03 | 水战因职业与地理成立、裴九娘初败影响篇四 | `qa: accept arc three microchapters` |
| 52 | 04 | 日常 36 章真正独立、旧稿破裂而不吞没生活 | `qa: accept arc four microchapters` |
| 53 | 05 | 主角分裂来自伦理、三方失控和权限链清楚 | `qa: accept arc five microchapters` |
| 54 | 06 | 全城节点均有前置、四次纠错而非一次总命令 | `qa: accept arc six microchapters` |

精确验证命令为：Task 49 `python scripts/validate_story.py --arc 01 --strict`；Task 50 使用 `--arc 02`；Task 51 使用 `--arc 03`；Task 52 使用 `--arc 04`；Task 53 使用 `--arc 05`；Task 54 使用 `--arc 06`。

必须通过：108 卡、档位与个人矩阵、功能配额、12 责任格、六情感锚点、覆盖进度、牺牲持续后果、入口/出口及相邻篇章反向验收。

## Task 55: 全季严格验收并锁定 Episode Gate

**Files:**
- Modify: `qa/production-status.json`
- Modify: `qa/production-status-ledger.md`
- Create: `qa/gates/scope-definitions/episode.json`
- Create: `qa/gates/input-manifests/episode.json`
- Create: `qa/gates/episode-gate.json`
- Create: `qa/reviews/episode-canon-review.md`
- Create: `qa/reviews/episode-character-review.md`
- Create: `qa/reviews/episode-continuity-review.md`

- [ ] **Step 1: 运行测试、骨架、分配、覆盖、连续性和全季验证**

```powershell
python -m unittest discover -s tests -p "test_story_validator.py" -v
python scripts/scaffold_story.py --check
python scripts/validate_story.py --stage allocation --strict
python scripts/validate_story.py --stage coverage --strict
python scripts/validate_story.py --stage continuity --strict
python scripts/validate_story.py --season S1 --strict
```

- [ ] **Step 2: 检查硬数量**

```powershell
@(rg '^## S1-E[0-9]{2}\b' story).Count
@(rg '^### S1-E[0-9]{2}-M[0-9]{2} / M[0-9]{3}\b' episodes).Count
```

Expected: 依次为 `36`、`648`。

- [ ] **Step 3: 检查占位和格式**

`qa/gates/scope-definitions/episode.json` 必须冻结六个微章正文文件、三份状态事件 JSONL、POV/功能/覆盖/线索/连续性实际值；仍会由 Character Final 补写的 U 档案显示字段和扩展 BG 字段不得混入 Episode 投影。

```powershell
rg -n 'TBD|TODO|FIXME|XXX|PLACEHOLDER|待定|以后再说|某角色|暂略|同上|\?\?\?' story episodes
git diff --check
```

Expected: `rg` 无输出；`git diff --check` 无输出。

- [ ] **Step 4: 运行 `python scripts/lock_gate.py --gate episode --scope episodes --prepare`；Canon、人物、连续性三名不同审读者签署同一输入清单哈希，修正后重跑全部验证并重新签署**
- [ ] **Step 5: 只通过 Gate 工具锁定并提交**

```powershell
python scripts/validate_project.py --scope episodes --strict
python scripts/lock_gate.py --gate episode --scope episodes --lock --review qa/reviews/episode-canon-review.md --review qa/reviews/episode-character-review.md --review qa/reviews/episode-continuity-review.md
python scripts/validate_project.py --scope episodes --strict
git add story episodes qa
git commit -m "qa: lock Linan season one narrative"
```

最终 Expected：

```text
PASS episodes=36 cards=648
PASS functions=312/204/132
PASS pov_tiers=230/108/72/80/48/16/72/22
PASS responsibility_cells=72 emotional_anchors=36
PASS labor>=324 unit_event_anchors=120/120 unit_returns>=40 background_used>=180
PASS missing_ids=0 duplicate_ids=0
PASS state_events=linked duration_violations=0 compiled_episode_violations=0
PASS unresolved_required_clues=0 placeholders=0 unlocked_items=0
```

## 并行纪律

- 可以并行起草不同篇章的只读提案，但正式 Tasks 13–48 必须按 `M001 → M648` 串行集成；任何正式正文、共享 QA 台账与三份 JSONL 都只能在 `-Begin` 成功后由当前持有原子集成锁的任务写入；
- 同一母集三个六章段不得由不同作者同时写，避免角色声音与状态断裂；
- 相邻篇章必须反向检查交接，后篇不得为方便自行挪用上游 POV、权限或物件；
- 已锁卡改变 POV 时，即使同档换人，也必须重跑个人、篇章、母集预算与责任/情感/状态审读；
- 跨档 POV 变更属于顶层规格变更，必须新增 Canon 变更记录。
