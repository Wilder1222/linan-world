# VIS-LW-V2｜女性人像参考锁定与编译规范

> 版本：`FPRL-V1.1`
> 状态：`ACTIVE-EXPLORATION-GUIDANCE`
> 适用：女性角色的 `ID-LOCK`、妆发状态、定妆肖像、情绪近景与叙事人像。
> 不适用：直接替换 Character Canon、把一张参考脸复制给角色、未经审批的外部图传入 Midjourney、或替代全身服装/地点/分镜规范。

本文件将本轮九张已检查的参考人像视觉语法，转译为《临安春信》V2 的可复用规则。它锁定的是**可迁移的表现关系**——脸部的克制结构、自然肤面、低饱和妆容、完整发型边缘的碎发、丝纱与受控光学柔化；它不定义“临安女性必须长成同一张脸”。

逐图的可见证据、内容哈希、可迁移/排除边界和 R01–R04 风格档案见[女性人像参考图原子观察账本](v2-female-portrait-reference-observations.md)。直接可复制的 Midjourney 模板、变量卡和已填示例见 [女性人像 MJ 提示词编译器](../midjourney/v2/female-portrait-prompt-builder.md)。世界路线、服装构造、参考图授权与已登记的资产提示词仍分别以 [V2 风格包](v2-urban-splendor-song-style-package.md)、[服装构造标准](v2-costume-construction-standard.md)、[参考图政策](v2-reference-policy.md) 和 [V2 资产库](../midjourney/v2/README.md) 为准。

## 1. 证据边界：先拆图，再写提示词

用户现已提供九张原始 JPEG。本轮已按实际可见像素检查了其人像、妆发、服装、光线和构图，并以匿名 `FPR-01` 至 `FPR-09` 与 SHA-256 写入[观察账本](v2-female-portrait-reference-observations.md)。这些图可以支持可迁移视觉原子的设计判断；它们仍不能自动提供作者、肖像、版权、训练、外传或 Midjourney 引用许可。

工作区中已有的妆发九宫格仍可作为辅助本地对照；实际参考包优先定义“暖侧后光、轻度雾化、局部碎发、杏桃/暖赭妆、灯火散景、花丝金属与轻纱动作”的来源证据。参考图不作为任何角色的脸部身份来源，也不自动外传。若要对另一张新图做相同处理，按下表执行。

| 输入 | 可以得出的结论 | 不可以得出的结论 | 下一步 |
|---|---|---|---|
| `FPR-SET-20260830-A` 九张实际 JPEG | 可按角色拆出可见的脸部形态范围、妆、发、服、光与构图；详见观察账本 | 作者/版权/肖像/外传许可、隐藏面部、真实焦段、动作时序 | 仅作本地设计期证据；以 `R01–R04` 转译为 V2 变量 |
| 对话文字、风格描述 | 可编辑的视觉方向、待验证 Prompt 假设 | 原图未显示的五官比例、真实镜头参数、原图版权 | 仅作为与实际观察相互校对的创作意图 |
| 本地 `raw/` 情绪板 | 可迁移的妆发、材质、光线、裁切与反例 | 新角色的身份、全身比例、外部使用授权 | 仅作设计期对照，遵守 V2 参考图政策 |
| 新提供的原始参考图 | 可按区域拆出可见的脸、妆、发、服、光、构图观察 | 隐藏面部、实际焦段、动作时序、授权 | `reference_ingest → reference_verify → reference_observe` |
| 用户选定的项目生成母版 | 角色连续性、同一角色后续 Image Prompt 候选 | 外部风格图的授权、全局世界 Canon | 记录批准、哈希、用途与生成会话后再使用 |

同一张参考图不得被写成一个“万能提示词”。脸部、肤面、妆容、头发、服装、光线和构图应分成互不覆盖的观察角色；例如光线不能覆盖脸部身份，妆容不能覆盖自然骨相。

## 2. 参考锁定层：哪些内容保持一致，哪些内容必须让角色不同

### 2.1 固定的是视觉语法，不是城市人种

| 维度 | FPRL 共同语法 | V2 中的边界 |
|---|---|---|
| 人像结构 | 自然解剖、轻微不对称、平顺的面颊至下颌过渡、避免极尖 V 脸和夸张圆眼 | 每位角色仍从 Canon 的年龄、职业、识别点和结构锚点出发；不可因模板抹平差异 |
| 眼睛与表演 | 细长杏眼家族、自然开度、眼尾可轻抬；情绪主要由视线、眼睑和嘴角的细微状态表现 | 眼型、眼距、眼角方向、眉形和眼神均可变；不把“漂亮”作为身份锚点 |
| 肤面 | 区域性明暗和暖色、细微自然纹理、眼唇湿润、克制高光、平滑高光滚降 | 不以“白、瓷、无瑕”替代真实肤面；年龄、户外工作、疲惫、妆面状态由角色与状态决定 |
| 妆容 | 薄底，杏桃/柔赭/桃玫瑰眼部与唇颊低饱和关系，细长但不过黑的眼线 | 妆容是 `AppearanceState`，不是稳定身份；劳动、成熟年龄与剧情状态可降低或改变浓度 |
| 头发 | 主体髻形或半束结构完整，边缘保留少量不规则面颊碎发与可读飞发 | 乌黑长发是年轻成年女性的默认方向，不覆盖年龄、职业、发量和发色的 Canon 事实 |
| 服装 | 完整交领、可读内中外层、真丝/麻/轻纱的差异受光、窄边或局部精工 | 不能将象牙白礼服、薄纱、玉饰或华冠泛化给所有女性；职业、财力和场合决定等级 |
| 光与光学 | 侧光或侧后光使发丝、丝纱、金属产生小而有来源的亮点；眼睛优先可读，背景按镜头尺度柔化 | 技术身份图先保持中性正面光；叙事图必须继续服从地点、时段和实际光源 |

### 2.2 Hard / Soft / Free 锁定矩阵

| 锁定级别 | 内容 | 编译要求 |
|---|---|---|
| `HARD · 项目 Canon` | 年龄、角色职业、稳定识别点、明确伤痕/劳动痕迹、既有获批母版、服装禁区 | 所有 Prompt 都必须保留；模板变量不得覆盖 |
| `HARD · V2 世界` | 自然人体与材质、完整交领/全袖/可承重服装、光源有物理来源、无仙侠/现代/塑料皮 | 直接用正向可见描述实现，不以冗长负面词表解决 |
| `SOFT · 参考锁定` | 柔和但可辨的面部关系、低饱和杏桃/桃玫瑰妆、完整发型加局部碎发、克制受控高光、丝纱层次 | 在年轻成年女性的妆发/肖像线中默认继承；若 Canon 或镜头用途冲突，应显式降级 |
| `FREE · 角色变量` | 脸型、眼型细节、眉鼻唇比例、肤色范围、年龄痕迹、发型、色盘、饰品、动作、阶层信息 | 每轮只改一个主要变量；由角色卡和场景卡填写 |
| `CONDITIONAL · 参考图` | 外部图像的身份、服装、构图或具体装饰 | 必须先有权利记录、角色化观察与人工批准；不能由文字描述自动获得 |

## 3. 可迁移的人像原子

以下原子来自参考方向的文字化提炼和工作区本地妆发板的可见范围。它们是 Prompt 的模块库，不是每张图都要全量使用的词袋。

### 3.1 身份几何：只用于近景或中景

**推荐关系**

- 面部可在柔和鹅蛋、略圆鹅蛋、微修长鹅蛋、柔和心形、成熟方圆之间变化；重点是颧颌过渡自然、下巴紧凑圆润而非针尖。
- 眼睛可在细长杏眼、温柔杏眼、清冷窄杏眼、轻丹凤走势之间变化；重点是中等开度、自然内眼角、窄而可见的眼睑褶皱。
- 鼻部使用自然中低山根、细直鼻梁、收束圆润鼻尖；嘴部使用柔和轮廓、下唇略有体积、低饱和珊瑚/桃玫瑰。
- 保留 `subtle natural facial asymmetry`，但不能用“凌乱、不对称”取代可辨身份。

**不应默认的关系**

- 统一瓜子脸、极高山根、欧式深眼窝、超大圆眼、过白眼白、厚重假睫毛、玻璃唇。
- 把单张侧脸的透视误读成永久脸型；未有正面、三分之四、侧面中性证据前，不锁定脸部。

### 3.2 Natural Human Rendering：抛光但不塑料

近景使用：

```text
delicate regional tonal variation, fine age-appropriate natural skin texture, restrained micro-specular highlights, subtle warmth around the cheeks, nose and eyelids, naturally hydrated lips, smooth highlight rolloff
```

半身时缩减为肤面体积、手部和材料分离；全身与远景不再塞入毛孔、唇纹、单根眉毛等不可见信息。所谓“清透”应靠区域暖色、薄组织受光、碎发、眼唇湿润和高光滚降表现，不使用 `porcelain skin`、`glass skin`、`flawless skin` 或无来源的全局发光。

### 3.3 妆容：可见位置而非抽象“高级感”

| 状态 | 可复制模块 | 适用 |
|---|---|---|
| `M01 轻透日常` | `sheer low-coverage historical makeup, muted apricot eyelids, fine elongated eyeliner following the natural eye contour, soft diffused peach-rose cheek warmth, muted peach-coral lips` | 身份母版、香铺/书坊/市井、年轻角色日常 |
| `M02 清冷克制` | `sheer breathable base, pale apricot-brown eyelids, very fine eyeliner, restrained lower-eye shading, muted rose-coral lips` | 文雅、夜雨、判断/警觉情绪 |
| `M03 春台/礼仪` | `refined sheer base, muted terracotta at the outer eyelids, fine elongated eyeliner, controlled soft cinnabar accents, tiny irregular gold-leaf accents near the outer eyes, muted coral lips` | 表演、雅集、正式社交；只在允许的华丽度内使用 |

`gold-leaf accents` 是局部矿物感细节，不等于现代亮片妆；浓黑眼线、韩式水光唇、满脸闪片和大面积高饱和正红均不属于此层。

### 3.4 头发：完整结构 + 局部生命感

| 状态 | 可复制模块 | 注意 |
|---|---|---|
| `H01 松散半束` | `raven-black hair in a loose historical half-up hairstyle, soft natural crown volume, irregular face-framing strands, fine flyaway hairs` | 适合年轻成年日常；不强制用于成熟或劳动角色 |
| `H02 松云髻` | `raven-black hair in a loosely structured historical updo, soft rounded volume, a few loose strands near the temples and cheeks` | 闺秀、社交、安静肖像 |
| `H03 结构高髻` | `raven-black hair arranged in a structured high updo, controlled sculptural volume, fine loose strands framing the face` | 高等级社交/表演；需服从发饰预算 |
| `H04 职业收束` | `neatly secured historical hair with a stable crown structure and only a few wind-touched strands near the face` | 水路、医工、劳动、行动状态 |

发丝的规则是“主体完整，边缘自然失序”。`messy hair`、`wild hair` 会破坏髻形与职业可信度；每张技术 ID 图也不必强行制造风吹碎发。

### 3.5 服装与饰物：用结构和材料取代 `luxurious hanfu`

基础结构以 V2 服装构造标准为准：

```text
complete crossed-collar construction, a visible inner layer, a structured middle layer, a controlled outer layer, full workable sleeves, a secure waist sash, a long vertical silhouette, differentiated matte silk, ramie, silk crepe and lightweight translucent gauze
```

女性近景只写进入画面的衣领、肩部、发饰和耳饰；全身才写腰封、裙线、袖口、鞋履、层数和布料承重。优先描述 `woven border`、`subtle floral jacquard`、`aged-gold hairpin`、`pale jade ornament`、`small pearl drops`，而非“贵气、奢华、华丽”。

表演/高礼仪状态最多使用“一处组织性主华丽点 + 两至三项协调收束”：例如花丝主簪、珍珠枝、窄金线、细长耳饰和腰间小饰。它不是冠冕堆饰；V2 继续禁止额前宝石、皇冠化头饰、露腰露肩、链甲胸衣、异域舞娘轮廓与无重力飘带。

### 3.6 光、构图与运动：将“电影感”拆成可见行为

| 目标 | 可复制模块 | 不要用 |
|---|---|---|
| 中性身份图 | `front-facing head-and-upper-torso framing, direct eye-level viewpoint, soft large-window daylight, pale reflected fill, complete collar readable` | 三分之四回眸、强逆光、前景纱、繁复背景；这些会污染身份比较 |
| 参考风格近景 | `three-quarter head turn, shoulders slightly angled away, eyes looking just past the camera, soft directional side light, gentle backlight through a few hair strands, shallow depth of field` | 只写 `cinematic`, `poetic`, `beautiful lighting` |
| 动态情绪图 | `caught mid-turn, believable torso rotation and weight shift, one broad translucent sleeve moving through the foreground, fabric following the body movement` | 失重袖摆、无来源风、把静态图当成动作证据 |
| 叙事环境肖像 | 一项明确地点事实 + 一项人物动作 + 前/中/远景关系 + 实际光源 | 仅写 `Linan`, `ancient city`, `market atmosphere` |

`compressed portrait perspective`、`shallow depth of field`、`eyes in precise focus`、`gradual focus falloff`、`creamy optical bokeh` 与 `subtle halation` 描述的是可见效果，不断言真实焦段、光圈或相机型号。

## 4. 按镜头尺度删减信息

| 资产线 | 必须优先 | 必须删减 | V2 参数起点 |
|---|---|---|---|
| `ID-LOCK` | 年龄、三项身份结构锚点、自然肤面、完整领口、职业小物、正面中性光 | 风、剧情动作、复杂头冠、环境地点、毛孔以外的过密肤面词 | `--v 8.2 --raw --ar 3:4 --s 70–100 --c 0–2` |
| `PORTRAIT-LOOK` | 脸部关系、妆、发、可见肩领、视线、侧/侧后光、眼睛焦点 | 全身构造、地点名、不可见鞋履与腰封 | `--v 8.2 --raw --ar 3:4 --s 95–140 --c 1–3` |
| `COSTUME-FULL` | 头身、承重、交领层次、袖型、腰封、裙线、鞋履、材质与动作关系 | 毛孔、唇纹、单根眉毛、微小眼影颗粒 | `--v 8.2 --raw --ar 2:3 --s 135–190 --c 2–3` |
| `NARRATIVE-HERO` | 角色已锁身份、动作、具体地点事实、前中后景、真实光源、材质反应 | 与镜头无关的形态清单、抽象地名与万能修饰词 | `--v 8.2 --ar 16:9 --s 180–260 --c 3–5` |

## 5. MJ 提示词写作合同

### 5.1 可见性优先的层级

每条 Prompt 先用一句观察逻辑回答：**镜头在何种可见瞬间、从什么角度看谁，让观众先看见什么？** 然后按以下顺序组织：

```text
1. 资产目的与主体
2. Character Canon：稳定身份、三项结构锚点、稳定肤面基线
3. Appearance State：当前妆容、发型、服装、首饰、临时肤面状态
4. 动作/视线与可见承重关系
5. 仅在需要时加入的具体环境
6. 构图、景深、焦点
7. 物理光源、阴影和曝光关系
8. 材料如何响应光
9. V2 的自然写实/受控光学处理
10. Midjourney 参数
```

角色事实优先于风格词；脸部几何优先于妆发；正向可见描述优先于万能 `--no`。最终命令不得含内部合同名、变量花括号、无效 Style URL、未选择的身份图或“Linan World”这类无法形成可见差异的世界观口号。

### 5.2 地点是否写入 Prompt

地点名本身不能代替画面。纯肖像、身份锁定与妆发探索不需要 `Linan`、`ancient city`、`worldbuilding` 等词；它们会挤占面部、妆发和光线的信息预算。

叙事镜头则必须写入**可见的世界事实**：例如“lattice window, pale plaster bounce, a working fragrance counter, paper-wrapped goods”，或者已登记地点的“covered riverside threshold, occupied paper-lantern pools, damp timber rail”。`Linan` 可以作为项目内语义标签保留在叙事 Prompt 中，但永远不能单独充当场景描述。

### 5.3 受控探索，而不是随机抽卡

1. 固定中性夹具（相同年龄、基础妆、完整领口、背景、光线与画幅）。
2. 第一轮只换脸型/颌面节奏；第二轮只换眼型关系；第三轮才比较妆容；第四轮比较发型；第五轮比较服装等级或光线。
3. 每一轮保留 2–4 个变体，只声明一个主假设；不要同时改变脸、服、光、动作和景深。
4. 用户选择后再进入 `CharacterMorphologySpec` 或 `AppearanceState`；漂亮的单张 Hero 图不等于身份已锁。
5. 失败时只修一条归属路径：如 `plastic_skin` 调整肤面/渲染，`hair_edge_failure` 调整发丝状态，`identity_drift` 返回形态夹具；不得“整条重写”。

### 5.4 `--no` 与参考图使用

默认不加 `--no`。只有复核出一个持续的、单一且安全的故障后，才使用 `--no text`、`--no watermark` 或 `--no logo`；不可把脸、皮肤、衣物、身体或一句抽象禁止语塞进负向参数。

外部参考图默认只在设计期本地观察。已获批、项目生成的同角色母版可在 Midjourney 网页端作为 Image Prompt 使用；其用途、权利、哈希、会话和人工选择理由必须记录。该步骤属于生产批准，不能由本模板自动触发。

## 6. CineWeave 使用路径

本项目不需要将每次 MJ 探索都伪装成完整 CineWeave 导入 JSON；但当任务跨参考图、角色、风格和 Prompt 时，必须按职责分工而不是把所有信息揉成一段话。

| 何时使用 | CineWeave Skill | 产物 / 关键限制 |
|---|---|---|
| 用户重新提供原始参考图，要求拆解或复刻 | `cineweave-reference` 的 `reference_ingest`、`reference_verify`、`reference_observe` | 将脸、肤面、妆、发、服、光、构图拆成原子观察；一图可有多条观察，但每条只一个主角色 |
| 要探索新角色的脸，但还没锁身份 | `cineweave-character` 的 `character_explore` / `character_morphology` | 共享中性夹具、一次只改一个形态轴；需正面/三分之四/侧面审查后才能锁定 |
| 仅更换妆容、发型、礼服或疲惫/雨后肤面 | `cineweave-character` 的 `appearance_state` | 不改 CharacterSpec；妆、发、服和临时肤面状态独立版本化 |
| 要把参考中的光学、色彩、抛光程度推广为世界语言 | `cineweave-style` 的 `style_analyze` / `style_compile` | 保持身份与物理光源独立；光晕是表现处理，不是光源本身 |
| 要把已锁事实转成 MJ 文本或做 A/B | `cineweave-prompt` 的 `prompt_design` / `prompt_compile` / `prompt_compare` / `prompt_repair` | 先简短后扩展，按镜头尺度分配信息；变体只改变声明的一个假设 |

上述路径的参考图与权利边界均受 [V2 参考图政策](v2-reference-policy.md) 约束。本文件使用了这些 Skill 的方法论，并以 `FPR-SET-20260830-A` 的本地可见观察更新了视觉原子；当前环境没有 CineWeave 运行时，因此它不声称已经生成正式 `ReferenceObservation`、外部引用、媒体或批准回执。

## 7. 人像复审清单

在将探索图升级为项目候选前，逐项核对：

- [ ] 角色仍符合 Canon 年龄、职业、识别点和身份锚点，没有被“同脸美女”覆盖。
- [ ] 面部是可辨的自然结构，不是极尖下颌、夸张大眼或一键磨皮。
- [ ] 肤面在同一物理光场中呈现区域暖色、有限高光和适龄纹理；眼唇、发丝、丝绸各自响应光。
- [ ] 妆容是低饱和历史妆而非现代浓妆；华丽妆只在春台/礼仪等允许状态出现。
- [ ] 发型主结构完整，碎发只在边缘服务视线或受风关系；成熟/劳动角色未被强制年轻黑长发。
- [ ] 服装有完整交领、内中外层、可活动袖口与身份对应的精工预算；没有华冠堆饰或幻想舞娘结构。
- [ ] 近景没有被无关地点词或全身细节挤占；叙事镜头则有明确地点事实、动作、空间层次与真实光源。
- [ ] 本轮比较只测试了一个主变量，结果与 Prompt 版本、参数、来源/批准状态可追溯。

## 8. 与当前 V2 资产库的关系

`production/midjourney/v2/` 中 1,134 条已登记资产提示词继续是当前唯一的正式生产入口。本文件和其对应的 Prompt Builder 提供的是：

1. 为新女性角色、妆发状态或被退回的肖像建立**可审计探索 Prompt**的规则；
2. 将用户提供的新参考图分解为可迁移原子而不污染角色身份的流程；
3. 让未来新增资产可以在注册进 Catalog 前先按同一视觉语法进行单变量验证。

一旦某条探索 Prompt 被选作正式资产，应以新增版本/记录的方式纳入 V2 Catalog；不可把本模板的方括号或示例文本直接当作已批准的项目交付物。
