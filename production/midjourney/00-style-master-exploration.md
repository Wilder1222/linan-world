# MJ-S1-STYLE｜第一季风格母版探索

> 目的：先选定“历史落地的真人古装剧”视觉语言，再让人物、地点与道具共享同一风格参考。每条是一个独立探索任务，不拼多格联系表。

## 选择标准

- 人物皮肤是自然皮肤而非磨皮或塑料；头发、衣料、纸、木、陶、铜和湿石材能被清楚区分。
- 光线必须找得到来源：天光、油灯、炉火、门灯或水面反光；不使用泛化全局辉光。
- 临安是高密度生活城市，而非宫殿、仙境或空旷古镇；画面有可使用的门槛、工作面、道路和排水关系。
- 选图时优先稳定的空间、光和材质，人物脸部不作为风格母版的评判对象。

## `MJ-S1-STYLE-01`｜春日香铺，日常材料基线

```text
The camera observes a narrow Southern Song dynasty Lin'an incense shop just after a spring shower, viewed from the street at standing eye level, so the open front counter, the deep workroom, and the damp alley beyond read in that order. A brass scale, shallow ash bowl, paper packets and a dark wooden cabinet sit on a worn timber counter; no person is present. Soft north daylight enters from the street, a small oil lamp only warms the rear shelf; wet blue-gray brick, honey-brown wood, off-white paper, dull brass and matte ceramic each reflect light differently. historically grounded live-action Chinese period drama, restrained color, natural human-scale architecture, no glamour retouch, no fantasy spectacle, no readable text --ar 16:9 --raw --s 60 --c 16
```

## `MJ-S1-STYLE-02`｜雨夜檐下，湿表面与低照度基线

```text
The camera observes a covered Lin'an lane during steady evening rain from just inside a shop doorway, so the dark timber post frames wet stone paving, a line of oil-paper umbrellas, and distant door lamps. No heroic subject; a practical wooden plank crosses a shallow puddle and a closed stall uses weighted oilcloth. Cool rain-diffused sky is the ambient light, small amber door lamps create local pools and reflected highlights only; wet timber, brick, oil paper, bamboo and mud remain materially distinct. historically grounded Southern Song city life, live-action period drama texture, restrained blue-gray and tea-brown palette, no neon, no magical glow, no modern objects, no readable signs --ar 16:9 --raw --s 60 --c 16
```

## `MJ-S1-STYLE-03`｜春台后台，舞台与劳动光基线

```text
The camera observes the backstage of a Southern Song performance hall from a slightly offset medium-wide viewpoint, so a repair table, hanging silk sleeves, a narrow passage to the stage and a dim dressing corner remain spatially legible. A copper basin, thread, folded costumes and a plain wood stool show active work without performers. A warm stage lamp leaks through the curtain while a cooler side window lights the repair table; silk, wood, copper, paper and worn floorboards have separate texture and age. historically grounded live-action Chinese period drama, labor before ornament, restrained realism, no opera fantasy, no modern spotlights, no large readable text --ar 16:9 --raw --s 60 --c 16
```

## `MJ-S1-STYLE-04`｜钱塘水路，潮汐与载重基线

```text
The camera observes a working Qiantang dock at early morning from a low but natural viewpoint beside a mooring post, so wet rope in the foreground, cargo handling space in the middle distance, and tide-marked water behind are readable. Wooden piles, bamboo baskets, oiled cloth cargo covers, a small service boat and a practical weighing area show use and weight; no named character. Overcast river daylight is the key light, one sheltered dock lamp remains weak and warm; wet hemp, dark timber, salt-stained bamboo, dull iron and muddy water respond differently. historically grounded Southern Song commercial waterfront, live-action period drama realism, no pirate fantasy, no towering modern skyline, no text --ar 16:9 --raw --s 60 --c 16
```

## `MJ-S1-STYLE-05`｜危机状态，公共协作而非灾难奇观

```text
The camera observes a rain-soaked temporary relief area in Southern Song Lin'an from a human eye-level wide view, so raised medicine bundles, a public cooking station, a marked walking route and a low shelter line can be understood as one working system. No central hero; the scene is prepared for people to move through it. Rainy daylight is broad and cool, practical lanterns provide only local warm light; bamboo, reed mats, oilcloth, damp earth, ceramic bowls and wet wood show real wear and weight. grounded historical disaster response, quiet collective labor, restrained live-action Chinese period drama, no apocalypse spectacle, no fantasy effects, no modern relief equipment, no readable banners --ar 16:9 --raw --s 50 --c 12
```

## 定版流程

1. 每条各出一轮；只比较同一条内的候选，不混合评价不同场景。
2. 从候选中选 1–2 张共同满足“可用空间、可见材质、有来源的光”的图片。
3. 任选一张作为 `<STYLE_REF_URL>`；若两张分别负责日景与低照度，可在 MJ 中并列添加，日后记录权重。
4. 将选定参考图、日期、模型版本/参数和理由写入 `05-season-1-mj-coverage.md` 的风格母版行；之后不覆盖原选择，只以新版本替换。
