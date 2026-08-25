# 《临安春信》Season Gate → P3 试点执行计划

> 版本：2026-08-26
> 当前阶段：P2 `SEASON-DRAFT`，S2-C 与 S2-06 已通过机器审阅；Season Gate 仍为 `OPEN`。
> 目标：先以两份独立审读锁定 Season Canon，再以 E01–E03 验证逐章剧本、表演、连续性与 AIGC 生产链。

## 一、已锁定基线

| 层级 | 当前状态 | 本阶段处理方式 |
|---|---|---|
| P0 Canon | `LOCKED` | 只读使用；不回写世界、时间、机制与历史事实 |
| P1 Character Foundation | `LOCKED` | 只读使用；不改人物身份、能力与关系事实 |
| P2 Season | `OPEN` | 完成 Season Gate 双审读；保留 U/BG 的下游边界 |
| P3 Episode/AIGC | `OPEN` | Season Gate 关闭后只做 E01–E03 试点，暂不批量扩展 |

现有有效输入：

- 36 集 `season-causal-ledger.json`；
- 648 章 `short-chapter-hook-map.json`；
- 悬疑/翻转、宋代生活活动、幽默与语域矩阵；
- `u-candidate-selection.json`：22 个 POV 候选、40 个自然回访候选；
- P0/P1 Gate 证书与全部基础审计报告。

`raw/` 与 `production/assets/` 是用户本地资产，不纳入本阶段提交、Gate 统计或回归基线。

## 二、Season Gate 前置收口（SG-00）

### 目标

把 S2-B 的“样本审阅”状态升级为可供 Season Gate 使用的全季审阅记录，避免账本已经全季化而矩阵报告仍停留在样本标签。

### 任务

1. 复核悬疑/翻转矩阵是否覆盖 E01–E36，且每篇都有中段重义与篇末不可逆揭示；
2. 复核活动矩阵是否每集都有关系或线索状态转移，重复活动有明确状态变化；
3. 复核幽默矩阵是否每集都有角色归属、语域转译、听者反应和情绪回收；
4. 生成全季审阅报告，统一使用 `REVIEWED-SEASON-PASS` 或 `OPEN`，不再将全季结果标作 `REVIEWED-SAMPLE-PASS`；
5. 若发现源数据问题，只回写物化脚本/源表，不直接手改派生 JSON。

### 产物

- `qa/reviews/season-mystery-review.json`；
- `qa/reviews/season-activity-review.json`；
- `qa/reviews/season-humor-review.json`；
- 对应审计脚本与回归测试更新（如有必要）。

### 通过条件

- 三份报告均为 `REVIEWED-SEASON-PASS`；
- 无现代词、禁用笑点、活动静态展示或重复状态转移；
- 不改写 P0/P1 事实，不绑定最终对白、镜头或 BG 微章。

## 三、Season Gate 双重独立审读

两份审读必须相互独立，先分别出报告，再做合并，不用一份报告代替另一份。

### SG-01｜因果与悬疑审读

**审读对象**：36 集因果账本、18 条悬疑/翻转链、648 章钩子。
**核心问题**：观众是否能沿“播种 → 误读 → 复核 → 重义 → 代价”追溯每次翻转？

检查项：

- 每集只有一个主问题，但能推动篇章问题；
- 每次揭示都有前置证据，不允许“突然知道”；
- 每集都有城市证据、职业动作、关系选择和不可逆代价；
- 章尾钩子能产生下一章的具体追问，连续章尾类型不机械重复；
- 篇间交接不是重新开局，而是由上一篇的代价生成下一篇压力；
- 悬疑揭示改变责任、关系或行动权限，而不只是增加信息。

**产物**：`qa/reviews/season-gate-causal-mystery-review.json`。
**通过线**：阻断项为 0；36/36 集与 648/648 章结构完整；所有发现均已分类为修复、接受或延期。

### SG-02｜关系、活动、幽默与可替换性审读

**审读对象**：17 条关系、活动矩阵、幽默矩阵、U 候选边界、BG 状态。
**核心问题**：人物情感、宋代生活与笑点是否真正改变选择，而非装饰主线？

检查项：

- 关系选择改变信任、边界、亏欠、依赖或未解决问题；
- 活动至少改变一条关系或线索，且回访时状态不同；
- 幽默属于角色，笑后回到真实情绪，不消费死亡、创伤、灾害或受害者；
- U 候选可由同类槽位替换，不承担不可替代的唯一真相；
- 未选 U 仍为 `RESERVED`；BG 仍无 `microchapter_ids` 与 `extension_ids`；
- 不以一次性和解、突然变强或现代热梗替代人物选择。

**产物**：`qa/reviews/season-gate-relationship-life-humor-review.json`。
**通过线**：阻断项为 0；关系/活动/幽默/可替换性均有可追溯证据；BG 边界保持通过。

### SG-03｜差异合并与例外处理

两份独立报告完成后，建立统一的例外清单：

| 级别 | 定义 | 处理 |
|---|---|---|
| BLOCKING | 破坏因果、人物事实、Gate 边界或 AIGC 可执行性 | 必须修复，Season Gate 不得关闭 |
| MAJOR | 会造成观众误读、关系跳跃或连续性断裂 | 修复或由负责人书面接受风险 |
| MINOR | 文案、命名或字段表现问题，不改变因果 | 可列入 P3 前修复清单 |
| DEFERRED | 只有逐场或 Episode Gate 才能决定的事项 | 保持 RESERVED，不提前拍板 |

**产物**：`qa/reviews/season-gate-exception-ledger.json`。
**规则**：不得静默覆盖冲突；每条发现必须有来源、责任人、处理结论和下一个 Gate。

### SG-04｜Season Gate 决议

只有在 SG-00、SG-01、SG-02、SG-03 全部满足通过条件后，才生成：

- `qa/gates/season-gate.json`；
- `qa/gates/input-manifests/season.json`；
- `qa/gates/scope-definitions/season.json`（如现有 Gate 工具需要）。

Season Gate 关闭时锁定的是 **Season Canon 与短章节拍**，不是最终对白、分镜或成片；U 只允许进入经审读的候选/替换边界，BG 继续等待 Episode Gate。

## 四、Season Gate 之后的 P3 E01–E03 试点

### P3-01｜试点输入冻结

- 为 E01–E03 建立 episode manifest；
- 锁定每集 18 个 `S1-E##-M##` 章 ID、人物/关系/活动/幽默引用；
- 只为实际进入逐场生产的 U 槽位写入最终身份；未使用 U 仍保持 RESERVED；
- 建立道具、服装、地点、声音和资产版本号；
- 不让试点反向修改 Season Canon，冲突先回到 Exception Ledger。

### P3-02｜E01 生产试点

每个 2–3 分钟短章必须同时有：

1. 正式短章剧本与对白；
2. Character State Sheet；
3. Emotion/Action Sheet；
4. Relationship Delta；
5. Continuity Ledger；
6. Blocking/Storyboard；
7. 静帧、视频、配音 Prompt；
8. 九项 QA：人物、情绪、动作、行为、关系、服化道、镜头、AIGC、故事。

E01 先验证：

- 2–3 分钟内冷钩、目标、阻力、证据/关系动作、选择代价和尾钩完整；
- 沈蘅、陆清和、顾行舟、林阿沅的表情和行为语法不漂移；
- “香匣/香丸/三色记录/防风灯”等道具跨章一致；
- 第一集的母女冲突、爱情萌芽和市井入口同时推进，不用旁白解释主题。

### P3-03｜E02、E03 递进试点

- E02 验证“正确选择由谁付账”、生活活动与经济压力的可拍性；
- E03 验证消息传播、群体误读、幽默回收和多关系并行；
- E02/E03 不复制 E01 的尾钩类型、场景节奏或表演动作；
- 每集完成后更新人物、关系、信息和道具连续性账本。

### P3-04｜Episode Gate 试点决议

每集九项 QA 均须达到 90/100 以上；任一项低于 90，必须回到对应层修复，不得用剪辑或 Prompt 掩盖。

试点 Gate 还要检查：

- 每章可独立发布又能衔接下一章；
- 角色动作具有意图，不是静态摆拍；
- 关系变化可在无台词时被看见；
- AI 生成中的脸、服装、道具、空间和声音连续；
- 幽默释放后回到真实代价；
- 生产资产可复用到 E04–E36。

### P3-05｜扩展决策

- E01–E03 全部通过：批准 E04–E12 批量生产；
- 只有 E01 通过：修订流程后再做 E02；
- 任一结构性问题反复出现：暂停扩展，回到 P3-01 或 Season Exception Ledger；
- 不以完成文件数量代替 Gate 通过。

## 五、推荐执行顺序与本阶段 Definition of Done

执行顺序：

`SG-00 全季矩阵收口 → SG-01 因果/悬疑 → SG-02 关系/活动/幽默/替换 → SG-03 例外合并 → SG-04 Season Gate → P3-01 输入冻结 → P3-02 E01 → P3-03 E02/E03 → P3-04 Episode Gate`。

本阶段（Season Gate 规划与收口）完成定义：

- 三份 S2-B 报告完成全季化；
- 两份独立 Season Gate 审读与例外账本生成；
- 所有阻断项关闭或明确延期；
- Season Gate 决议可由输入 manifest 重建；
- P0/P1 不被静默改写，U/BG 边界仍可审计；
- 只有 Season Gate 关闭后才启动 E01–E03 逐章生产。

## 六、当前不做

- 不在 Season Gate 前写最终对白、镜头、AIGC Prompt 或 U 唯一身份；
- 不把 BG 原型绑定到具体微章；
- 不因某个局部场景好看而改写已锁定的季级因果；
- 不把宋代活动写成风俗展览，不用现代热梗替代人物幽默；
- 不把 `production/assets/` 或 `raw/` 纳入 Git 提交。
