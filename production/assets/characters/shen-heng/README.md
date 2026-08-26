# 沈蘅视觉资产包 V1

本目录保存《临安春信》沈蘅的可复用角色视觉资产。资产以用户提供的三张肖像为身份依据，采用“一种资产类型一张图”的方式组织，并同时保留生成源图与 8K 成品。

## 身份参考优先级

1. `references/ref-identity-primary-front.png`：绝对身份母版，脸型、眼距、眼型、鼻唇比例与整体年龄感以此为准。
2. `references/ref-identity-softlight-portrait.jpeg`：柔光和转角辅助证据。
3. `references/ref-identity-neutral-side-light.jpeg`：较中性的面部体积与侧向受光辅助证据。
4. `source/00-identity/ID-001-neutral-identity-master-v2.png`：由前三张反向建立的中性身份派生母版，服务于后续资产扩展，不覆盖原始肖像。

## 一致性锁点

- 22 岁成年东亚女性；柔和、略修长的鹅蛋偏心形脸，下颌自然收束。
- 暖棕色杏仁眼，外眼角轻微上扬；自然平直眉；窄而精致、鼻尖柔和的鼻型；低饱和桃珊瑚唇。
- 安静、敏锐、温柔但有韧性的调香师气质，不做幼态甜妹或网红脸。
- 深棕黑长发，宋韵半束发为主结构；额头干净，无额饰、花钿或垂坠。
- 浅雾蓝绣领、乳白层叠外袍、灰豆绿腰封；青玉水滴耳饰作为基础外观锚点。
- 轻薄有妆感，半哑光肤面、区域色调变化、由真实光源产生的克制高光；不采用统一磨皮或镜面肤质。

## 目录

| 路径 | 用途 |
|---|---|
| `references/` | 原始肖像及从 `raw/` 选出的造型、工作、剧情参考 |
| `source/00-identity/` | 4 张身份与结构源图 |
| `source/01-expression-makeup-hair/` | 4 张表情、妆容、发型发饰源图 |
| `source/02-costume/` | 10 张服装源图 |
| `source/03-pose-motion/` | 4 张姿态与动作源图 |
| `source/04-props/` | 2 张道具源图 |
| `source/05-narrative/` | 6 张基础镜头与剧情源图 |
| `source/06-season-1-appearance/` | 7 张第一季分弧妆造状态源图 |
| `source/07-season-1-evidence/` | 6 张第一季证据系统源图 |
| `source/08-season-1-narrative/` | 25 张第一季关键叙事源图 |
| `source/drafts/` | 被 V2 替换的早期版本，不参与正式清单 |
| `8k/00-identity/` | 身份与结构资产 |
| `8k/01-expression-makeup-hair/` | 表情、妆容、发型发饰资产 |
| `8k/02-costume/` | C01–C10 十套服装资产 |
| `8k/03-pose-motion/` | 姿态与动作资产 |
| `8k/04-props/` | 随身配饰与调香工具资产 |
| `8k/05-narrative/` | 镜头景别与剧情剧照资产 |
| `8k/06-season-1-appearance/` | 第一季分弧妆造状态 8K 成品 |
| `8k/07-season-1-evidence/` | 第一季证据系统 8K 成品 |
| `8k/08-season-1-narrative/` | 第一季关键叙事 8K 成品 |
| `season-1/` | E01–E36 资产覆盖计划、来源状态与映射 |
| `prompts/` | ImageGen 提示词基线与各资产差异项 |
| `qa/` | 像素、哈希与质检记录 |
| `scripts/` | 可复现的 8K 编译与清单工具 |

## 正式资产索引（68 张）

### 身份与结构（4）

- `ID-001-neutral-identity-master-v2`：中性正面身份母版
- `ID-002-five-angle-head-sheet`：正面、左右 3/4、左右严格侧面五角度头部板
- `ID-003-fullbody-turnaround`：全身正面、严格侧面、背面三视图
- `ID-004-physical-detail-board`：面部、头发、右手职业痕迹和服装材质细节板

### 表情、妆容与发型（4）

- `EX-001-expression-sheet-a`：九种基础与正向/克制情绪
- `EX-002-expression-sheet-b`：九种压力、负向与恢复情绪
- `MK-001-makeup-nine-grid`：九种同脸妆容状态
- `HR-001-hairstyle-ornament-nine-grid-v2`：九种同脸发型发饰状态

### 服装（10）

- `C01-daily-costume`：日常
- `C02-work-costume`：调香工作
- `C03-social-costume`：社交拜访
- `C04-formal-costume`：正式礼仪
- `C05-night-costume`：夜间行动
- `C06-rain-costume`：雨天
- `C07-winter-costume`：冬季
- `C08-injured-costume`：受伤状态，左前臂干净包扎
- `C09-long-labor-costume`：长时间劳作
- `C10-story-special-costume`：关键剧情特别造型

### 姿态与动作（4）

- `PS-001-foundational-pose-sheet`：九种基础站、坐、转身与重心姿态
- `PS-002-emotional-pose-sheet`：九种情绪化身体姿态
- `AC-001-occupational-action-sheet-v2`：九种单人调香职业动作
- `AC-002-general-motion-sheet`：九种行走、回身、取物等通用动作

### 道具（2）

- `PR-001-personal-accessory-inventory`：个人配饰与随身物件清单板
- `PR-002-fragrance-tool-inventory`：调香工具清单板

### 镜头与剧情（6）

- `CAM-001-camera-framing-sheet`：九种景别和观察角度
- `NV-001-official-character-poster`：春日官方角色海报
- `NV-002-fragrance-shop-story-still`：香铺工作剧情剧照
- `NV-003-canal-daylight-story-still`：临水回身日景剧照
- `NV-004-rain-night-story-still`：雨夜发现线索剧照
- `NV-005-lamplight-evidence-story-still`：灯下验香剧照

### 第一季分弧妆造（7）

- `S1-AP-A01-spring-investigation`：E01–E06 春季查证状态
- `S1-AP-A02-rain-investigation`：E07–E12 雨季查证状态
- `S1-AP-A03-summer-field-verification`：E13–E18 夏季现场核验状态
- `S1-AP-A04-autumn-ordinary-life`：E19–E24 秋季普通生活与手稿状态
- `S1-AP-A05-winter-lockdown`：E25–E30 冬季封控状态
- `S1-AP-A06-flood-relief`：E31–E35 洪灾协同状态
- `S1-AP-A06-ending-spring-letter-house`：E36 春信屋结局状态

### 第一季证据系统（6）

- `S1-PR-A01-material-clue-board`：灰字、粮尘、地图、水路与唱词材料线
- `S1-PR-A02-old-case-privacy-board`：旧案缺页与隐私保护
- `S1-PR-A03-supply-water-combined-report-board`：供给、水源与联合报告
- `S1-PR-A04-osmanthus-manuscript-board`：桂香手稿与“事实 / 推断 / 未证”
- `S1-PR-A05-lockdown-epidemic-map-board`：封控、疫图与分布式信号
- `S1-PR-A06-spring-lantern-correction-board`：灯号、纠错与“今日柳绿”

### 第一季关键叙事（25）

覆盖 E01–E07、E10–E13、E15、E18–E19、E23–E25、E29–E33、E35–E36。新增锁定后补图为 E24 桂夜别席追踪、E25 病例图与堵渠图叠合、E31 失联表路线更正。逐集映射见 `season-1/season-1-coverage-plan.json`。Season Gate 已锁定且所有绑定来源哈希已纳入自动审计；Episode Gate 仍为 `OPEN`，逐场正式交付锁定后需要再审计，但不影响当前季级角色资产包的完成状态。

## 分辨率与图像处理约定

- 正式 8K 文件的长边固定为 `7680 px`；方形板为 `7680 × 7680`。
- 竖图与横图保持原始宽高比，不裁切内容。
- PNG 无损输出，写入 300 ppi 元数据；Lanczos3 重采样并仅做轻度结构锐化。
- 不添加胶片颗粒、抖动、色噪点或人工纹理。源图始终保留，因此 8K 层可随时重新编译。
- “8K”指成品文件的实际像素尺寸，不等同于声称生成模型原生拍摄了 8K 光学信息。

## 使用建议

锁脸时先引用三张原始身份肖像与 `source/00-identity/ID-001-neutral-identity-master-v2.png`；需要角度时追加 `ID-002`，需要身体和服装结构时追加 `ID-003`。每次只改变一个主变量（表情、角度、服装或光线），不要同时替换身份、妆造和场景。
