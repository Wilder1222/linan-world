# 沈蘅第一季视觉资产覆盖 V1

本层建立在已完成的 30 张通用角色资产之上，补齐第一季六篇的连续妆造、核心证据和沈蘅关键剧情节点。Season Gate 锁定后完成第二次覆盖审计并补入 E24、E25、E31；新增 38 张，整个沈蘅包共 68 张正式源资产和 68 张 8K 成品。

## 当前完成状态

- 第一季新增源图：38 / 38
- 第一季新增 8K 成品：38 / 38
- E01–E36 覆盖：36 / 36
- 全包自动质检：通过
- Season Gate 锁定输入与当前人物源哈希全部纳入自动审计；Episode Gate 仍为 `OPEN`，正式逐场绑定后需再审计。

## 权威与状态

- 人物源：`characters/central/chr-l1-01-shen-heng.md`，状态 `FOUNDATION-LOCKED`。
- 季纲源：`story/00-series-outline.md`、`story/01-causal-mystery-and-pacing-revision-v2.md`，状态 `FOUNDATION-DRAFT`。
- 锁定季级源：`story/season/season-causal-ledger.json`、`mystery-reversal-matrix.json`、`song-life-activity-matrix.json`、`humor-register-matrix.json`、`short-chapter-hook-map.json`、`u-candidate-selection.json`。
- 当前 `season_gate` 为 `LOCKED`、`episode_gate` 为 `OPEN`。本资产层已满足季级角色资产范围，不冒充 Episode Gate 后的逐场成片资产。
- 精确来源哈希、参考图角色和逐集映射保存在 `season-1-coverage-plan.json`。

## 新增资产类型

### 7 张篇章外观状态

- A01：惊蛰—春分，香铺与物证调查
- A02：清明—谷雨，西湖雨季与旧案调查
- A03：立夏—夏至，码头、井水与合报现场核验
- A04：白露—秋分，桂香普通生活与旧稿重读
- A05：立冬—大雪，冬疫、封锁与雪夜断信
- A06-FLOOD：冬至—灾中，暴雨救援与春灯协作
- A06-ENDING：灾后春分，春信屋和公共更正簿

### 6 张篇章核心证据板

每篇一张，无人物，分别锁定物证、旧案隐私、供应与水情合报、桂香与父亲手稿、封控疫图、春灯与更正规则。

### 25 张关键剧情剧照

覆盖 E01、E02、E03、E04、E05、E06、E07、E10、E11、E12、E13、E15、E18、E19、E23、E24、E25、E29、E30、E31、E32、E33、E35，以及 E36 的春信屋建立和“今日柳绿”终镜两张。

## 36 集覆盖规则

- 每集至少绑定一张篇章外观状态和一张篇章证据板。
- 当前季纲明确出现沈蘅关键选择，或微章草案分配沈蘅 POV 的集数，额外绑定独立剧情剧照。
- E14 只出现“账页尚未交给沈蘅”，不把她伪造进该场；E08–E09、E16–E17、E20–E22、E24–E28、E31、E34 保持篇章连续性覆盖，不虚构未写明的关键动作。
- 所有剧情剧照只锁沈蘅单人表演；其他角色待各自身份母版完成后再进入双人/群像资产，避免同脸或错误身份。

## 完成判据

1. `season-1-coverage-plan.json` 中 38 个新增 ID 均存在独立源 PNG。
2. 每个新增 ID 均存在长边 7680 px 的正式 PNG。
3. 36 集均有外观与证据覆盖，关键沈蘅集均有剧情覆盖。
4. 全包清单记录 68 个正式资产、尺寸、路径和 SHA-256。
5. 不存在 `.partial` 文件；项目单元测试和 manifest 严格校验通过。
6. Season Gate、锁定输入清单、人物源和季级矩阵哈希必须全部与当前工程一致；Episode Gate 锁定后重新审计逐场绑定。
