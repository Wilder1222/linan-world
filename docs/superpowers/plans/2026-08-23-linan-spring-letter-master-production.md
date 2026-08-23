# 《临安春信》全量内容生产 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从已确认的总设计出发，交付一套内部一致、可持续扩展、可直接进入分镜与 AIGC 生产的《临安春信》世界圣经、人物志、36 集母版、648 个微短章、120 张扩展故事卡和最终 DOCX 总册。

**Architecture:** 总规格是唯一 C0 顶层约束，生产按“Canon 基础 → 人物冻结 → 36 集冻结 → 648 章冻结 → 扩展与汇编”单向推进。每个阶段拥有独立源文件、机器可读清单、自动检查和人工叙事审读；下游若需改变上游，必须登记变更并让所有受影响项目退回复核。

**Tech Stack:** Markdown、JSON、Python 3 标准库、PowerShell、Git；最终文档使用工作区提供的文档运行时与 `python-docx`，渲染检查使用工作区文档工具链。

---

## 1. 权威输入与五份计划

唯一顶层规格：

- `docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md`
- 人物扩充基线提交：`58b8385`

执行计划按以下顺序使用：

1. `docs/superpowers/plans/2026-08-23-linan-canon-and-validation.md`
2. `docs/superpowers/plans/2026-08-23-linan-character-bible.md`
3. `docs/superpowers/plans/2026-08-23-linan-season-and-microepisodes.md`
4. `docs/superpowers/plans/2026-08-23-linan-extensions-and-delivery.md`

不得同时越过阶段门槛：Canon Gate 未通过时不写人物定稿；Character Foundation Gate 未通过时不锁 36 集；Season Gate 未通过时不写 648 章；Episode Gate 未通过时不补全 U 级最终档案；Character Final Gate 未通过时不汇编最终总册。

## 2. 最终交付物

| 系统 | 权威源 | 数量或边界 | 最终证明 |
|---|---|---:|---|
| 世界 Canon | `canon/` | 世界、城市、制度、历史、语言物质文化 | Canon Gate 全部通过 |
| 中央人物 | `characters/central/` | L1 5、L2 4、L3 3 | 12 份完整档案与 12×6 责任矩阵 |
| 重要人物 | `characters/important/` | A1 8、A2 8、A3 8 | 24 份完整档案及 10/6/2 POV 配额 |
| 市井常驻 | `characters/recurring/` | B 48 | 每人两条非中央关系、至少一章 POV |
| 单元人物 | `characters/unit/` | U 120 | 每人愿望、选择、余波；40 人再次出现 |
| 背景原型 | `characters/background/` 与 `characters/08-background-population-300-plus.md` | BG 300+ 组合 | 职业、阶层、时辰、场景与实际使用匹配 |
| 长剧母版 | `story/` | 6 篇、36 集 | 每集闭环与不可逆状态变化 |
| 微短章 | `episodes/` | 648 章 | ID 连续、目标/阻力/变化/结束按钮齐全 |
| 正篇功能配额 | `qa/function-allocation.json` | 312/204/132 | 自动计数等于规格 |
| 人物 POV 配额 | `qa/pov-allocation.json` | 230/108/72/80/48/16/72/22 | 自动计数总和 648 |
| 人物母集覆盖 | `qa/episode-coverage-matrix.json` | P/A/R/D 四类有效覆盖 | 达到各档位最低母集覆盖 |
| 扩展内容 | `extensions/` | 首批固定 120 张 | 时间插槽、正史级别、独立可读性合格 |
| 最终汇编 | `deliverables/linan-spring-letter-master-bible.docx` | 1 套 | 内容校验、DOCX 结构与逐页渲染通过 |

## 3. 阶段门槛

### Canon Gate

- 所有 Canon 文件有稳定 ID、权威范围与上游依赖；
- Y-13、Y0、Y+1 时间轴无冲突；
- 18 个主场景、旅行时间和汛期状态已锁；
- 春信采集、核验、纠错、隐私和灯号规则可执行；
- 城务司、临安府、殿前司权限闭合；
- 当代危机十步因果都有时间、地点、行动人和后果；
- `python scripts/validate_project.py --scope canon --strict` 返回零错误。

### Character Foundation Gate

- L1/L2/L3、A1/A2/A3、B 数量精确，U 120 个剧情席位与 BG 300 个原型已分配；
- 12 名中央人物六篇均有状态与责任；
- 24 名 A 级档位、POV、母集覆盖与结局责任匹配；
- 48 名 B 级每人拥有至少两条不经过中央人物的关系；
- 六条情感脊柱和七维关系状态可追踪；
- `python scripts/validate_project.py --scope character-foundation --strict` 返回零错误。

### Season Gate

- 36 集都有时间、地点、主视角、目标、阻力、选择、代价、不可逆变化和片尾转折；
- 12×6 主线责任、六情感轴、十步危机因果和终局四次纠错均被分配到明确集号；
- 每集 18 章的主视角与首要功能预分配完成；
- `python scripts/validate_project.py --scope season --strict` 返回零错误。

### Episode Gate

- 648 个正式 ID 与全局 ID 连续、唯一；
- 主线/人物/日常精确为 312/204/132；
- 人物 POV 精确为 230/108/72/80/48/16/72/22；
- 至少 324 章含真实职业或生活行为；
- 所有关键线索完成播种、误读或发酵、验证、回收；
- `python scripts/validate_project.py --scope episodes --strict` 返回零错误。

### Character Final Gate

- 120 名 U 级人物已结合实际单元事件完成姓名、职业、住处、关系、愿望、所守之物、选择与余波；
- 恰好 22 名 U 级拥有独占主视角，至少 40 名在首次单元后自然再现；
- A/B 的实际 POV 与母集覆盖落点和预留预算完全一致；
- 204 名命名人物无重复 ID、无孤立人物、无档位漂移；
- `python scripts/validate_project.py --scope characters --strict` 返回零错误。

### Delivery Gate

- 120 张扩展卡全部有正史等级、发生插槽、最早上线集与独立闭环；
- 全库无占位文字、断链、重复 ID 和冲突事实；
- DOCX 目录、标题、表格、分页与字体可读；
- 每页渲染图已人工检查，无截断、空白页、溢出或乱码；
- `python scripts/validate_project.py --scope all --strict` 返回零错误。

## 4. 总执行任务

### Task 1: 将获批修订稿转为正式生产基线

**Files:**
- Read: `docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md:3`
- Create: `qa/canon-change-log.md`

- [ ] **Step 1: 核对获批提交仍是当前祖先**

Run:

```powershell
git merge-base --is-ancestor 58b8385 HEAD
if ($LASTEXITCODE -ne 0) { throw '58b8385 is not an ancestor of HEAD' }
```

Expected: 无输出，退出码为 0。

- [ ] **Step 2: 核对规格已经处于正式生产状态**

第 3 行必须精确等于：

```markdown
> 状态：人物层级修订稿已获批准，进入全量内容生产
```

- [ ] **Step 3: 建立第一条 Canon 变更记录**

`qa/canon-change-log.md` 首条记录必须包含：

```markdown
# 《临安春信》Canon 变更记录

## CR-001｜人物层级扩充获批

- 日期：2026-08-23
- 上游提交：58b8385
- 旧结构：5 名核心、12 名关键、48 名常驻
- 新结构：L1 5、L2 4、L3 3、A1 8、A2 8、A3 8、B 48、U 120、BG 300+
- 影响范围：人物 ID、POV 预算、六篇责任、关系矩阵、剧情覆盖、扩展卡分配
- 状态：APPROVED
```

- [ ] **Step 4: 检查并提交生产基线**

Run:

```powershell
git diff --check
git add qa/canon-change-log.md
git commit -m "docs: approve Linan production baseline"
```

Expected: `git diff --check` 无输出；提交成功且仅包含 `qa/canon-change-log.md`。

### Task 2: 执行 Canon 与验证计划

**Files:**
- Read: `docs/superpowers/plans/2026-08-23-linan-canon-and-validation.md`
- Create/Modify: 该计划列出的 `canon/`、`qa/`、`scripts/`、`tests/` 文件

- [ ] **Step 1: 从第一项开始逐项执行 Canon 计划**
- [ ] **Step 2: 每个任务完成后运行该任务列出的测试与验证命令**
- [ ] **Step 3: 只有 `--scope canon --strict` 通过、两份审读签署同一输入清单哈希后，调用 `scripts/lock_gate.py` 生成 Canon Gate 证书；不得手改状态 JSON**
- [ ] **Step 4: 确认 Canon 子计划已提交 Gate 结果；总计划只做编排验收，不重复提交同一批文件**

Run:

```powershell
python scripts/validate_project.py --scope canon --strict
git status --short
```

Expected: 验证器输出 `PASS scope=canon errors=0`，随后工作树为空；若不为空，返回对应子计划修正或提交，不创建重复 Gate 提交。

### Task 3: 执行人物圣经计划的前置阶段

**Files:**
- Read: `docs/superpowers/plans/2026-08-23-linan-character-bible.md`
- Create/Modify: 该计划列出的 `characters/` 与人物 QA 文件

- [ ] **Step 1: 确认 Canon Gate 已锁**

Run:

```powershell
python scripts/validate_project.py --scope canon --strict
```

Expected: `PASS scope=canon errors=0`。

- [ ] **Step 2: 按“人物编号与名册 → 关系槽位骨架 → L1/L2/L3 → A1/A2/A3 → B → U 席位 → BG → 核心关系成品 → 六条情感脊柱”的顺序执行人物计划前置阶段**
- [ ] **Step 3: 运行人物数量、字段、关系度数、POV 预算和六篇状态验证**
- [ ] **Step 4: 只有前置人物验证全部通过后锁定 Character Foundation Gate**

Run:

```powershell
python scripts/validate_project.py --scope character-foundation --strict
git status --short
```

Expected: 验证器输出 `PASS scope=character-foundation errors=0 stable_characters=84 unit_slots=120`，工作树为空；Gate 提交由人物子计划完成。

### Task 4: 执行 36 集与 648 微短章计划

**Files:**
- Read: `docs/superpowers/plans/2026-08-23-linan-season-and-microepisodes.md`
- Create/Modify: 该计划列出的 `story/`、`episodes/` 与剧情 QA 文件

- [ ] **Step 1: 确认 Character Foundation Gate 已锁**

Run:

```powershell
python scripts/validate_project.py --scope character-foundation --strict
```

Expected: `PASS scope=character-foundation errors=0 stable_characters=84 unit_slots=120`。

- [ ] **Step 2: 先锁 36 集矩阵与六篇详细季纲**
- [ ] **Step 3: 通过 Season Gate 后，以每集 18 章、每 6 章一个局部闭环的批次完成 648 章**
- [ ] **Step 4: 对每集、每篇和全季分别执行结构审读、人物审读与连续性审读**
- [ ] **Step 5: 锁定 Episode Gate**

Run:

```powershell
python scripts/validate_project.py --scope season --strict
python scripts/validate_project.py --scope episodes --strict
git status --short
```

Expected: 依次输出 `PASS scope=season episodes=36` 与 `PASS scope=episodes microchapters=648 errors=0`，工作树为空；Season/Episode Gate 提交由剧情子计划完成。

### Task 5: 执行扩展、汇编与最终交付计划

**Files:**
- Read: `docs/superpowers/plans/2026-08-23-linan-extensions-and-delivery.md`
- Create/Modify: 该计划列出的 `extensions/`、`deliverables/` 与最终 QA 文件

- [ ] **Step 1: 确认 Episode Gate 已锁**
- [ ] **Step 2: 返回人物计划执行 U 级最终档案、实际 POV 与回访落点，锁定 Character Final Gate**
- [ ] **Step 3: 完成固定 120 张扩展卡并验证时间插槽与正史级别**
- [ ] **Step 4: 执行全库连续性、占位符、断链和配额审计**
- [ ] **Step 5: 汇编 DOCX，渲染每页并执行人工视觉检查**
- [ ] **Step 6: 锁定 Delivery Gate 并提交**

Run:

```powershell
python scripts/validate_project.py --scope all --strict
git status --short
```

Expected: `PASS scope=all errors=0 delivery=LOCKED` 且工作树为空；最终交付提交由扩展与交付子计划完成。

## 5. 变更纪律

- 已锁的 Canon 事实、稳定 ID、档位、数量和个人总预算不得直接覆盖；必须新增 `CR-###` 记录。各 Gate 明确声明为 `RESERVED` 的母集/微章绑定、覆盖格、U 实际 POV 与 BG 使用次数，可由其下游权威 QA 文件按 `RESERVED → ACTUAL` 落成，不视为改写上游事实。
- 稳定 ID 永不复用；删除内容保留 `RETIRED` 状态。
- 后篇作者不能自行修正前篇入口状态；应先修改上游并重新验证受影响范围。
- 自动验证只证明数量、字段和引用，不证明人物感动程度；每个 Gate 还需一名 Canon 审读者和一名人物叙事审读者签字。
- 作者不得把自己写的批次直接标记为 `LOCKED`。

## 6. 总完成判定

只有同时满足下列条件，才可宣称“整个剧本世界观、人物、剧情、发展、冲突、结局及扩展体系全部完成”：

- 四份阶段计划所有复选框均完成；
- 六个 Gate 全部为 `LOCKED`；
- 12 名中央、24 名重要、48 名常驻、120 名单元人物与 BG 原型均有权威来源；
- 36 集与 648 章均通过结构、人物和连续性审读；
- 爱情、友情、亲情、师徒、同袍制度与理想共同体六条情感轴均有逐篇证据；
- 所有关键人物至少一次为认为正确的事舍弃重要之物，并承受真实后果；
- 终局不是少数英雄代替全城，而是被前文认识的普通人用本职能力行动并互相纠错；
- 120 张扩展卡可以脱离主线持续讲临安生活；
- 最终 Markdown 源、JSON 清单、验证结果和 DOCX 汇编互相一致。
