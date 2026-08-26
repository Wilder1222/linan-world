# MJ-S1-COVERAGE｜第一季 MJ 提示词覆盖矩阵

> 本文件记录“提示词是否已准备”，不等同于图像已生成或 Episode Gate 已通过。
> 第一季季纲覆盖：36 名具名角色、18 个 Canon 地点、6 篇证据系统；范围源为 `story/season/season-causal-ledger.json`。

## 覆盖摘要

| 资产家族 | 提示词卡数 | 当前图像状态 | 提示词来源 |
|---|---:|---|---|
| 风格母版探索 | 5 | 待人工选定 | `00-style-master-exploration.md` |
| 中央人物 | 12 | 沈蘅已有资产；其余待生成 | `01-central-character-prompts.md` |
| 季纲配角 | 24 | 待探索 | `02-supporting-character-prompts.md` |
| Canon 地点 | 18 | 待生成 | `03-canon-location-prompts.md` |
| 道具/证据 | 13 | 沈蘅既有证据图可复审；其余待生成 | `04-prop-evidence-prompts.md` |
| 沈蘅季级关键叙事 | 25 | 已有图像，可用 MJ 重建/扩展 | `05-season-narrative-prompts.md` |
| 核心关系 | 17 | 待各人物身份母版与 Episode Gate 绑定 | `07-relationship-prompt-templates.md` |
| U 槽位 / BG 生态 | 19 | 待 Episode Gate 绑定具体槽位 | `08-unit-background-prompt-templates.md` |
| **合计** | **133** | 提示词已覆盖；生成与 QA 另行追踪 | 本目录 |

## 资产清单 → 提示词 ID

### 风格与人物

- [x] `MJ-S1-STYLE-01`–`05`：五个独立风格母版探索任务。
- [x] `MJ-CHR-L1-01`、`MJ-CHR-L2-01`、`MJ-CHR-L1-05`、`MJ-CHR-L1-02`、`MJ-CHR-L1-03`、`MJ-CHR-L1-04`、`MJ-CHR-L2-02`、`MJ-CHR-L2-03`、`MJ-CHR-L2-04`、`MJ-CHR-L3-01`、`MJ-CHR-L3-02`、`MJ-CHR-L3-03`。
- [x] `MJ-CHR-A1-01`–`08`：八名 A1 配角。
- [x] `MJ-CHR-A2-03`–`08`：六名实际进入季纲的 A2 配角。
- [x] `MJ-CHR-A3-02`、`MJ-CHR-A3-03`：两名实际进入季纲的 A3 配角。
- [x] `MJ-CHR-B-001`、`014`、`018`、`019`、`021`、`031`、`045`、`046`：八名实际进入季纲的 B 级角色。
- [x] `MJ-U-ARC1-02`、`MJ-U-ARC2-03`、`MJ-U-ARC3-05`、`MJ-U-ARC4-06`：覆盖 120 个 U 槽位的四类绑定模板。
- [x] `MJ-BG-ECO-01`–`15`：覆盖 300 个 BG 原型的 15 个生态模板。
- [ ] `CHR-U-001`–`120` 与 `CHR-BG-001`–`300`：待 Episode Gate 绑定后才填入具体职业、地点、时段与身份参考；不提前创建独立英雄肖像。

### 地点与证据

- [x] `MJ-LOC-001`–`018`：每个 Canon 地点都有无人物母版与状态版模板。
- [x] `MJ-PROP-OBJ-001`、`MJ-PROP-CLU-001`：旧香匣与近期黏合物。
- [x] `MJ-PROP-A01`–`A06`：六篇证据板。
- [x] `MJ-PROP-KIT-01`–`05`：香铺、水路、官署仓储、春台书坊、医馆安置区工具包。

### 沈蘅季级关键叙事资产

- [x] `S1-NV-E01`、`E02`、`E03`、`E04`、`E05`、`E06`、`E07`。
- [x] `S1-NV-E10`、`E11`、`E12`、`E13`、`E15`、`E18`。
- [x] `S1-NV-E19`、`E23`、`E24`、`E25`、`E29`、`E30`。
- [x] `S1-NV-E31`、`E32`、`E33`、`E35`、`E36A`、`E36B`。

### 核心关系

- [x] `MJ-REL-001`–`016` 以及 `MJ-REL-G01`：17 条关系均有边界、物件、距离和光源明确的视觉提示词。
- [ ] 关系成片绑定：必须等待相关人物身份母版通过和 Episode Gate；当前提示词只做关系视觉探索，不替代正式分镜。

## 每类提示词的验收点

| 类别 | 必须通过 | 失败时最小修复 |
|---|---|---|
| 风格 | 有来源的光、材料可区分、城市生活尺度、非仙侠 | 只改光源或代表媒介，不改地点事实 |
| 人物 | 年龄/职业正确、脸与体态稳定、手有职业动作、服装合阶层 | 先修 `<CHAR_REF_URL>` 或身份描述，不用加重风格词 |
| 地点 | 构造、动线、通行瓶颈、工作面、物理光正确 | 只修空间或状态块，不更改 Canon 地理 |
| 道具 | 几何/材质/使用状态可辨、来源未混淆、无错误文字 | 分离物件或改状态，不把多物证硬拼成谜底 |
| 叙事 | 单一主动作、知识状态不越级、人物与地点/道具连续 | 修本镜的姿态/物件/位置，最终双人戏等待 Episode Gate |

## 生成批次与输出路径

| 批次 | 先决条件 | 输出建议 |
|---|---|---|
| MJ-B0 | 选定 `<STYLE_REF_URL>` | `production/assets/style/`；保留全部候选和人工选图记录 |
| MJ-B1 | 风格母版通过 | `production/assets/characters/<slug>/source/00-identity/` |
| MJ-B2 | 对应人物母版通过 | `production/assets/locations/<loc-id>/source/` 与 `production/assets/props/` |
| MJ-B3 | 人物/地点/道具皆通过 | 季节状态、单人叙事资产与可组合素材 |
| MJ-B4 | Episode Gate 锁定 | 双人、群像、最终剧照/视频参考资产 |

## 本轮的最小执行队列

1. `MJ-S1-STYLE-01`–`05`，从候选中锁定一个风格参考。
2. `MJ-CHR-L2-01`、`MJ-CHR-L1-05`、`MJ-CHR-L2-02`：先完成 E01 所需的三个新身份母版；沈蘅复用现有母版。
3. `MJ-LOC-001`、`002`、`009` 与 `MJ-PROP-OBJ-001`、`MJ-PROP-CLU-001`：建立 E01 的无人物地点和物证连续性。
4. 通过 B0 人工 QA 后，再展开 E01–E06 的中央人物、12 个首篇地点和 `MJ-PROP-A01`。
