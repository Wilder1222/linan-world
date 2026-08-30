# 女性人像 MJ 提示词编译器｜V2 参考锁定模板

> 对应规范：[FPRL-V1.1 女性人像参考锁定与编译规范](../../style/v2-female-portrait-reference-lock.md)
> 用途：把角色 Canon、可控妆发状态与镜头任务，编译成可测试的 Midjourney 8.2 女性人像 Prompt。
> 边界：这是探索与编译模板，不是自动批准的 V2 Catalog 资产，也不包含任何外部参考图 URL 或未获批身份图。

本模板的目标是复现本轮九张已检查参考人像的**视觉语法**：自然但精修的人像、克制的杏桃/桃玫瑰妆、完整髻形与局部碎发、丝纱层次、侧向柔光、眼睛焦点和受控光学柔化。逐图证据与 `R01–R04` 档案见[参考图原子观察账本](../../style/v2-female-portrait-reference-observations.md)。模板复现视觉关系而非复制参考脸；精确重建具体构图或冠饰仍须有经批准的图像绑定。

## 1. 使用方式：先选资产线，再填变量

不要从一段“绝美、电影感、临安世界观”的长词串开始。先选当前图的唯一目的：

| 资产线 | 何时使用 | 不要混入 |
|---|---|---|
| `ID-LOCK` | 探索或确认脸部身份、年龄与基础面容 | 复杂环境、强风、回眸、华冠、剧情动作 |
| `PORTRAIT-LOOK` | 测试近景妆发、肤面、参考图的柔光与视线关系 | 全身服装构造、地点名、鞋履与腰封细节 |
| `APPEARANCE` | 已有身份锚点后测试日常/礼仪/春台妆发或领肩服装 | 改脸型、改年龄、改职业识别点 |
| `COSTUME-FULL` | 测试完整服装轮廓、承重、层数、材料和发饰关系 | 近景毛孔/唇纹/单根眉毛 |
| `NARRATIVE-HERO` | 把已锁角色放进已知剧情和地点 | 模糊的 `ancient city`、无关形态清单 |

每个 `{...}` 都必须在运行前替换为**一个实际可见的选择**；花括号、中文字段名和多选项不能直接复制进 Midjourney。

## 2. 最小输入卡

把下列卡片填完后，即可从第 7 节模板编译。未知项保持“未定义”，不要用抽象形容词强行补全。

```text
【资产线】ID-LOCK / PORTRAIT-LOOK / APPEARANCE / COSTUME-FULL / NARRATIVE-HERO
【角色】姓名、年龄、职业、已有 Canon 识别点（至少三项）
【本轮唯一变量】例如：只比较 F01 与 F03；或只比较 H01 与 H02
【参考档案】无 / R01 静风清透 / R02 灯火社交 / R03 春台花丝 / R04 轻纱斜向动作
【脸部族群】F01 / F02 / F03 / F04 / F05
【眼型】E01 / E02 / E03 / E04
【表情】G01 / G02 / G03 / G04
【妆容】M01 / M02 / M03
【发型】H01 / H02 / H03 / H04
【服装】C01 / C02 / C03 / C04
【饰物】A01 / A02 / A03 / A04
【姿态】P01 / P02 / P03 / P04
【光线】L01 / L02 / L03 / L04
【镜头】K01 / K02 / K03 / K04
【环境】无 / 已登记的可见地点事实
【比例与参数】按资产线填写；默认不加 --no
```

**编译前检查**：角色已有的姓名、年龄、职业、伤痕、工作痕迹、脸部锚点优先于下面的可变块。不要把一个柔和鹅蛋脸模板覆盖到所有角色，更不能让 20 岁角色和 50 岁角色拥有同一套肤面与发量。

## 3. 固定核心块：参考语法的最小共同部分

下面不是每条都必需，但它是 `PORTRAIT-LOOK` 和 `APPEARANCE` 的默认核心。需要时按镜头尺度裁剪。选择了 `R01–R04` 时，仅从对应档案加入一至两个源自参考的可见块；不可整包堆叠冠饰、粒子、浅景深和大幅动作。

```text
refined individual facial anatomy, subtle natural facial asymmetry,
delicate regional tonal variation, fine age-appropriate natural skin texture,
restrained micro-specular highlights, subtle warmth around the cheeks, nose and eyelids,
naturally hydrated lips, smooth highlight rolloff,
sheer low-coverage historical makeup,
structured historical hair with a few irregular face-framing strands,
complete crossed-collar clothing with visibly layered silk and lightweight gauze,
soft directional light, gentle ambient facial fill,
eyes in precise focus, gradual focus falloff, controlled optical softness
```

它描述的是“如何被看见”，不是城市名字、角色身份或一张固定脸。将全套核心块填入全身图会降低清晰度；完整删减规则见 [FPRL 第 4 节](../../style/v2-female-portrait-reference-lock.md#4-按镜头尺度删减信息)。

### 3.1 实际参考图的快捷附加块 `{REFERENCE_PROFILE}`

只选一个档案；每个档案最多再叠加一个与镜头直接相关的动作或环境块。逐图证据与 V2 排除项见[观察账本](../../style/v2-female-portrait-reference-observations.md#4-四个可复用的参考风格档案)。

| ID | English block | 推荐资产线 |
|---|---|---|
| `R01` 静风清透 | `soft directional side light, a gentle warm rim through a few face-framing hairs, neutral ambient facial fill, muted ivory and mist-grey layered silk, a quiet three-quarter head turn, eyes in precise focus, progressive focus falloff, controlled optical softness` | `PORTRAIT-LOOK`、日景 `APPEARANCE` |
| `R02` 灯火社交 | `waist-up three-quarter portrait, shoulders angled away and a restrained backward glance, complete crossed-collar ivory silk with a deep smoky-teal collar border, small pearl drops, warm paper-lantern pools behind her, cool muted exterior fill in the distance, occupied circulation softened into optical bokeh` | 夜景 `NARRATIVE-HERO`、社交 `APPEARANCE` |
| `R03` 春台花丝 | `a coordinated aged-gold filigree hairpin with small pearls and muted blue-green stones, a few fine metal tassels, dark teal collar trim, restrained antique-gold thread, tiny irregular gold-leaf accents near the outer eyes, small controlled highlights on metal and silk` | 春台/礼仪 `APPEARANCE` |
| `R04` 轻纱斜向动作 | `caught at the visible apex of a restrained turn, believable torso rotation and weight shift, one full translucent sleeve crossing the foreground, physically weighted silk following the arm, warm directional light passing through gauze, face and eyes remaining readable` | 动态 `NARRATIVE-HERO` |

`R03` 不等于大冠冕，`R04` 不等于漂浮粒子或露肩舞服；这些已在原图中出现但不属于临安 V2 的可迁移边界。

## 4. 变量库

### 4.1 脸部族群 `{FACE}`

每次选择一个。已有 Character Canon 的结构锚点优先；F01–F04 是年轻成年参考风格的探索范围，F05 用于成熟/英气角色，不能因为参考风格而取消其年龄痕迹。

| ID | English block | 可见意图 |
|---|---|---|
| `F01` | `refined soft oval face, smooth cheek-to-jaw transition, gently tapered lower face, compact softly rounded chin` | 基准柔和鹅蛋 |
| `F02` | `softly rounded oval face, slightly fuller cheeks, gentle cheek contour, softly tapered jaw, compact rounded chin` | 更亲和、生活感更强 |
| `F03` | `slightly elongated oval face, restrained cheek width, graceful vertical facial rhythm, smooth tapered jawline, small rounded chin` | 清冷、文雅、修长 |
| `F04` | `soft oval-heart face, gently defined upper cheek structure, subtle narrowing toward the jaw, small softly rounded chin` | 精致、灵动但不尖锐 |
| `F05` | `balanced soft-angular mature face, moderate cheek width, softened mandibular corners, compact chin, age-appropriate facial volume` | 成熟、女官、行动/职业角色 |

### 4.2 眼睛 `{EYES}`

| ID | English block |
|---|---|
| `E01` | `elongated almond-shaped dark brown eyes, moderate eye opening, subtly lifted outer corners, narrow natural double eyelids, soft lower eyelid contour` |
| `E02` | `soft elongated almond-shaped dark brown eyes, slightly rounded inner eye contour, moderate eye opening, gentle outer corners, restrained lower eyelid fullness` |
| `E03` | `long narrow almond-shaped dark brown eyes, restrained eye opening, slightly lifted outer corners, fine natural upper eyelid crease` |
| `E04` | `elongated almond-shaped eyes with a subtle phoenix-eye influence, gently raised outer corners, narrow elegant eye opening, restrained lower eyelid fullness` |

基础眉鼻唇可接在 `{EYES}` 后面：

```text
long naturally straight brows with a shallow arch and fine tapered tails,
a refined low-to-medium nasal root, a slender straight nose bridge and a compact softly rounded nose tip,
softly defined lips with a slightly fuller lower lip and a muted peach-coral tone
```

### 4.3 表情和视线 `{GAZE}`

| ID | English block | 使用限制 |
|---|---|---|
| `G01` | `calm focused gaze, relaxed mouth, quiet stillness in the expression` | ID 夹具、日常近景 |
| `G02` | `quiet distant gaze, slightly lowered eyelids, restrained mouth expression` | 清冷/判断；不要与热烈回眸混用 |
| `G03` | `soft attentive gaze, relaxed eyes, faint warmth around the mouth` | 亲密或温和人物 |
| `G04` | `focused sideways gaze, subtly tightened lower eyelids, a slight tension at the mouth` | 警觉/剧情瞬间 |

### 4.4 肤面 `{SKIN}`

只按镜头尺度选择一个版本。

| 镜头 | English block |
|---|---|
| 近景 | `warm-neutral complexion, delicate regional tonal variation, fine age-appropriate natural skin texture, restrained micro-specular highlights, subtle warmth around the cheeks, nose and eyelids, naturally hydrated lips, smooth highlight rolloff` |
| 半身 | `natural warm-neutral complexion, subtle tonal variation, restrained facial highlights, visible facial volume and natural lip texture` |
| 全身/远景 | `natural complexion with restrained highlights, the face, hands and garments responding consistently to the same light` |

不要使用 `flawless skin`、`poreless skin`、`porcelain skin`、`glass skin`、`ultra-smooth skin`。这些不是“清透”，而是塑料皮风险。

### 4.5 妆容 `{MAKEUP}`

| ID | English block | 状态 |
|---|---|---|
| `M01` | `sheer low-coverage historical makeup, muted apricot eyeshadow, fine elongated eyeliner following the natural eye contour, soft diffused peach-rose cheek warmth, muted peach-coral lips` | 默认日常 |
| `M02` | `sheer breathable base, pale apricot-brown eyelids, very fine eyeliner, restrained lower-eye shading, muted rose-coral lips` | 清冷/低调 |
| `M03` | `refined sheer base, muted terracotta at the outer eyelids, fine elongated eyeliner, controlled soft cinnabar accents, tiny irregular gold-leaf accents near the outer eyes, muted coral lips` | 春台/礼仪，需已允许的高等级状态 |

### 4.6 发型 `{HAIR}`

| ID | English block | 适合 |
|---|---|---|
| `H01` | `raven-black hair in a loose historical half-up hairstyle, soft natural crown volume, irregular face-framing strands, fine flyaway hairs` | 年轻成年日常 |
| `H02` | `raven-black hair in a loosely structured historical updo, soft rounded volume, a few loose strands near the temples and cheeks` | 安静肖像、社交 |
| `H03` | `raven-black hair arranged in a structured high updo, controlled sculptural volume, fine loose strands framing the face` | 高等级社交/表演 |
| `H04` | `neatly secured historical hair with a stable crown structure and only a few wind-touched strands near the face` | 劳动、行动、成熟角色 |

`raven-black` 是年轻成年默认值，不覆盖 Canon 中的银丝、发色变化或工作状态。若角色是成熟、户外劳动或已有母版，优先用其已锁发色/发量并只继承“主体完整、边缘少量碎发”的结构关系。

### 4.7 服装 `{COSTUME}`

服装结构必须符合 [V2 服装构造标准](../../style/v2-costume-construction-standard.md)。近景只选择 C01 或 C02 的可见领肩部分；全身才使用完整块。

| ID | English block | 适用 |
|---|---|---|
| `C01` | `a complete crossed-collar ivory silk inner robe, a mist-grey structured middle layer, a lightweight translucent gauze edge, a narrow woven collar border, minimal pale-jade details` | 技术母版/清雅 |
| `C02` | `a complete crossed-collar ivory silk inner robe, pale celadon and muted taupe layered silk, a light translucent outer gauze, restrained botanical jacquard, a narrow aged-gold edge, small jade and pearl details` | 日常精工/主角状态 |
| `C03` | `a complete crossed-collar old-rose and soft-celadon silk ensemble, a structured middle layer beneath aged-ivory translucent gauze, dark peacock-ink collar trim, floral jacquard and low-saturation gilt edging` | 春台/社交，不等于全员默认 |
| `C04` | `a complete crossed-collar work-ready silk-and-ramie outfit, a structured middle layer, full workable sleeves, a secure waist sash, a restrained woven border and one small profession-linked ornament` | 水路、医工、商铺、劳动 |

### 4.8 饰物 `{ACCESSORIES}`

| ID | English block | 限制 |
|---|---|---|
| `A01` | `one small aged-gold hairpin and a pale-jade ornament` | 基础 |
| `A02` | `fine aged-gold hairpins, small pearl drops and delicate tassel earrings` | 闺秀/社交 |
| `A03` | `a coordinated gilt-filigree hairpin, pearl sprigs, small pale-jade ornaments and delicate tassel earrings` | 春台/精致状态 |
| `A04` | `a small dark-wood pin, restrained brass hardware and one profession-linked personal ornament` | 劳动/职业 |

不要把 `A02` 或 `A03` 自动升级为 crown。项目 V2 禁止皇冠化头饰、额前垂饰和不受身份约束的珠宝堆砌。

### 4.9 姿态 `{POSE}`

| ID | English block | 适用 |
|---|---|---|
| `P01` | `level shoulders, relaxed upright posture, calm direct presence` | ID-LOCK |
| `P02` | `shoulders slightly angled away from the camera, a subtle three-quarter head turn, eyes looking just past the camera` | 近景参考风格 |
| `P03` | `shoulders turned away, head turning back, a restrained backward glance` | 已锁脸后的回眸 |
| `P04` | `caught mid-turn, believable torso rotation and weight shift, one broad translucent sleeve moving through the foreground, fabric following the body movement` | 动态情绪图；不作身份锁定证据 |

### 4.10 光线 `{LIGHT}`

| ID | English block | 用途 |
|---|---|---|
| `L01` | `soft large-window daylight, pale reflected fill, gentle dimensional facial shadows, complete collar and face clearly readable` | ID-LOCK |
| `L02` | `soft directional side light, gentle warm backlight through a few hair strands, soft neutral ambient facial fill, smooth highlight rolloff` | 参考风格近景 |
| `L03` | `soft neutral window light, restrained shadow transitions, subtle hair separation, controlled highlights on silk and small metal details` | 清冷/室内 |
| `L04` | `warm lantern key light, quiet blue-grey ambient fill, small controlled highlights on metal and silk, natural facial exposure` | 夜景叙事；必须加入实际灯具/地点 |

### 4.11 镜头 `{CAMERA}`

| ID | English block | 使用 |
|---|---|---|
| `K01` | `front-facing head-and-upper-torso framing, direct eye-level viewpoint, full collar readable, clean warm-ivory plaster background` | ID-LOCK |
| `K02` | `close portrait, three-quarter head turn, shallow depth of field, eyes in precise focus, gradual focus falloff, creamy optical bokeh, subtle halation` | 参考风格近景 |
| `K03` | `waist-up portrait, three-quarter body angle, clear facial focus, soft environmental separation, natural optical bokeh` | 半身妆发/关系图 |
| `K04` | `full body visible from head to feet, natural full-body perspective, moderate depth of field, clear cloth-to-body contact and complete footwear` | 服装验证 |

## 5. 环境块：只有叙事图才调用

地点标签本身没有足够的像素约束。对 `ID-LOCK`、`PORTRAIT-LOOK` 和 `APPEARANCE`，通常填“无”。对 `NARRATIVE-HERO`，仅从已锁地点/分镜中选择能看得见的事实。

| ID | English block | 使用条件 |
|---|---|---|
| `S01` | `beside a working fragrance counter with a brass scale, paper-wrapped goods, pale plaster bounce and a lattice window` | 香铺/道具和场景事实已登记 |
| `S02` | `at an occupied covered riverside threshold with damp timber rails, tied cargo bundles and a practical water route behind her` | 码头/水岸事实已登记 |
| `S03` | `at the edge of a performance-house backstage with mended sleeves, small oil lamps, a silk curtain and visible working circulation` | 春台后台事实已登记 |
| `S04` | `beside a carved railing and silk curtain above an occupied lantern-lit market, warm paper lantern pools receding into muted blue-grey distance` | 夜市/关系或主视觉，且地点允许 |

环境块必须接着一个动作和实际光源使用。例如 S01 可配 `her thumb pauses over a small fragrance packet beside the scale` 和 L03；不能只写“prosperous ancient city”。

## 6. 编译公式

### 6.1 `ID-LOCK`：只锁身份

```text
{SUBJECT: name, age, occupation},
{CANON_IDENTITY: three stable identity anchors},
{FACE}, {EYES}, {BROW_NOSE_LIPS}, {GAZE}, subtle natural facial asymmetry,
{SKIN: close portrait}, {MAKEUP},
{HAIR}, {VISIBLE_COLLAR_FROM_C01_OR_C04}, {ACCESSORIES},
{POSE:P01}, {LIGHT:L01}, {CAMERA:K01}
--v 8.2 --raw --ar 3:4 --s 70–100 --c 0–2
```

同一轮不可改变 `FACE`、`EYES`、`MAKEUP`、`HAIR` 和 `LIGHT` 中的多个主轴。先在统一中性夹具中比较脸；选中后才进入风格近景。

### 6.2 `PORTRAIT-LOOK`：复现参考图的近景视觉关系

```text
{SUBJECT},
{CANON_IDENTITY},
{FACE}, {EYES}, {BROW_NOSE_LIPS}, {GAZE}, subtle natural facial asymmetry,
{SKIN: close portrait}, {MAKEUP},
{HAIR}, {VISIBLE_COLLAR_FROM_C01_OR_C02}, {ACCESSORIES},
{POSE:P02_OR_P03}, {LIGHT:L02_OR_L03}, {CAMERA:K02}
--v 8.2 --raw --ar 3:4 --s 95–140 --c 1–3
```

此线复现的是“脸静、发丝轻动、衣料轻、光线柔”的关系，不能取代正面/三视图身份证据。

### 6.3 `APPEARANCE`：已锁角色只换妆发与领肩状态

```text
{LOCKED_SUBJECT_AND_IDENTITY},
{PRESERVED_FACE_AND_EYE_ANCHORS}, {GAZE},
{SKIN: close or medium}, {MAKEUP}, {HAIR},
{VISIBLE_COLLAR_FROM_C02_OR_C03}, {ACCESSORIES},
{POSE:P02}, {LIGHT:L02_OR_L03}, {CAMERA:K02_OR_K03}
--v 8.2 --raw --ar 3:4 --s 100–140 --c 1–3
```

该线不再填写新脸型或新年龄；要换脸应 fork 回 `ID-LOCK`/`CharacterMorphology`。

### 6.4 `COSTUME-FULL`：人和服装在一个物理世界中

```text
{LOCKED_SUBJECT}, {PRESERVED_VISIBLE_FACE_ANCHORS},
natural standing posture and believable weight bearing,
{HAIR}, {FULL_COSTUME:C01/C02/C03/C04}, {ACCESSORIES},
clear inner-middle-outer layer separation, full workable sleeves, secure waist sash,
matte silk, ramie, silk crepe and lightweight translucent gauze showing different weave, thickness, fold and light response,
{LIGHT:L01_OR_L03}, {CAMERA:K04}
--v 8.2 --raw --ar 2:3 --s 135–190 --c 2–3
```

这里肤面仅保持自然可读；把毛孔、唇纹、单根眉毛等近景信息删掉，把注意力转给比例、受力、内中外层、布料重量、腰封和鞋履。

### 6.5 `NARRATIVE-HERO`：把参考语法放入临安的具体场景

```text
{LOCKED_SUBJECT}, {PRESERVED_VISIBLE_FACE_ANCHORS},
{CURRENT_ACTION_AND_GAZE},
{HAIR}, {COSTUME}, {ACCESSORIES},
{SCENE_FACTS},
{POSE:P03_OR_P04},
{LIGHT: actual daylight / lantern / window source},
foreground object or fabric framing, an active middle-ground action, a receding usable route,
waist-up or environmental portrait, clear face and action priority, natural optical depth and controlled highlight bloom around actual bright sources
--v 8.2 --ar 16:9 --s 180–260 --c 3–5
```

`{SCENE_FACTS}` 只可来自 Canon 或已锁分镜。不要把环境需求塞进近景人像，也不要把肖像的单根发丝和唇纹塞进城市宽景。

## 7. 可直接运行的零状态与示例

以下示例均为文本探索模板，不是已批准角色资产。它们刻意不写 `Linan World`、不包含外部图片链接，也不使用“8K、masterpiece、perfect face”等空泛质量词。

### FPRL-01｜中性脸部比较夹具（仅改 `{FACE}`）

先把 `{FACE}` 依次替换为 F01、F02、F03、F04；除此以外不改动任何文字和参数。

```text
Front-facing casting portrait of an adult Chinese woman with individually distinctive, believable facial anatomy. {FACE}, elongated almond-shaped dark brown eyes with moderate eye opening and subtly lifted outer corners, narrow natural double eyelids, long naturally straight brows with a shallow arch and fine tapered tails, a refined low-to-medium nasal root, a slender straight nose bridge, a compact softly rounded nose tip, softly defined lips with a slightly fuller lower lip and a muted peach-coral tone, calm focused gaze, subtle natural facial asymmetry. Warm-neutral complexion, delicate regional tonal variation, fine age-appropriate natural skin texture, restrained micro-specular highlights, subtle warmth around the cheeks, nose and eyelids, naturally hydrated lips, smooth highlight rolloff. Sheer low-coverage historical makeup, muted apricot eyeshadow, fine elongated eyeliner following the natural eye contour, soft diffused peach-rose cheek warmth, muted peach-coral lips. Raven-black hair in a simple neatly secured historical half-up hairstyle, only a few fine face-framing strands. Complete crossed-collar ivory silk inner robe, mist-grey structured middle layer, narrow woven collar border, one small pale-jade hair ornament. Level shoulders, relaxed upright posture, calm direct presence. Front-facing head-and-upper-torso framing, direct eye-level viewpoint, full collar readable, clean warm-ivory plaster background, soft large-window daylight, pale reflected fill, gentle dimensional facial shadows. --v 8.2 --raw --ar 3:4 --s 82 --c 1
```

### FPRL-02｜参考图综合近景（不含地点）

```text
Adult Chinese woman with refined individual facial anatomy, a soft oval-heart face, gently defined upper cheek structure, subtle narrowing toward the jaw and a small softly rounded chin. Elongated almond-shaped dark brown eyes with moderate eye opening and subtly lifted outer corners, narrow natural double eyelids, long naturally straight brows with fine tapered tails, a low-to-medium nasal root, slender straight nose bridge, compact softly rounded nose tip, softly defined lips with a slightly fuller lower lip and muted peach-coral tone, calm focused gaze, subtle natural facial asymmetry. Warm-neutral complexion with delicate regional tonal variation, fine age-appropriate natural skin texture, restrained micro-specular highlights, subtle warmth around the cheeks, nose and eyelids, naturally hydrated lips, smooth highlight rolloff. Sheer low-coverage historical makeup, muted apricot eyeshadow, soft terracotta at the outer eyelids, fine elongated eyeliner, soft diffused peach-rose cheek warmth, muted peach-coral lips. Raven-black hair in a loosely structured historical half-up hairstyle with soft natural crown volume, a few irregular face-framing strands and fine flyaway hairs. A complete crossed-collar ivory silk inner robe, pale celadon and muted taupe layered silk visible at the shoulder, a light translucent gauze edge, restrained botanical jacquard, a narrow aged-gold edge, a small pale-jade hairpin and pearl drops. Shoulders slightly angled away from the camera, subtle three-quarter head turn, eyes looking just past the camera. Soft directional side light, gentle warm backlight through a few hair strands, soft neutral ambient facial fill, smooth highlight rolloff. Close portrait, eyes in precise focus, gradual focus falloff, creamy optical bokeh, subtle halation. --v 8.2 --raw --ar 3:4 --s 110 --c 2
```

### FPRL-03｜春台/高礼仪妆发状态（不使用皇冠）

```text
Adult Chinese woman with individually distinctive facial anatomy, a slightly elongated oval face, restrained cheek width, graceful vertical facial rhythm, smooth tapered jawline and small rounded chin. Long narrow almond-shaped dark brown eyes with restrained eye opening and slightly lifted outer corners, fine natural upper eyelid crease, straight brows with tapered tails, a slender straight nose, compact softly rounded nose tip, muted coral lips, quiet distant gaze, subtle natural facial asymmetry. Warm-neutral complexion, delicate regional tonal variation, fine age-appropriate natural skin texture, restrained facial highlights and naturally hydrated lips. Refined sheer historical base makeup, muted terracotta at the outer eyelids, fine elongated eyeliner, controlled soft cinnabar accents, tiny irregular gold-leaf accents near the outer eyes, muted coral lips. Raven-black hair arranged in a structured high updo with controlled sculptural volume and fine loose strands framing the face. Complete crossed-collar old-rose and soft-celadon silk ensemble, structured middle layer beneath aged-ivory translucent gauze, dark peacock-ink collar trim, floral jacquard and low-saturation gilt edging, a coordinated gilt-filigree hairpin, pearl sprigs, small pale-jade ornaments and delicate tassel earrings. Shoulders slightly angled away, a subtle three-quarter head turn, eyes looking just past the camera. Soft directional side light, gentle warm backlight through a few hair strands, soft neutral ambient facial fill, small controlled highlights on silk and metal, smooth highlight rolloff. Close portrait, eyes in precise focus, gradual focus falloff, creamy optical bokeh, subtle halation. --v 8.2 --raw --ar 3:4 --s 135 --c 2
```

### FPRL-04｜风、轻纱与回身（已锁脸后使用）

```text
Adult Chinese woman with a refined soft oval face, a smooth cheek-to-jaw transition, compact softly rounded chin, elongated almond-shaped dark brown eyes with subtly lifted outer corners, natural straight brows, a slender straight nose and muted peach-coral lips. Warm-neutral natural complexion with restrained highlights, muted apricot and soft terracotta historical makeup, raven-black hair in a loosely structured historical updo with a few wind-touched face-framing strands crossing the cheeks. Complete crossed-collar ivory silk inner robe, muted cinnabar and smoky charcoal layered outer garments, lightweight translucent silk gauze, broad flowing sleeves, restrained embroidered borders, one aged-gold hairpin and pale-jade ornament. Caught mid-turn with believable torso rotation and weight shift, one arm raised naturally, one broad translucent sleeve moving through the foreground, fabric following the body movement. Soft directional side light passing through the gauze, gentle backlight through individual hair strands, soft ambient facial fill, the face remaining clearly readable. Eyes in precise focus, foreground fabric softly blurred, controlled optical softness, dynamic diagonal composition. --v 8.2 --ar 3:4 --s 150 --c 3
```

### FPRL-05｜世界内的叙事人像（地点作为可见事实）

```text
Adult Chinese woman with a refined soft oval face, elongated almond-shaped dark brown eyes with subtly lifted outer corners, natural straight brows, a slender straight nose, muted peach-coral lips and a calm observant gaze. She wears a complete crossed-collar ivory silk inner robe, pale celadon and muted taupe layered silk, a light translucent outer gauze, restrained botanical jacquard, a narrow aged-gold edge and small jade details. Her thumb pauses over a paper-wrapped fragrance packet beside a brass scale, and she turns her head slightly toward a sound beyond the lattice window. Raven-black hair in a loosely structured half-up hairstyle with a few face-framing strands. At a working fragrance counter with paper-wrapped goods, ceramic jars, pale plaster bounce and a lattice window; a close tea vessel creates a quiet foreground, a shop assistant organizes goods in the middle ground, and a passable market route recedes beyond the threshold. Soft late-afternoon daylight enters through the lattice, pale walls and glazed ceramic return a soft fill, small material highlights remain controlled on silk, jade and brass. Waist-up portrait, three-quarter body angle, clear face and hand priority, soft environmental separation, natural optical bokeh, restrained highlight bloom only around the window-lit materials. --v 8.2 --ar 16:9 --s 190 --c 3
```

## 8. 对照实验与复审记录

每次生成都以小表记录，而不是凭记忆判断：

| 字段 | 示例 |
|---|---|
| Prompt 标识 | `FPRL-01/F03/E01` |
| 父版本 | `FPRL-01/F01` |
| 唯一变化 | `FACE: F01 → F03` |
| 不变条件 | `M01, H01, C01, L01, K01, --raw --ar 3:4 --s 82 --c 1` |
| 观察结果 | 结构可辨 / 眼型过圆 / 肤面过磨皮 / 发际通过 |
| 下个单变量修复 | 仅改 E01 → E03；保持其余块 |
| 选择状态 | `candidate` / `rejected` / `user-selected`；不是自动锁定 |

常见失败与最小修复路径：

| 故障 | 不要做 | 只改哪里 |
|---|---|---|
| `plastic_skin` | 重写整条 Prompt 或加“ultra realistic” | `{SKIN}`：降低无瑕词，保留区域色差/微高光/滚降 |
| `same_face_drift` | 给所有人追加同一串五官词 | 回到角色 Canon；只修 `{FACE}` 或 `{EYES}` 一个形态轴 |
| `hair_edge_failure` | 用 `messy hair` 覆盖 | `{HAIR}`：保持髻形，增加/减少一处面颊碎发 |
| `over-ornamented` | 用冗长 `--no` 禁止珠宝 | `{ACCESSORIES}`：A03 → A02 或 A01；保持服装结构 |
| `fantasy_costume` | 增加“historically accurate”空词 | `{COSTUME}`：恢复完整交领、全袖、内中外层与窄边精工 |
| `portrait_on_wrong_background` | 继续加“cinematic atmosphere” | 近景删环境；叙事图改成一个已登记的 `{SCENE_FACTS}` 块 |

## 9. 升级到正式 V2 资产的条件

本文件中的文本探索成为正式资产前，必须同时满足：

1. 用户明确选中候选，且角色 Canon 与三项结构锚点未被改写；
2. `ID-LOCK` 至少具有正面、三分之四、侧面所需的中性连续性证据；
3. 当前妆发/服装作为独立 `AppearanceState` 记录，未冒充稳定身份；
4. 任何使用的项目生成 Image Prompt 已记录来源、哈希、用途与审批；
5. Prompt 以新版本/新记录进入 `production/midjourney/v2` Catalog，而非覆盖旧 Prompt；
6. 通过 V2 视觉 QA、角色连续性和对应资产线的验收。

在此之前，它们是可复现的探索假设，不是已生成、已批准或已锁定的世界资产。
