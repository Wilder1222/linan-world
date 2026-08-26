# MJ-S1-UNIT-BG｜U 槽位与生态群像提示词模板

> 来源：`qa/character-roster.json`、`qa/background-usage.json`。
> U 槽位和 BG 原型在 Season Gate 后仍可替换，不能提前取得具名角色的脸、经历或剧情权力。这里提供的是可执行的 MJ 模板；只有 Episode Gate 把具体槽位绑定到地点、时段、职业状态后，才填写变量并生成。

## 共同原则

- 每个 BG 都是有职业、时段、材质和行动的城市居民，不能是静态“人群装饰”。
- 生成顺序：先做生态服装/动作语言，再在具体剧集绑定时生成单个可识别面孔；不提前创建 300 张英雄肖像。
- 把 `<AGE_BAND>`、`<OCCUPATION>`、`<LOCATION_ID>`、`<TIME>`、`<WORK_STATE>`、`<MATERIALS>` 替换为已绑定原型的字段；不得拿 U/BG 模板替代具名角色。
- 人物模板：`--ar 2:3 --raw --s 50 --c 12 --sref <STYLE_REF_URL>`；环境群像模板：`--ar 16:9 --raw --s 50 --c 10 --sref <STYLE_REF_URL>`。
- 共同排除：`--no fantasy, xianxia, generic wuxia costume, glamour portrait, modern object, modern signage, watermark, logo, readable text`。

## U 槽位（120 个）

### `MJ-U-ARC1-02`｜U-001–030：生活访客

```text
The camera observes an East Asian <AGE_BAND> life visitor in Southern Song Lin'an at <LOCATION_ID> during <TIME>, so a specific everyday errand, one carried object and a realistic reason to pause are clear. The visitor is <OCCUPATION>, wearing practical class-appropriate layers with visible <MATERIALS>; they complete the errand before reacting to the unusual information. Natural local light and a real circulation route, no heroic framing.
```

### `MJ-U-ARC2-03`｜U-031–060：职业问题节点

```text
The camera observes an East Asian <AGE_BAND> <OCCUPATION> facing one concrete work problem at <LOCATION_ID> during <TIME>, so the tool, the work surface, the obstruction and the next practical choice are readable. Their clothing, hands and posture show <MATERIALS> and <WORK_STATE>; they do not possess official, medical, navigation or investigative authority not assigned by the binding. Physical local light, human-scale Southern Song workplace, no heroic pose.
```

### `MJ-U-ARC3-05`｜U-061–090：危机承受者

```text
The camera observes an East Asian <AGE_BAND> <OCCUPATION> navigating <WORK_STATE> at <LOCATION_ID>, so a visible safety constraint, one dependent person or object, and the cost of the route choice are clear. Practical clothing is wet, dusty, raised or layered only as the state requires; <MATERIALS> show real wear. The person acts within ordinary skills and waits, detours or asks for help when necessary. Grounded Southern Song crisis life, no disaster spectacle.
```

### `MJ-U-ARC4-06`｜U-091–120：道德选择触发者

```text
The camera observes an East Asian <AGE_BAND> <OCCUPATION> at <LOCATION_ID> during <TIME>, so one ordinary responsibility, one incomplete record or limited resource, and a choice that leaves a cost are readable. Their stance stays within <WORK_STATE>; a tool or personal item made of <MATERIALS> anchors the decision. No speechmaking and no privileged knowledge, only a visible human-scale choice in Southern Song Lin'an.
```

## BG 生态原型（300 个）

每条对应 `CHR-BG-###` 的 20 人区间。生成时使用相应记录中的年龄段、阶层、地点和班次字段；先用“环境群像版”验证生态，再用“单人锚点版”锁住一个要重复出现的非具名居民。

### `MJ-BG-ECO-01`｜BG-001–020：香药与医药

```text
The camera observes a small working cluster in the Lin'an aromatics-and-medicine ecosystem, so herb packets, paper wrapping, delivery counts and a narrow shop route show a real trade rhythm. East Asian workers of varied bound ages and class bands handle <MATERIALS> in <WORK_STATE> at <LOCATION_ID>; no one looks like a lead character. Natural shop and lane light, wood, paper, ceramic, hemp and powder remain distinct.
```

### `MJ-BG-ECO-02`｜BG-021–040：街食与街坊

```text
The camera observes a Southern Song Lin'an street-food and neighborhood work cluster, so a cooking task, shared bowls, a small credit exchange and a passable lane route are visible. East Asian residents of varied bound ages work with <MATERIALS> at <LOCATION_ID> during <TIME>; crowd density follows <WORK_STATE>, not spectacle. Stove and door light are local, steam, ceramic, wet brick and cloth remain tactile.
```

### `MJ-BG-ECO-03`｜BG-041–060：春台前场

```text
The camera observes the front-of-house ecosystem around Chun Tai, so ticket handling, waiting, food sharing and a safe path between stage entry and night market are clear. Bound East Asian workers and audience members in practical layers use <MATERIALS> at <LOCATION_ID>; no modern venue devices and no starring performer. Lantern and stove light, bamboo, paper, silk and wet stone stay distinct.
```

### `MJ-BG-ECO-04`｜BG-061–080：后台与夜市

```text
The camera observes a backstage-and-night-market labor cluster, so costume repair, cookware cleaning, stall packing and the route under eaves are visible. Bound East Asian workers of varied ages use <MATERIALS> in <WORK_STATE> at <LOCATION_ID>; every person has a practical task, none is posed as decoration. Warm local lamps meet cool ambient night, silk, oilcloth, wood and ceramic remain tactile.
```

### `MJ-BG-ECO-05`｜BG-081–100：书坊、画铺与印刷

```text
The camera observes a book, painting and printing work cluster in Lin'an, so paper drying, block carving, map measuring, thread binding and a customer threshold establish an economy of knowledge. Bound East Asian workers use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; writing is abstract and no map is omniscient. North-window light, paper, ink, wood, silk and glue remain distinct.
```

### `MJ-BG-ECO-06`｜BG-101–120：码头与脚夫

```text
The camera observes a Qiantang dock and porter cluster, so weighing, carrying, waiting for berth and protecting a cargo route are visible. Bound East Asian workers of varied ages and strength work with <MATERIALS> at <LOCATION_ID> during <TIME>; loads have weight and the dock has order. Overcast river light and local dock lamps, wet hemp, wood, iron and bamboo remain tactile.
```

### `MJ-BG-ECO-07`｜BG-121–140：船只、渔业与水居者

```text
The camera observes a riverboat, fishing and water-dweller cluster, so net repair, tide observation, cooking, mooring and a safe boat path are physically clear. Bound East Asian residents use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; boats respect tide, loading and night mooring limits. River daylight and boat lamps, wet timber, rope, water and oilcloth remain distinct.
```

### `MJ-BG-ECO-08`｜BG-141–160：酒肆、客舍与旅人

```text
The camera observes a tavern, guesthouse and travel cluster, so bed registration, meal service, luggage drying and a visible exit route show temporary life without turning it into surveillance. Bound East Asian workers and travelers use <MATERIALS> at <LOCATION_ID>; no one is an all-knowing informant. Door and table lamps, wood, ceramic, cloth, paper and damp cloaks remain tactile.
```

### `MJ-BG-ECO-09`｜BG-161–180：书吏与跑腿

```text
The camera observes a city-clerk and runner ecosystem, so copying, time stamping, carrying sealed papers, waiting for a signature and eating a cold meal fit one real work cycle. Bound East Asian workers use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; an order cannot skip formal sign-off. Window and desk lamp light, paper, ink, rope tags, copper and wood remain distinct.
```

### `MJ-BG-ECO-10`｜BG-181–200：军伍与城门

```text
The camera observes a city-gate guard and soldier ecosystem, so queue control, injury check, gate-chain work, cargo inspection and rest rotation are visible without action fantasy. Bound East Asian workers use <MATERIALS> at <LOCATION_ID> during <TIME>; authority is procedural and limited. Torchlight and rainy daylight, iron, stone, wet wood and oilcloth remain tactile.
```

### `MJ-BG-ECO-11`｜BG-201–220：贸易、仓储与搬运

```text
The camera observes a warehouse and trade-haulage ecosystem, so scale work, grain-sack lifting, sealing, loss recording and a clear loading path demonstrate finite resources. Bound East Asian workers use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; no infinite storage and no unmarked cargo. High-window light and guard lamps, grain, hemp, seal clay, timber and iron remain distinct.
```

### `MJ-BG-ECO-12`｜BG-221–240：寺院与救济

```text
The camera observes a temple and relief ecosystem, so porridge distribution, medicine sorting, hand washing, child care and a fair queue route are visible as skilled work. Bound East Asian residents use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; recipients are active people, not anonymous suffering. Rainy daylight and low practical lamps, bamboo, ceramic, cloth, wet earth and wood remain tactile.
```

### `MJ-BG-ECO-13`｜BG-241–260：北客与安置居民

```text
The camera observes a northern guest and resettlement-resident ecosystem, so bedding, travel bundles, a name-list desk, cooking work and a route choice are visible without reducing people to a crowd. Bound East Asian residents use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; no misery spectacle and no generic refugee tableau. Cloudy daylight, shelter lamps, reed mats, oilcloth, bamboo, paper and mud remain tactile.
```

### `MJ-BG-ECO-14`｜BG-261–280：家务、照料与女性劳动

```text
The camera observes a household-care and women-workers ecosystem, so washing, mending, feeding, accounting, child supervision and a shared working threshold show agency and labor. Bound East Asian residents use <MATERIALS> at <LOCATION_ID> during <TIME>; no ornamental harem imagery and no passive background posing. Window, stove and door light are physical sources; cloth, wood, water, ceramic and paper remain tactile.
```

### `MJ-BG-ECO-15`｜BG-281–300：节庆与公共空间

```text
The camera observes a Lin'an festival and public-space ecosystem, so lamp handling, queue management, food sharing, route marking and public correction can occur in the same believable space. Bound East Asian residents use <MATERIALS> at <LOCATION_ID> in <WORK_STATE>; celebration never erases rain, cost, crowd safety or record keeping. Lantern and ambient night light, paper, bamboo, copper, wet stone and cloth remain distinct.
```

## 单人锚点后缀

当一个已绑定的 BG 需要在多场回访时，追加：

```text
single recurring non-named resident, <AGE_BAND>, <OCCUPATION>, one stable facial-geometry choice selected by human review, the same practical hairstyle and class-appropriate clothing baseline, one work action only
```

生成后记录为该 `CHR-BG-###` 的 `<BG_REF_URL>`；它不得被复用于另一个 BG、U 槽位或具名角色。
