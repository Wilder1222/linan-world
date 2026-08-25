from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "qa/gates/scope-definitions/p3-pilot-e01-e03.json"
MANIFEST_PATH = ROOT / "qa/gates/input-manifests/p3-pilot-e01-e03.json"
REPORT_PATH = ROOT / "qa/reviews/p3-pilot-input-freeze-review.json"
PILOT_EPISODES = ["S1-E01", "S1-E02", "S1-E03"]
PILOT_CHAPTER_IDS = [f"{episode_id}-M{index:02d}" for episode_id in PILOT_EPISODES for index in range(1, 19)]
INPUT_PATHS = [
    "qa/gates/season-gate.json",
    "qa/gates/input-manifests/season.json",
    "story/season/season-causal-ledger.json",
    "story/season/mystery-reversal-matrix.json",
    "story/season/song-life-activity-matrix.json",
    "story/season/humor-register-matrix.json",
    "story/season/short-chapter-hook-map.json",
    "story/season/u-candidate-selection.json",
    "qa/reviews/season-gate-exception-ledger.json",
    "production/ai/v6-character-asset-bible/README.md",
    "production/ai/v6-character-asset-bible/00-system/01-character-asset-bible-master-standard.md",
    "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md",
    "production/ai/v6-character-asset-bible/02-expression/expression-asset-standard.md",
    "production/ai/v6-character-asset-bible/03-pose-motion/pose-motion-asset-standard.md",
    "production/ai/v6-character-asset-bible/04-costume/costume-system-standard.md",
    "production/ai/v6-character-asset-bible/05-voice/voice-dialogue-standard.md",
    "production/ai/v6-character-asset-bible/06-relationship/relationship-state-standard.md",
    "production/ai/v6-character-asset-bible/07-continuity/continuity-ledger-standard.md",
    "production/ai/v6-character-asset-bible/08-prompt-templates/aigc-character-prompt-system.md",
    "production/ai/v6-character-asset-bible/09-production-workflow/linan-standard-sop.md",
    "production/ai/v6-character-asset-bible/10-episode-gate/episode-delivery-gate.md",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate() -> list[dict]:
    findings: list[dict] = []
    season_gate = ROOT / "qa/gates/season-gate.json"
    production_status = load(ROOT / "qa/production-status.json")
    if not season_gate.exists() or load(season_gate).get("status") != "LOCKED":
        findings.append({"code": "season_gate_not_locked", "severity": "BLOCKING"})
    if production_status.get("episode_gate") != "OPEN":
        findings.append({"code": "episode_gate_not_open", "actual": production_status.get("episode_gate"), "severity": "BLOCKING"})
    for relative in INPUT_PATHS:
        if not (ROOT / relative).exists():
            findings.append({"code": "pilot_input_missing", "path": relative, "severity": "BLOCKING"})
    hooks = load(ROOT / "story/season/short-chapter-hook-map.json")
    pilot_entries = [item for item in hooks.get("entries", []) if item.get("episode_id") in PILOT_EPISODES]
    if hooks.get("status") != "SEASON-DRAFT" or len(pilot_entries) != 54:
        findings.append({"code": "pilot_hook_scope_invalid", "actual": len(pilot_entries), "severity": "BLOCKING"})
    if {item.get("chapter_id") for item in pilot_entries} != set(PILOT_CHAPTER_IDS):
        findings.append({"code": "pilot_chapter_ids_incomplete", "severity": "BLOCKING"})
    selection = load(ROOT / "story/season/u-candidate-selection.json")
    if any(item.get("named_identity") is not None for item in selection.get("slots", [])):
        findings.append({"code": "u_identity_bound_before_episode_gate", "severity": "MAJOR"})
    background = load(ROOT / "qa/background-usage.json")
    if background.get("static_decoration_records") != 0 or any(item.get("microchapter_ids") or item.get("extension_ids") for item in background.get("archetypes", [])):
        findings.append({"code": "bg_bound_before_episode_gate", "severity": "MAJOR"})
    return findings


def prepare() -> dict:
    findings = validate()
    if findings:
        report = {"schema_version": 1, "status": "OPEN", "scope": "P3-01 E01-E03 input freeze", "findings": findings}
        write(REPORT_PATH, report)
        return report
    items = [
        {"id": f"P3-PILOT-{index:02d}", "path": relative, "mode": "whole_file", "sha256": sha256_file(ROOT / relative)}
        for index, relative in enumerate(INPUT_PATHS, 1)
    ]
    scope = {
        "schema_version": 1,
        "gate": "p3-pilot-e01-e03",
        "scope": "p3-pilot-e01-e03",
        "prerequisites": ["season"],
        "declared_frozen_items": [item["id"] for item in items],
        "pilot_episodes": PILOT_EPISODES,
        "chapter_ids": PILOT_CHAPTER_IDS,
        "asset_policy": "Use v6 character asset standards as inputs; user-local production/assets and raw remain outside the commit and freeze scope.",
        "items": [{key: value for key, value in item.items() if key != "sha256"} for item in items],
    }
    manifest = {
        "schema_version": 1,
        "gate": "p3-pilot-e01-e03",
        "scope": "p3-pilot-e01-e03",
        "status": "P3-PILOT-DRAFT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pilot_episodes": PILOT_EPISODES,
        "chapter_total": len(PILOT_CHAPTER_IDS),
        "items": items,
        "boundaries": {
            "final_dialogue": "DEFERRED-UNTIL-EPISODE-GATE",
            "shot_ids": "DEFERRED-UNTIL-EPISODE-GATE",
            "u_unique_identity": "DEFERRED-UNTIL-EPISODE-GATE",
            "bg_microchapter_and_extension_bindings": "DEFERRED-UNTIL-EPISODE-GATE",
        },
    }
    write(SCOPE_PATH, scope)
    write(MANIFEST_PATH, manifest)
    report = {
        "schema_version": 1,
        "status": "REVIEWED-P3-INPUT-PASS",
        "scope": "P3-01 E01-E03 input freeze",
        "pilot_episodes": PILOT_EPISODES,
        "chapter_total": len(PILOT_CHAPTER_IDS),
        "input_total": len(items),
        "scope_definition": "qa/gates/scope-definitions/p3-pilot-e01-e03.json",
        "input_manifest": "qa/gates/input-manifests/p3-pilot-e01-e03.json",
        "findings": [],
        "deferred_boundary": manifest["boundaries"],
        "deferred_followup": [
            "P3-02 才开始 E01 逐章剧本、Character State、Relationship Delta 与连续性账本。",
            "E01–E03 试点仍需 Episode Gate 九项 QA；未通过不得扩展 E04–E36。",
        ],
    }
    write(REPORT_PATH, report)
    return report


if __name__ == "__main__":
    result = prepare()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-P3-INPUT-PASS" else 1)
