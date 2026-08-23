# 《临安春信》扩展内容、全库 QA 与总册交付 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不稀释正篇因果的前提下，完成 120 张可独立扩展的日常／人物／节气／职业故事卡、40 组周边叙事钩子、全库连续性审计，并从 Markdown 单源汇编一份逐页验收通过的《临安春信·全剧总圣经》DOCX。

**Architecture:** 本计划只能在 Character Final Gate 锁定后执行。扩展卡只读取 C0 状态锁，不得反向改写正篇或人物关系文件。每张卡同时记录正史等级、发生插槽和最早上线集；内容 QA、连续性 QA、DOCX 结构 QA 与逐页视觉 QA 是四道独立门。Markdown 是权威源，DOCX 是可再生成交付物，任何生成报告都不是 Canon。

**Tech Stack:** Markdown、JSON/JSONL、Python 3 标准库、`unittest`、bundled `python-docx`、PowerShell、Git；DOCX 使用 `documents` 技能的 `compact_reference_guide` preset 与 `editorial_cover` 首页面型，并优先使用技能自带 `render_docx.py` 渲染。

---

## 1. 固定 120 张扩展内容结构

| 栏目 | 数量 | 主要功能 | 至少纯日常 | 至少独立观看 |
|---|---:|---|---:|---:|
| 《鹤鸣巷日常》 | 12 | 饮食、邻里、家务、成长、女性生活 | 12 | 12 |
| 《今日无事》 | 12 | 明确无阴谋的治愈、尴尬、失落和微小快乐 | 12 | 12 |
| 《临安人物小传》 | 12 | 非主线独白、过去、职业与一次选择 | 4 | 10 |
| 《四时临安》 | 12 | 二十四节气、花木、雨雪、服饰、食物 | 12 | 12 |
| 《百工春信》 | 12 | 香药、纸墨、修伞、船工、刻版、医药 | 4 | 10 |
| 《春台夜话》 | 12 | 瓦舍、曲艺、妆造、人情与传播责任 | 2 | 8 |
| 《钱塘水路》 | 12 | 船帮、码头、鱼市、潮汐与商旅 | 2 | 8 |
| 《停云来客》 | 12 | 每位新客带入一处外部世界 | 2 | 8 |
| 《城中异闻》 | 12 | 可独立闭环的生活悬疑 | 0 | 6 |
| 《春信外传》 | 12 | C1 关键空白、前史与灾后余波 | 0 | 0 |
| 合计 | 120 |  | 50 | 86 |

硬底线仍以“纯日常至少 48、无需主线知识至少 78”为准；上表预留 2 与 8 张安全余量。

正史等级锁定为：`EX-0109—0120` 是 C1；`EX-0001—0084` 是 C2；`EX-0085—0100` 是 C3；`EX-0101—0108` 是 C4。总计 C1 12、C2 84、C3 16、C4 8。C3/C4 必须在标题和卡头显著标识软正史或非正史。

## Task 1: 建立扩展 Schema、清单和失败测试

**Files:**
- Create: `extensions/00-expansion-rules.md`
- Create: `qa/expansion-manifest.json`
- Create: `scripts/validate_extensions.py`
- Create: `scripts/accept_extension_task.ps1`
- Create: `tests/test_extension_validator.py`
- Modify: `scripts/validate_project.py`

- [ ] **Step 0: 确认 Character Final Gate 已锁；未锁即停止**

```powershell
python scripts/validate_project.py --scope characters --strict
```

Expected: `PASS scope=characters character_final_gate=LOCKED`。

- [ ] **Step 1: 写扩展卡字段**

每张卡必须包含：

```markdown
- ID：EX-0001—EX-0120
- 正史等级：C1/C2/C3/C4
- 栏目：十种固定栏目之一
- 标题：
- 发生插槽：Y-13 前／Y-13 至 Y0／两篇之间／Y+1／无年份
- `slot_after`：正篇状态锚点
- `slot_before`：下一正篇状态锚点；无年份卡必须写 `not_applicable`
- `effective_interval`：由前后锚点组成的半开区间
- `release_after`：最早上线正篇锚点
- `target_seconds`：120—180，生产目标 145—165
- `beat_seconds`：入口／愿望／阻力／选择／结束五段，合计必须等于 `target_seconds`
- 主角 ID：
- 配角 ID：
- 背景人口原型 ID：CHR-BG-### 列表；只有画面中实际从事允许行为时填写
- 地点 ID：
- 节气：
- 行业／职业：
- 是否纯日常：
- 是否无需主线知识：
- 独立入口：
- 当下愿望：
- 微小阻力：
- 所守之物：
- 自主选择：
- 相称代价：
- `character_outcomes`：至少为领衔与每名有效支持角色各写一项 `{character_id, seed_role: lead|support, seen: true|false, understanding: understood|misunderstood|unknown}`
- `ending_focus_character_id`：必须引用 `character_outcomes` 中一人
- `ending_understanding`：必须与该人的 `understanding` 完全一致；这是本卡情绪结尾的单一统计口径
- 结束后余波：
- 允许深化的软状态：
- 禁止改变的 C0 硬状态：
- 可衍生周边：
```

- [ ] **Step 2: 先写失败测试**

必须覆盖：卡数非 120、重复 ID、非法正史等级、未知时间锚点、`slot_after/slot_before` 倒置或跨越非相邻状态锁、上线早于泄密门槛、任一等级越权改写 C0、C3/C4 被正篇引用、时长或五段和错误、节气缺失、栏目数量错误、纯日常不足 48、独立观看不足 78、B 双种子角色结果不合格、每批结束焦点的误解/无人知道配额不足、断链角色/地点、非法 BG 使用及不同 BG 原型不足 90。不同卡共享同一合法时间窗不是错误。

- [ ] **Step 3: 实现验证器并接入总验证器**

`scripts/validate_extensions.py` 支持 `--stage schema|counts|canon|coverage|release|all --strict`；`validate_project.py --scope extensions` 调用全量验证。

`scripts/accept_extension_task.ps1` 只接受 `-Task 3` 至 `-Task 12`，内部以不可编辑映射锁定每项的 12 个 ID、目标文件和提交信息；依次运行栏目验证、`git diff --check`，只暂存映射文件、`qa/expansion-manifest.json` 与 `qa/background-usage.json` 后提交。提供 `-DryRun` 只打印将执行的文件、ID 和提交信息，越界任务必须非零退出。

- [ ] **Step 4: 测试并提交**

```powershell
python -m unittest tests.test_extension_validator -v
pwsh -File scripts/accept_extension_task.ps1 -Task 3 -DryRun
git diff --check
git add extensions/00-expansion-rules.md qa/expansion-manifest.json scripts/validate_extensions.py scripts/accept_extension_task.ps1 scripts/validate_project.py tests/test_extension_validator.py
git commit -m "build: add expansion content validator"
```

## Task 2: 锁定扩展时间槽、角色覆盖与发行规则

**Files:**
- Create: `extensions/06-release-and-canon-manifest.md`
- Modify: `qa/expansion-manifest.json`
- Create: `qa/extension-unit-return-links.json`
- Create: `qa/extension-time-anchor-registry.json`

- [ ] **Step 1: 为 120 个 ID 预分栏目、正史等级与时间槽**

时间槽锁定为：Y-13 前 `EX-0109—0120` 共 12；Y-13 至 Y0 为 `EX-0025—0036` 与 `EX-0061—0066` 共 18；Y0 六篇之间为 `EX-0001—0024`、`EX-0049—0060`、`EX-0067—0084` 共 54；Y+1 为 `EX-0037—0048`、`EX-0085—0096` 共 24；无年份为 `EX-0097—0108` 共 12。合计 120。

先在 `qa/extension-time-anchor-registry.json` 以严格序号登记：`PRE-Y13-OPEN`、`Y-13-OPEN`、`Y-13-END`、`Y0-OPEN`（同时是 `ARC1-OPEN` 的唯一别名）、`ARC1-END`、`ARC2-OPEN`、`ARC2-END`、`ARC3-OPEN`、`ARC3-END`、`ARC4-OPEN`、`ARC4-END`、`ARC5-OPEN`、`ARC5-END`、`ARC6-OPEN`、`ARC6-END`、`ENDING`、`Y+1-OPEN`、`Y+1-END`。每个可用窗口另列唯一 `window_id`、相邻 `slot_after`、`slot_before`、包含端规则和允许的发生插槽；只有注册表显式列出的相邻对合法。Y-13 前 12 卡统一使用开区间 `PRE-Y13-OPEN < event < Y-13-OPEN`，Y+1 卡只能使用 `ENDING < event < Y+1-END` 内登记的相邻窗口；无年份卡两端均为 `not_applicable`。验证器只拒绝未知锚点、倒置、未注册的跨锁窗口或发生插槽不匹配；不同卡可以共享同一合法窗口，不做卡与卡之间的区间重叠检查。

- [ ] **Step 2: 锁定角色覆盖**

- `EX-0001—0024` 的 24 个领衔席位按稳定 ID 顺序给 12 名中央人物每人两席；
- `EX-0025—0048` 的 24 个领衔席位按稳定 ID 顺序给 24 名 A 每人一席；
- `EX-0049—0096` 的 48 个领衔席位按稳定 ID 顺序给 48 名 B 每人一席；`EX-0001—0048` 再按顺序各挂一名 B 为有效支持角色，使每名 B 恰有两则首批种子；
- 每名 B 的领衔种子 `EX-0049—0096` 在其 `character_outcomes` 项固定为 `understood`；B001—B024 的支持种子 `EX-0001—0024` 固定为 `misunderstood`，B025—B048 的支持种子 `EX-0025—0048` 固定为 `unknown`，从而逐人满足“一则被理解＋一则误解或无人知道”，不能只用全库比例替代；
- 建立 `U-RETURN-SLOT-01—40`，只从 Character Final Gate 已证明“首个事件后在另一母集自然回场”的实际 U 名单中绑定人物；若合格者多于 40，按首次回场母集、微章与稳定 ID 排序后取前 40，并保持四类单元用途均有代表；
- `U-RETURN-SLOT-01—28` 分别作为 `EX-0001—0028` 的生活回访支持角色，`U-RETURN-SLOT-29—40` 分别领衔 `EX-0097—0108`；`qa/extension-unit-return-links.json` 保存槽位、实际 CHR-U ID、正篇首事件、正篇回场、扩展卡及所读取关系网哈希；扩展阶段不得修改 `characters/relations/03-unit-return-network.md`；
- 同一张卡可为多名人物计“种子”，但领衔覆盖只能计第一或共同第一主角。

- [ ] **Step 3: 锁定二十四节气与场景/行业覆盖**

24 节气由季节卡精确覆盖：EX-0037 立春/雨水、0038 惊蛰/春分、0039 清明/谷雨、0040 立夏/小满、0041 芒种/夏至、0042 小暑/大暑、0043 立秋/处暑、0044 白露/秋分、0045 寒露/霜降、0046 立冬/小雪、0047 大雪/冬至、0048 小寒/大寒。全库至少 12 个行业、12 个主场景；相邻六张不得都发生在同一生活圈。

- [ ] **Step 3A: 锁定纯日常与独立观看卡位**

`pure_life=true`：EX-0001—0024、0025—0028、0037—0048、0049—0052、0061—0062、0073—0074、0085—0086，共 50。

`standalone=true`：EX-0001—0024、0025—0034、0037—0048、0049—0058、0061—0068、0073—0080、0085—0092、0097—0102，共 86。

- [ ] **Step 4: 写泄密门槛**

Y-13 与关键前史即使发生得早，只要涉及旧信被截、三仓、沈怀川错误、顾行舟旧身份或宋惟敬妻儿真相，`release_after` 必须晚于正篇首次揭示。

正史权限逐级验证：C1 可补关键空白但不得与 C0 冲突；C2 只读 C0 硬状态；C3/C4 不得被 C0—C2 或正篇当作事实源；所有等级都不得回写正篇人物、关系或状态事件文件。

- [ ] **Step 5: 验证并提交**

```powershell
python scripts/validate_extensions.py --stage release --strict
git add extensions/06-release-and-canon-manifest.md qa/expansion-manifest.json qa/extension-unit-return-links.json
git commit -m "extensions: lock release slots and cast coverage"
```

Expected: `unit_return_slots=40 actual_ids=40 source_hash=verified character_files_modified=0`。

## Tasks 3–12: 完成十个固定扩展栏目

每行独立完成 12 张卡并单独提交，同时修改 `qa/background-usage.json` 的 `extension_ids`。所有故事均使用 2—3 分钟结构：入口 5—12 秒、愿望 20—35 秒、职业或关系阻力 65—95 秒、选择 20—35 秒、结束 8—18 秒；五段精确相加为 120—180 秒，生产目标 145—165 秒。公开空间若出现可辨认人群，必须使用符合地点、时辰和劳动状态的 `CHR-BG-###`；120 张合计至少实际使用 90 个不同 BG 原型。

| Task | ID | 栏目／文件 | 内容硬项 | 精确验收命令 |
|---:|---|---|---|---|
| 3 | EX-0001—0012 | 《鹤鸣巷日常》→Create `extensions/01-daily-life-library.md` | 吃饭、赊账、家务、相亲、邻里；12 张全为纯日常 | `pwsh -File scripts/accept_extension_task.ps1 -Task 3` |
| 4 | EX-0013—0024 | 《今日无事》→Modify `extensions/01-daily-life-library.md` | 无阴谋；至少 3 张以误解、2 张以无人知道结束 | `pwsh -File scripts/accept_extension_task.ps1 -Task 4` |
| 5 | EX-0025—0036 | 《临安人物小传》→Create `extensions/03-character-side-stories.md` | 不把档案念成旁白；每篇必须有当下选择 | `pwsh -File scripts/accept_extension_task.ps1 -Task 5` |
| 6 | EX-0037—0048 | 《四时临安》→Create `extensions/02-seasonal-library.md` | 12 张共同覆盖 24 节气，每张双节气或主/副节气 | `pwsh -File scripts/accept_extension_task.ps1 -Task 6` |
| 7 | EX-0049—0060 | 《百工春信》→Create `extensions/04-professions-and-objects.md` | 至少 12 行业；错误劳动细节必须经 Canon 审读修正 | `pwsh -File scripts/accept_extension_task.ps1 -Task 7` |
| 8 | EX-0061—0072 | 《春台夜话》→Modify `extensions/03-character-side-stories.md` | 台前/后台各半；表演、妆造、生计和流言责任并存 | `pwsh -File scripts/accept_extension_task.ps1 -Task 8` |
| 9 | EX-0073—0084 | 《钱塘水路》→Modify `extensions/04-professions-and-objects.md` | 潮、船、鱼市、脚夫、船工家庭；不把水路只当追逐背景 | `pwsh -File scripts/accept_extension_task.ps1 -Task 9` |
| 10 | EX-0085—0096 | 《停云来客》→Modify `extensions/03-character-side-stories.md` | 12 位不同来客，不同地域/阶层/目的，不全是线索携带者 | `pwsh -File scripts/accept_extension_task.ps1 -Task 10` |
| 11 | EX-0097—0108 | 《城中异闻》→Modify `extensions/01-daily-life-library.md` | 生活悬疑独立闭环，至少 4 张答案不是犯罪 | `pwsh -File scripts/accept_extension_task.ps1 -Task 11` |
| 12 | EX-0109—0120 | 《春信外传》→Modify `extensions/03-character-side-stories.md` | C1 关键空白；补充但不得推翻 C0 | `pwsh -File scripts/accept_extension_task.ps1 -Task 12` |

每项固定步骤：

- [ ] **Step 1: 读取 `slot_after` 对应人物、物件、关系、知识与地点状态**
- [ ] **Step 2: 写 12 张完整故事卡，不以主线阴谋作为默认结尾**
- [ ] **Step 3: 按 `ending_understanding` 验证本批至少两张以 `misunderstood`、至少一张以 `unknown` 结束；Tasks 7—10 的 B 领衔人物仍保持 `understood`，这些卡必须由另一名有效支持人物承担结束焦点，禁止改写 B 的领衔种子结果来凑配额**
- [ ] **Step 4: 检查删除本卡不会破坏正篇理解**
- [ ] **Step 5: 运行本任务表中的精确验收命令；辅助脚本只提交本行栏目文件及两个指定 QA 账本**

## Task 13: 完成 40 组周边叙事钩子

**Files:**
- Create: `extensions/05-merchandise-story-hooks.md`

- [ ] **Step 1: 写 8 组书信与春信笺**

每组包括物件来源、角色使用场景、可印文字边界、避免泄密规则和一个免费可读故事入口。

- [ ] **Step 2: 写 8 组香方与节气卡**
- [ ] **Step 3: 写 8 组地图、场景图与路线探索**
- [ ] **Step 4: 写 8 组食谱、曲谱、酒肆菜单与百工图鉴**
- [ ] **Step 5: 写 8 组角色音频、环境声与节气短片**
- [ ] **Step 6: 检查所有关键剧情均可不购买周边而理解**
- [ ] **Step 7: 提交**

```powershell
git add extensions/05-merchandise-story-hooks.md
git commit -m "extensions: define forty merchandise story hooks"
```

## Task 14: 锁定 120 张扩展内容

**Files:**
- Modify: `extensions/06-release-and-canon-manifest.md`
- Modify: `qa/expansion-manifest.json`
- Modify: `qa/background-usage.json`
- Create: `qa/reviews/extensions-canon-review.md`
- Create: `qa/reviews/extensions-character-review.md`

- [ ] **Step 1: 运行全量测试和验证**

```powershell
python -m unittest tests.test_extension_validator -v
python scripts/validate_extensions.py --stage all --strict
python scripts/validate_characters.py --stage background --strict
python scripts/validate_project.py --scope extensions --strict
```

Expected:

```text
PASS expansion_total=120 IDs=unique
PASS C1=12 C2=84 C3=16 C4=8
PASS solar_terms=24/24 industries>=12 locations>=12
PASS pure_life>=48 standalone>=78
PASS B_seed_coverage=48/48 U_return_links=40
PASS extension_background_used>=90 invalid_background_uses=0
PASS duration=120..180 target=145..165 B_emotional_pairs=48/48
PASS release_leaks=0 hard_state_mutations=0 canon_direction_violations=0
```

- [ ] **Step 2: Canon 审读时间槽、状态锁和正史等级**
- [ ] **Step 3: 人物审读独立愿望、相称代价与“不总被理解”**
- [ ] **Step 4: 修正后提交**

```powershell
git add extensions qa
git commit -m "qa: lock Linan expansion library"
```

## Task 15: 建立全库连续性模拟与最终内容门禁

**Files:**
- Read: `qa/canon-fact-registry.json`
- Read: `qa/state/microchapter-state-events.jsonl`
- Read: `qa/state/relationship-events.jsonl`
- Read: `qa/state/clue-events.jsonl`
- Create: `scripts/validate_continuity.py`
- Create: `tests/test_continuity_validator.py`
- Create: `qa/reports/qa-report.json`
- Create: `qa/reports/qa-report.md`
- Create: `qa/reports/continuity-errors.csv`
- Create: `qa/reports/placeholder-scan.txt`
- Create: `qa/content-source-manifest.json`
- Modify: `scripts/validate_project.py`

- [ ] **Step 1: 先写失败测试**

测试同人同时出现在不可达地点、路程不足、伤势自动恢复、物件双持、人物提前知道事实、错误认知无来源、更正无旧误认、钱债跳变、关系只用单一好感度、线索缺环、事件 `before` 不等于上一 `after`、重叠有效区间、无权威 Canon fact、终局能力 E30 前未铺垫、扩展越权改变 C0。

- [ ] **Step 2: 按 M001—M648 顺序模拟状态**

按 M001—M648 读取三份状态事件 JSONL，并以 `qa/canon-fact-registry.json` 解析权威优先级；模拟时间、地点、伤病、知识、物件、职业、钱财、债务、身份、七维关系和线索知情范围。Markdown 只用于核对引用 ID，不作为状态解析源；扩展卡只从对应锚点读取状态，不进入正篇写回。

- [ ] **Step 3: 建立内容源清单并扫描断链与占位**

`qa/content-source-manifest.json` 明确枚举最终汇编会读取的 Canon、人物档案、关系、故事、微章和扩展正文。把 `scripts/validate_project.py` 的 `content`/`all` 内容扫描改为只读取这份清单，不扫描 `qa/` 报告、规则 Schema、`scripts/`、`tests/`、计划或扫描输出本身，避免规则文字与报告自撞；同时检查清单内 Markdown 链接及人物、地点、物件、线索 ID。

`qa-report.json` 必须记录 `content_source_manifest_sha256`、清单中每个源文件的路径/哈希/字节数及总体 Merkle 根；`placeholder-scan.txt` 只写扫描规则集哈希、匹配总数和结构化位置，不复制禁止词本身。DOCX 的文本与 OOXML 在结构审计阶段另扫。

- [ ] **Step 4: 生成固定摘要并通过全量测试**

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate_continuity.py --strict
python scripts/validate_project.py --scope content --strict
```

Expected:

```text
LINAN QA PASS
canon_errors=0 character_errors=0 story_errors=0
emotion_errors=0 expansion_errors=0 continuity_errors=0 placeholder_errors=0
micro_total=648 expansion_total=120
```

- [ ] **Step 5: 提交内容门禁**

```powershell
git add scripts tests qa/content-source-manifest.json qa/reports
git commit -m "qa: add complete Linan narrative gate"
```

## Task 16: 设计 DOCX 单源汇编与版式系统

**Required skill:** `documents`

**Files:**
- Create: `deliverables/assembly-manifest.json`
- Create: `qa/runtime-dependencies.json`
- Create: `qa/template-selection.json`
- Create: `scripts/build_master_bible.py`
- Create: `scripts/audit_docx.py`
- Create: `scripts/finalize_docx_fields.ps1`
- Create: `tests/test_docx_delivery.py`

- [ ] **Step 1: 加载 bundled workspace dependencies**

执行代理先调用 workspace dependency loader，把本次返回的 Python、Node、documents skill root、Poppler、LibreOffice/Word 可用性和版本写入 `qa/runtime-dependencies.json`。后续命令只从该 JSON 读取路径，不硬编码用户目录，不使用系统 Python/Node，也不临时联网安装依赖；路径或版本变化时旧 DOCX QA 自动失效。

- [ ] **Step 2: 打开 document template picker**

若用户未提供模板，由执行代理调用文档模板选择器一次，并把选择来源、模板路径/资源 ID 与 SHA-256 写入 `qa/template-selection.json`。若用户选中模板，先执行文档技能的模板提炼与一页样张渲染，模板 token 覆盖通用 preset，但不得破坏可读性、固定表格几何和东亚字体；只有用户取消、无合适模板或工具不可用时，才记录原因并回退到 `compact_reference_guide` preset 与 `editorial_cover` 首页面型。

- [ ] **Step 3: 解析并写入完整 token map**

通用 token 固定：Letter 纵向、四边 1440 DXA、页眉/页脚距边 720 DXA、正文宽 9360 DXA；拉丁字体 Calibri，`east_asia_font_override=Microsoft YaHei`；正文 11 pt、字色 `#242A2E`、1.25 倍行距、段后 6 pt、孤行/寡行控制开启。H1 为 16 pt/`#234F4A`/段前 14 pt/段后 6 pt，H2 为 13 pt/`#3F625D`/12/4，H3 为 12 pt/`#596B67`/10/3，均 `keep_with_next=true`。列表左缩进 540 DXA、悬挂 360 DXA并使用真实 numbering。表格 `tblW=9120`、`tblInd=120`，`tblGrid` 与 `tcW` 一致，cell margins 上下 80、左右 120 DXA，表头填充 `#DFE9E6`、10 pt 加粗，禁止 autofit 与固定行高。

首面使用 `editorial_cover` 的居中长篇手册结构，但遵守 header template 的“标题块无下边框”硬约束。标题 26 pt/`#183F3A`，副题 12 pt/`#596B67`，底部版本与 Canon 状态 10 pt/`#68716E`；标题为《临安春信·全剧总圣经》，副题写世界观、人物志、第一季 36 集、648 微短章与扩展库。

- [ ] **Step 4: 写明确输入顺序，不使用 glob**

`deliverables/assembly-manifest.json` 顶层必须写 `content_source_manifest_sha256`、与 `qa/reports/qa-report.json` 相同的 `content_source_merkle_root`、`runtime_dependencies_sha256` 与 `template_selection_sha256`。它再逐项列出，不得用目录名或 glob 代替：全部 Canon；12 个中央人物档案；24 个 A 级档案；8 个 B 级分卷；4 个 U 席位卷与 12 个 U 最终档案卷；15 个 BG 原型卷；关系索引、非中央关系网、17 个核心 REL 与六条情感脊柱；总季纲、六篇季纲与 `story/07-clue-and-payoff-ledger.md`；六个微章文件；全部扩展栏目文件；最终 QA 摘要。每个输入项另写 `sha256`、`base_heading_level`、`include_in_toc`、`render_mode`。所有同时属于 `qa/content-source-manifest.json` 的输入必须路径与 SHA-256 逐项一致；允许加入生成型 QA 摘要，但不得以它替代或遮蔽任何内容源。目录只收 H1—H3 的卷/篇/集；648 张微章使用 `MicroCardTitle` 自定义样式且 `include_in_toc=false`，以纵向卡片段落渲染，禁止九列宽表。不得把生成报告当作前文事实源。

- [ ] **Step 5: 写 DOCX 结构测试**

测试：输入文件全存在、哈希匹配且唯一；assembly 的内容源清单哈希、Merkle 根以及逐路径哈希与 `qa-report.json`/内容源清单相同；runtime 与 template 哈希匹配当前 JSON；标题层级连续；真实 TOC 与页码字段；目录不含 648 个微章标题；真实列表；表格固定几何；token map 完整；无内部 JSON 注释与占位；人物/微章/扩展卡计数与 QA 一致。`scripts/finalize_docx_fields.ps1` 必须在隐藏 Word COM 可用时更新 Fields/TOC 并保存，Word 不可用时用 LibreOffice 在受控临时目录更新后原子替换；两者都不可用则失败。

- [ ] **Step 6: 提交构建工具**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python -m unittest tests.test_docx_delivery -v
git add deliverables/assembly-manifest.json qa/runtime-dependencies.json qa/template-selection.json scripts/build_master_bible.py scripts/audit_docx.py scripts/finalize_docx_fields.ps1 tests/test_docx_delivery.py
git commit -m "build: add Linan master bible assembler"
```

## Task 17: 生成并结构审计最终 DOCX

**Files:**
- Create: `deliverables/linan-spring-letter-master-bible.docx`
- Create: `qa/reports/docx-finalization.json`
- Create: `qa/reports/docx-structure.json`

- [ ] **Step 1: 先完成内容 QA**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\validate_project.py --scope content --strict
```

- [ ] **Step 2: 紧邻第一次 DOCX 作者命令，只执行一次 artifact 标记**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.node "$($deps.documents_skill_root)\container_tools\mark_artifact_operation_started.mjs" --operation-kind create --expected-output-count 1 --output-format docx
```

- [ ] **Step 3: 从 Markdown 单源生成，随后更新字段并保存最终 DOCX**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\build_master_bible.py --manifest deliverables\assembly-manifest.json --out deliverables\linan-spring-letter-master-bible.docx
pwsh -File scripts\finalize_docx_fields.ps1 -Document deliverables\linan-spring-letter-master-bible.docx -Runtime qa\runtime-dependencies.json -Report qa\reports\docx-finalization.json
```

禁止拼接多个临时 DOCX。字段更新完成后不得再有任何会保存 DOCX 的步骤。

- [ ] **Step 4: 对字段已更新的最终 DOCX 做结构审计**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\audit_docx.py deliverables\linan-spring-letter-master-bible.docx --manifest deliverables\assembly-manifest.json --json qa\reports\docx-structure.json --strict
```

检查 OOXML 可打开、标题/TOC/页码、章节顺序、字体、页边距、编号、表格几何、链接、书签、无内部元数据与占位；`docx-finalization.json` 与 `docx-structure.json` 都必须保存并核对 `docx_sha256`、`assembly_manifest_sha256`、`content_source_manifest_sha256`、`content_source_merkle_root`、`runtime_dependencies_sha256` 与 `template_selection_sha256`。结构报告还要逐项验证 assembly 与内容源清单交集的路径和哈希完全相同，并与 finalization 报告的最终 DOCX 哈希一致；任一来源 JSON 或内容源变化，旧报告立即失效。

- [ ] **Step 5: 修正所有结构问题后从 Step 3 重做并提交生成候选**

```powershell
git add deliverables/linan-spring-letter-master-bible.docx qa/reports/docx-finalization.json qa/reports/docx-structure.json
git commit -m "build: assemble Linan master bible candidate"
```

## Task 18: 渲染、逐页视觉检查并迭代

**Files:**
- Create: `scripts/render_master_bible.ps1`
- Create: `scripts/scan_docx_render.py`
- Create: `qa/reports/render-manifest.json`
- Create: `qa/reports/render-review.json`
- Generate: `qa/render/master-bible/page-*.png`

- [ ] **Step 1: 优先用 documents 技能的 canonical renderer**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
$renderer=Join-Path $deps.documents_skill_root 'render_docx.py'
& $deps.python $renderer deliverables\linan-spring-letter-master-bible.docx --output_dir qa\render\master-bible --emit_pdf
```

- [ ] **Step 2: 若且仅若缺少 LibreOffice，使用只读 Word COM 后备渲染**

`scripts/render_master_bible.ps1` 必须先验证当前 DOCX 哈希等于 `docx-structure.json`，再隐藏、只读打开 Word，导出 PDF 且以 `SaveChanges=0` 关闭；随后用依赖清单中的 Poppler 生成逐页 PNG，并再次确认 DOCX 哈希未变。字段与 TOC 已在 Task 17 更新，本步骤禁止保存。其他渲染错误不得绕过，应先修复。

- [ ] **Step 3: 自动扫描页图**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\scan_docx_render.py --docx deliverables\linan-spring-letter-master-bible.docx --structure qa\reports\docx-structure.json --input-dir qa\render\master-bible --out qa\reports\render-manifest.json --strict
```

检查页图尺寸、零字节、纯白异常页、内容触边、重复页、PDF/PNG 页数一致；`render-manifest.json` 必须记录并验证与 `docx-structure.json` 相同的 `docx_sha256`，另存 `pdf_sha256`、页数及每页图片 SHA-256。

- [ ] **Step 4: 逐页以 100% 比例人工检查**

每一页都必须检查：裁切、重叠、缺字、字体替换、表格跨页、标题孤行、目录与页码、页眉页脚、异常空白。联系表只用于定位，不得代替逐页检查。

`qa/reports/render-review.json` 顶层写 `render_manifest_sha256`、与结构/渲染清单一致的 `docx_sha256` 与 `pdf_sha256`；每页写 `page`、实际 `image_sha256`、`status`、`issues`，并与 manifest 一一对应。DOCX、PDF、任一页图或 render manifest 变化，旧逐页审核自动失效。

- [ ] **Step 5: 发现任何问题就修改 DOCX 生成器、重新生成、重做结构审计、重新渲染并重新逐页检查**

## Task 19: 锁定 Delivery Gate 与交付哈希

**Files:**
- Create: `qa/reports/final-gate.json`
- Create: `deliverables/linan-spring-letter-master-bible.sha256`
- Create: `deliverables/delivery-manifest.json`
- Create: `scripts/build_final_gate.py`
- Create: `tests/test_final_gate.py`
- Modify: `scripts/validate_project.py`
- Modify: `tests/test_validate_project.py`
- Modify: `qa/production-status.json`
- Create: `qa/gates/scope-definitions/delivery.json`
- Create: `qa/gates/input-manifests/delivery.json`
- Create: `qa/gates/delivery-gate.json`
- Create: `qa/reviews/delivery-content-review.md`
- Create: `qa/reviews/delivery-visual-review.md`

- [ ] **Step 1: 核对四道门**

内容 QA、连续性 QA、DOCX 结构 QA、最新哈希逐页视觉 QA 均为 PASS。

- [ ] **Step 2: 先写最终门禁的失败测试**

覆盖：DOCX 哈希与 `.sha256` 不同、结构报告绑定不同 DOCX 或 assembly manifest、渲染报告绑定不同 DOCX/PDF、逐页审核绑定错误 render manifest 或页图、审核页数与渲染页数不同、内容 QA 源树哈希变化、任一输入报告在门禁生成后变化、交付清单引用错误 final-gate/Gate 证书哈希、试图让清单哈希自身造成循环依赖。不得以 mtime 判断新旧。

- [ ] **Step 3: 实现非循环的后验哈希链并生成交付清单**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\build_final_gate.py --write-ready
```

绑定链固定为：`qa-report.json` 验证内容源清单、Merkle 根与逐源哈希；assembly manifest 保存同一内容源清单哈希/Merkle 根并逐项引用相同源文件哈希，同时绑定 runtime/template JSON；`docx-finalization.json` 与 `docx-structure.json` 绑定最终 DOCX、assembly、同一内容源版本及同一 runtime/template；`render-manifest.json` 绑定同一 DOCX、PDF、页数和逐页图片哈希；`render-review.json` 绑定 render manifest、同一 DOCX/PDF 与全部页图。`final-gate.json` 逐字段验证内容源清单哈希、Merkle 根、assembly 交集路径/哈希、runtime/template SHA-256 和各报告中的 DOCX/PDF/页图哈希完全相等后，保存最终 DOCX、批准规格、内容/连续性/结构/渲染/逐页审核报告哈希和 `PASS` 判定，不能只读取报告中的 PASS 字样。

`--write-ready` 生成 `.sha256`、`final-gate.json` 与状态为 `READY_FOR_LOCK` 的 delivery manifest，但不手改 Gate 状态。此时 delivery manifest 保存 DOCX、final-gate、内容源清单哈希/Merkle 根、运行时 JSON 哈希、模板 JSON 哈希、页数和逐页检查数，不保存自身哈希，也暂不写 Gate 证书哈希。

- [ ] **Step 4: 准备输入清单、双审读、锁 Gate，再完成非循环交付清单**

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python -m unittest tests.test_final_gate -v
& $deps.python scripts\build_final_gate.py --verify-ready
& $deps.python scripts\lock_gate.py --gate delivery --scope delivery --prepare
```

内容交付审读者与视觉交付审读者分别检查同一准备清单，在两份审读文件 TOML 头签署其 SHA-256。若修改任一输入，重新从 `--write-ready` 开始。

```powershell
$deps=Get-Content qa/runtime-dependencies.json | ConvertFrom-Json
& $deps.python scripts\lock_gate.py --gate delivery --scope delivery --lock --review qa/reviews/delivery-content-review.md --review qa/reviews/delivery-visual-review.md
& $deps.python scripts\build_final_gate.py --finalize-manifest --gate-certificate qa/gates/delivery-gate.json
& $deps.python scripts\build_final_gate.py --verify
& $deps.python scripts\validate_project.py --scope delivery --strict
& $deps.python scripts\validate_project.py --scope all --strict
git diff --check
```

`lock_gate.py` 对 delivery 的 `--prepare` 与 `--lock` 都调用 `build_final_gate.py --verify-ready`，而不调用此时必然尚未满足的最终 delivery strict validator；`--lock` 仍须验证输入投影、前置证书与两份审读哈希。锁定后，`--finalize-manifest` 才把清单状态写为 `LOCKED` 并加入 Gate 证书 SHA-256，再运行最终 `validate_project --scope delivery --strict`。Gate 证书不哈希最终 delivery manifest，且其 scope projection 排除从 `READY_FOR_LOCK` 变为 `LOCKED` 的状态字段和新增证书哈希；manifest 单向引用证书，因此没有循环。最终 validator 验证 DOCX、内容源↔assembly 桥接、runtime/template provenance、所有报告、final-gate、证书、最终清单和状态；`--scope all` 明确依次运行 content 与 delivery 全部子验证器。

Expected:

```text
LINAN FINAL GATE PASS
source_qa=PASS docx_structure=PASS
render_pages 与 pages_reviewed 为相同的正整数
visual_defects=0 placeholders=0 delivery_hash=verified
```

- [ ] **Step 5: 提交最终交付物**

```powershell
git add deliverables qa/reports qa/gates qa/reviews/delivery-content-review.md qa/reviews/delivery-visual-review.md qa/production-status.json scripts/build_final_gate.py scripts/validate_project.py tests/test_final_gate.py tests/test_validate_project.py
git commit -m "docs: deliver Linan Spring Letter master bible"
```

## 最终证据清单

完成时必须同时存在：

1. `qa/content-source-manifest.json`：全部权威内容源与源树哈希；
2. `qa/reports/qa-report.json`：所有内容规则零错误，并绑定内容源树；
3. `qa/canon-fact-registry.json`：事实优先级与冲突为零；
4. `qa/pov-allocation.json` 与生成视图 `qa/pov-budget-matrix.md`：648 个 POV 精确闭合；
5. `qa/function-allocation.json`：主线、关系、日常精确为 312/204/132；
6. `qa/episode-coverage-matrix.json` 与生成视图 `qa/episode-coverage-matrix.md`：人物实际覆盖而非预留；
7. `qa/emotional-anchor-bindings.json` 与 `qa/emotional-spine-matrix.md`：六轴六篇共 36 格；
8. 12×6 中央责任格的实际母集与微章绑定证据；
9. `qa/background-usage.json`：正篇与扩展的 BG 实际使用；
10. `story/07-clue-and-payoff-ledger.md`、`qa/clue-ledger.json` 与 `qa/state/clue-events.jsonl`：线索四节点闭合；
11. `qa/expansion-manifest.json`：120 张及比例通过；
12. `qa/reports/continuity-errors.csv`：只有表头；
13. `qa/reports/placeholder-scan.txt`：零匹配；
14. `deliverables/assembly-manifest.json`：显式输入、样式与输入哈希；
15. `qa/reports/docx-structure.json`：结构通过并绑定最终 DOCX；
16. `qa/reports/render-manifest.json`：绑定同一 DOCX/PDF 的完整页清单；
17. `qa/reports/render-review.json`：每页对应最新 manifest 与哈希且均为 PASS；
18. 六个 Gate 证书、各 Gate 双审读签署及前置证书哈希链；
19. `qa/reports/final-gate.json` 与 `deliverables/delivery-manifest.json`：总状态 PASS/LOCKED 且哈希链有效；
20. 最终 DOCX 与 `.sha256` 一致。
