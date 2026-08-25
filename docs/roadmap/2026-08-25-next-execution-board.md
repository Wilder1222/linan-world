# 《临安春信》下一阶段执行看板

> 版本：2026-08-25 / P0 Canon、P1 Character Foundation 已锁定
>
> 目的：把“下一步做什么”变成可交付、可审计、不可跨 Gate 的生产任务。本文是执行看板，不替代 P0/P1 Canon；任何下游文件都必须回指本看板规定的字段和验收条件。

## 当前基线

| Gate | 状态 | 可以做什么 | 不可以做什么 |
|---|---|---|---|
| P0 Canon | `LOCKED` | 使用世界、时间、春信机制、城市系统和 36 集配额 | 改写 Canon 事实而不重开 Gate |
| P1 Character Foundation | `LOCKED` | 使用 84 名具名人物、17 条关系、6 条情感脊柱和 B 级生活细节 | 在人物卡里写入具体母集、微短章或镜头绑定 |
| P2 Season | `OPEN` | 使用已完成的 36 集因果、悬疑翻转、活动、幽默与 648 短章钩子，准备 Episode Gate | 直接写正式对白、最终 U 身份或 BG 微章绑定 |
| P3 Episode/AIGC | `OPEN` | 仅在 Season Gate 后制作 E01–E03 试点 | 在 Season Gate 前批量生产成片资产 |

## 审计后确认（2026-08-25）

本轮对 P0/P1 的机器报告、Gate 证书、输入哈希和跨文件边界进行复核，结论如下：

- P0 Canon：`LOCKED`，生产质量审计 `REVIEWED-PASS`。
- P1 Character Foundation：`LOCKED`，中央/重要/常驻人物、关系证据、情感脊柱、L/A 状态链和 B 级生活细节审计均为 `REVIEWED-PASS`。
- U/BG 的 `scene/dialogue/shot` 以及具体微章绑定仍为 `RESERVED`，这是下游 Gate 依赖，不是 P1 缺陷。
- `production/assets/` 与 `raw/` 是本地用户资产，不纳入本轮 Gate、提交或完成度统计；视觉资产生产属于 P3 Episode/AIGC。
- 当前没有需要回写 P0/P1 的阻断项；下一轮重点从“人物基础锁定”转向“36 集 Season 因果可执行化”。

## S2-A 样本结果（2026-08-25）

- `story/season/season-causal-ledger.json` 已生成 36/36 集记录；E01–E06 为 `SAMPLE-DRAFT`，E07–E36 明确保持 `DRAFT-SCAFFOLD`。
- E01–E06 已逐集补齐“播种 → 误读 → 复核 → 重义 → 不可逆代价 → 选择 → 尾钩 → 下一追问”，并回指城市证据、地点、人物、关系和职业能力。
- `scripts/audit_season_causal_ledger.py` 已通过：结构完整、样本引用可追溯、相邻样本尾钩类型不重复；审阅报告为 `REVIEWED-SAMPLE-PASS`。
- Season Gate 仍保持 `OPEN`。本样本只证明因果账本格式与第一篇局部链条可执行，不代表 E07–E36、活动矩阵、幽默矩阵或 648 短章已完成。

## S2-B 样本结果（2026-08-25）

- `mystery-reversal-matrix.json`：18 条季级悬疑覆盖 36 集；每篇至少有中段重义与篇末不可逆揭示，连续集尾钩翻转类型不重复。
- `song-life-activity-matrix.json`：36 个活动绑定；每项都有史实形态锚点、创作解释边界、关系变化或线索变化、选择和连续性代价。
- `humor-register-matrix.json`：36 个角色化幽默绑定；逐条标注意图、潜台词、听者反应、笑点回收、时代转译与禁用目标，未使用现代网络词。
- 三份审阅报告均为 `REVIEWED-SAMPLE-PASS`；季因果账本已回写每集 `activity_ids` 与 `humor_ids`。
- 这些矩阵仍是 Season 层样本草案：S2-C 还需把它们绑定到 E07–E36 的完整因果账本和 648 个 2–3 分钟短章，Season Gate 继续保持 `OPEN`。

## S2-C 全季结果（2026-08-25）

- `season-causal-ledger.json` 已从六集样本升级为 36/36 集 `SEASON-DRAFT`；E07–E36 每集均补齐中心问题、开场状态、城市证据、关系选择、职业动作、播种/误读/复核/重义、不可逆代价、选择、片尾钩子和下一追问。
- 新增 `short-chapter-hook-map.json` 与 schema，648/648 章按 36×18 展开；每章约 150 秒，具备单一 POV、功能、冷钩、目标/阻力、证据或关系动作、选择代价、章尾钩子、下一追问和状态变化。
- `scripts/audit_season_causal_ledger.py` 与 `scripts/audit_season_s2c.py` 均通过，报告为 `REVIEWED-SEASON-PASS`；人物、关系、地点、事件、观察和职业能力引用可追溯，集内连续尾钩类型不重复。
- S2-C 仍不关闭 Season Gate：短章是节拍层，不是最终对白/分镜/AIGC；下一阶段应进入 U 候选与自然回访边界，然后再做 Season Gate 双重审读。

## S2-06 U 候选结果（2026-08-25）

- `story/season/u-candidate-selection.json` 已从 120 个 RESERVED 槽位中选择 22 个 POV 候选与 40 个自然回访候选；22/22 POV 均回溯到集/章上下文，40/40 回访候选均有首次出现与回场原因。
- `scripts/audit_season_u_candidates.py` 已通过，报告为 `REVIEWED-SEASON-PASS`；40 个选中槽位仍可替换，另有 22 个 POV 候选保留为替换池，80 个未选槽位继续保持 RESERVED。
- S2-06 不写入唯一姓名、最终 scene/dialogue/shot ID，也不修改 `qa/unit-slots.json`；BG 300 个原型仍保持 RESERVED，`microchapter_ids` 与 `extension_ids` 继续为空。
- Season Gate 仍保持 `OPEN`；SG-01 因果/悬疑独立审读已通过，下一步是 SG-02 关系/活动/幽默/可替换性独立审读。

## SG-01 因果与悬疑独立审读结果（2026-08-26）

- 新增 `scripts/audit_season_gate_causal_mystery.py` 与 `tests/test_season_gate_causal_mystery.py`，报告为 `REVIEWED-SEASON-PASS`。
- 36/36 集均具备唯一中心问题、城市证据、职业动作、关系选择、不可逆代价和可回接尾钩；选择行动者与 POV/关系角色可追溯。
- 18/18 条悬疑/翻转链均具备播种、误读、复核、重义、代价与篇末揭示，阶段绑定到对应集；重义会改变关系状态或行动状态。
- 648/648 章均具备可执行字段，18 章/集，尾钩类型不相邻重复；每集首章开场、尾章尾钩类型与下一追问均回接季级因果账本。
- 本审读不锁定最终对白、shot ID、U 唯一身份或 BG 微章 ID；SG-02 未通过前 Season Gate 继续保持 `OPEN`。

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
- 完成条件：648/648 章齐全；每集 18 章；单章一个首要 POV、一个叙事功能、一个状态变化；相邻章尾钩不重复，且尾章绑定本集片尾钩子。**已完成：`REVIEWED-SEASON-PASS`。**

### S2-06｜U 候选与回访准备

- 输入：S2-01 与 S2-05。
- 输出：`story/season/u-candidate-selection.json`、`qa/reviews/season-u-boundary-review.json`。
- 完成条件：只从 120 个预留槽位中选择候选；22 个 POV 槽位、至少 40 个自然回访候选均可回溯到集/章；未选 U 继续保持 `RESERVED`；不在此阶段给 BG 写入具体微章 ID。

**已完成：`REVIEWED-SEASON-PASS`。**

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

## 下一阶段计划（2026-08-26）

详细执行计划见：`docs/roadmap/2026-08-26-season-gate-and-p3-plan.md`。

执行顺序固定为：

`SG-00 全季矩阵收口 → SG-01 因果/悬疑独立审读 → SG-02 关系/活动/幽默/可替换性独立审读 → SG-03 例外合并 → SG-04 Season Gate → P3-01 输入冻结 → P3-02 E01 → P3-03 E02/E03 → P3-04 Episode Gate`。

SG-00 已完成：S2-B 三份报告已升级为 `REVIEWED-SEASON-PASS`，源矩阵为 `SEASON-DRAFT`，现在进入 SG-01 因果/悬疑独立审读；Season Gate 仍保持 `OPEN`。

## 本轮立即执行的三项任务

1. 保持 S2-C 与 S2-06 产物和 P0/P1 锁定事实同步，禁止旧脚本把全季账本回滚为脚手架；
2. 准备 Season Gate 的两份独立审读：一份查因果与悬疑，一份查关系、活动、幽默和可替换性；
3. Season Gate 通过后再进入 E01–E03 Episode/AIGC 试点，不提前绑定 U 唯一身份或 BG 微章。

## 下一次执行批次（建议按一个短冲刺完成）

### Sprint S2-A｜因果账本骨架与 E01–E06 样本

1. 建立 `story/season/season-causal-ledger.schema.json` 与 `story/season/season-causal-ledger.json`，先生成 36 条 `DRAFT` 记录；
2. 完成 E01–E06 的全部字段，逐条回指 Canon 事实、人物关系 ID、职业能力和地点 ID；
3. 为每集补齐“播种 → 误读 → 复核 → 重义 → 代价 → 尾钩 → 下一集追问”；
4. 建立 `scripts/audit_season_causal_ledger.py`，至少检查 36/36 字段完整、ID 可回溯、尾钩有下一集追问、代价非空；
5. 输出 `qa/reviews/season-causal-ledger-review.json`，先允许 `REVIEWED-SAMPLE-PASS`，不提前关闭 Season Gate。

**S2-A 通过条件**：E01–E06 六集完整、机器审计无结构性发现、人工抽读能解释每个翻转的前置证据与关系代价。

### Sprint S2-B｜悬疑、活动、幽默并行登记

在 S2-A 样本通过后，再并行登记：

- `story/season/mystery-reversal-matrix.json`：事实/责任/关系三类翻转轮换；
- `story/season/song-life-activity-matrix.json`：活动必须改变关系或线索；
- `story/season/humor-register-matrix.json`：笑点必须有语域、反应和情绪回收；
- 对应三份 `qa/reviews/*-review.json`，统一使用 `REVIEWED-SAMPLE-PASS` → `REVIEWED-PASS` 的升级路径。

**S2-B 通过条件**：没有连续同型尾钩；活动不再是静态风俗展示；幽默不消费灾难与受害者，且笑后能回到真实情绪。

### Sprint S2-C｜扩展 E07–E36 与 648 章钩子图

1. 用通过的 E01–E06 模板扩展 E07–E36 因果账本；
2. 再生成 `story/season/short-chapter-hook-map.json`，每集 18 章、每章一个 POV/功能/状态变化；
3. 运行连续三章尾钩轮换、状态转移、关系与职业动作覆盖审计；
4. 最后才做 U 候选和自然回访分配，未选 U 继续保持 `RESERVED`。

**S2-C 通过条件**：36/36 集与 648/648 章齐全，尾钩均能产生下一追问；U 可替换，BG 未提前绑定具体微章。

### Season Gate 之后的 P3 入口

Season Gate 关闭后只启动 E01–E03 试点。每个短章必须同时有正式稿、人物状态、关系 Delta、连续性账本、Blocking/Storyboard、静帧/视频/配音 Prompt 和九项 QA；任何单项低于 90 分都不扩展到下一集。

## 禁止跨 Gate

- 不在 P2 重写 P0/P1 已锁事实；
- 不用突然知道、突然变强或一次性和解解决翻转；
- 不把宋代活动写成旅游画册；
- 不让现代热梗破坏人物时代语域；
- 不把 `FOUNDATION-LOCKED` 误读为已完成 Season/Episode 绑定。
