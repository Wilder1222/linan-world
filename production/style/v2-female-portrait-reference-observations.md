# VIS-LW-V2｜女性人像参考图原子观察账本

> 参考包：`FPR-SET-20260830-A`
> 状态：`LOCAL-DESIGN-OBSERVATIONS`
> 范围：九张由用户明确指认为本轮对话参考图的 JPEG，仅用于本地设计期的人像、妆发、服装、光线与构图分析。
> 权利与外传：来源、作者、肖像授权、训练/外传许可均未声明；不得自动上传、公开、作为 Midjourney Image Prompt 或 Style Reference。

本文件是 [女性人像参考锁定与编译规范](v2-female-portrait-reference-lock.md) 的图像证据补充。它只记录画面中可观察到的关系，并将推断、不可迁移项和 V2 项目化转译分开。它不是人物身份库，不从任何参考脸提取或合成角色面部身份。

## 1. 本地证据包

为保护本地来源路径与文件名，下面只保留会话内引用 ID、画布和 SHA-256。哈希可验证所分析的字节未变，但不能证明作者、版权、授权、拍摄设备、历史准确性或任何生成服务可用权利。

| ID | 画布 | SHA-256 | 主要可观察角色 | 置信度 |
|---|---:|---|---|---|
| `FPR-01` | 1150×1536 | `cdbba419d7dfcef2449e4cecfaa8eb6920c55e90cbcd358093ac1bf5d04a4408` | 风动日景半身、轻纱、侧后光 | 高 |
| `FPR-02` | 1536×860 | `4f06ef153d265fe284f1faccd6ab0843b1e2145382229384dca40c5f033cdbfd` | 灯火街市半身、服装层次、回望 | 高 |
| `FPR-03` | 860×1536 | `03db42f15f364eacbe70fac2d7e65b888f0fee79d5952788972135025e275e48` | 华丽冠饰近景、金属/玉石受光、前景遮挡 | 高 |
| `FPR-04` | 860×1536 | `a5e594ff750fb2bdede15614d1c8c936d818db0219278a66354d75449ff36b87` | 抬臂定格、轻纱袖摆、暖光方向 | 高 |
| `FPR-05` | 1157×1536 | `fdfccd78adb9acb96a0b1ec010061c63d6eb3178e52ef1e976150bceeab4cfed` | 极近景肤面、眼妆、发丝边光 | 高 |
| `FPR-06` | 1150×1536 | `159684b67cada29c5669e3c5944649a8485d8851ec2d1019f09ef1510620c625` | 窗边暗色衣料、近景回望、柔焦层次 | 高 |
| `FPR-07` | 1150×1536 | `0abf1f8c51d81169611b4bf9553b3d8c8d8090ff3c6b64098f909afa256c29f8` | 高机位斜向构图、袖摆前景、深色/朱红对比 | 高 |
| `FPR-08` | 1150×1536 | `ddb5ff2d96f4366a535512d4b98870dd6637abb182b44cc05e1b307165d92eda` | 冠饰近景、局部金箔/珠光、深青与铜金 | 高 |
| `FPR-09` | 1150×1536 | `0900d7bebbacd42a25f967cf1fe329222f662aae4e5285069467ca27c3ed98d7` | 华丽头饰、反射高光、发丝遮面与眼睛焦点 | 高 |

这些 ID 是本地观察别名，不是 CineWeave 的正式 `ReferenceAsset`。当前环境未发现 `cineweave-studio` CLI，因此没有捏造入库回执或 `ReferenceObservation` schema ID；若要进入可执行生产链，必须在具备运行时的环境重新 ingest / verify，并将下面的原子观察绑定到精确资产。

## 2. 图像级观察与污染边界

| 图组 | 可见的共同机制 | 可迁移到 V2 的内容 | 不能直接迁移 / 原因 |
|---|---|---|---|
| `FPR-01 / 05 / 06`：清透风动近景 | 年轻成年女性的柔和脸部轮廓；乌发主体完整但面颊有少量碎发；暖侧后光在发缘形成细亮；背景强虚化，脸部明亮、边缘柔化 | 三分之四或近正面视线、细长杏眼家族、少量面颊碎发、暖侧后光、浅景深、象牙/灰蓝/茶褐轻层 | 强度很高的柔肤和全画面雾化不作为人类肤面标准；脸不能成为任何角色的身份来源 |
| `FPR-02`：灯火社交半身 | 三分之四半身、回望、灯笼形成暖色散景；象牙外层、深青领缘、局部花枝绣与珍珠/细流苏；人物与环境同处一光场 | 夜市/瓦舍的人物置入、深青领缘 + 象牙轻纱 + 小面积绣花、灯火前景/背景散景、眼睛优先的回望 | 背景文字不可用；低胸内层不能覆盖 V2 完整高交领；不能把所有夜景都做成同一暖色散景 |
| `FPR-03 / 08 / 09`：华丽近景 | 鎏金花丝、细链、珍珠、蓝绿小宝石、黑发高髻、金属与丝绸的差异高光；发丝和首饰穿入前景，脸部仍是第一注意点 | 春台/礼仪可使用主发簪或花丝组件、珍珠枝、细链/流苏、蓝绿小宝石、局部矿物金箔；用方向光让金属出现小亮点 | 顶部大面积冠冕、额前吊饰/宝石、过量链坠与首饰墙不进入 V2；它们会把临安城市女性推向宫廷或幻想角色 |
| `FPR-04 / 07`：舞动与袖摆 | 斜向构图、手臂/袖摆进入前景、身体转向、半透面料受光、朱红与深色面料产生节奏 | 春台、节庆或情绪动作可使用一条有承重的前景袖摆、被灯/日光照亮的薄纱、斜向身体关系 | 静帧不能证明动作时序；漂浮颗粒、露肩/低胸/裸露腰部、无理由的大幅失重纱不是 V2 的日常或正式服装规范 |

## 3. 原子化可见观察

下表按 CineWeave 的角色边界拆开：每个原子只说明一个主角色，避免把同一张漂亮图误用为“脸、衣服、光、构图全都要照搬”的万能源。

| 观察 ID | 主角色 | 可观察证据 | 排除 / 不确定性 | 下游消费者 |
|---|---|---|---|---|
| `FPR-ATOM-FACE-FAMILY` | `face_morphology` | 参考集合反复出现柔和鹅蛋至柔和心形的脸部外轮廓、平顺的颊颌过渡、细长杏眼、自然中等眼裂、柔和的小至中等唇部；脸部常留少量自然不对称 | 仅能建立可探索的形态**范围**，不能建立单一角色脸、真实身份或精确比例；透视和后期柔化会改变比例读数 | `character_explore`、`character_morphology` |
| `FPR-ATOM-SKIN-STYLE` | `skin_material` | 近景中可见暖中性肤色、眼睑/面颊/鼻部轻微暖色、唇部柔润、很平滑的高光滚降和脸部柔焦 | 原图的细节被显著理想化/平滑处理；不能作为“无毛孔”或角色基线肤色的依据 | `appearance_state`、`style_compile` |
| `FPR-ATOM-MAKEUP` | `makeup` | 杏桃至暖赭色眼影集中于上眼睑与眼尾；细长自然眼线；桃珊瑚至柔砖红唇；华丽图有局部不规则金箔或珠光 | 化妆被柔焦和暖光影响，颜色不能当作绝对色样；大面积亮片、厚睫毛和极高饱和红唇不在证据中 | `appearance_state` |
| `FPR-ATOM-HAIR` | `hair` | 乌发/深发色、发顶或髻形有稳定体积；前额、太阳穴、面颊有少量松散细发；侧后光会点亮单根发丝 | 发丝比例在不同图差别很大；“乱发”不是稳定特征，完整主结构必须保留 | `appearance_state` |
| `FPR-ATOM-COSTUME-LIGHT` | `costume` | 多层浅色丝/纱、深青或朱红的局部边缘、花枝绣/提花、宽袖与腰部的分层；金属、珠玉、绣线与丝纱的反光不同 | 若干图有低胸、露肩、悬浮感与重度幻想化饰物；只能转译材料和层次，不照搬轮廓 | `appearance_state`、V2 服装构造 |
| `FPR-ATOM-CAPTURE` | `capture` | 近景到半身、三分之四回望、前景袖摆/首饰/发丝遮挡、浅景深、眼睛清晰、边缘和背景渐进失焦 | 不能从静图断言焦段、光圈、真实相机或运动轨迹 | `director`、`prompt_compile` |
| `FPR-ATOM-LIGHT` | `lighting` | 主光多从侧后方或高处暖向射入；脸部有柔和环境填充；发丝、金属、薄纱边缘出现小亮点；背景通常比脸暗或更虚 | 画外的真实光源/布光设备不可见；所有高光应由临安场景中的日光、窗光、灯火或反射重新动机化 | `scene_light_state`、`style_light_grammar` |
| `FPR-ATOM-COMPOSITION` | `composition` | 人脸并非总居中；人物经常转头、侧目或被袖摆/饰物局部遮住；姿态和前景制造对角线 | 静态图不能证明舞蹈节奏、相机运动或表演过程 | `director`、`prompt_compile` |

## 4. 四个可复用的参考风格档案

### R01｜静风清透肖像

**源**：`FPR-01 / FPR-05 / FPR-06`
**可保留**：轻微转头、温暖侧后发缘、低对比雾灰/象牙背景、乌发局部松散、杏桃薄妆、眼睛为第一焦点。
**V2 转译**：让象牙、淡雾蓝、茶褐或柔青的完整交领进入肩颈画面；使用窗光、低角度日光或浅墙反射解释亮面；皮肤保持区域暖色与适龄纹理，而不是复制磨皮。
**不要带入**：无来源白雾、整个脸的瓷器化抛光、没有结构的长发披散。

```text
soft directional side light, a gentle warm rim through a few face-framing hairs, neutral ambient facial fill, muted ivory and mist-grey layered silk, a quiet three-quarter head turn, eyes in precise focus, progressive focus falloff, controlled optical softness
```

### R02｜灯火社交回望

**源**：`FPR-02`
**可保留**：三分之四半身、人物略偏画面一侧、背后纸灯/人流形成暖色散景、深青领缘与象牙薄纱、珍珠和细流苏的局部亮点。
**V2 转译**：只在实际存在的瓦舍、夜市、楼廊或室内灯火场景使用；暖色必须来自纸灯、油灯、烛火或其反射，远处以低饱和蓝灰平衡。
**不要带入**：不可读/错误招牌、只有灯笼却没有使用者的空城、低胸内搭。

```text
waist-up three-quarter portrait, shoulders angled away and a restrained backward glance, complete crossed-collar ivory silk with a deep smoky-teal collar border, small pearl drops, warm paper-lantern pools behind her, cool muted exterior fill in the distance, occupied circulation softened into optical bokeh
```

### R03｜春台花丝华彩

**源**：`FPR-03 / FPR-08 / FPR-09`
**可保留**：古金花丝、珍珠、蓝绿小宝石、细长流苏、局部金箔、深青/朱红/象牙关系、发丝与首饰的边缘高光。
**V2 转译**：选择一个花丝簪或小型高髻饰物作为主精工点，以珍珠枝/细链/耳饰收束；把宝石和金属压至小面积；让灯或日光产生稀疏可控的亮点。
**不要带入**：大冠冕、额前悬链和宝石、全头铺满金属、无原因的镜面珠宝和全脸亮片。

```text
a coordinated aged-gold filigree hairpin with small pearls and muted blue-green stones, a few fine metal tassels, dark teal collar trim, restrained antique-gold thread, tiny irregular gold-leaf accents near the outer eyes, small controlled highlights on metal and silk
```

### R04｜轻纱斜向动作

**源**：`FPR-04 / FPR-07`
**可保留**：斜向身体关系、抬臂/转身、前景宽袖、朱红与墨色的节奏、被方向光照亮的半透面料。
**V2 转译**：用走位、转身、台上表演、回廊风或船行解释动作与布料；袖摆应有织物重量、与手臂相连、保留完整交领和全袖。
**不要带入**：悬浮火点、白雾、过度裸露、无法承重的披帛或持续“神女化”姿态。

```text
caught at the visible apex of a restrained turn, believable torso rotation and weight shift, one full translucent sleeve crossing the foreground, physically weighted silk following the arm, warm directional light passing through gauze, face and eyes remaining readable
```

## 5. 从参考到临安的编译规则

参考包提供的是**表现语法**，而当前世界需要的是**角色与社会语义**。因此编译时遵循：

```text
V2 Character Canon / locked identity
  + chosen appearance state
  + R01/R02/R03/R04 one reference profile
  + concrete scene facts only when shot needs them
  + V2 physical light and costume construction
  → concise observable MJ prompt
```

- `R01–R04` 不能替代角色姓名、年龄、职业、识别点或已批准的人物母版。
- 同一张参考图的华丽冠饰、肤面平滑、灯光和构图不能一起被当成硬锁；应选择此镜头真正需要的一个或两个原子。
- 近景只用脸/肤面/妆发/肩领/光；全身图转向人体、衣物、腰封、袖摆与承重；叙事图才加入具体的临安地点事实。
- 参考中的“暖金色”是高光和边光的可见关系，不是要求全世界永远处于 golden hour。
- 不使用 `Linan World`、`premium`、`masterpiece`、`8K`、`beautiful lighting` 等词替代上述可见关系。

## 6. 审查与下一步

| 任务 | 当前状态 | 需要的下一步 |
|---|---|---|
| 视觉拆解 | 已完成本地可见观察 | 用 R01–R04 作为 FPRL 变量库 |
| 人物身份 | 未从参考图取得，且不应取得 | 对每个项目角色单独做中性三视图与人工选择 |
| 风格/服装转译 | 已给出 V2 兼容与排除规则 | 通过 `PORTRAIT-LOOK`、`APPEARANCE`、`COSTUME-FULL` 单变量测试验证 |
| 外部生成引用 | 未批准 | 仅在权利、用途和人工批准记录齐全后，由用户手动附加项目生成图 |
| 正式 CineWeave 绑定 | 未创建 | 在可用运行时做 ingest / verify / role-scoped observation / binding；不要用本 Markdown 替代正式合同 |
