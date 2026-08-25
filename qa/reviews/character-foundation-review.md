# Character Foundation 人工审读清单

> 状态：`OPEN`。机器校验已通过，但 Gate 尚未锁定。以下审读必须在进入 Season Gate 前完成。

当前自动内容审计见 `qa/reviews/character-foundation-audit.json`：84 份人物档案、17 份关系档案与 36 个情感状态锚点均已覆盖，自动发现项为 0。关系 Foundation 证据已登记于 `qa/relationship-evidence.json`（17 组 × 8 个快照 = 136 个锚点），但最终 scene/dialogue/shot ID 仍需 Season/Episode Gate 回填；年龄推定与 U/BG 下游绑定仍需人工/后续 Gate 确认。

B 级年龄与生活圈机器审计见 `qa/reviews/recurring-demographic-audit.json`：48/48 已检查，自动发现项为 0；8 个生活圈各抽 2 人的人工样本审读见 `qa/reviews/recurring-sample-review.json`，16/16 通过；其余 32 人仍保留为扩展审读对象。

L/A 状态链机器审计见 `qa/reviews/profile-state-chain-audit.json`：36 份档案、360 个状态节点已检查，自动发现项为 0；人工仍需确认每个状态的动作、空间、信息状态和关系移交能直接转译为镜头执行。

逐项跟踪矩阵见 `qa/reviews/character-foundation-review-matrix.json`：12 名中央人物与 24 名 A 级重要人物已完成一轮生产级审读并标记 `REVIEWED-PASS`；B 级样本已覆盖 8/8 生活圈，17 条关系和 6 条情感脊柱仍保持 `REVIEW-PENDING`，不得将机器通过误报为 Gate 已关闭。

## 审读标准

每名 L/A 人物逐项确认：

- 身份、职业、年龄与南宋生活常识不冲突；
- 稳定欲望、阴影欲望、坚守与缺陷来自同一生活逻辑；
- 七问中的“放弃什么”是安全、名声、收入、店铺、归宿、爱情、家人理解、政治前途、旧信念或回家机会之一，而不是泛泛“受伤”；
- 十个状态节点都能写出目标、误判、选择、代价、关系变化和下一状态移交；
- 情绪能由呼吸、视线、面部张力、手部、重心、距离和行动表现；
- 至少两条非中央关系会改变人物选择，且关系同时保留爱/怨、感激/嫉妒、依赖/抗拒或责任/逃避等混合情感；
- 不依赖隐藏血统、突然能力、全知信息、廉价和解或主角光环；
- 现代观众可识别的边界、照护、职业理想、信息失真、迁徙和选择权，必须通过宋代身份与活动转译，不出现现代网络词。

每名 B 人物逐项确认：

- 首次日常场景不以给主角递线索为唯一目的；
- 职业能力在早期已展示，终局回响只是能力的公共协作，不是临时升级；
- 现实压力、收入和关系债务具体可见；
- 终局职业回响不清除旧账，也不把人物封成“群众英雄”。

## 当前待审条目

- [x] 12 名中央人物：已逐人完成动作/情绪/选择链审读。
- [x] A1-A3 批次 24 名重要人物：已逐人确认独立目标、代价和与中央人物的非替代性。
- [x] B 级样本：8 个生活圈各抽 2 人，确认年龄推定、职业流程和非中央关系真实可演；其余 32 人保留扩展审读。
- [ ] 17 个关系档案：Foundation 证据锚点已补入；人工确认七维状态与八个快照的证据是否真的改变人物选择，Season/Episode Gate 再回填最终场次、物件、台词和镜头 ID。
- [ ] 六条情感脊柱：确认 36 个状态锚点不会自动和解，且每篇至少有一项不可逆代价。
- [ ] U/BG 登记：确认 U 尚未提前获得唯一故事身份，BG 每次使用均能绑定地点、时段和劳动状态。

## 阻断项规则

出现以下任一项，Character Foundation Gate 保持 `OPEN`：

1. 任一人物需要改名、改档位、改 POV 预算或改关系 ID；
2. 任一状态节点只有情绪形容词，没有可观察动作和选择代价；
3. 任一关系被写成单一“好感度”或一次性和解；
4. 任一 U/BG 记录被提前写成主线既成事实；
5. 任一审读发现与 Canon 事实冲突。

## Gate 关闭前命令

```powershell
python scripts/validate_characters.py --stage foundation --strict
python scripts/validate_project.py --scope character-foundation --strict
python scripts/audit_character_content.py
python scripts/audit_recurring_demographics.py
python scripts/audit_profile_state_chains.py
python scripts/build_character_foundation_review_matrix.py
python -m unittest discover -s tests -q
```

只有机器校验通过、人工清单全部勾选、阻断项为 0，才可生成 `qa/gates/character-foundation-gate.json` 并锁定下一阶段依赖。
