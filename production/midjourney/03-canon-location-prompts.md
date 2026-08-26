# MJ-S1-LOC｜18 个 Canon 地点提示词

> 来源：`canon/city/03-...md` 至 `08-...md`。
> 先生成无人物地点母版，确认建筑、动线、材质、职业工作面和光源；人物只在地点母版通过后进入画面。

## 共同参数与状态版模板

地点母版默认：`--ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL> --no fantasy, palace grandeur, modern architecture, neon, modern vehicles, watermark, logo, readable text`。

状态版在母版提示词中只替换一个明确状态块，不改变地点结构：

```text
[STATE: rain] steady rain, queues compressed beneath eaves, oil-paper coverings weighted down, shallow water diverted by practical planks, cooler daylight, door lamps only local
[STATE: night] activity reduced to the stated night use, practical oil lamps and gate lights, dark areas remain dark, no theatrical global glow
[STATE: flood or lockdown] raised goods, a recorded walking route, changed access point and visible labor; no invented shortcut or new secret room
```

## `MJ-LOC-001`｜鹤鸣巷

```text
The camera observes a lived-in Lin'an lane from standing eye level just after rain, so the shared incense shop frontage, wonton stall, umbrella repair stall and narrow water-lane doorways read as one working neighborhood. A charcoal brazier, shallow food bowls, umbrella ribs, paper packets and a practical plank across a puddle show daily use; no named character is present. Cool rainy daylight and small eave lamps; blue-gray brick, wet timber, oil paper, bamboo and mud respond differently. historical Southern Song neighborhood life, no hidden passage, no modern signage --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-002`｜沈家香铺

```text
The camera observes a narrow family incense shop from the street-facing counter, so a brass scale in the front room, a dark wooden storage rack, an ash basin, an old incense chest and the narrow street door are all spatially connected. The counter is set for weighing, sifting ash, sealing paper and writing accounts; the rear storage room is visible but not enlarged into a secret chamber. Window daylight is key, a rear oil lamp is secondary; brass, wood, paper, ceramic and ash are distinct. historically grounded Southern Song small business, no person, no modern laboratory, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-003`｜香药街

```text
The camera observes a tight Lin'an aromatics-and-medicine street at walking height, so shop drawers, oil-paper parcels, rain coverings, a fragrance cart and a narrow turn in the lane establish a dense trade route. A seller's work surface and a porter path share the limited space; price and supply can be read through materials and movement, not magical clues. Low shop lamps meet diffuse street daylight; timber drawers, hemp rope, ceramic jars, oil paper and wet stone are tactile. historical Southern Song commerce, no all-knowing market, no modern pharmacy, no readable signs --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-004`｜御街

```text
The camera observes Imperial Street in Lin'an at a human eye-level wide view, so the ordered stone thoroughfare, paper notices on a public board, delivery path, shopfronts and a route around official traffic remain readable. The street has real bottlenecks for sedan chairs, clerks, porters and pedestrians; revised notices visibly cover but do not erase older paper. Daylight on stone is the key light, shop lamps are local accents; wood signs, paper notices, stone, cloth and horse-worn ground show use. historical Southern Song urban circulation, no palace shortcut, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-005`｜御街夜市

```text
The camera observes a dense Lin'an night market from the edge of a food stall, so a queue, shared eating tables, lanterns, small game stalls and the path toward Chun Tai performance hall are readable without crowding into spectacle. Practical oilcloth covers, bamboo skewers, ceramic bowls, small fragrance packets and damp stone show consumption and conversation; no named people. Lanterns and stove fire form separate warm pools in otherwise dark humid air; bamboo, oilcloth, ceramic, copper and wet paper retain texture. historical Southern Song nightlife, no electric lights, no loudspeaker, no readable signs --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-006`｜春台瓦舍

```text
The camera observes Chun Tai performance hall from backstage looking toward the stage opening, so the repair table, hanging costume sleeves, makeup corner, narrow passage and stage edge establish how people work and move. A copper basin, sewing kit, folded silk, stool and stage receipts show rehearsal and aftercare; the backstage is functional, not a palace dressing room. A warm stage lamp leaks through the curtain while a cooler work light holds the repair table; silk, wood, paper, copper and worn boards are distinct. historical Southern Song performance labor, no fantasy opera effects, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-007`｜西湖画舫

```text
The camera observes a working West Lake pleasure boat from its covered deck at a seated human height, so the table for tea, folded canopy, mooring rope, side rail and weather-facing water remain physically connected. The boat is prepared for travel and conversation, with a practical route dependence on wind and berth rather than luxury excess. Lake daylight and reflected water light are the key sources, a small boat lamp is secondary; damp wood, rope, cloth canopy, ceramic tea ware and water each behave differently. historical Southern Song lake travel, no floating palace, no impossible speed, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-008`｜西泠书坊与画铺

```text
The camera observes a Lin'an bookshop and picture-mounting workshop from a north-window worktable, so a woodblock area, paper-drying line, map-measuring surface, storage chest and customer threshold read as one production space. Knives are put away, paper is raised from damp ground and map versions are physically separated; no person is present. Cool north-window daylight is key and a covered lamp accents wet ink; bamboo paper, mulberry paper, woodblock, silk backing and glue have distinct surfaces. historical Southern Song printing and drawing labor, no magical map, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-009`｜停云酒肆

```text
The camera observes Tingyun Tavern from a table facing the entrance, so shared tables, a keeper's counter, the doorway, a side route toward guest rooms and a practical place to store a knife are visible in one depth line. Bowls, cups, damp cloaks and a spare meal setting suggest travelers, boat workers and officials sharing a room without turning it into a secret chamber. Door-lamp and table-lamp pools shape the night; wood, ceramic, oiled cloth, charcoal and skin-scale wear feel real. historical Southern Song tavern life, no modern bar, no spy-fantasy control room, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-010`｜钱塘码头

```text
The camera observes a Qiantang working dock beside a mooring post at low natural height, so a weighing zone, waiting berth, cargo path, tide marks and repair space communicate actual movement and load. Wooden piles, hemp ropes, bamboo baskets, oilcloth-covered cargo and a small guard lamp show verification, hauling and waiting for tide; no named figure. Clouded river daylight is key, dock lamps only glint locally; salt-stained wood, wet hemp, bamboo, iron and muddy water are distinct. historical Southern Song commerce, no pirate fantasy, no modern harbor, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-011`｜青鹞

```text
The camera observes the transport boat Qingyao from the deck at a medium-wide working angle, so the bow lamp, cargo hold hatch, rope cleats, wet plank path and stern steering space make the vessel's limits understandable. It is a maintained working boat with room for cargo, crew meals and rescue gear only when the water permits; no hero ship decoration. Overcast water is the key light, a covered bow lamp adds a small warm reflection; timber, hemp, iron, oiled canvas and river water stay tactile. historical Southern Song river transport, no impossible speed, no oversized vessel, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-012`｜船坊与水上茶摊

```text
The camera observes a boat-repair shed opening onto a small water tea stall, so a lifted repair plank, tools hung above flood height, a kettle, rope coil and waiting space make shared labor visible. Hammer, saw, boiling water and wood shavings imply a place for repair, waiting and careful conversation; no named person. Side daylight is key, stove fire provides local warmth; timber, iron, hemp, ceramic and river mud have distinct surfaces. historical Southern Song river craft, no miracle repair, no modern machinery, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-013`｜城务司

```text
The camera observes the Lin'an city affairs office from a slightly raised but natural corner of the duty room, so damp maps hanging high, divided ledgers, seal paste, shift plaques and a frequently revised route board reveal a real coordination system. A public-facing petition path and a clerk worktable share the room; there is no unlimited command center. Pale window light gives the key exposure, desk lamps create local pools; paper, rope tags, copper seals, wet wood and ink remain materially distinct. historical Southern Song administration, no modern control room, no unreadable wall of data, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-014`｜三仓

```text
The camera observes the Three Warehouses from a human-scale interior view at an open counting point, so separate official, merchant and relief storage zones, a scale, raised grain sacks, seal clay and fire buckets make accountability visible. The heavy doors, high windows and hauling route show real limits; grain is finite and damage would leave traces. High-window daylight and one guard lamp expose dust and wood grain; earth wall, timber beam, hemp sack, grain, seal clay and iron have distinct texture. historical Southern Song storage and relief logistics, no infinite granary, no fire spectacle, no readable labels --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-015`｜城门、桥闸与查验口

```text
The camera observes a Lin'an gate and bridge-sluice inspection point from the queue's eye level, so the wet bridge planks, identity-check table, gate chain, water mechanism and alternate walking path show why access takes time. A cargo ticket bundle, rope barrier and waiting area make the bottleneck physical; no personal token bypasses the procedure. Rainy daylight is broad, torch and gate lamps are local; stone, wet timber, iron, oilcloth and watergrass are tactile. historical Southern Song civic infrastructure, no grand fortress fantasy, no modern barricade, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-016`｜小济堂与寺院行堂

```text
The camera observes Xiaoji Hall clinic joined to a temple porridge line from a medium-wide human-height viewpoint, so diagnosis bench, medicine shelves, hand-washing point, case-record table, cooking area and patient route are spatially clear. Bowls, ceramic jars, reed mats, cloth partitions and raised medicine bundles show triage and care without declaring a citywide diagnosis. Window daylight and cabinet lamps give practical source light; wood, ceramic, bamboo, cloth and damp paper differ visibly. historical Southern Song clinic and temple relief, no magical medicine, no modern hospital, no readable text --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-017`｜松风客舍

```text
The camera observes Songfeng Guesthouse from a corridor looking toward a registration table, so a bed alcove, cloth partition, luggage shelf, corridor lamp and visible exit route establish privacy and routine. A plain bed ledger, raised travel bundles, wash basin and tea kettle show arrivals, debts and care without making the inn a surveillance machine. Cool corridor daylight meets a weak oil lamp; wood bed, cloth, bamboo basket, paper and damp travel clothes carry everyday wear. historical Southern Song lodging, no modern hotel, no secret archive, no readable guest list --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```

## `MJ-LOC-018`｜城南安置区

```text
The camera observes a Southern Lin'an temporary resettlement area at eye-level wide angle, so raised shelters, public kitchen, water point, child-care corner, name-list desk and drainage path form an understandable living system. Bamboo frames, reed mats, oilcloth, wooden stakes, ceramic bowls and a practical route for moving medicine show residents as active users rather than anonymous crowd decoration. Rainy daylight is key, shelter lamps create only small warm pools; wet earth, bamboo, cloth, wood and ceramic remain tactile. historical Southern Song relief and public health, quiet collective labor, no apocalyptic spectacle, no modern aid equipment, no readable banners --ar 16:9 --raw --s 55 --c 12 --sref <STYLE_REF_URL>
```
