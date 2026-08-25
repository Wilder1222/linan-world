# 《临安春信》故事内容索引

> 当前状态：Season Gate 已于 2026-08-26 锁定；36 集仍为 P2 `SEASON-DRAFT`，E01–E36 因果账本、18 条悬疑/翻转链、648 个 2–3 分钟短章钩子、关系/活动/幽默输入与 S2-06 U 候选边界均通过机器审阅。最终对白、分镜、U 唯一身份与 BG 微章 ID 仍等待 Episode Gate。

## 已纳入

| 文件 | 内容 | 状态 |
|---|---|---|
| `story/00-series-outline.md` | 六篇、36 集城市事件、人物选择、代价和片尾变化 | FOUNDATION-DRAFT |
| `story/08-ensemble-finale-echo-matrix.md` | 普通职业能力在终局的回响与旧账规则 | FOUNDATION-DRAFT |
| `story/01-causal-mystery-and-pacing-revision-v2.md` | 欧美式因果推进、韩剧式关系回报、六层悬疑梯与 36 集翻转矩阵 | FOUNDATION-DRAFT |
| `story/03-humor-and-register-standard-v1.md` | 角色幽默指纹、热梗时代转译、轻微出戏感边界与 AI 表演字段 | FOUNDATION-DRAFT |
| `story/season/season-causal-ledger.schema.json` | P2 Season Gate 因果账本字段、状态边界与引用结构 | LOCKED-SCHEMA |
| `story/season/season-causal-ledger.json` | 36 集完整结构化因果账本；每集含目标、阻力、复核、重义、代价、选择与尾钩 | SEASON-DRAFT |
| `qa/reviews/season-causal-ledger-review.json` | S2-C 全季审阅：36/36 因果字段、引用、职业能力与尾钩 | REVIEWED-SEASON-PASS |
| `story/season/mystery-reversal-matrix.json` | 18 条季级悬疑，覆盖 36 集，含播种/误读/复核/重义/代价/篇末揭示 | SEASON-DRAFT |
| `story/season/song-life-activity-matrix.json` | 36 个活动绑定，宋代生活、现代情绪入口、关系/线索状态转移 | SEASON-DRAFT |
| `story/season/humor-register-matrix.json` | 36 个角色化笑点，语域转译、反应顺序、情绪回收与禁用目标 | SEASON-DRAFT |
| `qa/reviews/season-mystery-review.json` | S2-B/SG-00 全季悬疑/翻转矩阵审阅 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-activity-review.json` | S2-B/SG-00 全季宋代生活活动矩阵审阅 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-humor-review.json` | S2-B/SG-00 全季幽默/语域矩阵审阅 | REVIEWED-SEASON-PASS |
| `story/season/short-chapter-hook-map.schema.json` | 648 短章钩子、状态变化与时长字段规范 | LOCKED-SCHEMA |
| `story/season/short-chapter-hook-map.json` | 36×18 短章入口、目标阻力、证据/关系动作、选择代价与尾钩 | SEASON-DRAFT |
| `qa/reviews/season-s2c-review.json` | S2-C 全季账本与短章钩子审阅 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-hook-review.json` | 648 短章逐章字段、18 章/集、尾钩轮换与回接审阅 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-gate-causal-mystery-review.json` | SG-01 独立审读：36 集因果、18 条悬疑/翻转链、648 章钩子与前置证据回接 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-gate-relationship-life-humor-review.json` | SG-02 独立审读：关系、宋代活动、幽默、U 可替换性与 BG 边界 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-gate-exception-ledger.json` | SG-03 差异合并、责任人、延期结论与下一个 Gate | REVIEWED-SEASON-PASS |
| `qa/gates/season-gate.json` | SG-04 Season Gate 决议与 27 个输入哈希绑定 | LOCKED |
| `qa/gates/input-manifests/season.json` | Season Gate 可重建输入 manifest | LOCKED-MANIFEST |
| `qa/gates/scope-definitions/season.json` | Season Gate 冻结输入范围与前置 Gate | LOCKED-SCOPE |
| `story/season/u-candidate-selection.schema.json` | U 槽位候选、POV 映射、自然回访与 Gate 边界字段规范 | LOCKED-SCHEMA |
| `story/season/u-candidate-selection.json` | 22 个 POV 候选、40 个自然回访候选及 120 槽位保留状态 | SEASON-DRAFT |
| `qa/reviews/season-u-boundary-review.json` | S2-06 候选可追溯性、可替换性、U/BG 边界审阅 | REVIEWED-SEASON-PASS |
| `story/drafts/01-microchapter-648-beatmap-v7-draft.md` | 648 个唯一微章 ID 与节拍位置草图 | SCAFFOLD-DRAFT |
| `extensions/00-song-life-and-modern-emotion-entry-library-v1.md` | 24 张宋代生活活动卡、现代情绪入口与主线候选插槽 | FOUNDATION-DRAFT |

## 微短章审核结论

648 个 ID 唯一且覆盖 36×18；S2-C 已为每章补齐 POV、叙事功能、冷钩、目标/阻力、证据或关系动作、选择代价、章尾钩子、下一追问与状态变化。它仍是 Season 层可执行节拍，不等同于逐句对白、分镜或 AIGC 成片稿；这些必须在 Episode Gate 后绑定。

## U 候选边界审核结论

S2-06 从 `qa/unit-slots.json` 的 120 个 RESERVED 槽位中选出 22 个 POV 候选与 40 个自然回访候选；每个 POV 候选都有集/章上下文回溯，每个自然回访候选都有首次出现与回场原因。其余槽位继续保持 RESERVED；候选仅锁定可替换的功能位置，不写入姓名、最终关系、scene/dialogue/shot ID。BG 仍保持 Episode Gate 前不得写入 `microchapter_ids` 与 `extension_ids`。

## SG-00 全季矩阵收口结论

悬疑/翻转、宋代生活活动、幽默/语域三份矩阵已完成 36 集全季覆盖审阅，报告均为 `REVIEWED-SEASON-PASS`；源矩阵状态统一为 `SEASON-DRAFT`。它们现在可以作为 Season Gate 的正式输入，但仍不绑定最终对白、镜头、U 唯一身份或 BG 微章。

## SG-01 因果与悬疑独立审读结论

`qa/reviews/season-gate-causal-mystery-review.json` 已完成重建并为 `REVIEWED-SEASON-PASS`：36/36 集中心问题、城市证据、职业动作、关系选择、不可逆代价和片尾回接完整；18/18 条悬疑链均可沿“播种 → 误读 → 复核 → 重义 → 代价”追溯；648/648 章具备可执行钩子，且每集尾章与季账本尾钩类型、下一追问一致。SG-02 仍待独立审读，Season Gate 保持 `OPEN`。

## SG-02 关系、生活活动与幽默独立审读结论

`qa/reviews/season-gate-relationship-life-humor-review.json` 已完成重建并为 `REVIEWED-SEASON-PASS`：17 条关系的 136 条阶段证据、36 个活动、36 个幽默绑定、120 个 U 槽位与 300 个 BG 原型均通过边界审读。关系、活动与笑点都具备状态变化或情绪回收；U 仍可替换，BG 未提前绑定。SG-03 仍待建立例外账本，Season Gate 保持 `OPEN`。

## SG-03 例外账本结论

`qa/reviews/season-gate-exception-ledger.json` 已完成重建并为 `REVIEWED-SEASON-PASS`：两份独立报告没有未决 BLOCKING/MAJOR/MINOR 项，5 条边界项均明确延期到 Episode Gate，且保留 U/BG 与 Season/Episode 的边界。下一步是 SG-04 Season Gate 决议，当前仍保持 `OPEN`。

## SG-04 Season Gate 决议结论

`qa/gates/season-gate.json` 已生成并锁定，input manifest 与 scope definition 可重建 27 个季级输入。锁定范围是 Season Canon 与短章节拍；5 条 `DEFERRED-UNTIL-EPISODE-GATE` 边界仍保留，Episode Gate 继续开放，下一阶段进入 P3-01。
