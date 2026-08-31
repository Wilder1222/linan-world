# 《临安春信》

这是一个以 Canon、人物关系、Season 因果和可审计视觉生产为核心的项目。当前 P0 Canon、P1 Character Foundation 与 P2 Season Gate 已锁定；P3 E01 Episode Gate 仍开放。

## 从这里开始

- [项目状态与 Gate](qa/production-status.json)
- [Canon 总索引](canon/00-canon-index.md)
- [故事索引](story/00-story-index.md)
- [角色总表](qa/character-roster.json)
- [Season → P3 执行计划](docs/roadmap/2026-08-26-season-gate-and-p3-plan.md)
- [V2 视觉提示词入口](production/midjourney/v2/README.md)
- [E01 生产入口](production/episodes/S1-E01/README.md)

## 权威链

`Canon → Characters / Relationships → Season → Episode → V2 visual production → QA / Gate`

上游锁定输入不可由下游资产反向改写。`raw/` 与 `production/assets/` 保存本地参考和生成候选，不自动进入 Gate 或成为最终交付；必须经过对应的 manifest、QA 和 Gate 证据。

旧版提示词、过期实现计划和明确重复文件已从工作区移除；历史追溯使用 Git 历史与现存 QA 报告。

## 主要目录

- `canon/`：世界、城市、机制与时间事实。
- `characters/`、`relationships/`：人物基础与关系边界。
- `story/`：系列、Season 账本和短章节拍。
- `production/`：V2 提示词、Episode 生产文件和本地资产。
- `qa/`：机器审计、输入 manifest、Gate 证书和状态。
- `scripts/`、`tests/`：确定性物化脚本、审计器和回归测试。

## 校验

```powershell
pytest -q
python scripts/validate_project.py --scope manifest --strict
python scripts/validate_project.py --scope content --strict
node scripts/validate_mj_v8_2_catalog.cjs
python scripts/audit_canon_production_quality.py
```
