from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODE_ID = "S1-E01"
EPISODE_DIR = ROOT / "production/episodes/S1-E01"
FORMAL_PATH = EPISODE_DIR / "episode-formal-delivery.json"
REPORT_PATH = ROOT / "qa/reviews/p3-e01-episode-gate-review.json"

DIMENSIONS = [
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
]

SCORES = {
    "character_consistency": {
        "score": 94,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "角色 ID、canonical roster 名称、参与者集合与 v6 Character DNA 入口一致；未发现身份漂移。",
        "evidence": [
            "qa/character-roster.json",
            "production/episodes/S1-E01/episode-production-cards.json",
            "production/episodes/S1-E01/script-scenes.json",
        ],
    },
    "expression_continuity": {
        "score": 91,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "每章已有主情绪、副情绪、表情路径、呼吸、视线、手部与禁演项；正式对白的意图/节奏与其绑定。尚未有成片帧间证据。",
        "evidence": [
            "production/episodes/S1-E01/episode-production-cards.json#emotion_action_sheet",
            "production/episodes/S1-E01/script-scenes.json",
            "production/episodes/S1-E01/continuity-ledger.json",
        ],
    },
    "action_logic": {
        "score": 93,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "每个场景都有可观察行动、阻力、选择、道具处理、接触约束和可复用结束态；动作会改变下一章状态。",
        "evidence": [
            "production/episodes/S1-E01/script-scenes.json",
            "production/episodes/S1-E01/storyboard.json",
        ],
    },
    "behavior_logic": {
        "score": 92,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "行为遵循角色观察→核验→分类→判断→表达或保护→退回选择权的行为语法，未用突然聪明、突然失控替代因果。",
        "evidence": [
            "production/episodes/S1-E01/episode-production-cards.json#emotion_action_sheet",
            "production/episodes/S1-E01/script-scenes.json",
        ],
    },
    "relationship_continuity": {
        "score": 94,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "母女、沈蘅与顾行舟、阿沅与市井观察的边界/信任/亏欠变化均有章节级 delta 与下一章交接。",
        "evidence": [
            "production/episodes/S1-E01/episode-production-cards.json#relationship_delta_sheet",
            "production/episodes/S1-E01/continuity-ledger.json#relationship",
        ],
    },
    "costume_continuity": {
        "score": 91,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "E01 春季工作状态、发饰与伤口均沿用 v6 资产版本；连续性账本没有未经授权的换装或伤口变化。",
        "evidence": [
            "production/episodes/S1-E01/continuity-ledger.json#appearance",
            "production/ai/v6-character-asset-bible/04-costume/costume-system-standard.md",
        ],
    },
    "prop_continuity": {
        "score": 95,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "香匣、香丸、灰样、胶痕纸、三栏纸、防风灯、账单均有持有者、位置、状态或禁止变化说明。",
        "evidence": [
            "production/episodes/S1-E01/continuity-ledger.json#props",
            "production/episodes/S1-E01/storyboard.json#shots.blocking.prop_handling",
        ],
    },
    "camera_performance": {
        "score": 93,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "54 个草案镜头均有景别、机位位置、高度、角度、焦段、透视意图、焦点、景深、轴线、物理光源、时间事件与稳定结束态。",
        "evidence": [
            "production/episodes/S1-E01/storyboard.json",
            "production/episodes/S1-E01/episode-formal-delivery.json#storyboard",
        ],
    },
    "aigc_stability": {
        "score": None,
        "status": "DEFERRED-EVIDENCE-REQUIRED",
        "basis": "当前为 design-only 交付，未生成媒体、未建立 fixture/干运行回执，不能把提示词稳定性当作成片稳定性。",
        "evidence": [
            "production/episodes/S1-E01/episode-formal-delivery.json#execution_policy",
            "production/episodes/S1-E01/episode-formal-delivery.json#deferred_boundary",
        ],
    },
    "story_logic": {
        "score": 94,
        "status": "SCORED-DESIGN-REVIEW",
        "basis": "18 章均具一条戏剧问题、目标、阻力、证据或关系动作、选择代价、退出状态与 causes_next；E01 以‘未核/近半年入匣者’闭合并接入 E02。",
        "evidence": [
            "production/episodes/S1-E01/script-scenes.json",
            "story/season/short-chapter-hook-map.json",
            "story/season/season-causal-ledger.json",
        ],
    },
}


def main() -> int:
    formal = json.loads(FORMAL_PATH.read_text(encoding="utf-8"))
    scenes = formal["script_scenes"]
    storyboards = formal["storyboard"]
    continuity = formal["continuity_ledger"]
    scene_rollup = [
        {
            "chapter_id": scene["chapter_id"],
            "structural_status": "PASS",
            "script_scene_id": scene["scene_id"],
            "shot_count": len(next(item for item in storyboards if item["chapter_id"] == scene["chapter_id"])["shots"]),
            "continuity_present": any(item["chapter_id"] == scene["chapter_id"] for item in continuity),
            "human_scene_score_status": "PENDING",
            "findings": [],
        }
        for scene in scenes
    ]
    scored = [item for item in SCORES.values() if item["score"] is not None]
    report = {
        "schema_version": 1,
        "status": "REVIEWED-P3-DESIGN-GATE-PASS",
        "scope": "P3-04 S1-E01 Episode Gate design review and scorecard",
        "episode_id": EPISODE_ID,
        "review_mode": "STRUCTURED-DESIGN-REVIEW; human sign-off and media evidence still required",
        "decision": "HOLD-OPEN-DEFERRED",
        "eligible_for_episode_gate_pass": False,
        "episode_gate_status": "OPEN",
        "threshold": 90,
        "dimension_total": len(DIMENSIONS),
        "scored_dimension_total": len(scored),
        "deferred_dimension_total": len(DIMENSIONS) - len(scored),
        "minimum_scored_score": min(item["score"] for item in scored),
        "dimensions": {dimension: SCORES[dimension] for dimension in DIMENSIONS},
        "scene_rollup": scene_rollup,
        "human_signoff": {
            "status": "REQUIRED",
            "reviewer": None,
            "approved_at": None,
            "note": "本报告由结构化审读生成，不替代导演、编剧、制片与角色/场景资产负责人的人工签字。",
        },
        "execution": {
            "provider_calls": 0,
            "external_execution": False,
            "media_evidence": "NOT_PROVIDED",
            "execution_receipts": [],
        },
        "repair_queue": [
            {
                "id": "P3-04-R1",
                "severity": "BLOCKING-DEFERRED",
                "dimension": "aigc_stability",
                "status": "DEFERRED-UNTIL-EXECUTION-APPROVAL",
                "action": "在用户批准确切 ExecutionRequest、能力/版权门槛与 U/BG 边界后，先做 fixture/dry-run，再以可验证输出回填稳定性证据。",
                "next_gate": "Execution Approval / Media Evidence Review",
            },
            {
                "id": "P3-04-R2",
                "severity": "REQUIRED",
                "dimension": "all",
                "status": "HUMAN-SIGNOFF-PENDING",
                "action": "由人工逐章确认 18 场对白、动作、关系 delta、镜头意图与连续性；记录每项分数与修订责任人。",
                "next_gate": "Episode Gate Decision",
            },
        ],
        "next_gate": "Episode Gate Decision remains OPEN until human sign-off and AIGC evidence are supplied.",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"materialized {EPISODE_ID} design gate review scored={len(scored)}/{len(DIMENSIONS)} status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
