# 《临安春信》故事内容索引

> 当前状态：36 集已进入 P2 `SEASON-DRAFT`；E01–E36 因果账本、648 个 2–3 分钟短章钩子与 S2-06 U 候选边界均通过机器审阅；Season Gate 仍保持 `OPEN`，尚未绑定最终对白、分镜、U 唯一身份或 BG 微章 ID。

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
| `story/season/mystery-reversal-matrix.json` | 18 条季级悬疑，覆盖 36 集，含播种/误读/复核/重义/代价/篇末揭示 | SAMPLE-DRAFT |
| `story/season/song-life-activity-matrix.json` | 36 个活动绑定，宋代生活、现代情绪入口、关系/线索状态转移 | SAMPLE-DRAFT |
| `story/season/humor-register-matrix.json` | 36 个角色化笑点，语域转译、反应顺序、情绪回收与禁用目标 | SAMPLE-DRAFT |
| `qa/reviews/season-mystery-review.json` | S2-B 悬疑/翻转矩阵审阅 | REVIEWED-SAMPLE-PASS |
| `qa/reviews/season-activity-review.json` | S2-B 宋代生活活动矩阵审阅 | REVIEWED-SAMPLE-PASS |
| `qa/reviews/season-humor-review.json` | S2-B 幽默/语域矩阵审阅 | REVIEWED-SAMPLE-PASS |
| `story/season/short-chapter-hook-map.schema.json` | 648 短章钩子、状态变化与时长字段规范 | LOCKED-SCHEMA |
| `story/season/short-chapter-hook-map.json` | 36×18 短章入口、目标阻力、证据/关系动作、选择代价与尾钩 | SEASON-DRAFT |
| `qa/reviews/season-s2c-review.json` | S2-C 全季账本与短章钩子审阅 | REVIEWED-SEASON-PASS |
| `qa/reviews/season-hook-review.json` | 648 短章逐章字段、18 章/集、尾钩轮换与回接审阅 | REVIEWED-SEASON-PASS |
| `story/season/u-candidate-selection.schema.json` | U 槽位候选、POV 映射、自然回访与 Gate 边界字段规范 | LOCKED-SCHEMA |
| `story/season/u-candidate-selection.json` | 22 个 POV 候选、40 个自然回访候选及 120 槽位保留状态 | SEASON-DRAFT |
| `qa/reviews/season-u-boundary-review.json` | S2-06 候选可追溯性、可替换性、U/BG 边界审阅 | REVIEWED-SEASON-PASS |
| `story/drafts/01-microchapter-648-beatmap-v7-draft.md` | 648 个唯一微章 ID 与节拍位置草图 | SCAFFOLD-DRAFT |
| `extensions/00-song-life-and-modern-emotion-entry-library-v1.md` | 24 张宋代生活活动卡、现代情绪入口与主线候选插槽 | FOUNDATION-DRAFT |

## 微短章审核结论

648 个 ID 唯一且覆盖 36×18；S2-C 已为每章补齐 POV、叙事功能、冷钩、目标/阻力、证据或关系动作、选择代价、章尾钩子、下一追问与状态变化。它仍是 Season 层可执行节拍，不等同于逐句对白、分镜或 AIGC 成片稿；这些必须在 Episode Gate 后绑定。

## U 候选边界审核结论

S2-06 从 `qa/unit-slots.json` 的 120 个 RESERVED 槽位中选出 22 个 POV 候选与 40 个自然回访候选；每个 POV 候选都有集/章上下文回溯，每个自然回访候选都有首次出现与回场原因。其余槽位继续保持 RESERVED；候选仅锁定可替换的功能位置，不写入姓名、最终关系、scene/dialogue/shot ID。BG 仍保持 Episode Gate 前不得写入 `microchapter_ids` 与 `extension_ids`。
