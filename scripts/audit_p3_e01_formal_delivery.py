from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODE_ID = "S1-E01"
EPISODE_DIR = ROOT / "production/episodes/S1-E01"
PACKET_PATH = EPISODE_DIR / "episode-formal-delivery.json"
SCRIPT_PATH = EPISODE_DIR / "script-scenes.json"
STORYBOARD_PATH = EPISODE_DIR / "storyboard.json"
CONTINUITY_PATH = EPISODE_DIR / "continuity-ledger.json"
REPORT_PATH = ROOT / "qa/reviews/p3-e01-formal-preflight-review.json"
EXPECTED_DIMENSIONS = 10
EXPECTED_IDS = [f"{EPISODE_ID}-M{index:02d}" for index in range(1, 19)]
SOURCE_PATHS = [
    "production/episodes/S1-E01/episode-production-cards.json",
    "story/season/short-chapter-hook-map.json",
    "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md",
    "production/ai/v6-character-asset-bible/10-episode-gate/episode-delivery-gate.md",
]


def finding(code: str, severity: str = "BLOCKING", **details: object) -> dict:
    return {"code": code, "severity": severity, **details}


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict:
    findings: list[dict] = []
    if not PACKET_PATH.exists():
        findings.append(finding("formal_packet_missing"))
        report = {"schema_version": 1, "status": "OPEN", "findings": findings}
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    packet = load_json(PACKET_PATH)
    script_wrapper = load_json(SCRIPT_PATH)
    storyboard_wrapper = load_json(STORYBOARD_PATH)
    continuity_wrapper = load_json(CONTINUITY_PATH)
    cards = load_json(EPISODE_DIR / "episode-production-cards.json")["cards"]
    roster = load_json(ROOT / "qa/character-roster.json")
    names_by_id = {item["id"]: item["name"] for item in roster["named_characters"]}
    known_ids = set(names_by_id)

    scenes = packet.get("script_scenes", [])
    storyboards = packet.get("storyboard", [])
    continuity = packet.get("continuity_ledger", [])
    if packet.get("status") != "P3-03-DRAFT":
        findings.append(finding("formal_packet_status_invalid", actual=packet.get("status")))
    if packet.get("episode_gate_status") != "OPEN":
        findings.append(finding("episode_gate_not_open", actual=packet.get("episode_gate_status")))
    if packet.get("execution_policy") != "DESIGN-ONLY; no provider calls, media claims, or final render receipts.":
        findings.append(finding("execution_policy_not_design_only"))
    if packet.get("qa_policy") != {"dimensions": EXPECTED_DIMENSIONS, "threshold": 90, "status": "PENDING-EPISODE-GATE"}:
        findings.append(finding("qa_policy_invalid", actual=packet.get("qa_policy")))
    if packet.get("deferred_boundary", {}).get("aigc_generation") != "DEFERRED-UNTIL-EPISODE-GATE-APPROVAL":
        findings.append(finding("aigc_generation_not_deferred"))
    if packet.get("deferred_boundary", {}).get("u_unique_identity") != "DEFERRED-UNTIL-EPISODE-GATE":
        findings.append(finding("u_binding_not_deferred"))
    if packet.get("deferred_boundary", {}).get("bg_bindings") != "DEFERRED-UNTIL-EPISODE-GATE":
        findings.append(finding("bg_binding_not_deferred"))

    source_manifest = {item.get("path"): item.get("sha256") for item in packet.get("source_manifest", [])}
    for path in SOURCE_PATHS:
        if source_manifest.get(path) != sha256(path):
            findings.append(finding("source_manifest_stale_or_missing", path=path))

    scene_ids = [scene.get("chapter_id") for scene in scenes]
    storyboard_ids = [scene.get("chapter_id") for scene in storyboards]
    continuity_ids = [scene.get("chapter_id") for scene in continuity]
    if scene_ids != EXPECTED_IDS or len(scenes) != 18:
        findings.append(finding("formal_script_scene_rows_not_ordered_or_complete", actual=scene_ids))
    if storyboard_ids != EXPECTED_IDS or len(storyboards) != 18:
        findings.append(finding("storyboard_scene_rows_not_ordered_or_complete", actual=storyboard_ids))
    if continuity_ids != EXPECTED_IDS or len(continuity) != 18:
        findings.append(finding("continuity_rows_not_ordered_or_complete", actual=continuity_ids))
    if script_wrapper.get("scenes") != scenes or storyboard_wrapper.get("scenes") != storyboards or continuity_wrapper.get("scenes") != continuity:
        findings.append(finding("formal_wrapper_payload_mismatch"))
    if script_wrapper.get("status") != "P3-03-DRAFT" or storyboard_wrapper.get("status") != "P3-03-DRAFT" or continuity_wrapper.get("status") != "P3-03-DRAFT":
        findings.append(finding("formal_wrapper_status_invalid"))

    cards_by_id = {card["chapter_id"]: card for card in cards}
    for scene, storyboard, ledger in zip(scenes, storyboards, continuity):
        chapter_id = scene.get("chapter_id")
        if chapter_id not in cards_by_id:
            findings.append(finding("formal_scene_missing_source_card", chapter_id=chapter_id))
            continue
        required = ("scene_id", "episode_id", "scene_spec_ref", "location_ids", "participants", "dramatic_question", "objective", "obstacle", "entry_state", "beats", "choice", "exit_state", "causes_next", "continuity_refs", "dialogue_boundary")
        missing = [field for field in required if not scene.get(field)]
        if missing:
            findings.append(finding("formal_scene_required_fields_missing", chapter_id=chapter_id, fields=missing))
        if scene.get("scene_id") != f"SCN-{chapter_id}" or scene.get("episode_id") != EPISODE_ID:
            findings.append(finding("formal_scene_identity_invalid", chapter_id=chapter_id))
        if scene.get("status") != "DRAFT-EPISODE-GATE":
            findings.append(finding("formal_scene_status_invalid", chapter_id=chapter_id))
        if scene.get("dialogue_boundary", "").find("镜头") < 0:
            findings.append(finding("dialogue_boundary_missing_no_camera_rule", chapter_id=chapter_id))
        if any(key in beat for beat in scene.get("beats", []) for key in ("camera", "shot_id", "storyboard")):
            findings.append(finding("camera_instruction_leaked_into_script_scene", chapter_id=chapter_id))
        if not all(beat.get("action") and beat.get("subtext") and beat.get("dialogue") for beat in scene.get("beats", [])):
            findings.append(finding("formal_scene_beat_incomplete", chapter_id=chapter_id))
        participants = set(scene.get("participants", []))
        if not participants <= known_ids:
            findings.append(finding("formal_scene_unknown_participant", chapter_id=chapter_id, ids=sorted(participants - known_ids)))
        for beat in scene.get("beats", []):
            for dialogue in beat.get("dialogue", []):
                speaker_id = dialogue.get("speaker_id")
                speaker_name = dialogue.get("speaker")
                if speaker_id not in known_ids or speaker_id not in participants:
                    findings.append(finding("dialogue_speaker_not_bound_to_scene", chapter_id=chapter_id, speaker_id=speaker_id))
                elif names_by_id[speaker_id] != speaker_name:
                    findings.append(finding("dialogue_speaker_name_mismatch", chapter_id=chapter_id, speaker_id=speaker_id, actual=speaker_name, expected=names_by_id[speaker_id]))
        if not set(scene.get("continuity_refs", [])) >= set(scene.get("location_ids", [])):
            findings.append(finding("formal_scene_continuity_location_refs_missing", chapter_id=chapter_id))
        if storyboard.get("scene_id") != scene.get("scene_id") or storyboard.get("status") != "DRAFT-EPISODE-GATE":
            findings.append(finding("storyboard_scene_binding_invalid", chapter_id=chapter_id))
        shots = storyboard.get("shots", [])
        if len(shots) != 3:
            findings.append(finding("storyboard_shot_count_invalid", chapter_id=chapter_id, actual=len(shots)))
        shot_ids = [shot.get("shot_id") for shot in shots]
        if shot_ids != [f"{chapter_id}-S0{index}" for index in range(1, 4)] or len(set(shot_ids)) != len(shot_ids):
            findings.append(finding("storyboard_shot_ids_invalid", chapter_id=chapter_id, actual=shot_ids))
        for shot in shots:
            if not shot.get("purpose") or not shot.get("blocking") or not shot.get("camera") or not shot.get("composition") or not shot.get("light", {}).get("physical_sources") or not shot.get("temporal", {}).get("start") or not shot.get("temporal", {}).get("event") or not shot.get("temporal", {}).get("end") or not shot.get("stable_end_state"):
                findings.append(finding("storyboard_shot_fields_incomplete", chapter_id=chapter_id, shot_id=shot.get("shot_id")))
            if shot.get("camera", {}).get("axis_side") != "preserve":
                findings.append(finding("storyboard_axis_preservation_missing", chapter_id=chapter_id, shot_id=shot.get("shot_id")))
        if ledger.get("scene_id") != scene.get("scene_id") or ledger.get("status") != "DRAFT-EPISODE-GATE":
            findings.append(finding("continuity_scene_binding_invalid", chapter_id=chapter_id))
        if not ledger.get("characters") or not ledger.get("space_and_time", {}).get("location_ids") or not ledger.get("props", {}).get("continuity_refs") or not ledger.get("handoff"):
            findings.append(finding("continuity_entry_incomplete", chapter_id=chapter_id))
        if set(ledger.get("characters", {})) != participants:
            findings.append(finding("continuity_character_set_mismatch", chapter_id=chapter_id))
        if any("provider" in json.dumps(item, ensure_ascii=False).lower() and "call" in json.dumps(item, ensure_ascii=False).lower() for item in (scene, storyboard, ledger)):
            findings.append(finding("provider_execution_claim_in_formal_payload", chapter_id=chapter_id))

    checks = {
        "formal_script_complete_and_playable": not any(item["code"].startswith("formal_scene_") or item["code"].startswith("dialogue_") for item in findings),
        "storyboard_bound_to_script": not any(item["code"].startswith("storyboard_") for item in findings),
        "continuity_bound_to_script": not any(item["code"].startswith("continuity_") for item in findings),
        "source_manifest_current": not any(item["code"] == "source_manifest_stale_or_missing" for item in findings),
        "no_provider_execution": not any(item["code"] == "provider_execution_claim_in_formal_payload" for item in findings),
        "ten_dimension_qa_pending": packet.get("qa_policy", {}).get("status") == "PENDING-EPISODE-GATE" and packet.get("qa_policy", {}).get("threshold") == 90,
        "final_u_bg_deferred": all(value == "DEFERRED-UNTIL-EPISODE-GATE" for value in (packet.get("deferred_boundary", {}).get("u_unique_identity"), packet.get("deferred_boundary", {}).get("bg_bindings"))),
    }
    report = {
        "schema_version": 1,
        "status": "REVIEWED-P3-PREFLIGHT-PASS" if not findings else "OPEN",
        "scope": "P3-03 S1-E01 formal script, storyboard and continuity preflight review",
        "episode_id": EPISODE_ID,
        "script_scene_total": len(scenes),
        "storyboard_scene_total": len(storyboards),
        "draft_shot_total": sum(len(scene.get("shots", [])) for scene in storyboards),
        "continuity_scene_total": len(continuity),
        "checks": checks,
        "findings": findings,
        "deferred_followup": [
            "Episode Gate 仍需由人工逐章审阅对白、Blocking、Storyboard 与表演边界。",
            "十项 QA（人物、表情、动作、行为、关系、服装、道具、镜头、AIGC 稳定性、故事）仍为 PENDING，阈值 90。",
            "当前仅为设计稿预审；未调用外部生成器，U/BG 绑定与最终成片继续冻结。",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "REVIEWED-P3-PREFLIGHT-PASS" else 1)
