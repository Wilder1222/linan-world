# Canon 变更日志

## CR-001｜项目基线

- **状态**：APPROVED
- **范围**：六篇、36集、648微短章、人物档位和生产顺序。
- **来源**：`docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md`

## CR-002｜Canon 治理与 P0 基础源

- **状态**：APPROVED FOR FOUNDATION REVIEW
- **范围**：稳定 ID、术语、时间锚点、城市、水系、春信、制度、经济、卫生和物质文化文件。
- **原则**：不改变现有世界圣经、36集结局或648章预算；只把隐含规则补成唯一权威源。
- **后续**：Canon Gate 证书签署前，所有事实仍可由双审读者提出修正。

## CR-003｜P0 Canon Gate 输入清单

- **状态**：READY FOR TWO-PERSON REVIEW
- **范围**：31 个 Canon 冻结文件、事实登记、依赖矩阵和严格校验器。
- **输入清单**：`qa/gates/input-manifests/canon.json`
- **SHA-256**：`E397AAC77157F01BB5D4FABBA1D5C8C4CC37E7B1F133D8724CEEA4801C1B834A`
- **验证结果**：17 项单元测试通过；`scope=canon`、事实冲突和占位扫描均为 0。
- **限制**：未伪造人工签名；`qa/production-status.json` 中 `canon_gate` 保持 `OPEN`。
