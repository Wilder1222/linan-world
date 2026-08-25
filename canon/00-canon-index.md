# 《临安春信》Canon 内容索引

> 顶层权威：`docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md`
>
> 当前状态：`LOCKED`。31 个 Canon 冻结文件已通过确定性校验、双角色分域审读和 Canon Gate 证书锁定；不得反向覆盖顶层规格。

## 已纳入的基础源

世界、时间、城市、水系、春信、制度、经济、公共卫生、语言与物质文化已经拆成 31 个稳定输入文件，完整清单与冻结顺序见 `qa/gates/scope-definitions/canon.json`。本索引只做入口，不复制专项文件的第二套规则。

| 稳定范围 | 状态 | 机器校验 |
|---|---|---|
| 世界与主题 | LOCKED | `canon/01-world-bible.md` |
| 城市、水系与地点 | LOCKED | `canon/02-linan-city-atlas.md`、`canon/city/` |
| 春信与灯号 | LOCKED | `canon/03-spring-letter-system.md`、`canon/system/` |
| 历史与时间 | LOCKED | `canon/04-history-and-timeline.md` |
| 制度、经济与健康 | LOCKED | `canon/05-government-economy-and-daily-life.md`、`canon/institutions/` |
| 语言与物质文化 | LOCKED | `canon/06-language-and-material-culture.md` |

## 来源

- 来源文件：`D:\Downloads\linan-spring-letter-complete-world-v7.zip`
- SHA-256：`28018006FABE68D4EA4AEF5D579EBFD7303DA37C5B8ECB07728808CCF3918EE9`
- 审阅记录：`docs/reviews/2026-08-24-v7-zip-integration-review.md`

## C0 权威顺序

批准的总规格与本索引优先于专项 Canon；专项 Canon 优先于人物与关系档案；人物与关系档案优先于 36 集季纲；季纲优先于 648 个微短章；扩展卡只能补充，不能反向改写前述事实。Markdown 是解释视图，跨文件连续性读取 `qa/canon-fact-registry.json`。

## Canon 文件地图

| 稳定范围 | 权威文件 | 下游使用 |
|---|---|---|
| 世界边界与主题 | `canon/01-world-bible.md` | 所有人物与故事 |
| 城市空间和水系 | `canon/02-linan-city-atlas.md`、`canon/city/` | 分集、行动、分镜 |
| 春信机制 | `canon/03-spring-letter-system.md`、`canon/system/` | 线索、悬疑、公共信息 |
| 历史时间 | `canon/04-history-and-timeline.md` | 年龄、事件顺序、节气 |
| 经济与制度 | `canon/05-government-economy-and-daily-life.md`、`canon/institutions/` | 权力、供应、灾害因果 |
| 语言与物质文化 | `canon/06-language-and-material-culture.md` | 对白、服化道、职业动作 |

所有 Canon 文件进入人物、季纲和微短章前，必须通过 `python scripts/validate_project.py --scope canon --strict`。
