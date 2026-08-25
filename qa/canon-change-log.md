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

- **状态**：LOCKED
- **范围**：31 个 Canon 冻结文件、事实登记、依赖矩阵和严格校验器。
- **输入清单**：`qa/gates/input-manifests/canon.json`
- **SHA-256**：`1ADBF9458DB80781FDFED34C06A1B0028F11CE1B8824DF121F38BD8FE328E245`
- **证书**：`qa/gates/canon-gate.json`
- **验证结果**：18 项单元测试通过；`scope=canon`、事实冲突和占位扫描均为 0。
- **审读**：`world-systems-audit` 与 `narrative-continuity-audit` 两个分域角色审读均为 PASS；二者不是外部人工姓名签署。
- **下游约束**：人物基础、季纲、分集和成片不得修改已锁定 Canon；如需变更，必须新增变更记录并重新开启 Gate。
