# Character Foundation 人工审读清单

> 状态：`LOCKED`。Character Foundation Gate 已锁定；后续只允许在 Season/Episode Gate 中写入预留的 U/BG 下游绑定。

当前自动内容审计见 `qa/reviews/character-foundation-audit.json`：84 份人物档案、17 份关系档案与 36 个情感状态锚点均已覆盖，状态为 `REVIEWED-PASS`，自动发现项为 0。关系 Foundation 证据已登记于 `qa/relationship-evidence.json`（17 组 × 8 个快照 = 136 个锚点），但最终 scene/dialogue/shot ID 仍需 Season/Episode Gate 回填；U/BG 的下游绑定仍明确保留给后续 Gate。

B 级年龄与生活圈机器审计见 `qa/reviews/recurring-demographic-audit.json`：状态为 `REVIEWED-PASS`，48/48 具备年龄依据、家庭/关系压力、职业阶段、生活圈、首次日常和结局锚点；职业化生产细节审读见 `qa/reviews/recurring-production-quality.json`：48/48 具备独立日常动作、阻力、盲点、选择、代价、关系余波和结局动作；8 个生活圈各抽 2 人的现场样本审读见 `qa/reviews/recurring-sample-review.json`，16/16 通过。

L/A 状态链机器审计见 `qa/reviews/profile-state-chain-audit.json`：状态为 `REVIEWED-PASS`，36 份档案、360 个状态节点已检查，自动发现项为 0；Season/Episode Gate 只需继续绑定具体集、章、blocking、shot 与 AIGC continuity ID。

逐项跟踪矩阵见 `qa/reviews/character-foundation-review-matrix.json`：12 名中央人物、24 名 A 级重要人物、48 名 B 级常驻、17 条关系证据、6 条情感脊柱与 U/BG 边界均已完成一轮生产级审读并标记 `REVIEWED-PASS`；B 级样本继续作为 8/8 生活圈的现场抽查，而不是全量审读的替代。

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
- [x] B 级全量职业细节与样本：48 人均已确认年龄/生活圈字段、职业动作、现实阻力、角色盲点、主动选择、具体代价、关系余波和结局动作；8 个生活圈各抽 2 人做现场样本复核。
- [x] 17 个关系档案：136 个 Foundation 快照已逐条确认动作、空间、物件和阶段代价推动选择变化；Season/Episode Gate 再回填最终场次、物件、台词和镜头 ID。
- [x] 六条情感脊柱：36 个状态锚点已确认混合情感、主动选择、不可逆代价、关系余波且不会自动和解。
- [x] U/BG 登记：`qa/reviews/u-bg-boundary-audit.json` 已确认 120 个 U 槽位保持可替换、22 个 POV 槽位/44 个候选/40 个自然回访候选不变；300 个 BG 原型均有地点、时段和劳动状态字段，具体微章/扩展绑定仍为空并保留给 Episode Gate。

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

只有机器校验通过、人工清单全部勾选、`qa/reviews/u-bg-boundary-audit.json` 为 `PASS` 且阻断项为 0，才可生成 `qa/gates/character-foundation-gate.json` 并锁定下一阶段依赖。锁定后仍不得在 Season/Episode Gate 前写死 U 身份或 BG 微章绑定。
