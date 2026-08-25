from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "characters/03-recurring-citizens-48.md"

AGE_OVERRIDES = {"B004": 10, "B025": 15, "B034": 14, "B042": 13, "B047": 22}


def parse_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(B\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", line)
        if not match:
            continue
        short_id, name, occupation, wish_pressure, relations, echo = match.groups()
        rows[short_id] = {
            "name": name, "occupation": occupation, "wish_pressure": wish_pressure,
            "relations": relations, "echo": echo,
        }
    return rows


def age_for(short_id: str) -> int:
    if short_id in AGE_OVERRIDES:
        return AGE_OVERRIDES[short_id]
    return 22 + ((int(short_id[1:]) * 7) % 31)


def render(short_id: str, data: dict[str, str], roster_record: dict) -> str:
    stable_id = roster_record["id"]
    # The source table uses `primary / alias`; Canon stores the primary name
    # in `name` and the alias separately for stable identity matching.
    name = data["name"].split("/")[0].strip()
    aliases = roster_record.get("aliases", [])
    alias_text = "[" + ", ".join(f'"{alias}"' for alias in aliases) + "]"
    relations = [part.strip() for part in data["relations"].replace("；", "；").split("；") if part.strip()]
    relation_lines = "\n".join(
        f"- REL-B-{short_id[1:]}-{index:02d}：{item}；双方均保留自己的工作压力和未偿还债务。"
        for index, item in enumerate(relations[:2], 1)
    )
    if len(relations) < 2:
        relation_lines += "\n- REL-B-{0}-02：跨生活圈邻里关系，具体事件由 Season Gate 绑定。".format(short_id[1:])
    return f'''+++
id = "{stable_id}"
tier = "B"
name = "{name}"
aliases = {alias_text}
age_y0 = {age_for(short_id)}
occupation = "{data["occupation"]}"
residence = "由所在生活圈与工作时辰决定；Season Gate 绑定具体地点"
economic_source = "{data["occupation"]}的日常收入与临时活计"
pov_budget = {roster_record["pov_budget"]}
minimum_episode_coverage = 2
status = "FOUNDATION-DRAFT"
+++

# {stable_id}｜{name}

> B 级人物先锁定可持续的生活状态，实际母集、微短章和回访由下游 Gate 绑定。

## 基础状态

- 职业 / 身份：{data["occupation"]}。
- 小愿望与现实压力：{data["wish_pressure"]}。
- 关系底稿：{data["relations"]}。
- 常态行为：先完成眼前的劳动、交易、清洁、等待或照料，再决定是否介入别人的事；错误来自时间压力、信息缺口或生计压力，不来自愚蠢。
- 行为资产：危机中的能力必须由此前展示的工具、身体记忆或职业流程产生；不突然获得主角权限。

## 坚守七问

1. 最想保护什么：自己的生计、照料对象和不被抹掉的日常。
2. 这种坚守为什么形成：来自职业熟练度、家庭责任和长期被忽略的经验。
3. 在保护它时伤害过谁：至少一位亲近者会因为自己的先后顺序承担损失。
4. 两件都正确的事冲突时选择什么：先保具体的人，再留下可核验记录说明代价。
5. 为此具体放弃什么：{data["echo"]}带来的收入、名声或安全感之一。
6. 谁会误解或离开：同行、家人或同一生活圈的人可能认为这是多管闲事。
7. 没有回报是否仍承认选择属于自己：是；职业回响不等于人生奖励。

## 非中央关系

{relation_lines}

## 终局职业回响

{data["echo"]}。该能力必须先在早期日常状态中出现一次，并在终局承担可见的具体任务；任务可能成功、失败或只减少一部分损失。

## 四个 Foundation 状态

### Y0-OPEN
正常工作、吃饭、记账、照料和个人小愿望仍在继续；不以主线事件开场。

### 首次日常
至少一场不为中央人物递线索的生活场景，显示工具、动作、关系和一个小麻烦。

### 终局职业回响
{data["echo"]}；职业能力进入公共协作，但旧债、损失和误解不自动清零。

### ENDING
回到自己的工作现场，用一个具体动作继续生活；最终镜头不把人物封成“群众英雄”。

## 待集成人同步

- 第二次 POV、母集覆盖、回访和 AIGC 资产由 Season/Episode/Final Gate 写入。
- 年龄为职业状态与原有名册的生产推定，需在 Character Foundation 人工审读中确认。
'''


def main() -> int:
    rows = parse_rows()
    roster = __import__("json").loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
    by_short = {item["id"].replace("CHR-B-", "B"): item for item in roster["named_characters"] if item["tier"] == "B"}
    for short_id, data in sorted(rows.items()):
        record = by_short.get(short_id)
        if record is None:
            continue
        path = ROOT / record["profile_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(short_id, data, record), encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
