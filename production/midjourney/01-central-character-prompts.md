# MJ-S1-CHR｜12 名中央人物提示词

> 来源：`production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md`。
> 这些是身份母版探索提示词，不是已完成资产的声明。除沈蘅外，先不把未选定的面部细节写入 Canon；从候选中人工选定后才创建 `<CHAR_REF_URL>`。

## 共同生成方式

每张角色母版只生成一个人物。第一轮使用“探索提示词”；锁定一张合格身份图后，把它放入 MJ 的 Omni/Character Reference 槽，并以同一段主体提示词补齐服装、姿态和场景资产。

**探索参数**：`--ar 2:3 --raw --s 60 --c 15`
**锁定后参数**：`--ar 2:3 --raw --s 55 --c 3 --sref <STYLE_REF_URL>`，并在参考槽加入 `<CHAR_REF_URL>`。
**共同排除**：`--no fantasy, xianxia, wuxia pose, glamour studio portrait, plastic skin, modern clothing, modern objects, watermark, logo, readable text`

### 独立资产后缀

每个角色的资产应在相同主体提示词后追加一个后缀，分别单独生成：

- `ID-001`：`three-quarter full-body neutral work stance, both hands visible, feet grounded, no action flourish --ar 2:3`
- `ID-002`：`head and upper torso at a three-quarter angle, neutral expression, hairline and ears visible, face is the primary target --ar 3:4`
- `ID-003`：`full body profile-to-three-quarter turn, plain background, garment silhouette and practical shoes visible --ar 2:3`
- `ACT-001`：`one profession-specific action only, one eye-line change, weight visibly carried by the correct hand or stance --ar 16:9`

不要把 `ID-001`–`ACT-001` 拼在同一张“九宫格”里。每张通过后再由本地清单组装联系表。

## `MJ-CHR-L1-01`｜沈蘅

现有身份资产已完成；将 `production/assets/characters/shen-heng/source/00-identity/ID-001-neutral-identity-master-v2.png` 上传并记录为 `<CHAR_REF_URL>`。新的季节、行动和剧情资产应复用该参考，不重新探索脸。

```text
The camera observes Shen Heng, a 22-year-old adult East Asian incense-material verifier, in a narrow Lin'an fragrance workshop at a three-quarter full-body distance, so her slightly elongated soft oval-to-heart face, warm brown almond eyes, clean forehead, dark brown-black half-up Song-style hair, slim steady build and powder-marked right fingertips are legible before the worktable. She pauses just before smelling a sample with tweezers, breath held briefly; one hand steadies a paper edge and the other keeps the tool suspended. Pale mist blue, milk white and gray bean-green spring work layers, a small celadon jade teardrop earring, no excessive ornament. North daylight is the key light, a rear oil lamp only warms the shelf; skin, paper, wood, ceramic and brass remain physically distinct. grounded Southern Song Lin'an live-action period drama, evidence-first restraint --ar 2:3 --raw --s 55 --c 3 --sref <STYLE_REF_URL> --oref <CHAR_REF_URL>
```

`ACT-001` 使用：`cutting a small incense sample and leaving a measured ash record, gaze moves object to hand to person`。

## `MJ-CHR-L2-01`｜陆清和

```text
The camera observes Lu Qinghe, a 45-year-old East Asian woman who runs a Lin'an incense shop, at a practical full-body distance in the shop's front room, so a mature oval-round face, fine lines at the eyes and mouth, a few early gray strands in a neat low bun, strong knuckles and the posture of long daily labor read before the room. She is not posing: one hand locks a cash box while the other smooths a paper corner, listening without looking up. Worn layered work clothing in muted tea brown, smoke gray and softened indigo, modest functional hairpin, no luxury display. Window daylight crosses the counter; a small oil lamp catches only the brass scale. natural skin texture, used fabric, paper, timber and brass, historically grounded Southern Song domestic commerce --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`turning down a lamp wick and closing the narrow shop door after checking the street`。

## `MJ-CHR-L1-05`｜顾行舟

```text
The camera observes Gu Xingzhou, a 29-year-old East Asian tavern keeper familiar with water-and-land escort routes, from a medium full-body viewpoint inside a modest Lin'an tavern, so his above-average height, stable shoulders and back, clean practical silhouette, shallow old brow-bone scar and steady hands read before the doorway. He stands where he can see the exit, quietly moving a knife away from a table before setting down a cup; his body is low-centered rather than theatrical. Dark tea, weathered charcoal and subdued blue work layers, simple belt, no noble ornament. A door lamp gives the key light and a table lamp warms his hands; wood, ceramic, damp oiled cloth and skin are natural and distinct. grounded Southern Song live-action drama, protective attention without domineering pose --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`drawing a water-and-land route with one finger on a plain paper map, then returning the choice to someone off frame`。

## `MJ-CHR-L1-02`｜柳十四 / 柳望舒

```text
The camera observes Liu Shisi, also called Liu Wangshu, a 24-year-old East Asian lead performer at Chun Tai performance hall, from a three-quarter full-body backstage view, so a supple but sharp facial structure, alert mobile eyes, long light frame and the contrast between stage poise and private restraint are readable. She is midway through removing one hair ornament after a performance, not smiling for an audience; one sleeve is being straightened with practiced precision. Refined but work-worn silk layers in muted pomegranate, ink blue and old ivory, stage makeup visibly lighter around the eyes and lips but never modern glamour. Warm stage spill meets a cooler backstage window; silk, copper, wooden floor and skin have separate texture. historically grounded Southern Song theater labor, live-action realism, no courtesan stereotype --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`scanning an audience from the stage edge, then letting the public smile disappear when she turns backstage`。

## `MJ-CHR-L1-03`｜周砚之

```text
The camera observes Zhou Yanzhi, a 26-year-old East Asian draftsperson and structural recorder, at a medium full-body distance beside a Lin'an bookshop drawing table, so his lean build, slightly narrow shoulders, fine clear features, ink-marked hands and orderly clothes read with the rolled map. Before speaking he pauses, pressing the paper edge flat and checking the boundary of the room. Clean but modest gray-blue and off-white scholar-work layers, no ceremonial rank. North-window daylight is the main light; a covered lamp gives a small reflection to wet ink. Bamboo paper, wood, silk map backing and ink are visibly different. grounded Southern Song technical labor, live-action period drama, no romantic scholar pose --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`measuring a passage with a cord, then rolling the map tighter when an inconsistency is found`。

## `MJ-CHR-L1-04`｜裴九娘

```text
The camera observes Pei Jiuniang, a 30-year-old East Asian water-route transport leader, on the deck of a working riverboat from a medium full-body viewpoint, so her sturdy agile frame, outdoor-weathered skin, low center of gravity and rope-worn hands are clear before the river. She checks water level, a rope knot and a plank seam in that order, one boot taking real weight on wet boards; she does not pose as a fighter. Practical blue-green and smoke-brown layered river work clothes, sleeves tied back, hair secured low, no ornamental armor. Overcast river daylight is key; a covered boat lamp adds a small warm reflection. Wet timber, hemp rope, iron fastening, oiled cloth and water have distinct physical surfaces. grounded Southern Song commercial transport, live-action realism --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`tightening a mooring line while looking first at the waterline, then at the person waiting to board`。

## `MJ-CHR-L2-02`｜林阿沅

```text
The camera observes Lin Ayuan, an 18-year-old East Asian market observer, from a practical three-quarter full-body view at the edge of Heming Lane, so her quick everyday presence, loose strands of hair, flour-and-rain-marked hands and attentive eyes are readable before the crowd. She is folding an oil-paper packet while her eyes track a small change in a neighbor's routine; her body leans forward with curiosity but remains occupied by work. Light layered clothing in softened green, clay beige and faded blue, inexpensive and mobile, no elaborate hair ornaments. Spring overcast daylight is key, a nearby stall fire warms only the lower edge. Paper, flour, damp cloth, wood and skin remain tactile. grounded Southern Song neighborhood life, lively but not childish, live-action drama --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`counting familiar customers' meal bowls, then quietly correcting a note before passing it on`。

## `MJ-CHR-L2-03`｜余青禾

```text
The camera observes Yu Qinghe, a 23-year-old East Asian healer, at a medium full-body distance inside a small clinic, so a neat clear face, hands marked by medicine powder and ink, controlled diagnosis pace and practical posture are readable before the medicine cabinet. She asks about water and time while comparing a small record with a patient's visible condition; her chin lifts slightly under challenge but the hands slow down. Clean restrained gray-green and warm off-white medical work layers, sleeves clear of the work surface, no magical healer imagery. Window daylight and a low medicine-cabinet lamp create believable source light. Ceramic jars, paper, wood, cloth and skin show distinct roughness. grounded Southern Song medical labor, live-action period drama --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`sorting observations, tentative judgment and diagnosis into separate areas of a plain case record`。

## `MJ-CHR-L2-04`｜高问

```text
The camera observes Gao Wen, a 34-year-old East Asian lower-level city official, from a medium full-body view in a Lin'an duty office, so his durable non-heroic build, tired face from late work, important waist token and the weight of clerical responsibility are visible before the desk. He places two dispatches side by side, pauses over the signature space, and removes the waist token only at the edge of a moral decision. Muted official work layers in charcoal, dusty blue and faded brown, practical rather than ornate. Cool window light is key, an oil lamp marks ink and seal paste locally. Paper, copper, worn wood, damp map and skin are natural and distinct. grounded Southern Song administration, weary wit without caricature --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`checking the number of injured and available people before publicly signing a revised gate order`。

## `MJ-CHR-L3-01`｜宋惟敬

```text
The camera observes Song Weijing, an East Asian man over 40 who represents the city-wide order system, from a composed medium full-body distance in a map-filled duty room, so his clean restrained appearance, sharp controlled presence, minimal movement and precisely ordered desktop are visible before any expression. A report contradicts the current plan; he rechecks its time, source and paper edge without theatrical anger. Severe but not villainous official clothing in deep ink, dried tea and muted slate, no excessive insignia. Pale window light defines the desk; a single oil lamp makes small highlights on the seal and wet map. Wood, paper, copper and cloth carry practical wear. historically grounded Southern Song bureaucracy, live-action realism, no evil-smirk stereotype --ar 2:3 --raw --s 55 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`aligning several reports by timestamp, then stopping when a local witness account will not fit the central summary`。

## `MJ-CHR-L3-02`｜黎见山

```text
The camera observes Li Jianshan, an East Asian merchant-route leader around 50, from a medium full-body viewpoint at a private trading table, so his broad gentle presence, smile lines, careful but unshowy dress and polished social control are readable before the tea service. He offers a way out while placing a tea cup down a little too firmly; the smile remains but the eyes deepen. Layered merchant clothing in muted warm brown, ink green and aged ivory, good fabric but no ostentatious wealth. A side window provides soft key light, a table lamp catches tea glaze and paper fibers. Silk, worn wood, ceramic, paper and skin remain realistic. grounded Southern Song commerce and social obligation, live-action drama, no obvious villain coding --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`rechecking a trade route ledger while leaving one unfavorable page visible instead of covering it`。

## `MJ-CHR-L3-03`｜贺兰度

```text
The camera observes He Landu, a 28-year-old East Asian organizer within the northern-return community, from a medium full-body eye-level view in a crowded schoolroom or relief meeting space, so his upright stance, direct gaze and ability to stand at the center of a group are clear without making him a heroic icon. He begins by addressing the group, then stops and turns to ask one person their name; hands are open but not raised in a speech pose. Simple well-kept layers in deep blue, weathered brown and off-white, no military fantasy costume. Broad daylight enters through paper windows, one practical lamp warms a record board. Bamboo, paper, worn cloth and wood remain tactile. grounded Southern Song civic life, sincere idealism with human limits, live-action realism --ar 2:3 --raw --s 60 --c 15 --sref <STYLE_REF_URL>
```

`ACT-001` 使用：`giving space for individual names to be entered into a public list rather than speaking over them`。
