# 《临安春信》AI 生产与视觉资产

本目录承载从 V2 视觉提示词到 Episode 生产卡、角色资产与 QA 证据的生产文件。Canon、人物事实和 Season 因果仍以各自目录的锁定输入为准。

## 当前状态

- 当前视觉契约为 `VIS-LW-V2`，唯一活动中的提示词入口是 `midjourney/v2/`。
- `episodes/` 保存 E01 试点的生产卡、正式剧本草案、Storyboard 与连续性账本；Episode Gate 仍为 `OPEN`。
- `assets/` 保存本地生成资产及其 manifest/QA 证据。角色包的技术完整不等于已通过 V2 视觉复核或逐场 Episode 绑定。

## 目录职责

- `midjourney/`：V2 提示词目录与视觉生产说明；旧版提示词不再作为活动输入。
- `episodes/`：逐集生产输入与交付草案。
- `assets/`：本地源图、8K 文件、参考图和机器可读审计结果。

## 生产边界

最终对白、镜头、U 唯一身份、BG 微章绑定和可验证媒体证据必须在 Episode Gate 流程中完成。`raw/` 与 `assets/` 中的本地文件不自动进入 Gate 或提交清单，只有被明确纳入并通过 QA 的证据才可提升为交付输入。
