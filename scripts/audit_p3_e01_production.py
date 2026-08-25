from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "production/episodes/S1-E01/episode-production-cards.json"
REPORT_PATH = ROOT / "qa/reviews/p3-e01-production-scaffold-review.json"
EPISODE_ID = "S1-E01"
EXPECTED_DIMENSIONS = {
    "character_consistency",
    "expression_continuity",
    "action_logic",
    "behavior_logic",
    "relationship_continuity",
    "costume_continuity",
    "prop_continuity",
    "camera_performance",
    "aigc_stability",
    "story_logic",
}
REQUIRED_CARD_FIELDS = {
    "chapter_id",
    "episode_id",
    "sequence",
    "duration_seconds",
    "pov",
    "story_card",
    "character_state_sheet",
    "emotion_action_sheet",
    "relationship_delta_sheet",
    "continuity_ledger",
    "episode_bindings",
    "production_control",
    "qa_gate",
}
SOURCE_PATHS = [
    "qa/character-roster.json",
    "qa/relationship-evidence.json",
    "story/season/season-causal-ledger.json",
    "story/season/short-chapter-hook-map.json",
    "story/season/song-life-activity-matrix.json",
    "story/season/humor-register-matrix.json",
    "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md",
    "production/ai/v6-character-asset-bible/02-expression/expression-asset-standard.md",
    "production/ai/v6-character-asset-bible/03-pose-motion/pose-motion-asset-standard.md",
    "production/ai/v6-character-asset-bible/04-costume/costume-system-standard.md",
    "production/ai/v6-character-asset-bible/06-relationship/relationship-state-standard.md",
    "production/ai/v6-character-asset-bible/07-continuity/continuity-ledger-standard.md",
    "production/ai/v6-character-asset-bible/09-production-workflow/linan-standard-sop.md",
    "production/ai/v6-character-asset-bible/10-episode-gate/episode-delivery-gate.md",
]


def finding(code: str, severity: str = "BLOCKING", **details: object) -> dict:
    return {"code": code, "severity": severity, **details}


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def audit() -> dict:
    findings: list[dict] = []
    if not PACKET_PATH.exists():
        findings.append(finding("production_packet_missing"))
        report = {"schema_version": 1, "status": "OPEN", "findings": findings}
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    roster = load("qa/character-roster.json")
    names_by_id = {item["id"]: item["name"] for item in roster["named_characters"]}
    episode = next(item for item in load("story/season/season-causal-ledger.json")["episodes"] if item["episode_id"] == EPISODE_ID)
    activity = next(item for item in load("story/season/song-life-activity-matrix.json")["entries"] if item["episode_id"] == EPISODE_ID)
    humor = next(item for item in load("story/season/humor-register-matrix.json")["entries"] if item["episode_id"] == EPISODE_ID)
    cards = packet.get("cards", [])
    expected_ids = [f"{EPISODE_ID}-M{index:02d}" for index in range(1, 19)]

    if packet.get("status") != "P3-02-SCAFFOLD-DRAFT":
        findings.append(finding("packet_status_invalid", actual=packet.get("status")))
    if packet.get("episode_gate_status") != "OPEN":
        findings.append(finding("episode_gate_not_open", actual=packet.get("episode_gate_status")))
    if len(cards) != 18 or [card.get("chapter_id") for card in cards] != expected_ids:
        findings.append(finding("card_rows_not_ordered_or_complete", actual=len(cards)))
    source_manifest = {item.get("path"): item.get("sha256") for item in packet.get("source_manifest", [])}
    for path in SOURCE_PATHS:
        if source_manifest.get(path) != sha256(path):
            findings.append(finding("source_manifest_stale_or_missing", path=path))

    for card in cards:
        chapter_id = card.get("chapter_id")
        missing = sorted(REQUIRED_CARD_FIELDS - set(card))
        if missing:
            findings.append(finding("card_required_fields_missing", chapter_id=chapter_id, fields=missing))
            continue
        pov = card["pov"]
        if pov.get("id") not in names_by_id:
            findings.append(finding("card_pov_unknown", chapter_id=chapter_id, pov_id=pov.get("id")))
        elif names_by_id[pov["id"]] != pov.get("name"):
            findings.append(finding("card_pov_name_mismatch", chapter_id=chapter_id, actual=pov.get("name"), expected=names_by_id[pov["id"]]))
        if card.get("episode_id") != EPISODE_ID or not 120 <= int(card.get("duration_seconds", 0)) <= 180:
            findings.append(finding("card_episode_or_duration_invalid", chapter_id=chapter_id))

        story = card["story_card"]
        for key in ("function", "cold_hook", "scene_goal", "obstacle", "evidence_or_relationship_action", "choice_cost", "tail_hook", "next_chase", "state_delta"):
            if not story.get(key):
                findings.append(finding("card_story_field_empty", chapter_id=chapter_id, field=key))
        if story.get("dialogue_status") != "DEFERRED-UNTIL-EPISODE-GATE" or story.get("shot_id_status") != "DEFERRED-UNTIL-EPISODE-GATE":
            findings.append(finding("card_story_boundary_not_deferred", chapter_id=chapter_id))

        for section in ("character_state_sheet", "emotion_action_sheet", "relationship_delta_sheet", "continuity_ledger"):
            if not all(value not in (None, "", [], {}) for value in card[section].values()):
                findings.append(finding("card_execution_section_incomplete", chapter_id=chapter_id, section=section))
        bindings = card["episode_bindings"]
        if bindings.get("activity", {}).get("activity_id") != activity["activity_id"] or bindings.get("humor", {}).get("humor_id") != humor["humor_id"]:
            findings.append(finding("card_episode_binding_mismatch", chapter_id=chapter_id))
        if any(bindings.get(key, {}).get("placement_status") != "DEFERRED-UNTIL-EPISODE-GATE" for key in ("activity", "humor")):
            findings.append(finding("card_episode_binding_placement_not_deferred", chapter_id=chapter_id))

        controls = card["production_control"]
        for hard in controls.get("control_channels", {}).get("hard", []):
            if hard.get("fallback", {}).get("action") != "block":
                findings.append(finding("hard_control_without_block_fallback", chapter_id=chapter_id, channel=hard.get("channel")))
        if controls.get("provider_calls") != 0 or controls.get("capability_gate", {}).get("action") != "block_external_execution":
            findings.append(finding("external_execution_not_blocked", chapter_id=chapter_id))
        if controls.get("license_profile", {}).get("status") != "PROJECT-CANON-ONLY":
            findings.append(finding("license_profile_not_project_canon_only", chapter_id=chapter_id))
        if controls.get("asset_recipe", {}).get("mode") != "planning-only":
            findings.append(finding("asset_recipe_not_planning_only", chapter_id=chapter_id))
        if not controls.get("evidence_bundle", {}).get("bundle_id"):
            findings.append(finding("evidence_bundle_missing", chapter_id=chapter_id))

        qa = card["qa_gate"]
        if qa.get("status") != "PENDING-EPISODE-GATE" or qa.get("threshold") != 90:
            findings.append(finding("card_qa_gate_status_invalid", chapter_id=chapter_id))
        dimensions = qa.get("dimensions", {})
        if set(dimensions) != EXPECTED_DIMENSIONS:
            findings.append(finding("card_qa_dimensions_invalid", chapter_id=chapter_id, actual=sorted(dimensions)))
        for dimension, result in dimensions.items():
            if result.get("status") != "PENDING" or result.get("score") is not None:
                findings.append(finding("card_qa_dimension_prematurely_scored", chapter_id=chapter_id, dimension=dimension))
        if "dialogue" in card or "shot_id" in card:
            findings.append(finding("card_contains_premature_final_artifact_id", chapter_id=chapter_id))

    report = {
        "schema_version": 1,
        "status": "REVIEWED-P3-SCAFFOLD-PASS" if not findings else "OPEN",
        "scope": "P3-02 S1-E01 deterministic production-card scaffold review",
        "episode_id": EPISODE_ID,
        "chapter_total": len(cards),
        "checks": {
            "cards_complete_and_ordered": len(cards) == 18 and [card.get("chapter_id") for card in cards] == expected_ids,
            "canonical_pov_identity": not any(item["code"] == "card_pov_name_mismatch" for item in findings),
            "source_manifest_current": not any(item["code"] == "source_manifest_stale_or_missing" for item in findings),
            "cineweave_hard_controls_block": not any(item["code"] == "hard_control_without_block_fallback" for item in findings),
            "external_execution_blocked": not any(item["code"] == "external_execution_not_blocked" for item in findings),
            "ten_dimension_qa_pending": not any(item["code"].startswith("card_qa_") for item in findings),
            "deferred_episode_boundary_preserved": packet.get("deferred_boundary", {}).get("final_dialogue") == "DEFERRED-UNTIL-EPISODE-GATE",
        },
        "findings": findings,
        "deferred_followup": [
            "逐章正式对白、场景切分与 Blocking/Storyboard 仍需在 Episode Gate 完成。",
            "活动与幽默只绑定到 E01 级输入，具体场次与反应顺序仍需 Episode Gate 决定。",
            "E01 通过本脚手架审读不等于成片可执行；十项 QA 必须逐章达到 90 分。",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-P3-SCAFFOLD-PASS" else 1)
