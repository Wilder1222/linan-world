# 《临安春信》下一阶段执行看板

> 版本：2026-08-25 / P0 Canon、P1 Character Foundation 已锁定
>
> 目的：把“下一步做什么”变成可交付、可审计、不可跨 Gate 的生产任务。本文是执行看板，不替代 P0/P1 Canon；任何下游文件都必须回指本看板规定的字段和验收条件。

## 当前基线

| Gate | 状态 | 可以做什么 | 不可以做什么 |
|---|---|---|---|
| P0 Canon | `LOCKED` | 使用世界、时间、春信机制、城市系统和 36 集配额 | 改写 Canon 事实而不重开 Gate |
| P1 Character Foundation | `LOCKED` | 使用 84 名具名人物、17 条关系、6 条情感脊柱和 B 级生活细节 | 在人物卡里写入具体母集、微短章或镜头绑定 |
| P2 Season | `OPEN` | 建立 36 集因果、悬疑翻转、活动与幽默登记 | 直接写正式对白、最终 U 身份或 BG 微章绑定 |
| P3 Episode/AIGC | `OPEN` | 仅在 Season Gate 后制作 E01–E03 试点 | 在 Season Gate 前批量生产成片资产 |

## 执行顺序

### S2-01｜36 集因果账本（第一优先级）

- 输入：`story/00-series-outline.md`、`story/01-causal-mystery-and-pacing-revision-v2.md`、P0/P1 Gate 证书。
- 输出：`story/season/season-causal-ledger.json`、`qa/reviews/season-causal-ledger-review.json`。
- 每集字段：`episode_id`、`arc_id`、`central_question`、`opening_state`、`city_evidence`、`relationship_choice`、`profession_action`、`clue_seed`、`misread`、`recheck`、`reframe`、`irreversible_cost`、`episode_choice`、`tail_hook`、`next_chase`。
- 完成条件：36/36 行完整；每行都有城市证据、关系选择、职业动作、不可逆代价；每次翻转均可沿“播种→误读→复核→重义”回溯。

### S2-02｜季级悬疑与翻转矩阵

- 输入：S2-01 账本和现有 6 篇主线。
- 输出：`story/season/mystery-reversal-matrix.json`、`qa/reviews/season-mystery-review.json`。
- 每条悬疑字段：`mystery_id`、`question`、`planted_episode`、`apparent_answer`、`recheck_episode`、`true_reframe`、`cost_of_knowing`、`information_owner`、`audience_knowledge`、`character_misread`。
- 完成条件：每篇至少 1 次中段重义和 1 次篇末不可逆揭示；事实翻转、责任翻转、关系翻转轮换；连续两集不得使用同型尾钩。

### S2-03｜宋代生活活动矩阵

- 输入：S2-01 账本、P1 生活圈与人物职业能力。
- 输出：`story/season/song-life-activity-matrix.json`、`qa/reviews/season-activity-review.json`。
- 首批活动：夜市、茶坊、瓦舍/杂剧、游湖画舫、灯会、花市/香会、相扑、棋局、书坊刻书、赛龙舟/水上竞渡、修船、家庭饮食、婚嫁议礼、寺院行脚、雨季避水。
- 每项字段：`activity_id`、`episode_window`、`location`、`participants`、`surface_goal`、`obstacle`、`relationship_delta`、`clue_delta`、`choice`、`state_transfer`、`continuity_cost`。
- 完成条件：活动至少改变一条关系或线索；不能只做时代布景；同一活动在回访时必须有状态变化。

### S2-04｜幽默与语域矩阵

- 输入：`story/03-humor-and-register-standard-v1.md`、P1 人物行为指纹。
- 输出：`story/season/humor-register-matrix.json`、`qa/reviews/season-humor-review.json`。
- 每条字段：`humor_id`、`episode_id`、`speaker`、`scene_context`、`surface_line`、`intention`、`subtext`、`listener_reaction`、`laugh_release`、`emotional_recovery`、`forbidden_target`。
- 完成条件：冷笑话、错位反问、物件笑点、一本正经的荒谬和“抢先一步”行为均有角色归属；笑点不消费死亡、创伤、洪灾、饥荒或受害者；笑后回到真实情绪。

### S2-05｜648 短章钩子图

- 输入：S2-01 至 S2-04。
- 输出：`story/season/short-chapter-hook-map.json`、`qa/reviews/season-hook-review.json`。
- 每章字段：`chapter_id`、`episode_id`、`pov_id`、`function`、`cold_hook`、`goal_obstacle`、`evidence_or_relationship_action`、`choice_cost`、`tail_hook_type`、`tail_hook`、`next_chase`、`state_delta`。
- 默认时长：2–3 分钟；结构为 0–10 秒冷钩子、10–45 秒目标阻力、45–100 秒证据/关系动作、100–150 秒选择代价、最后 10–20 秒尾钩。
- 完成条件：648/648 章齐全；每集 18 章；单章一个首要 POV、一个叙事功能、一个状态变化；连续三章不重复尾钩类型。

### S2-06｜U 候选与回访准备

- 输入：S2-01 与 S2-05。
- 输出：`story/season/u-candidate-selection.json`、`qa/reviews/season-u-boundary-review.json`。
- 完成条件：只从 120 个预留槽位中选择候选；22 个 POV 槽位、至少 40 个自然回访候选均可回溯到集/章；未选 U 继续保持 `RESERVED`；不在此阶段给 BG 写入具体微章 ID。

### S2-07｜Season Gate

- 输入：S2-01 至 S2-06 的正式产物、两份独立审读、严格校验报告。
- 通过条件：36 集无因果断裂；每集有城市证据、关系选择、职业动作、代价和尾钩；悬疑翻转可回溯；活动和幽默改变剧情/关系；U 可替换、BG 未绑定。

## Season Gate 之后：P3 试点

先只做 E01–E03。每个 2–3 分钟短章必须同时输出：

1. 正式短章稿；
2. Character State Sheet；
3. Relationship Delta；
4. Continuity Ledger；
5. Blocking/Storyboard；
6. 静帧、视频、配音 Prompt；
7. 九项 QA（人物、情绪、动作、行为、关系、服化道、镜头、AIGC、故事）。

单项低于 90 分不进入下一集；E01–E03 通过后才扩展 E04–E36。`U` 的唯一身份和 `BG` 的具体微章绑定仍由对应 Season/Episode Gate 写入。

## 本轮立即执行的三项任务

1. 建立 `story/season/season-causal-ledger.json` 的 schema 与 36 集空白记录；
2. 从 E01–E06 开始填写第一篇，先验证“香灰见字→五信初合”的线索回溯和尾钩轮换；
3. 用第一篇样本反向校验关系选择、职业动作、宋代活动和幽默是否都能产生不可逆代价，再批量扩展 E07–E36。

## 禁止跨 Gate

- 不在 P2 重写 P0/P1 已锁事实；
- 不用突然知道、突然变强或一次性和解解决翻转；
- 不把宋代活动写成旅游画册；
- 不让现代热梗破坏人物时代语域；
- 不把 `FOUNDATION-LOCKED` 误读为已完成 Season/Episode 绑定。
