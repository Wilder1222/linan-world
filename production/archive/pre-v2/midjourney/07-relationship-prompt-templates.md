# MJ-S1-REL｜17 条核心关系的视觉提示词模板

> 来源：`relationships/00-emotional-relationship-bible.md` 与 `characters/relations/core/`。
> 关系提示词只能在相关人物身份母版已通过后使用。它们用于探索距离、动作、物件与空间边界；不是 Episode Gate 前的最终双人/群像剧照授权。

## 引用与安全边界

- 当前 MidJourney 的单人物/物件引用能力不能替代双人身份 QA。双人探索应优先让一人正脸、另一人三分之四或背身，并人工检查两人身份；必要时先生成无脸的物件/距离构图。
- 每条只保留一项关系动作：递回物件、让路、站开、拒绝触碰、共同抬物、各自核对记录或公开承担。
- 未明确允许的身体接触不生成。情绪冲突以距离、视线、物件和工作顺序表达，不用相拥或对峙姿势偷换关系进度。
- 基础参数：`--ar 16:9 --raw --s 50 --c 5 --sref <STYLE_REF_URL>`；每条最后追加 `--no fantasy, xianxia, romance-poster pose, modern objects, watermark, logo, readable text`。

## 通用句式

```text
The camera observes [A] and [B] at [a locked location] from [human-scale viewpoint], so [one shared object or route], [physical distance], and [one relationship action] read in that order. [A] is [state]; [B] is [state]. [Physical light] is the source; [materials] remain distinct. grounded Southern Song Lin'an live-action period drama, no unearned reconciliation.
```

## 关系卡

### `MJ-REL-001`｜沈蘅 × 顾行舟｜核心爱情

```text
The camera observes Shen Heng and Gu Xingzhou at the closed threshold of Tingyun Tavern from a side medium-wide view, so one route paper between them, an arm's-length distance, and Gu returning the choice of where to go are readable in that order. Shen keeps one hand on the paper, guarded but listening; Gu stands clear of the exit and does not touch her. Door lamp and table lamp are the only sources, wet wood, paper, ceramic and cloth remain tactile. grounded Southern Song Lin'an live-action period drama, no unearned reconciliation.
```

### `MJ-REL-002`｜柳十四 × 周砚之｜爱情与创作

```text
The camera observes Liu Shisi and Zhou Yanzhi in Chun Tai backstage from a three-quarter medium view, so an unfinished drawing, a removed hairpin, their separated work surfaces and a respectful distance are readable. Liu holds the hairpin instead of posing; Zhou rolls the drawing before asking permission to continue. Cool work light meets warm stage spill, silk, paper, wood and copper remain distinct. grounded Southern Song creative labor, no romantic poster pose.
```

### `MJ-REL-003`｜沈蘅 × 柳十四｜友情与竞争

```text
The camera observes Shen Heng and Liu Shisi at the edge of a night-market passage, so one source slip, their different ways of reading the crowd, and a small space left between them are clear. Shen keeps the slip unclassified; Liu watches the people rather than the paper, neither yields the other's method. Lantern and stove light are local, wet stone, paper and silk remain tactile. grounded Southern Song friendship with disagreement, no forced embrace.
```

### `MJ-REL-004`｜裴九娘 × 顾行舟｜生死旧交

```text
The camera observes Pei Jiuniang and Gu Xingzhou on the working deck of Qingyao from a low natural medium view, so a route map, wet rope, the line of the boat rail and their separate work positions are visible. Pei checks the waterline; Gu leaves the route decision with her and steps back from the rope. Overcast river light and a small bow lamp, wet timber, hemp and oilcloth remain physical. grounded Southern Song river labor, no heroic clasp.
```

### `MJ-REL-005`｜沈蘅 × 陆清和｜母女

```text
The camera observes Shen Heng and Lu Qinghe across the incense-shop counter from a side medium view, so the old incense chest, a bowl of food left to cool, their hands stopping short of the same object and the narrow shop exit are readable. Lu is still doing a household task; Shen preserves the evidence without taking it from her by force. Window light and a rear oil lamp, brass, paper, wood and ceramic remain tactile. grounded Southern Song mother-daughter conflict, no instant reconciliation.
```

### `MJ-REL-006`｜沈蘅 × 沈怀川｜父女与遗产

```text
The camera observes Shen Heng alone with Shen Huaichuan's unfinished manuscript and old incense chest at a worktable, so the absence of the father, the visible page edge and her choice not to invent what is missing are central. Her hand stops above the paper; no ghost, reflection, vision or second person appears. One oil lamp and weak street light, paper, ash, wood and brass remain tactile. grounded Southern Song inheritance and uncertainty.
```

### `MJ-REL-007`｜陆清和 × 沈怀川｜夫妻与旧案

```text
The camera observes Lu Qinghe alone closing the fragrance-shop rear storage after handling Shen Huaichuan's old record, so the absence of her husband, the locked chest, a folded worn garment and the act of putting evidence away are readable. She closes the door without destroying the page; no apparition and no flashback figure. Low oil-lamp light, aged wood, paper, cloth and brass remain physical. grounded Southern Song grief and unresolved history.
```

### `MJ-REL-008`｜沈三娘 × 林阿沅｜养育与放手

```text
The camera observes Shen Sanniang and Lin Ayuan at a Heming Lane wonton stall from a medium side view, so a bowl of hot soup, an account book, a list being carried out and the moment of letting go are readable. Shen steadies the bowl instead of grabbing the paper; Lin accepts the warmth but keeps the list in her own hand. Dawn stove light and cool lane daylight, ceramic, steam, paper, wood and cloth are tactile. grounded Southern Song family labor, no sentimental hug.
```

### `MJ-REL-009`｜黎见山 × 黎令仪｜养父女

```text
The camera observes Li Jianshan and Li Lingyi at a merchant-account table from a restrained medium view, so one favorable ledger page, one copied unfavorable page, a tea cup and the clear space between their hands are readable. Li Jianshan offers a path to safety; Li Lingyi leaves both pages visible rather than accepting a private arrangement. Side-window light and table lamp, paper, ceramic, wood and silk remain tactile. grounded Southern Song care entangled with control, no simplified villainy.
```

### `MJ-REL-010`｜余仲仁 × 余青禾｜师徒与亲情

```text
The camera observes Yu Zhongren and Yu Qinghe at Xiaoji Hall from a medium worktable view, so two separate observation notes, a medicine-cabinet key and the cautious distance of a teaching relationship are clear. Yu Zhongren holds the key but does not hand it over yet; Yu Qinghe points to a recorded observation without claiming a diagnosis. Window light and cabinet lamp, paper, ceramic, wood and cloth remain distinct. grounded Southern Song medicine, no magical cure.
```

### `MJ-REL-011`｜程野老 × 周砚之｜师徒与成全

```text
The camera observes Cheng Yelao and Zhou Yanzhi in Xiling bookshop from a medium map-table view, so a public map, an older seal, a space for the student's name and their different hand positions are visible. Cheng places his seal beside rather than over Zhou's work; Zhou leaves the responsibility line open. North-window light, paper, woodblock, ink and silk backing remain tactile. grounded Southern Song craft mentorship, no triumphant graduation pose.
```

### `MJ-REL-012`｜高问 × 顾行舟｜制度与同袍

```text
The camera observes Gao Wen and Gu Xingzhou at a rain-wet inspection barrier from an eye-level medium-wide view, so a revised order, a route out of frame, their different duties and a practical clearance distance are readable. Gao checks the signature chain; Gu provides risk information but does not take the order from him. Rainy daylight, gate torch, paper, iron, wet wood and oilcloth remain physical. grounded Southern Song civic duty, no action-hero standoff.
```

### `MJ-REL-013`｜顾行舟 × 曹肃｜旧同袍

```text
The camera observes Gu Xingzhou and Cao Su at a city gate from a side medium view, so the newly revised order, gate chain, the space between former comrades and the opening route remain readable. Gu places the revised order where Cao can read it; Cao sees it and reaches for the mechanism without any handshake. Torchlight and rainy daylight, stone, iron, wet wood and paper are tactile. grounded Southern Song professional reconciliation, no martial pose.
```

### `MJ-REL-014`｜高问 × 曹肃｜上下级与守门

```text
The camera observes Gao Wen and Cao Su at a gate inspection table from a human-scale medium view, so the counter-signed order, injury count, queue route and their shared responsibility are clear. Gao leaves the counter-signature visible; Cao waits for the formal revision before ordering the gate opened. Rainy light and torchlight, paper, iron, stone and oilcloth remain distinct. grounded Southern Song procedure under pressure, no rebellious fantasy.
```

### `MJ-REL-015`｜章允中 × 宋惟敬｜程序忠诚

```text
The camera observes Zhang Yunzhong and Song Weijing in the city duty office from a restrained medium view, so a chain of signatures, withheld source papers and an open route board make the mentor relationship visible through procedure. Zhang lays the full chain in public view; Song remains still behind an orderly desk, neither man dramatizes the breach. Cool window light and desk lamp, ink, paper, copper and wood remain tactile. grounded Southern Song administration, no villain confrontation.
```

### `MJ-REL-016`｜贺兰度 × 许含章｜理想与相反选择

```text
The camera observes He Landu and Xu Hanzhang in a northern-return community schoolroom from an eye-level medium-wide view, so an open roster, a relief bundle, two opposing paths through the room and their refusal to decide for another person are clear. He Landu faces the group; Xu Hanzhang protects an individual's space beside the list. Paper-window daylight and a low lamp, bamboo, paper, cloth and wood remain tactile. grounded Southern Song civic disagreement, no romantic pose.
```

### `MJ-REL-G01`｜五信协作群

```text
The camera observes five distinct professional work positions around a shared Lin'an evidence table from a wide human-height view, so separated source packets, multiple map versions, an open correction space and the group refusing a single central stack are readable. Faces are secondary and no individual is meant to be a hero; every person has one different practical tool or record. Window light and table lamps are physical sources, paper, rope, brass, ash, wood and wet map paper remain distinct. grounded Southern Song public collaboration, no superhero-team tableau, no readable text.
```

`MJ-REL-G01` 必须在五位相关人物的身份、服装和单人行动资产全部通过后再执行；若 MJ 无法稳定维持五张面孔，优先将它当作无脸/背身的空间与道具构图参考。
