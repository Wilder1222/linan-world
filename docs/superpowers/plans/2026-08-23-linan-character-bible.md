# 《临安春信》分级人物圣经 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把“五名主角”扩展成真正承担全剧因果的 12 名中央人物、24 名重要人物、48 名市井常驻、120 名单元人物和 300 个背景人口原型，并以可验证的 POV、关系、职业、牺牲和六篇状态证明每个人不是功能型 NPC。

**Architecture:** 人物生产分两次冻结。Character Foundation Gate 在季纲前锁定 84 名稳定角色、120 个 U 级剧情席位、300 个 BG 原型、关系席位与 POV 预算；Character Final Gate 在 648 章后补全 U 级实际档案、实际出场与回访。人物事实保存在独立档案，关系事实保存在关系档案，视角和状态只由 QA 矩阵计数，入口文件只做索引而不复制权威正文。

**Tech Stack:** Markdown、JSON、Python 3 标准库、`unittest`、PowerShell、Git。

---

## 1. 冻结边界与人物总量

| 档位 | 数量 | 第一季 POV | 最低母集覆盖 | 冻结阶段 |
|---|---:|---:|---:|---|
| L1 | 5 | 230 | 每人 24 集 | Foundation |
| L2 | 4 | 108 | 每人 16 集 | Foundation |
| L3 | 3 | 72 | 每人 12 集 | Foundation |
| A1 | 8 | 80 | 每人 12 集 | Foundation |
| A2 | 8 | 48 | 每人 8 集 | Foundation |
| A3 | 8 | 16 | 每人 4 集 | Foundation |
| B | 48 | 72 | 每人 2 集 | Foundation 预留，Final 核实 |
| U | 120 | 22 | 单元制 | Foundation 分配席位，Final 完成档案 |
| BG | 300 | 0 | 不设 | Foundation |

命名人物总数固定为 204；BG 首批固定写满 300 个原型。档位表示叙事责任，不表示道德价值。

## Task 1: 建立人物 Schema、清单与失败测试

**Files:**
- Create: `characters/00-character-schema.md`
- Create: `qa/character-roster.json`
- Create: `scripts/validate_characters.py`
- Create: `tests/test_character_validator.py`
- Modify: `scripts/validate_project.py`

- [ ] **Step 1: 先写 13 类失败测试**

`tests/test_character_validator.py` 必须包含以下测试名：

```python
test_duplicate_character_id_fails
test_duplicate_alias_without_declaration_fails
test_wrong_tier_count_fails
test_wrong_individual_pov_budget_fails
test_missing_guard_answer_fails
test_missing_noncentral_relationship_fails
test_missing_state_checkpoint_fails
test_relationship_pair_duplicate_fails
test_relationship_dimension_without_evidence_fails
test_unit_slot_count_fails
test_background_archetype_count_fails
test_unit_finalization_before_episode_lock_fails
test_non_toml_or_malformed_front_matter_fails
```

Run:

```powershell
python -m unittest tests.test_character_validator -v
```

Expected: 因 `scripts.validate_characters` 尚不完整而失败。

- [ ] **Step 2: 写人物档案统一字段**

`characters/00-character-schema.md` 必须精确定义：

- front matter 固定使用 `+++` 包围的 TOML，由 Python 3.11+ 标准库 `tomllib` 解析，禁止 YAML；字段为 `id`、`tier`、`name`、`aliases`、`age_y0`、`occupation`、`residence`、`economic_source`、`pov_budget`、`minimum_episode_coverage`、`status`；
- 身份与外在：籍贯、阶层、职业流程、外貌、体态、年龄/职业痕迹、四季服装、随身物；
- 内在：公开身份、隐藏经历、他人误解、欲望、恐惧、价值观、缺点、底线、秘密；
- 表达：语言节奏、口头习惯、沉默方式、动作习惯、不依赖台词的关心方式；
- 现实：一日作息、技能、能力边界、收入、债务、照料责任；
- 关系：亲属、朋友、恩情、敌意及至少两条不经过 L1—L3 的关系；
- 坚守七问：①最想保护什么；②这种坚守为什么形成；③在保护它时伤害过谁；④两件都正确的事冲突时选择什么；⑤为此具体放弃什么；⑥谁会因此误解、怨恨或离开；⑦即使没有回报，是否仍承认这个选择属于自己；
- 状态：历史事实 `Y-13`；当季与未来检查点 `Y0-OPEN`、`ARC1-END` 至 `ARC6-END`、`ENDING`、`Y+1`，合计十个状态字段；`ARC6-END` 记录危机解决时状态，`ENDING` 记录人物独有结局画面，二者不得合并；
- 变化：错误选择、真实伤害、代价、主动改变、主题关系、独有结局画面。

L1—L3 与 A1—A3 必须满足全部十个状态字段；B 使用 `Y0-OPEN`、首次日常、终局职业回响、`ENDING` 四个状态；U 使用首事件、余波与回场（如有）状态。验证器按档位选择 Schema，不得要求 U 伪造全年成长弧。

- [ ] **Step 3: 实现人物验证器的阶段接口**

`scripts/validate_characters.py` 必须以 `parse_profile_toml(path)` 先解析且拒绝未知/重复字段，再实现 roster、profile、central、important、recurring、unit-slots、unit-final、background、relationship-slots、relationships、emotional-spines、foundation、final 十三个阶段。每个阶段返回按 `error_code|stable_id|path|field` 排序的错误列表，CLI 有错误时退出 1、无错误时退出 0；`unit-final` 必须读取 Episode Gate 证书而非状态字符串。

CLI 必须支持：

```text
--stage roster|profile|central|important|recurring|unit-slots|unit-final|background|relationship-slots|relationships|emotional-spines|foundation|final
--character-id CHR-L1-01（示例；接受注册表内任一稳定人物 ID）
--write-generated-views
--strict
```

- [ ] **Step 4: 让总验证器调用人物验证器**

`scripts/validate_project.py --scope character-foundation` 调用 `validate_foundation`；`--scope characters` 调用 `validate_final`。

- [ ] **Step 5: 运行测试并提交**

```powershell
python -m unittest tests.test_character_validator -v
git diff --check
git add characters/00-character-schema.md qa/character-roster.json scripts/validate_characters.py scripts/validate_project.py tests/test_character_validator.py
git commit -m "build: add tiered character validation"
```

Expected: 12 tests passed；`git diff --check` 无输出。

## Task 2: 建立完整人物编号、路径和入口索引

**Files:**
- Create: `characters/00-character-index.md`
- Create: `characters/01-central-cast-12.md`
- Create: `characters/02-important-cast-24.md`
- Create: `characters/03-recurring-citizens-48.md`
- Create: `characters/04-unit-characters-120.md`
- Create: `characters/08-background-population-300-plus.md`
- Create: `characters/central/00-central-index.md`
- Create: `characters/important/00-important-index.md`
- Create: `characters/recurring/00-recurring-index.md`
- Create: `characters/unit/00-unit-index.md`
- Create: `characters/background/00-background-index.md`
- Modify: `qa/character-roster.json`

- [ ] **Step 1: 锁定 12 名中央人物 ID 与文件**

| ID | 人物 | 独立档案 |
|---|---|---|
| CHR-L1-01 | 沈蘅 | `characters/central/chr-l1-01-shen-heng.md` |
| CHR-L1-02 | 柳十四／柳望舒 | `characters/central/chr-l1-02-liu-shisi-liu-wangshu.md` |
| CHR-L1-03 | 周砚之 | `characters/central/chr-l1-03-zhou-yanzhi.md` |
| CHR-L1-04 | 裴九娘 | `characters/central/chr-l1-04-pei-jiuniang.md` |
| CHR-L1-05 | 顾行舟 | `characters/central/chr-l1-05-gu-xingzhou.md` |
| CHR-L2-01 | 陆清和 | `characters/central/chr-l2-01-lu-qinghe.md` |
| CHR-L2-02 | 林阿沅 | `characters/central/chr-l2-02-lin-ayuan.md` |
| CHR-L2-03 | 余青禾 | `characters/central/chr-l2-03-yu-qinghe.md` |
| CHR-L2-04 | 高问 | `characters/central/chr-l2-04-gao-wen.md` |
| CHR-L3-01 | 宋惟敬 | `characters/central/chr-l3-01-song-weijing.md` |
| CHR-L3-02 | 黎见山 | `characters/central/chr-l3-02-li-jianshan.md` |
| CHR-L3-03 | 贺兰度 | `characters/central/chr-l3-03-helan-du.md` |

- [ ] **Step 2: 锁定 24 名 A 级 ID 与文件**

| ID | 人物 | 独立档案 |
|---|---|---|
| CHR-A1-01 | 沈三娘 | `characters/important/chr-a1-01-shen-sanniang.md` |
| CHR-A1-02 | 周伯安 | `characters/important/chr-a1-02-zhou-boan.md` |
| CHR-A1-03 | 余仲仁 | `characters/important/chr-a1-03-yu-zhongren.md` |
| CHR-A1-04 | 顾念娘 | `characters/important/chr-a1-04-gu-nianniang.md` |
| CHR-A1-05 | 许含章 | `characters/important/chr-a1-05-xu-hanzhang.md` |
| CHR-A1-06 | 章允中 | `characters/important/chr-a1-06-zhang-yunzhong.md` |
| CHR-A1-07 | 黎令仪 | `characters/important/chr-a1-07-li-lingyi.md` |
| CHR-A1-08 | 曹肃 | `characters/important/chr-a1-08-cao-su.md` |
| CHR-A2-01 | 陈桂婆 | `characters/important/chr-a2-01-chen-guipo.md` |
| CHR-A2-02 | 宋十九 | `characters/important/chr-a2-02-song-shijiu.md` |
| CHR-A2-03 | 沈怀川 | `characters/important/chr-a2-03-shen-huaichuan.md` |
| CHR-A2-04 | 贺九 | `characters/important/chr-a2-04-he-jiu.md` |
| CHR-A2-05 | 石六 | `characters/important/chr-a2-05-shi-liu.md` |
| CHR-A2-06 | 罗见潮 | `characters/important/chr-a2-06-luo-jianchao.md` |
| CHR-A2-07 | 程野老 | `characters/important/chr-a2-07-cheng-yelao.md` |
| CHR-A2-08 | 方书娘 | `characters/important/chr-a2-08-fang-shuniang.md` |
| CHR-A3-01 | 祝小满 | `characters/important/chr-a3-01-zhu-xiaoman.md` |
| CHR-A3-02 | 李观澜 | `characters/important/chr-a3-02-li-guanlan.md` |
| CHR-A3-03 | 江酌月 | `characters/important/chr-a3-03-jiang-zhuoyue.md` |
| CHR-A3-04 | 唐绮／阿绮 | `characters/important/chr-a3-04-tang-qi.md` |
| CHR-A3-05 | 段星河 | `characters/important/chr-a3-05-duan-xinghe.md` |
| CHR-A3-06 | 丁小七 | `characters/important/chr-a3-06-ding-xiaoqi.md` |
| CHR-A3-07 | 赵十一娘 | `characters/important/chr-a3-07-zhao-shiyiniang.md` |
| CHR-A3-08 | 慧明 | `characters/important/chr-a3-08-huiming.md` |

- [ ] **Step 3: 锁定 B、U、BG 号码范围**

- B：`CHR-B-001`—`CHR-B-048`；其中 `CHR-B-008` 固定为崔满堂／崔老板，`CHR-B-019` 固定为孟小川／阿七；
- U：`CHR-U-001`—`CHR-U-120`；
- BG：`CHR-BG-001`—`CHR-BG-300`，后续只追加，不复用已退役号码。

- [ ] **Step 4: 运行 roster 验证并提交**

```powershell
python scripts/validate_characters.py --stage roster --strict
git add characters qa/character-roster.json
git commit -m "docs: lock Linan character roster and IDs"
```

Expected:

```text
PASS L1=5 L2=4 L3=3 A1=8 A2=8 A3=8 B=48 U=120
PASS stable_named_characters=84 reserved_unit_ids=120 future_named_total=204
PASS duplicate_ids=0 duplicate_aliases=0
```

## Task 3: 建立关系 ID、七维状态和非中央关系席位

**Files:**
- Create: `characters/05-relationships-and-state.md`
- Create: `characters/07-emotional-debts-and-contradictions.md`
- Create: `characters/relations/00-relationship-schema.md`
- Create: `characters/relations/00-relationship-index.md`
- Create: `characters/relations/01-noncentral-l-a-mesh.md`
- Create: `characters/relations/02-recurring-cross-system-mesh.md`
- Create: `characters/relations/03-unit-return-network.md`
- Create: `characters/relations/core/rel-001-shen-heng-gu-xingzhou.md`
- Create: `characters/relations/core/rel-002-liu-shisi-zhou-yanzhi.md`
- Create: `characters/relations/core/rel-003-shen-heng-liu-shisi.md`
- Create: `characters/relations/core/rel-004-pei-jiuniang-gu-xingzhou.md`
- Create: `characters/relations/core/rel-005-shen-heng-lu-qinghe.md`
- Create: `characters/relations/core/rel-006-shen-heng-shen-huaichuan.md`
- Create: `characters/relations/core/rel-007-lu-qinghe-shen-huaichuan.md`
- Create: `characters/relations/core/rel-008-shen-sanniang-lin-ayuan.md`
- Create: `characters/relations/core/rel-009-li-jianshan-li-lingyi.md`
- Create: `characters/relations/core/rel-010-yu-zhongren-yu-qinghe.md`
- Create: `characters/relations/core/rel-011-cheng-yelao-zhou-yanzhi.md`
- Create: `characters/relations/core/rel-012-gao-wen-gu-xingzhou.md`
- Create: `characters/relations/core/rel-013-gu-xingzhou-cao-su.md`
- Create: `characters/relations/core/rel-014-gao-wen-cao-su.md`
- Create: `characters/relations/core/rel-015-zhang-yunzhong-song-weijing.md`
- Create: `characters/relations/core/rel-016-helan-du-xu-hanzhang.md`
- Create: `characters/relations/core/rel-g01-five-signal-group.md`
- Create: `qa/character-state-matrix.md`
- Create: `qa/episode-coverage-matrix.json`
- Create: `qa/episode-coverage-matrix.md`
- Create: `qa/relationship-seven-dimension-matrix.md`

- [ ] **Step 1: 定义不可合并的七个关系维度**

每条 `REL` 分别记录亲近、信任、亏欠、依赖、敬意、怨恨、共同秘密，强度为 0—4；不得求总分。每一数值都附剧情证据，每一方向都记录表面行为、自觉动机、未承认动机、情感债务。

- [ ] **Step 2: 预留八个状态快照**

`Y0-OPEN`、`ARC1-END`、`ARC2-END`、`ARC3-END`、`ARC4-END`、`ARC5-END`、`ARC6-END`、`Y+1`。`Y-13` 作为人物史事实，不计入八个当季关系快照；人物档案另有 `ENDING` 独有结局检查点，关系档案只在其改变七维关系时把证据附入 `ARC6-END` 或 `Y+1`，因此关系快照仍为八个。

- [ ] **Step 3: 预建 16 对核心关系及一个群体关系的独立骨架文件；此时只锁 ID、双方、Y0 基线、关联档案和后续快照字段，不伪装为八快照成品**

```text
REL-001 沈蘅—顾行舟
REL-002 柳十四—周砚之
REL-003 沈蘅—柳十四
REL-004 裴九娘—顾行舟
REL-005 沈蘅—陆清和
REL-006 沈蘅—沈怀川
REL-007 陆清和—沈怀川
REL-008 沈三娘—林阿沅
REL-009 黎见山—黎令仪
REL-010 余仲仁—余青禾
REL-011 程野老—周砚之
REL-012 高问—顾行舟
REL-013 顾行舟—曹肃
REL-014 高问—曹肃
REL-015 章允中—宋惟敬
REL-016 贺兰度—许含章
REL-G01 五信协作群
```

- [ ] **Step 4: 预分配非中央关系度数**

- 36 名 L/A 人物每人至少两条对方不是 L1—L3 的关系；
- 48 名 B 每人至少两条非主线关系，至少一条跨生活圈；
- 同一人物对只使用一个 `REL` ID；
- U 回访网络预留至少 40 个席位。

`qa/episode-coverage-matrix.json` 保存机器可读席位，`qa/episode-coverage-matrix.md` 只能由 JSON 生成，人物档案不得另写一套覆盖数字。

- [ ] **Step 5: 验证并提交**

```powershell
python scripts/validate_characters.py --stage relationship-slots --strict
git add characters/05-relationships-and-state.md characters/07-emotional-debts-and-contradictions.md characters/relations qa/character-state-matrix.md qa/episode-coverage-matrix.json qa/episode-coverage-matrix.md qa/relationship-seven-dimension-matrix.md
git commit -m "docs: establish Linan relationship graph"
```

Expected: 17 个核心关系骨架唯一；L/A 与 B 关系度数预留全部合格；未完成快照被识别为合法预留而非成品。

## Tasks 4–15: 完成 12 名中央人物独立档案

每一行是一个独立任务和独立提交。写作前读取规格第 4.4、6.2、6.6、6.7 与第 9 节及 Task 3 已建立的关联 `REL` 骨架；完成后单独运行 Profile 验证。

| Task | ID | 人物文件 | POV | 必须证明的选择链 | Commit |
|---:|---|---|---:|---|---|
| 4 | CHR-L1-01 | `characters/central/chr-l1-01-shen-heng.md` | 52 | 放弃证明父亲完全正确，公开其错误记录，并建立允许纠错的春信屋 | `characters: define Shen Heng` |
| 5 | CHR-L1-02 | `characters/central/chr-l1-02-liu-shisi-liu-wangshu.md` | 44 | 放弃头牌身份、收入与庇护，以本名承担真实讲述 | `characters: define Liu Shisi` |
| 6 | CHR-L1-03 | `characters/central/chr-l1-03-zhou-yanzhi.md` | 42 | 放弃画院前程，公开可能被视为泄防的民用图 | `characters: define Zhou Yanzhi` |
| 7 | CHR-L1-04 | `characters/central/chr-l1-04-pei-jiuniang.md` | 46 | 将原信存入受保护私情簿，放弃即时清白以保护幸存者 | `characters: define Pei Jiuniang` |
| 8 | CHR-L1-05 | `characters/central/chr-l1-05-gu-xingzhou.md` | 46 | 公开旧身份与完整风险，停止以保护替别人决定 | `characters: define Gu Xingzhou` |
| 9 | CHR-L2-01 | `characters/central/chr-l2-01-lu-qinghe.md` | 30 | 交出香匣和丈夫错误，承受信誉损失并放手让女儿选择 | `characters: define Lu Qinghe` |
| 10 | CHR-L2-02 | `characters/central/chr-l2-02-lin-ayuan.md` | 28 | 放弃安全撤离位置，建立失联名册并承担街坊生计 | `characters: define Lin Ayuan` |
| 11 | CHR-L2-03 | `characters/central/chr-l2-03-yu-qinghe.md` | 26 | 公开病例、失去医局荐书，却保住专业判断证据 | `characters: define Yu Qinghe` |
| 12 | CHR-L2-04 | `characters/central/chr-l2-04-gao-wen.md` | 24 | 穿官服反签开路，失去官职且不以此免除先前执行封锁的责任 | `characters: define Gao Wen` |
| 13 | CHR-L3-01 | `characters/central/chr-l3-01-song-weijing.md` | 28 | 公开真实数据、撤回封锁建议、促成两署改令并交权受审 | `characters: define Song Weijing` |
| 14 | CHR-L3-02 | `characters/central/chr-l3-02-li-jianshan.md` | 24 | 公开第三仓与真账保住供应，同时坐实罪责、失去商业帝国 | `characters: define Li Jianshan` |
| 15 | CHR-L3-03 | `characters/central/chr-l3-03-helan-du.md` | 20 | 放弃政治时机和地下网络，先救自己原想代表的流民 | `characters: define Helan Du` |

每项固定执行：

- [ ] **Step 1: 写满 Schema 的全部字段和七个坚守问题**
- [ ] **Step 2: 为六篇各写“目标—误判—选择—代价—关系变化—状态移交”**
- [ ] **Step 3: 写至少两条非中央关系和一个不依赖台词的关心动作**
- [ ] **Step 4: 明确能力边界，禁止隐藏血统、突然武力升级或反派洗白**
- [ ] **Step 5: 使用本任务行的精确 ID 运行 `python scripts/validate_characters.py --stage profile --character-id ID --strict`，只暂存该行人物文件并使用该行 Commit 文本提交；关联 REL 骨架和共享状态矩阵只读，关系与状态提案写在人物档案的“待集成人同步”区，由 Task 22 的集成人统一落盘**

Expected: `required_fields=complete guard_answers=7/7 profile_state_checkpoints=10/10 history=1 season_future=9 relationship_snapshots=8 noncentral_relations>=2`。

## Task 16: 完成 8 名 A1 一级重要人物

**Files:**
- Create: `characters/important/chr-a1-01-shen-sanniang.md`
- Create: `characters/important/chr-a1-02-zhou-boan.md`
- Create: `characters/important/chr-a1-03-yu-zhongren.md`
- Create: `characters/important/chr-a1-04-gu-nianniang.md`
- Create: `characters/important/chr-a1-05-xu-hanzhang.md`
- Create: `characters/important/chr-a1-06-zhang-yunzhong.md`
- Create: `characters/important/chr-a1-07-li-lingyi.md`
- Create: `characters/important/chr-a1-08-cao-su.md`

- [ ] **Step 1: 按下表逐人写档案，每人 10 个 POV、至少 12 集覆盖、至少四篇出现**

| 人物 | 独立副线 | 终局不可替代行动 |
|---|---|---|
| 沈三娘 | 热饭、母女控制与放手、街坊赊账 | 放弃母女安全撤离，组织公共灶并把账簿交给阿沅 |
| 周伯安 | 旧春信恐惧、伞骨编码、重启责任 | 公开旧规失误，搭建灯架与可纠错的街巷信号 |
| 余仲仁 | 医者尺度、老去焦虑、师徒决裂 | 交药柜钥匙给青禾，但不能替她拿回已失前程 |
| 顾念娘 | 非血缘家庭、债契与演员生计 | 解除旧契、让艺人自行决定是否上街传信 |
| 许含章 | 保存流民姓名、温和赈济、与贺兰度相爱护相反对 | 接管名册、拒绝替贺兰度求情但不抛弃流民 |
| 章允中 | 程序忠诚、局部知情、盖章责任 | 公开完整签押链，证明选择性呈报如何形成命令 |
| 黎令仪 | 养育恩债、账房能力、揭露义父 | 复制并交出真账，爱养父却不替其选择辩护 |
| 曹肃 | 守门职责、旧同袍、军令边界 | 依据改令实际开门并带所部救灾，接受军法审查 |

- [ ] **Step 2: 每完成一人即运行 Profile 验证并单独提交**

```powershell
python scripts/validate_characters.py --stage profile --character-id CHR-A1-01 --strict
```

依次验证至 `CHR-A1-08`；八次提交信息固定为 `characters: define Shen Sanniang`、`Zhou Boan`、`Yu Zhongren`、`Gu Nianniang`、`Xu Hanzhang`、`Zhang Yunzhong`、`Li Lingyi`、`Cao Su`。

- [ ] **Step 3: 验证 A1 汇总**

```powershell
python scripts/validate_characters.py --stage important --strict
```

Expected: `A1=8 pov=80 coverage_reservations>=96 arcs_per_character>=4`。

## Task 17: 完成 8 名 A2 二级重要人物

**Files:**
- Create: `characters/important/chr-a2-01-chen-guipo.md`
- Create: `characters/important/chr-a2-02-song-shijiu.md`
- Create: `characters/important/chr-a2-03-shen-huaichuan.md`
- Create: `characters/important/chr-a2-04-he-jiu.md`
- Create: `characters/important/chr-a2-05-shi-liu.md`
- Create: `characters/important/chr-a2-06-luo-jianchao.md`
- Create: `characters/important/chr-a2-07-cheng-yelao.md`
- Create: `characters/important/chr-a2-08-fang-shuniang.md`

- [ ] **Step 1: 按职业知识与三阶段小弧线逐人完成档案**

| 人物 | 职业知识 | 必须成立的选择 |
|---|---|---|
| 陈桂婆 | 衣物泥、血、烟、香、油痕；独居者习惯 | 冒险寻找无人登记的独居老人，不等主角命令 |
| 宋十九 | 巷道、跑腿信用、孤儿生存 | 拒送未经核验的恐慌消息，哪怕失去最大一笔钱 |
| 沈怀川 | 香药、旧春信、Y-13 证据 | 六次 POV 只能由已认证来源触发，必须区分事实与当代理解 |
| 贺九 | 鱼种、水温、水质 | 放弃鱼货与生计窗口，先报污染并带渔民救人 |
| 石六 | 不识字的计数、装卸、码头节奏 | 用劳动记忆揭穿假货单，承担被行会排斥 |
| 罗见潮 | 船行调度、风险与船工家庭 | 调出全部船救人，承受损船和债务而非突然发财 |
| 程野老 | 绘画、名声、师徒成全 | 在民用图旁落印共担指控，不用一句和解抹平旧伤 |
| 方书娘 | 纸墨、雕版、书坊经营 | 暂停盈利刻印公开指引，并建立更正版本制度 |

- [ ] **Step 2: 每人写 6 个 POV 预算、至少 8 集覆盖和至少两篇跨度**
- [ ] **Step 3: 每人单独验证、单独提交**
- [ ] **Step 4: 特别运行沈怀川限知重建检查**

```powershell
python scripts/validate_characters.py --stage profile --character-id CHR-A2-03 --strict
```

Expected: `sourced_reconstructions=6 omniscient_flashbacks=0`。

## Task 18: 完成 8 名 A3 三级重要人物

**Files:**
- Create: `characters/important/chr-a3-01-zhu-xiaoman.md`
- Create: `characters/important/chr-a3-02-li-guanlan.md`
- Create: `characters/important/chr-a3-03-jiang-zhuoyue.md`
- Create: `characters/important/chr-a3-04-tang-qi.md`
- Create: `characters/important/chr-a3-05-duan-xinghe.md`
- Create: `characters/important/chr-a3-06-ding-xiaoqi.md`
- Create: `characters/important/chr-a3-07-zhao-shiyiniang.md`
- Create: `characters/important/chr-a3-08-huiming.md`

- [ ] **Step 1: 每人完成 2 个不同母集 POV、至少 4 集覆盖及一次职业回响**

| 人物 | 日常记忆点 | 危机选择／职业回响 |
|---|---|---|
| 祝小满 | 攒钱买簪、花价与年轻女孩友情 | 用花色做路标，同时承认自己也会怕、会想先保住簪子 |
| 李观澜 | 把新闻改成故事、胆小贫嘴 | 先公开更正自己的误传，再用声音发布通路信息 |
| 江酌月 | 琵琶节拍、安静友情、声音创伤 | 在无法演奏时用敲击信号接续曲信 |
| 唐绮／阿绮 | 妆造劳动、台前体面、卸妆后的照料 | 放弃珍贵妆料处理伤口并记录失散艺人 |
| 段星河 | 落榜、文人优越与羞耻 | 从轻视刻工到亲手抄写救灾告示，不获得功名补偿 |
| 丁小七 | 酒肆喜剧、赊账、普通胆怯 | 明知害怕仍守后门与热水，不突然变成武林高手 |
| 赵十一娘 | 客籍隐私、房钱与世故 | 开放客房安置流民，同时保护住客名册不被滥用 |
| 慧明 | 柴米账、床位和施粥秩序 | 开仓并坚持可核验公平，不以慈悲台词替代分配工作 |

- [ ] **Step 2: 每人单独验证、单独提交**
- [ ] **Step 3: 汇总验证 A2/A3**

```powershell
python scripts/validate_characters.py --stage important --strict
```

Expected: `A2=8 pov=48`、`A3=8 pov=16`，24 名 A 全部有两条非中央关系。

## Task 19: 完成 48 名 B 级市井常驻人物

**Files:**
- Create: `characters/recurring/chr-b-001-007-he-ming-lane-and-aromatics.md`
- Create: `characters/recurring/chr-b-008-013-spring-stage-and-night-market.md`
- Create: `characters/recurring/chr-b-014-018-xiling-books-and-painting.md`
- Create: `characters/recurring/chr-b-019-025-qiantang-docks-and-canal.md`
- Create: `characters/recurring/chr-b-026-030-tavern-guesthouse-and-travelers.md`
- Create: `characters/recurring/chr-b-031-036-government-city-and-military.md`
- Create: `characters/recurring/chr-b-037-042-clinic-temple-and-relief.md`
- Create: `characters/recurring/chr-b-043-048-huichuan-north-return-and-warehouses.md`

- [ ] **Step 1: 每卷逐人锁定姓名、年龄、职业、住处、经济压力、日常愿望、所守之物、错误与关键选择**
- [ ] **Step 2: 每人写七个坚守问题的简版答案、两条非主线关系和一个危机职业回响**
- [ ] **Step 3: 锁定 POV 分布**

48 人每人一个首要 POV；以下 24 人再得一个：

```text
CHR-B-001、CHR-B-002、CHR-B-003、CHR-B-004、CHR-B-008、CHR-B-009、
CHR-B-010、CHR-B-014、CHR-B-015、CHR-B-019、CHR-B-020、CHR-B-021、
CHR-B-025、CHR-B-026、CHR-B-027、CHR-B-031、CHR-B-032、CHR-B-037、
CHR-B-038、CHR-B-040、CHR-B-043、CHR-B-044、CHR-B-045、CHR-B-046
```

这 24 人每人必须填写 `second_pov_reason`、`arc_responsibility`、`indispensable_choice` 与 `why_one_pov_is_insufficient`；Foundation Gate 验证理由和篇章责任，Season Gate 再绑定具体母集与微章，禁止只因人气、场景方便或数字凑配额获得第二 POV。

- [ ] **Step 4: 为每人预留至少两集：E01—E18 至少一次可独立成立的日常状态，E31—E36 至少一次由自身职业能力产生的危机回响；两次都必须是 `P/A/R/D` 有效覆盖，且至少一次不为中央人物递线索**
- [ ] **Step 5: 每卷单独验证和提交，最后运行汇总**

```powershell
python scripts/validate_characters.py --stage recurring --strict
```

Expected:

```text
PASS recurring=48 distribution=7,6,5,7,5,6,6,6
PASS pov_total=72 second_pov_characters=24
PASS guard_lines=48/48 nonmain_relations>=2 characters=48/48
PASS early_daily_state=48/48 final_professional_echo=48/48
```

## Task 20: 分配 120 个 U 级单元人物席位

**Files:**
- Create: `characters/unit/slots/01-life-visitors-u001-u030.md`
- Create: `characters/unit/slots/02-professional-problems-u031-u060.md`
- Create: `characters/unit/slots/03-crisis-bearers-u061-u090.md`
- Create: `characters/unit/slots/04-moral-choice-triggers-u091-u120.md`

- [ ] **Step 1: 为每个席位锁定 ID、用途类别、生活圈、建议篇章窗口、非中央关系席位，并按主动性、风险、不可逆后果和主题独特性记录 POV 候选理由**
- [ ] **Step 2: 建立 `U-POV-SLOT-01`—`U-POV-SLOT-22` 共 22 个未绑定人物的预算槽；四类各保留至少 11 名候选，共形成不少于 44 人的候选池，Foundation Gate 不得提前把槽位硬绑给前 22 个 ID**
- [ ] **Step 3: 标出至少 40 个自然回访候选，回访理由必须是工作、消费、债务、照料或邻里关系**
- [ ] **Step 4: 验证并提交**

```powershell
python scripts/validate_characters.py --stage unit-slots --strict
git add characters/unit
git commit -m "characters: allocate 120 unit character slots"
```

Expected: 四类各 30；未绑定 POV 预算槽 22；候选池至少 44 且四类各至少 11；回访候选至少 40。

## Task 21: 完成 300 个 BG 背景人口原型

**Files:**
- Create: `characters/background/chr-bg-001-020-aromatics-and-medicine.md`
- Create: `characters/background/chr-bg-021-040-street-food-and-neighborhood.md`
- Create: `characters/background/chr-bg-041-060-spring-stage-front-of-house.md`
- Create: `characters/background/chr-bg-061-080-backstage-and-night-market.md`
- Create: `characters/background/chr-bg-081-100-books-painting-and-printing.md`
- Create: `characters/background/chr-bg-101-120-docks-and-porters.md`
- Create: `characters/background/chr-bg-121-140-boats-fishing-and-water-dwellers.md`
- Create: `characters/background/chr-bg-141-160-tavern-guesthouse-and-travel.md`
- Create: `characters/background/chr-bg-161-180-government-clerks-and-runners.md`
- Create: `characters/background/chr-bg-181-200-soldiers-and-city-gates.md`
- Create: `characters/background/chr-bg-201-220-trade-warehouses-and-haulage.md`
- Create: `characters/background/chr-bg-221-240-temple-and-relief.md`
- Create: `characters/background/chr-bg-241-260-northern-guests-and-refugees.md`
- Create: `characters/background/chr-bg-261-280-household-care-and-women-workers.md`
- Create: `characters/background/chr-bg-281-300-festivals-and-public-spaces.md`
- Create: `qa/background-usage.json`

- [ ] **Step 1: 每个条目写满十维字段**

`年龄段｜职业｜阶层｜地域｜家庭状态｜活动时辰｜服装材质｜所在地点｜正在做的劳动/消费/等待/照料/争执｜可自然互动对象`

每个 `CHR-BG-###` 另写 `eligible_location_ids`、`eligible_time_windows`、`eligible_work_states`；`qa/background-usage.json` 为 300 个 ID 建立空的 `microchapter_ids` 与 `extension_ids`，后续只由剧情与扩展计划写入实际使用，不得用“可使用”冒充“已出场”。

- [ ] **Step 2: 检查同一场景的阶层、性别、年龄和劳动状态不整齐同质化**
- [ ] **Step 3: 每卷 20 人，逐卷提交；最后验证**

```powershell
python scripts/validate_characters.py --stage background --strict
```

Expected: `background_prototypes=300 ecosystems=15 eligibility_complete=300/300 usage_slots_initialized=300 static_decoration_records=0`。

## Task 22: 写完 17 个核心关系档案

**Files:**
- Modify: `characters/relations/core/rel-001-shen-heng-gu-xingzhou.md`
- Modify: `characters/relations/core/rel-002-liu-shisi-zhou-yanzhi.md`
- Modify: `characters/relations/core/rel-003-shen-heng-liu-shisi.md`
- Modify: `characters/relations/core/rel-004-pei-jiuniang-gu-xingzhou.md`
- Modify: `characters/relations/core/rel-005-shen-heng-lu-qinghe.md`
- Modify: `characters/relations/core/rel-006-shen-heng-shen-huaichuan.md`
- Modify: `characters/relations/core/rel-007-lu-qinghe-shen-huaichuan.md`
- Modify: `characters/relations/core/rel-008-shen-sanniang-lin-ayuan.md`
- Modify: `characters/relations/core/rel-009-li-jianshan-li-lingyi.md`
- Modify: `characters/relations/core/rel-010-yu-zhongren-yu-qinghe.md`
- Modify: `characters/relations/core/rel-011-cheng-yelao-zhou-yanzhi.md`
- Modify: `characters/relations/core/rel-012-gao-wen-gu-xingzhou.md`
- Modify: `characters/relations/core/rel-013-gu-xingzhou-cao-su.md`
- Modify: `characters/relations/core/rel-014-gao-wen-cao-su.md`
- Modify: `characters/relations/core/rel-015-zhang-yunzhong-song-weijing.md`
- Modify: `characters/relations/core/rel-016-helan-du-xu-hanzhang.md`
- Modify: `characters/relations/core/rel-g01-five-signal-group.md`
- Modify: `qa/relationship-seven-dimension-matrix.md`

- [ ] **Step 1: 每条关系写双向四层动机、七维八快照及每次变化的剧情证据**
- [ ] **Step 2: 每条至少包含一次两种相反感情同时为真的场面**
- [ ] **Step 3: 禁止用一次道歉恢复全部信任；修复与原谅必须分开记录**
- [ ] **Step 4: 从 17 个 REL 权威文件重新生成七维矩阵，验证并提交；矩阵是只读视图，不得反向改写 REL 事实**

```powershell
python scripts/validate_characters.py --stage relationships --write-generated-views --strict
git add characters/relations/core qa/relationship-seven-dimension-matrix.md
git commit -m "characters: complete core relationship states"
```

Expected: `anchor_pairs=16 group_relations=1 dimensions=7 snapshots=8 duplicate_pairs=0`。

## Task 23: 完成六条情感脊柱

**Files:**
- Create: `characters/06-values-sacrifices-and-emotional-arcs.md`
- Create: `characters/emotional-spines/00-emotional-spines-index.md`
- Create: `characters/emotional-spines/01-love.md`
- Create: `characters/emotional-spines/02-friendship.md`
- Create: `characters/emotional-spines/03-family.md`
- Create: `characters/emotional-spines/04-mentorship.md`
- Create: `characters/emotional-spines/05-comrades-and-institutions.md`
- Create: `characters/emotional-spines/06-ideal-community.md`

- [ ] **Step 1: 爱情引用 REL-001、REL-002；友情引用 REL-003、REL-004、REL-G01**
- [ ] **Step 2: 亲情引用 REL-005—009；师徒引用 REL-010、REL-011**
- [ ] **Step 3: 同袍制度引用 REL-012—015；理想共同体引用 REL-009、REL-015、REL-016**
- [ ] **Step 4: 每条脊柱写六篇状态变化，共 36 个稳定 `EM-A##-{SPINE}` 语义锚点；每格包含关系 ID、双重情感、七维前后目标、选择、代价和余波，但不在此阶段虚构母集或微章绑定**
- [ ] **Step 5: 验证并提交**

```powershell
python scripts/validate_characters.py --stage emotional-spines --strict
git add characters/emotional-spines characters/06-values-sacrifices-and-emotional-arcs.md
git commit -m "characters: lock six emotional spines"
```

Expected: `emotional_spines=6 arc_state_changes=36/36 unearned_perfect_reconciliations=0`。

## Task 24: 锁定 Character Foundation Gate

**Files:**
- Modify: `characters/00-character-index.md`
- Modify: `qa/character-state-matrix.md`
- Modify: `qa/background-usage.json`
- Modify: `qa/episode-coverage-matrix.json`
- Modify: `qa/episode-coverage-matrix.md`
- Modify: `qa/production-status.json`
- Create: `qa/gates/scope-definitions/character-foundation.json`
- Create: `qa/gates/input-manifests/character-foundation.json`
- Create: `qa/gates/character-foundation-gate.json`
- Create: `qa/reviews/character-foundation-canon-review.md`
- Create: `qa/reviews/character-foundation-narrative-review.md`

- [ ] **Step 1: 运行全部人物基础验证**

```powershell
python scripts/validate_characters.py --stage foundation --strict
python scripts/validate_project.py --scope character-foundation --strict
python scripts/lock_gate.py --gate character-foundation --scope character-foundation --prepare
```

Expected:

```text
PASS stable_characters=84 unit_slots=120 background_prototypes=300
PASS central_pov=410 important_pov=144 recurring_pov=72 reserved_unit_pov=22
PASS relationships=complete emotional_spines=36/36
```

Foundation Gate 只冻结稳定 ID、档位、数量、个人 POV 总预算、U 类别/候选/预算槽、BG 适用范围及关系语义。`qa/gates/scope-definitions/character-foundation.json` 对人物档案与 REL 语义做整文件/稳定 region 哈希，对混合 QA 文件只投影这些冻结字段。`suggested_arc`、实际母集/微章、U 实际 POV 绑定、覆盖格和 BG 使用次数均保持 `RESERVED`，分别由 Season/Episode Gate 在各自 QA 权威文件中落成；这些声明过的 `RESERVED → ACTUAL` 转换不构成 Canon 改写，也不得修改已锁人物事实。

- [ ] **Step 2: Canon 审读者检查年龄、时间、职业、官署权限、地理和物件，并在审读文件 TOML 头签署准备步骤输出的输入清单哈希**
- [ ] **Step 3: 人物审读者检查坚守、真实缺点、非中央关系、牺牲前置与独立结局，由另一 reviewer ID 签署同一输入哈希**
- [ ] **Step 4: 修正意见后必须重新验证、重新 `--prepare` 并更新两份签署；只有 `lock_gate.py` 可以写入 `LOCKED`**
- [ ] **Step 5: 提交**

```powershell
git diff --check
python scripts/lock_gate.py --gate character-foundation --scope character-foundation --lock --review qa/reviews/character-foundation-canon-review.md --review qa/reviews/character-foundation-narrative-review.md
python scripts/validate_project.py --scope character-foundation --strict
git add characters qa
git commit -m "qa: lock Linan character foundation"
```

## Task 25: 在 Episode Gate 后完成 120 名 U 级最终档案

**Files:**
- Read: `qa/unit-selection.json`
- Read: `qa/episode-coverage-matrix.json`
- Modify: `qa/character-roster.json`
- Create: `characters/unit/profiles/chr-u-001-010.md`
- Create: `characters/unit/profiles/chr-u-011-020.md`
- Create: `characters/unit/profiles/chr-u-021-030.md`
- Create: `characters/unit/profiles/chr-u-031-040.md`
- Create: `characters/unit/profiles/chr-u-041-050.md`
- Create: `characters/unit/profiles/chr-u-051-060.md`
- Create: `characters/unit/profiles/chr-u-061-070.md`
- Create: `characters/unit/profiles/chr-u-071-080.md`
- Create: `characters/unit/profiles/chr-u-081-090.md`
- Create: `characters/unit/profiles/chr-u-091-100.md`
- Create: `characters/unit/profiles/chr-u-101-110.md`
- Create: `characters/unit/profiles/chr-u-111-120.md`
- Modify: `characters/relations/03-unit-return-network.md`

- [ ] **Step 1: 确认 Episode Gate 已锁**

```powershell
python scripts/validate_project.py --scope episodes --strict
```

- [ ] **Step 2: 将 Season Gate 已锁的 120 个姓名、职业、住处与非主角关系逐项无变更写入 `qa/character-roster.json` 和最终档案，再补全当集愿望、所守之物、压力选择和余波；若身份需要改变，必须先退回 Season Gate 走变更记录**
- [ ] **Step 3: 将实际 22 名独占 POV 与微章 ID 写回档案；不得重复或临时增加**
- [ ] **Step 4: 将至少 40 人的自然回访集号、身份连续性和新状态写入关系网**
- [ ] **Step 5: 每卷十人验证并单独提交**

```powershell
python scripts/validate_characters.py --stage unit-final --strict
```

Expected: `unit_profiles=120 unit_pov=22 natural_returns>=40 autonomous_choices=120/120`。

## Task 26: 锁定 Character Final Gate

**Files:**
- Read: `qa/episode-coverage-matrix.json`
- Read: `qa/episode-coverage-matrix.md`
- Read: `qa/character-state-matrix.md`
- Read: `qa/background-usage.json`
- Modify: `qa/production-status.json`
- Create: `qa/gates/scope-definitions/character-final.json`
- Create: `qa/gates/input-manifests/character-final.json`
- Create: `qa/gates/character-final-gate.json`
- Create: `qa/reviews/character-final-canon-review.md`
- Create: `qa/reviews/character-final-narrative-review.md`

- [ ] **Step 1: 对照 648 章核实个人 POV 和实际母集覆盖，不接受只有预留没有正文的席位**
- [ ] **Step 1A: 本任务只读 Episode Gate 已冻结的覆盖、状态与 BG 正篇使用数据；若发现需修正，必须先撤回并重锁 Episode Gate，禁止在 Character Final 阶段反向改写**
- [ ] **Step 2: 验证 L1/L2/L3 不连续四集无状态更新；A/B 不只作为提名或背景出现**
- [ ] **Step 3: 验证 120 名 U 每人至少有一个实际 `P/A/R/D` 事件锚点；至少 40 人在首次事件之后的另一母集自然回场，不能以扩展卡代替正篇回场**
- [ ] **Step 4: 对照 `qa/background-usage.json` 验证 300 个 BG 均可用，正篇实际使用至少 180 个不同原型；每次使用的地点、时辰、劳动状态均落在原型允许范围，单个原型不得跨互斥职业充当万能人群**
- [ ] **Step 5: 验证 204 名命名人物无孤立节点、无档位漂移、无别名冲突**
- [ ] **Step 5A: `qa/gates/scope-definitions/character-final.json` 冻结 204 份命名人物事实、U 正篇事件/回场、正篇 POV 与 BG `microchapter_ids`；扩展阶段才会填的 BG `extension_ids` 保持 `RESERVED`，不进入本 Gate 投影**
- [ ] **Step 6: 完成人物与 Canon 双审读；先运行 `python scripts/lock_gate.py --gate character-final --scope characters --prepare`，两名不同审读者在 TOML 头签署同一输入清单哈希；任何修正后都须重新准备和签署**
- [ ] **Step 7: 只通过 Gate 工具锁定，执行最终验证和提交**

```powershell
python scripts/validate_characters.py --stage final --strict
python scripts/validate_project.py --scope characters --strict
python scripts/lock_gate.py --gate character-final --scope characters --lock --review qa/reviews/character-final-canon-review.md --review qa/reviews/character-final-narrative-review.md
python scripts/validate_project.py --scope characters --strict
git diff --check
git add characters qa
git commit -m "qa: lock complete Linan character bible"
```

Expected:

```text
PASS named_characters=204 background_prototypes=300
PASS POV=230/108/72/80/48/16/72/22 total=648
PASS unit_event_anchors=120/120 unit_returns>=40 background_used>=180
PASS emotional_spines=36/36 isolated_characters=0
PASS character_final_gate=LOCKED
```

## 并行纪律

- 可并行写不同独立人物档案，但公共索引、关系索引和状态矩阵只能由集成人维护；
- 同一人物与其核心关系档案不能由两个作者同时改；
- 关系事实以 `REL` 文件为准，人物档案只引用，不复制七维数值；
- U 级在 Episode Gate 前只能分配席位，不能声称最终人物已完成；
- 任何人物档位、个人 POV 总额或稳定 ID 变更必须新增 Canon 变更记录并重跑 Season/Episode Gate。
