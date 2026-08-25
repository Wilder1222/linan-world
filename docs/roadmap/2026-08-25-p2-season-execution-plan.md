# 《临安春信》P2 Season 执行计划

> 版本：2026-08-25 / Character Foundation Gate 已锁定
>
> 目标：把 36 集母版变成可机器审计、可拆成 648 个 AI 短章、可承接后续逐场制作的 Season Canon。P2 不写成片台词，不提前锁死 U 身份，也不把 BG 绑定到具体微章。

具体执行顺序、产物路径与本轮立即开工项见 `docs/roadmap/2026-08-25-next-execution-board.md`。

## 0. 当前基线

- P0 Canon：`LOCKED`
- P1 Character Foundation：`LOCKED`
- P2 Season：`OPEN`
- P3 Episode/AIGC：`OPEN`
- 已有上游参考：`story/00-series-outline.md`、`story/01-causal-mystery-and-pacing-revision-v2.md`、`story/03-humor-and-register-standard-v1.md`

## 1. P2 任务分解

### P2-01｜36 集因果账本（最高优先级）

为每集建立一条机器可读记录，字段固定为：

`episode_id / arc_id / central_question / opening_state / city_evidence / relationship_choice / profession_action / clue_seed / misread / recheck / reframe / irreversible_cost / episode_choice / tail_hook / next_chase`

每集必须同时具备：

- 一个城市系统证据；
- 一个关系选择，而不是只有关系情绪；
- 一个职业动作，且动作来自已锁人物能力；
- 一次“播种 → 误读 → 复核 → 重义”；
- 一项不可逆代价；
- 一个能直接转成下一集开场追问的尾钩。

验收：36/36 集字段完整；任何翻转都能回指前置证据，不允许临时降临的信息。

### P2-02｜季级悬疑与翻转矩阵

为每条主线登记：

`mystery_id / question / planted_episode / apparent_answer / recheck_episode / true_reframe / cost_of_knowing / information_owner / audience_knowledge / character_misread`

翻转按三类控制：

1. **事实翻转**：同一物证被重新解释；
2. **责任翻转**：正确方案的代价转移到具体的人；
3. **关系翻转**：保护、恩情、秩序或理想改变为控制、债务、封锁或排除。

每一篇至少有一个中段重义和一个篇末不可逆揭示；不得连续两集使用同一种尾钩。

### P2-03｜AI 短章钩子规格（648 章）

默认每章 2–3 分钟；单章只允许一个首要 POV、一个叙事功能、一个状态变化：

| 时间 | 功能 |
|---|---|
| 0–10 秒 | 冷钩子：异常物、关系越界、制度动作、生活反常或倒计时 |
| 10–45 秒 | 角色目标与阻力，明确“谁要什么” |
| 45–100 秒 | 证据推进或关系动作，禁止纯解释 |
| 100–150 秒 | 主动选择与具体代价 |
| 最后 10–20 秒 | 尾钩：物证、误判、越界、制度反应、生活异常、倒计时六类轮换 |

验收：每集 18 章；章尾能回指下一章的 `next_chase`；连续三章不得重复同类尾钩。

### P2-04｜宋代生活活动与人物关系矩阵

将活动登记为可追踪事件，而不是风俗插图。首批活动池：

- 夜市、茶坊、瓦舍/杂剧、游湖画舫、灯会、花市与香会；
- 相扑、棋局、书坊刻书、赛龙舟/水上竞渡、修船与码头饭；
- 家庭饮食、邻里互助、婚嫁议礼、寺院行脚、雨季避水。

每项活动必须有：人物目标、现场阻力、关系变化、线索变化、选择、状态移交、连续性成本。活动至少推进一条关系或改变一条线索，不能只展示时代风貌。

### P2-05｜幽默与语域矩阵

以 `story/03-humor-and-register-standard-v1.md` 为准，建立：

`humor_id / speaker / scene_context / surface_line / intention / subtext / listener_reaction / laugh_release / emotional_recovery / forbidden_target`

允许：冷笑话、错位反问、物件笑点、一本正经的荒谬、抢先一步的“老六”式行为；热梗必须翻译成宋代语境。笑点不得消费死亡、创伤、洪灾、饥荒或制度受害者，并且笑意结束后必须回到人物真实情绪。

### P2-06｜U 候选与 Season 绑定准备

- 只从 120 个预留槽位中选出 Season 候选，不改 Foundation 已锁字段；
- 22 个 POV 槽位必须一一映射并可回溯到集/章；
- 至少 40 个自然回访候选要有首次出现与回场原因；
- 非候选 U 仍保持 `RESERVED`，不得在季纲中被写成既成身份。

### P2-07｜Season Gate

Gate 输入必须包括：36 集因果账本、季级悬疑/翻转矩阵、活动矩阵、幽默矩阵、U 候选分配与审读记录。通过条件：

- 36 集无因果断裂；
- 每集至少一项城市证据、关系选择、职业动作和不可逆代价；
- 每个尾钩都有下一集追问；
- U 仍可替换，BG 仍未提前绑定微章；
- 活动推进剧情/关系，幽默不削弱代价；
- 两份独立审读与严格校验均通过。

## 2. 推荐执行顺序

1. 先做 P2-01，锁定 36 集因果字段与篇间责任链；
2. 并行做 P2-02、P2-04、P2-05，所有悬疑、活动和笑点都必须挂到具体集/章；
3. 再做 P2-03，把每集拆成 18 个短章并轮换尾钩；
4. P2-06 只做候选与回访准备，不提前写死 U；
5. 运行 Season 机器审计与双人审读，锁定 Season Gate；
6. Season Gate 锁定后，进入 E01–E03 生产试点，再批量展开 E04–E36。

## 3. P3 试点的验收指标

E01–E03 每章均需输出：正式短章稿、人物状态卡、关系 Delta、连续性账本、镜头表、静帧/视频/配音 Prompt。单项低于 90 分不得进入下一阶段；重点验证钩子密度、人物稳定性、宋代活动的因果功能、幽默收放和 AIGC 道具连续性。

## 4. 明确不做

- 不在 P2 重新改写 P0 Canon 或 P1 人物事实；
- 不把文件数量当完成度；
- 不用“突然知道”“突然变强”“一次性和解”解决翻转；
- 不让生活活动变成旅游画册，不让笑点抹平代价；
- 不在 Season/Episode Gate 前把 U/BG 写成唯一主线事实。
