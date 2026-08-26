# 沈蘅 ImageGen 提示词集 V1

## 生成模式

- Provider：Codex 内置 ImageGen
- 工作方式：三张用户肖像作为身份参考；最终正面肖像为最高优先级
- 输出原则：一种资产类型单独生成一张图；无文字、无水印、无现代物件
- 表现原则：南宋临安生活感、克制电影光、低噪点、可读材质；不采用仙侠滤镜或塑料磨皮

## 固定参考图

1. `references/ref-identity-primary-front.png`
2. `references/ref-identity-softlight-portrait.jpeg`
3. `references/ref-identity-neutral-side-light.jpeg`
4. 身份扩展时可追加 `source/00-identity/ID-001-neutral-identity-master-v2.png`

## 身份锁定基线

```text
Preserve exactly the same adult East Asian woman's facial identity from the references, with the primary front portrait as absolute authority: elongated soft oval-heart face, gently tapered jaw, large warm-brown almond eyes with a slight upward outer lift, natural straight softly feathered brows, refined narrow nose with softly rounded tip, softly defined peach-coral lips, identical facial spacing and bone structure. Age 22, clearly adult, quiet, observant, gentle yet resilient. Long dark brown-black hair in a restrained Song-inspired half-up structure, clean forehead without forehead jewelry. Pale mist-blue embroidered collar, milk-white layered robe, muted sage waist sash, delicate celadon drop earrings. Light translucent makeup, semi-matte skin with subtle regional tonal variation, restrained highlight following the physical light source, fine natural surface detail, no uniform beauty-filter smoothing.
```

## 统一画面编译基线

```text
Historically grounded Southern Song-inspired Lin'an and Jiangnan costume-drama language; broad motivated key light, restrained warm edge where appropriate, source-consistent eye catchlights, controlled shadow transitions, physical separation of skin, silk gauze, woven cloth, jade, ceramic, paper, wood and metal. Immaculate clarity, very low-noise cinematic finish, no text, no logo, no watermark, no modern accessories, no fantasy crown, no forehead ornament.
```

## 各资产差异项

| ID | 单张图的核心指令 |
|---|---|
| ID-001 | 中性正面胸像；头部直立；五官无遮挡；暖灰背景；均匀柔光；身份结构优先 |
| ID-002 | 五角度头部板；左右严格侧面、左右 3/4、正面；同一表情、妆容和比例 |
| ID-003 | 全身三视图；正面、90° 侧面、背面；头到鞋完整；衣服结构一致 |
| ID-004 | 面部、发际与发丝、右手干粉/纸张痕迹、衣领刺绣和织物微距 |
| EX-001 | 九宫格：平静、自然开心、安慰、关心、克制亲密、羞愧、悲伤、警觉、坚定 |
| EX-002 | 九宫格：恐惧、愤怒、嫉妒、内疚、失望、无助、希望、绝望、释然 |
| MK-001 | 九宫格妆容；底妆轻薄；以眼唇强度、气色和工作状态做单轴变化 |
| HR-001 | 九宫格发型发饰；脸、妆容和衣领完全不变；从日常半束到礼仪、工作、雨夜状态 |
| C01 | 乳白外袍、浅雾蓝绣领、灰豆绿腰封；清洁日常状态 |
| C02 | 窄袖、可操作的工作层次；右手自由；围裙式保护层和工具袋 |
| C03 | 克制的访客造型；稍精致的纹样与小型随身礼盒 |
| C04 | 宋韵正式礼服；端庄层次；不使用夸张凤冠或仙侠头饰 |
| C05 | 深青灰外层；夜间低反光；行动便利但不做刺客装 |
| C06 | 蓝灰防雨外层；衣摆和袖缘可见轻微湿润；肤面不油亮 |
| C07 | 象牙、青灰冬层；真实保暖织物与克制毛边 |
| C08 | 左前臂干净包扎；无血腥；右手继续承担职业动作 |
| C09 | 长时间劳作后的细小褶皱、粉末与纸尘；不做破败化 |
| C10 | 关键剧情特别造型；在固定色谱上增加更深的青与银灰结构 |
| PS-001 | 九宫格基础姿态；正站、侧站、自然坐、转身、俯身观察、蹲取、回望等 |
| PS-002 | 九宫格情绪身体姿态；克制、封闭、警觉、决断、疲惫、释然等 |
| AC-001 | 九宫格单人职业动作；称量、夹取、研磨、筛粉、闻香、记录、核验、封装、收纳 |
| AC-002 | 九宫格通用动作；步行、停步、回身、抬手、递物、取物、坐下、起身、快速离开 |
| PR-001 | 无人物物件板；青玉簪、木簪、耳饰、香囊、信笺套、腰扣、布鞋；材质微距 |
| PR-002 | 无人物工具板；竹镊、试香纸、粉碟、瓷罐、石臼、软刷、空白账册、铜秤、布袋 |
| CAM-001 | 九宫格景别；眼睛特写、脸部、胸像、腰部、3/4、全身、侧面、背面、右手工作特写 |
| NV-001 | 竖幅春日官方角色海报；园池石栏；手持空白香札；冷柔前侧光加暖轮廓光 |
| NV-002 | 横幅香铺工作剧照；右手竹镊、左手空白香札；窗光、瓷罐、秤与香材 |
| NV-003 | 横幅临水回身日景；自然步态；香囊；桥、柳、铺面与水面纵深 |
| NV-004 | 竖幅雨夜线索剧照；单人；油纸伞偏侧；暖灯与冷雨双色结构 |
| NV-005 | 横幅灯下验香；右手试香纸、左手证据纸；油灯暖光与窗外微冷轮廓 |

## 约束说明

- 多格资产必须在同一张图内保持相同脸部几何，不将九个格子画成九个相似人物。
- 三视图、姿态板和动作板不承担电影海报任务，背景与光线保持可读和中性。
- 剧情剧照允许改变天气与色温，但不得改变脸型、眼距、鼻唇比例、年龄感和基础发色。
- 道具板不得出现人物、手、文字或标签。
