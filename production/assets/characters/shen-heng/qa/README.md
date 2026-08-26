# 沈蘅资产包质检记录

## 自动检查结果

- 正式源资产：68 / 68
- 正式 8K 成品：68 / 68
- 分类数量：身份 4、表情妆发 4、服装 10、姿态动作 4、道具 2、基础镜头剧情 6、第一季妆造 7、第一季证据 6、第一季叙事 25
- 第一季覆盖：38 个新增 ID 全部存在，E01–E36 共 36 集均有妆造与证据覆盖；锁定季账本中沈蘅承担 POV、职业动作或集末选择的集数均有独立叙事图
- 8K 分辨率：全部文件长边为 7680 px
- 文件完整性：全部非空，并已记录源图与 8K 图的 SHA-256
- 临时文件：0
- 身份参考：三张用户肖像均存在
- 机器可读报告：`asset-audit.json`
- 全量文件清单：`../asset-manifest.json`
- 第一季视觉联系表：`season-1-contact-sheet.jpg`（38 张季级资产，仅用于 QA，不计入正式资产）

## 视觉检查要点

- 主脸以 `ref-identity-primary-front.png` 为绝对母版；中性母版 V1 已移入 drafts，不参与正式输出。
- 发型九宫格采用修订后的 V2；职业动作板采用去除多余人物后的 V2。
- 雨夜剧情图已移除背景中的模糊人物，画面保持单一角色。
- 三视图包含头到鞋的正面、严格侧面和背面；五角度头部板补足正面肖像缺失的侧向结构证据。
- 两张表情板合计覆盖 18 种情绪，统一发型、衣领、妆面和背景。
- 十套服装延续同一色谱与身体比例；受伤造型仅保留左前臂干净包扎，无血腥表现。
- 两张道具板无人物、无文字；材质按玉、木、银、织物、陶瓷、纸、竹、石与铜区分。
- 皮肤统一使用半哑光、区域色调变化和受光面克制高光，未添加颗粒噪点。
- 第一季图像按六个篇章维护连续妆造；关键文字仅保留剧情需要的“今岁无春”“疑报”“事实 / 推断 / 未证”“更正”“今日柳绿”。
- Season Gate 为 `LOCKED`；人物源、Season Gate、输入 manifest 与六份季级矩阵均逐文件核对 SHA-256。Episode Gate 为 `OPEN`，锁定后需复审逐场绑定。

## 验证命令

```powershell
$env:NODE_PATH='C:\Users\ww\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
& 'C:\Users\ww\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' scripts\build-manifest.cjs ..
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate_project.py --scope manifest --strict
```
