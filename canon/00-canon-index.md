# 《临安春信》Canon 内容索引

> 顶层权威：`docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md`
>
> 当前状态：`FOUNDATION-REVIEW-READY`。本目录内容已通过确定性校验并生成 Canon Gate 输入清单，正式锁定仍需两位独立审读者签署；不得反向覆盖顶层规格。

## 已纳入的基础源

| 文件 | 内容 | 状态 |
|---|---|---|
| `canon/01-world-bible.md` | 临安八个生活系统、危机放大回路、武侠边界、生活优先原则、后续地域扩展 | FOUNDATION-DRAFT |

## 仍需补齐的 Canon 文件

时间轴、城市图谱、水系与旅行时间、春信协议、官署权限、经济与公共卫生、语言及物质文化，按 Canon 计划继续拆分；本次扩展包没有足够结构化字段替代这些机器可验证文件。

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
