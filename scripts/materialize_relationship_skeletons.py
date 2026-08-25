from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLOTS = ROOT / "qa/relationship-slots.json"

DIMENSIONS = ("亲近", "信任", "亏欠", "依赖", "敬意", "怨恨", "共同秘密")
SNAPSHOTS = ("Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END", "ARC6-END", "Y+1")


def safe_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")


def render(relation: dict) -> str:
    relation_id = relation["id"]
    left = relation["left"]
    right = relation["right"]
    kind = relation["kind"]
    members = relation.get("members", [])
    member_text = "、".join(members) if members else "非群组双人关系"
    dimension_blocks = []
    for dimension in DIMENSIONS:
        dimension_blocks.append(
            f"### {dimension}\n"
            f"- 可观察证据：由 {left} 与 {right} 的站位、物件交接、称谓变化或公开/隐瞒行为呈现。\n"
            f"- 冲突问题：双方对‘谁有权决定、谁承担代价、谁可以先知道’的判断不一致。\n"
            f"- 发展要求：每个 ARC 至少出现一次具体动作或选择改变该维度；禁止只用旁白宣布关系变化。\n"
            f"- 当前状态：FOUNDATION-SKELETON，待 Episode/Character Final 绑定场次、台词与连续性证据。"
        )
    snapshots = []
    for snapshot in SNAPSHOTS:
        snapshots.append(
            f"### {snapshot}\n"
            f"- 关系位置：{kind}；成员/对象：{member_text}。\n"
            f"- 进入状态：双方带着各自的现实目标和未偿还债务进入该阶段。\n"
            f"- 触发事件：由该阶段的主线危机或宋代日常活动触发一次可见选择。\n"
            f"- 离开状态：至少一项七维状态发生可追溯变化；具体场次由下游 Gate 回填。"
        )
    return f'''---
id: {relation_id}
left: {left}
right: {right}
kind: {kind}
status: SKELETON
---

# {relation_id}｜{left} × {right}｜{kind}

## 关系命题

这段关系不是单一情感标签，而是两个有独立生计、欲望和底线的人，在互相需要又互相限制的条件下持续作出选择。关系必须改变人物行动，不承担主线的关系不进入生产稿。

## 双方动机与选择冲突

- {left}：保留自己的目标、秘密和拒绝权；不得被写成只为关系服务。
- {right}：保留自己的目标、秘密和拒绝权；不得被写成只为关系服务。
- 主要冲突：保护/控制、忠诚/诚实、恩情/责任、理想/具体的人之间至少形成一轮不可同时满足的选择。
- 关系回报：不是自动和解，而是学会在旧账仍在时重新协作或重新设定边界。

## 七维状态

{chr(10).join(dimension_blocks)}

## 八个快照

{chr(10).join(snapshots)}

## 生产绑定清单

- 最少一场生活活动：把关系放入宋代具体空间（夜市、瓦舍、游船、茶坊、相扑、灯会、修船或看诊等）。
- 最少一次幽默/尴尬：幽默必须改变距离、误解或选择，不作为无关插科。
- 最少一次边界动作：递回物件、让路、站开、拒绝触碰或公开承认欠债。
- 最少一次不可逆代价：关系变化必须带来时间、名誉、收入、资格或安全上的损失。
- 下游待回填：scene_id、dialogue_id、shot_ids、asset_ids、continuity_delta。
'''


def main() -> int:
    data = json.loads(SLOTS.read_text(encoding="utf-8"))
    target = ROOT / "characters/relations/core"
    target.mkdir(parents=True, exist_ok=True)
    for relation in data.get("relationships", []):
        path = target / f"{relation['id'].lower()}.md"
        path.write_text(render(relation), encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
