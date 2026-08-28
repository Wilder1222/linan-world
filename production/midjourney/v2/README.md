# 《临安春信》V2 Midjourney 8.2 全量资产提示词

> Catalog: `LINAN-VIS-LW-V2-MJ8.2` · 1131 resolved prompt records · generated 2026-08-28.

This is the V2-only source of active Midjourney prompts. It contains complete V8.2 parameter strings for every declared target in the coverage contract; it does not treat an unbound reference image or a range template as a production prompt.

Every narrative prompt uses the active cinematic New Song visual grammar: motivated daylight or practical lantern light, physical silk/paper/wood/water response, readable working depth and controlled optical softness. Technical continuity tasks deliberately retain clean neutral presentation.

## Start here: central master-reference selection

Run only the twelve `ID-001` prompts in [core-master-reference](core-master-reference.md) first. Each is a text-only, front-facing master-reference selection task. The twelve `HERO-001` prompts are deliberately blocked until the user returns an approved project-generated master render; then attach that approved image manually in the Midjourney web UI and retain the supplied hero text.

## Family counts

- background-archetype: 300
- character: 171
- city-establishing: 3
- episode-shot: 54
- location: 126
- prop-evidence: 12
- relationship: 136
- season-episode: 36
- shen-heng-package: 163
- style-calibration: 10
- unit-slot: 120

## Copyable prompt files

- [core-master-reference](core-master-reference.md) — current first-pass character workflow
- [background-archetype](prompts/background-archetype.md)
- [character](prompts/character.md)
- [city-establishing](prompts/city-establishing.md)
- [episode-shot](prompts/episode-shot.md)
- [location](prompts/location.md)
- [prop-evidence](prompts/prop-evidence.md)
- [relationship](prompts/relationship.md)
- [season-episode](prompts/season-episode.md)
- [shen-heng-package](prompts/shen-heng-package.md)
- [style-calibration](prompts/style-calibration.md)
- [unit-slot](prompts/unit-slot.md)

## Machine-readable artifacts

- `../v2-asset-prompt-catalog.json`: full authority, facts snapshot and copyable text for every target.
- `../v2-asset-prompt-inventory.json`: one-to-one inventory contract.
- `compiled/asset-prompts-v8.2.jsonl`: flat import/export form.
- `validation/prompt-catalog-report.json`: generated coverage report.

## Runtime reference policy

The direct text does not contain a fake style URL or an unsupported identity parameter. After an approved V2 Style Reference or project-generated identity render exists, use the documented optional V8.2 binding policy in the catalog and `production/style/v2-reference-policy.md`; never attach raw user references automatically.
