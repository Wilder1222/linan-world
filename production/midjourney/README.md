# 《临安春信》MidJourney 资产提示词库

> 版本：MJ-S1-PROMPT-V1 · 2026-08-26
> 范围：第一季人物、地点、道具、证据板与资产生成流程。
> 上游：`qa/character-roster.json`、`story/season/season-causal-ledger.json`、`canon/city/`、`production/ai/v6-character-asset-bible/`。

## 使用顺序

1. 先执行 `00-style-master-exploration.md` 的独立探索任务，人工选定一张风格母版并上传 MidJourney；记录为 `<STYLE_REF_URL>`。
2. 使用 `01-central-character-prompts.md` 生成每个中央人物的独立身份母版。每次只生成一个人物、一个角度或一个状态；选定后记录为该角色的 `<CHAR_REF_URL>`。
3. 使用 `02-supporting-character-prompts.md` 进行配角的身份探索。配角未被 Canon 锁定的脸部几何必须在人工选图后才写入资产卡。
4. 使用 `03-canon-location-prompts.md` 生成无人物的地点母版和状态版；人物进入场景前先锁定地点的空间关系、主光和材质。
5. 使用 `04-prop-evidence-prompts.md` 生成单件道具和证据组。关键道具要分别保留完好、使用/标记、受损/封存状态。
6. 只有在人物、地点和道具母版已经通过人工核验后，才生成双人、群像或剧照；其精确镜头仍须等待 Episode Gate。

## MidJourney 参数约定

- 本库默认使用当前 MidJourney 默认模型；提示词不把模型版本写死。视觉测试可加 `--raw`，以降低默认风格对事实细节的改写。
- `--ar` 是交付画幅：身份近中景 `3:4`，全身 `2:3`，地点/叙事 `16:9`，道具/证据 `3:2`。
- 母版探索可用 `--c 12–20`；选中方向后，资产正式生成降为 `--c 0–5`。`--s 40–100` 用于事实优先的人物、道具和空间；不以高 stylize 代替设计判断。
- `<STYLE_REF_URL>` 是人工选定的风格参考。网站端放进 Style Reference 栏；Discord 端以 `--sref <STYLE_REF_URL> --sw 100` 绑定。
- `<CHAR_REF_URL>` 是人工选定的单人身份母版。网站端放进当前模型提供的 Omni/Character Reference 栏；使用支持 Omni Reference 的 Discord 工作流时，以 `--oref <CHAR_REF_URL>` 绑定。不要把服装状态、场景图片当成永久身份参考。
- `<IMAGE_REF_URL>` 仅用于需要保留构图或物件几何的 Image Prompt，放在文本最前；它不是风格或人物身份的替代品。

MidJourney 的 Style Reference、Image Prompt 与人物/Omni Reference 都是“引导”而非逐像素复制；所以每个正式资产仍需做身份、地理、道具和文字 QA。参数与引用槽的当前用法以 [MidJourney 官方 Style Reference 文档](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)、[Image Prompts 文档](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts) 和 [Omni Reference 文档](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference)为准。

## 固定约束

**必须保留**：南宋临安的生活尺度；职业动作来源；人物年龄、身份和关系边界；地点的通行逻辑；纸、木、织物、陶、铜、绳与湿表面的材质差异；自然且有来源的光。

**可探索**：未锁定人物的面部几何、五官组合、局部服装纹样与非关键陈设；这些必须经过人工选图后才能成为母版。

**必须避免**：仙侠/玄幻符号、悬浮特效、现代建筑和电子设备、网红滤镜、塑料皮肤、泛化武侠姿势、无来源的可读大段文字、水印与商标。文本是关键剧情信息时，先出无字版，再在后期排版正确文字。

## 命名与记录

每次任务在资产清单中记录：`prompt_id`、版本、输入参考图 URL、MJ 参数、生成日期、候选格、人工选择、输出文件、SHA-256、QA 结论。示例：

```text
MJ-CHR-L1-05-ID-001-v1 | <STYLE_REF_URL> | <CHAR_REF_URL> | --ar 3:4 --raw --s 60 --c 3
```

不要依赖 seed 作为身份一致性证明；使用参考图、可见结构锚点和人工 QA 记录连续性。

## 提示词库索引

- [风格母版探索](00-style-master-exploration.md)
- [中央人物提示词](01-central-character-prompts.md)
- [季纲配角提示词](02-supporting-character-prompts.md)
- [18 个 Canon 地点提示词](03-canon-location-prompts.md)
- [关键道具与证据提示词](04-prop-evidence-prompts.md)
- [沈蘅第一季关键叙事提示词](05-season-narrative-prompts.md)
- [第一季提示词覆盖矩阵](06-season-1-mj-coverage.md)
- [核心关系视觉提示词](07-relationship-prompt-templates.md)
