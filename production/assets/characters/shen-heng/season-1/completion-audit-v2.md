# 沈蘅第一季角色视觉资产技术审计 V2

审计日期：2026-08-31

## 范围结论

本包完成的是 68 张源图与 68 张 8K 成品的技术整理和机器审计；它们仍是历史候选，不代表已通过当前 V2 风格/身份复核，也不是 Episode Gate 后的逐场成片、对白或镜头交付。Episode Gate 当前为 `OPEN`，未来锁定时应按新输入哈希和逐场绑定复审。

## 要求与证据

| 要求 | 权威证据 | 结论 |
|---|---|---|
| 使用 `raw/` 三张母版保持身份 | `season-1-coverage-plan.json` 中三张 SHA-256；`asset-audit.json` 的 `identityReferenceHashParity` | 技术通过；待 V2 视觉复核 |
| 按项目设定和第一季剧本生成 | `qa/gates/season-gate.json` 为 `LOCKED`；人物源、Gate、输入 manifest 和季级矩阵哈希匹配 | 输入通过；待逐场绑定复核 |
| 梳理完整资产类型 | 9 个正式分类：4 身份、4 表情妆发、10 服装、4 姿态动作、2 道具、6 基础镜头、7 季妆造、6 季证据、25 季叙事 | 通过 |
| 每一种资产独立一张图 | 68 个唯一资产 ID 对应 68 张独立源 PNG；无重复文件名 | 通过 |
| 第一季覆盖 | 36/36 集有妆造与证据；锁定季账本中沈蘅承担 POV、职业动作或集末选择的 23 集全部有独立叙事图 | 通过 |
| 8K 成品 | 68/68 张成品长边为 7680 px，PNG、300 ppi 元数据、保持原宽高比 | 通过 |
| 极致细节、电影感、无噪点方向 | ImageGen 生产提示词锁定材质、物理光、真人古装剧和无颗粒；8K 编译仅 Lanczos3 与轻度结构锐化，不添加噪点 | 通过 |
| 分类存入当前项目 | `source/00-*` 至 `source/08-*` 与对应 `8k/00-*` 至 `8k/08-*`；源图分类路径自动检查 | 通过 |
| 文件完整性 | SHA-256 清单完整、无缺失输出、无空文件、无 `.partial` | 通过 |
| 工程兼容 | 项目单元测试通过；`validate_project.py --scope manifest --strict` 通过 | 通过 |

## Episode Gate / V2 复审重点

- `S1-NV-E24-osmanthus-farewell-tracker`：桂夜空席、病例缺席与下一季追踪。
- `S1-NV-E25-case-map-overlap`：病例位置图与堵渠图叠合复核，不替代余青禾的诊断职责。
- `S1-NV-E31-missing-ledger-route-correction`：接入既有失联表并更正断桥路线，不替代阿沅的建表职责。

## 机器可读证据

- `../asset-manifest.json`：68 张源图/8K 成品路径、尺寸、字节数与 SHA-256。
- `../qa/asset-audit.json`：分类、分辨率、Gate、权威源哈希、母版哈希一致性及叙事覆盖检查。
- `season-1-coverage-plan.json`：38 张季级资产与 E01–E36 映射。
- `../qa/season-1-contact-sheet.jpg`：38 张季级资产视觉联系表。
