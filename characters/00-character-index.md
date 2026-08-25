# 《临安春信》人物内容索引

> 当前状态：`FOUNDATION-LOCKED`。P0 Canon 与 P1 Character Foundation Gate 均已锁定；人物母集与基础行为边界冻结，Season/Episode 绑定仍保持 `RESERVED`。

## 已纳入

| 文件 | 覆盖范围 | 状态 |
|---|---|---|
| `characters/01-central-cast-12.md` | 12 名 L1/L2/L3 中央人物完整人物核、六篇弧线、结局 | FOUNDATION-LOCKED |
| `characters/03-recurring-citizens-48.md` | 48 名市井常驻的职业、愿望、压力、非中央关系与终局职业回响 | FOUNDATION-LOCKED |
| `characters/06-values-sacrifices-and-emotional-arcs.md` | 12 名中央人物的珍贵之物、阴影欲望、最终舍弃与未获补偿 | FOUNDATION-LOCKED |
| `characters/central/` | 12 名 L1/L2/L3 独立可执行人物档案（身份、行为、七问、十个状态节点） | FOUNDATION-LOCKED |
| `characters/important/` | 24 名 A1/A2/A3 独立可执行人物档案 | FOUNDATION-LOCKED |
| `characters/recurring/` | 48 名 B 级独立生活状态与职业回响档案 | FOUNDATION-LOCKED |
| `characters/relations/core/` | 16 个双人关系与 1 个五信协作群的七维/八快照语义骨架 | FOUNDATION-LOCKED |
| `characters/emotional-spines/` | 六条情感脊柱、36 个 `EM-A##-{SPINE}` 语义锚点 | FOUNDATION-LOCKED |
| `qa/character-roster.json` | 84 名稳定名册、POV 预算、U/BG 槽位总约束 | MACHINE-AUTHORITY |
| `qa/unit-slots.json` | 120 个 U 席位、22 个 POV 槽、候选池与自然回访池 | MACHINE-AUTHORITY |
| `qa/background-usage.json` | 300 个 BG 生态原型及地点/时段/劳动状态可用性 | MACHINE-AUTHORITY |
| `qa/relationship-slots.json` | 17 个关系槽位、七维状态与八个快照约束 | MACHINE-AUTHORITY |
| `qa/emotional-spines.json` | 六条情感脊柱的 36 个状态变化约束 | MACHINE-AUTHORITY |

## ID 映射规则

扩展包使用 `B001`—`B048` 简写；正式稳定 ID 仍为 `CHR-B-001`—`CHR-B-048`。`B008 崔满堂/崔老板` 与 `B019 孟小川/阿七` 与当前计划的固定席位一致，其余姓名作为 Character Foundation 阶段的候选定稿。

U 级目前只冻结席位和候选池，尚未进入具体故事身份；BG 目前只冻结生态原型和可用性，不得当作静态装饰。下一阶段必须在 Season Gate 锁定后，回填 U 的唯一姓名/事件身份、BG 的微章与扩展使用记录，并重新跑 Character Foundation 与 Season 交叉校验。

## 下一步执行顺序

1. 完成 P1 人物基础层的六个独立校验：central → important → recurring → unit-slots → background → relationships/emotional-spines。
2. 对 12 名中央与 24 名重要人物做人工角色审读：身份不漂移、选择有代价、关系不是单一好感度、情绪可由动作表现。
3. Character Foundation Gate 已锁定；人物基础档案保持 `FOUNDATION-LOCKED`，不得在 Season/Episode Gate 之外写入母集或微短章绑定。
4. 当前推进 36 集悬疑因果、每集微短章钩子、宋代生活活动与现代情绪入口；U/BG 只在对应集章绑定后转为 `ASSIGNED`。
