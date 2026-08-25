from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODE_ID = "S1-E01"
OUTPUT_DIR = ROOT / "production/episodes/S1-E01"
OUTPUT_PATH = OUTPUT_DIR / "episode-production-cards.json"
README_PATH = OUTPUT_DIR / "README.md"

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

PROFILE_BY_ID = {
    "CHR-L1-01": {
        "name": "沈蘅",
        "profile_ref": "characters/central/chr-l1-01-shen-heng.md",
        "default_state": "调香铺工作状态；先看物，再看手，最后看人；呼吸稳定。",
        "expression_path": "触发后先移开视线落到物件；呼吸变浅；把物件摆正；再以短句回应。",
        "breath": "平静中慢；核验时短暂停气；情绪越强越压低而不是加快。",
        "gaze": "物→手→人；需要判断时在记录、证物和对方之间往返。",
        "hands": "压纸边、摆正器物、闻香前停镊；记录前留空。",
        "weight": "轻微前倾，脚步稳定；面对压力先收窄动作范围。",
        "behavior_logic": "观察→核验→分类→判断→表达；不以感觉替代证据。",
        "voice": "中低音、中慢速；结论前停半拍；愤怒时更低、更精确。",
        "forbidden": "冷艳面瘫、突然大哭、无证据宣布结论、把亲情冲突演成胜负。",
    },
    "CHR-L2-01": {
        "name": "陆清和",
        "profile_ref": "characters/central/chr-l2-01-lu-qinghe.md",
        "default_state": "香铺掌柜工作状态；一边做事一边听，手上保持生活动作。",
        "expression_path": "先继续整理、翻账或拨灯；眼神短暂停在女儿身上；恐惧转为关门、收钱、确认孩子安全。",
        "breath": "做事时均匀；恐惧时吸气变短但动作更整齐；怒时不提高音量。",
        "gaze": "先看账、门、炉火和货架，再看人；不在冲突中长时间凝视。",
        "hands": "锁钱匣、翻账、整理货架、拨灯芯、盖炉、抚平纸角。",
        "weight": "重心贴近柜台与家务路线；争执时不后退，先把物件归位。",
        "behavior_logic": "生活秩序→家人安全→生计→道德判断→自己的情感。",
        "voice": "低声、短句；真正愤怒时叫全名；爱意用留饭、留灯和留药表达。",
        "forbidden": "恶母、歇斯底里、只恨亡夫、用哭喊替代生活账单。",
    },
    "CHR-L2-02": {
        "name": "林阿沅",
        "profile_ref": "characters/central/chr-l2-02-lin-ayuan.md",
        "default_state": "馄饨铺忙碌状态；边做事边说，眼睛追踪客人的饭量和来去。",
        "expression_path": "好奇先前倾；被认真听见后突然安静；羞耻时笑得更大、视线飘开并马上补救。",
        "breath": "忙时碎而有节奏；说快前会吸一口气；发现错误后先停一下再重说。",
        "gaze": "追踪手、碗、门口和饭量变化；先看变化再找能确认的人。",
        "hands": "记在油纸上、添汤、数碗、擦桌、回头确认空位。",
        "weight": "前倾、轻快；要承担责任时脚步会突然稳住。",
        "behavior_logic": "看到→确认→帮忙→可能说快→学会纠错。",
        "voice": "生活化、快慢不齐；重要事实前会主动放慢。",
        "forbidden": "幼稚化、一直咋呼、凭闲话直接下诊断、用热闹掩盖受伤。",
    },
    "CHR-L1-05": {
        "name": "顾行舟",
        "profile_ref": "characters/central/chr-l1-05-gu-xingzhou.md",
        "default_state": "酒肆掌柜与路线熟手；站位能看出口，先观察再动作。",
        "expression_path": "先确认门、灯、危险物；关心不直接说而是完成安全检查；羞耻转去做具体任务；恐惧可能缩短他人的选择路径。",
        "breath": "平静慢；警觉时短而低；接近失控时屏息半拍后才伸手。",
        "gaze": "出口→危险物→对方脚下→对方眼睛；不长时间凝视表达深情。",
        "hands": "挪刀、挂灯、看门、画路线、扶椅、收杯。",
        "weight": "低重心、离门近；关系冲突时先站开，若失控抓腕属于重大连续性事件。",
        "behavior_logic": "危险判断→最短生路→信息控制→情感处理；成长为告知风险→让对方决定。",
        "voice": "低、中速、少字；温柔时更慢；不以命令代替请求。",
        "forbidden": "霸总化、全程深情凝视、把保护直接等同控制、未经铺垫抓人。",
    },
}

FUNCTION_EMOTION = {
    "生活入口": ("日常专注", "不愿承认异常"),
    "异常进入": ("警觉", "维持生活秩序的焦虑"),
    "跨过门槛": ("好奇", "害怕越界"),
    "职业验证": ("谨慎确认", "对误判的防备"),
    "生活承载": ("共情", "不想把人变成数字"),
    "第一闭环": ("暂时松动", "更大问题逼近"),
    "换生活圈": ("被看见", "阶层差异带来的不安"),
    "关系碰撞": ("靠近与摩擦", "怕失去选择权"),
    "中点改义": ("重新判断", "旧解释被推翻的不适"),
    "制度/利益反应": ("压力", "不愿承认代价落到自己人"),
    "落到具体人": ("心疼", "无力感"),
    "关系状态变化": ("亲近或疏离", "亏欠"),
    "提出方案": ("决意", "害怕方案伤人"),
    "看见代价": ("羞愧", "仍想坚持正确"),
    "执行": ("集中", "失败恐惧"),
    "真相兑现": ("克制的震动", "无法补回的损失"),
    "伦理决定": ("承担", "不被理解"),
    "母集闭环": ("短暂喘息", "下一层问题已打开"),
}


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def split_obstacle(goal_obstacle: str) -> tuple[str, str]:
    goal, _, obstacle = goal_obstacle.partition("；阻碍：")
    return goal.removeprefix("目标："), obstacle


def source_manifest() -> list[dict]:
    return [{"path": path, "sha256": sha256(path)} for path in SOURCE_PATHS]


def build_card(
    hook: dict,
    episode: dict,
    activity: dict,
    humor: dict,
    evidence_by_id: dict[str, dict],
) -> dict:
    profile = PROFILE_BY_ID[hook["pov_id"]]
    primary, suppressed = FUNCTION_EMOTION[hook["function"]]
    goal, obstacle = split_obstacle(hook["goal_obstacle"])
    relation_ids = unique(
        episode["relationship_choice"]["relation_ids"]
        + activity["relationship_ids"]
        + humor["relationship_ids"]
    )
    evidence_items = [
        {
            "evidence_id": evidence_id,
            "semantic_role": "relationship-observation",
            "source_refs": ["qa/relationship-evidence.json"],
            "observation": evidence_by_id[evidence_id]["observable_action"],
            "rights": {
                "license_profile_ref": "license://linan-world/project-canon",
                "status": "PROJECT-CANON-ONLY",
            },
        }
        for evidence_id in episode["relationship_choice"]["evidence_ids"]
        if evidence_id in evidence_by_id
    ]
    return {
        "chapter_id": hook["chapter_id"],
        "episode_id": EPISODE_ID,
        "sequence": hook["sequence"],
        "duration_seconds": hook["duration_seconds"],
        "pov": {
            "id": hook["pov_id"],
            "name": hook["pov_name"],
            "canonical_identity_check": "qa/character-roster.json",
            "profile_ref": profile["profile_ref"],
            "asset_bible_ref": "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md",
        },
        "story_card": {
            "function": hook["function"],
            "cold_hook": hook["cold_hook"],
            "scene_goal": goal,
            "obstacle": obstacle,
            "evidence_or_relationship_action": hook["evidence_or_relationship_action"],
            "choice_cost": hook["choice_cost"],
            "tail_hook": {
                "type": hook["tail_hook_type"],
                "text": hook["tail_hook"],
            },
            "next_chase": hook["next_chase"],
            "state_delta": hook["state_delta"],
            "dialogue_status": "DEFERRED-UNTIL-EPISODE-GATE",
            "shot_id_status": "DEFERRED-UNTIL-EPISODE-GATE",
        },
        "character_state_sheet": {
            "entry_state": profile["default_state"],
            "exit_state": f"完成本章后，{hook['pov_name']}带着‘{hook['next_chase']}’离场；不得提前获得下一章未提供的信息。",
            "knowledge_before": "仅承接本章 cold_hook 与 Season Gate 已锁定的公开状态。",
            "knowledge_after": f"新增可见事实：{hook['evidence_or_relationship_action']}；下一步只追问：{hook['next_chase']}。",
            "appearance_ref": "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md",
            "costume_ref": "production/ai/v6-character-asset-bible/04-costume/costume-system-standard.md",
            "props_ref": ["story/season/season-causal-ledger.json", "story/season/short-chapter-hook-map.json"],
        },
        "emotion_action_sheet": {
            "primary_emotion": primary,
            "suppressed_secondary_emotion": suppressed,
            "expression_path": profile["expression_path"],
            "breath": profile["breath"],
            "gaze": profile["gaze"],
            "hands": profile["hands"],
            "body_weight": profile["weight"],
            "behavior_logic": profile["behavior_logic"],
            "voice_and_pace": profile["voice"],
            "scene_specific_action": hook["evidence_or_relationship_action"],
            "forbidden_performance": profile["forbidden"],
        },
        "relationship_delta_sheet": {
            "relation_ids": relation_ids,
            "character_ids": episode["relationship_choice"]["character_ids"],
            "episode_choice": episode["relationship_choice"]["choice"],
            "episode_delta": episode["relationship_choice"]["delta"],
            "chapter_boundary": "本章不新增身体接触权限；任何靠近、退开或替人做决定都必须在正式 Blocking 中记录。",
            "trust_boundary_debt": "沿用本集关系选择与证据快照；本章只推进一项可观察变化，不清零旧账。",
            "unresolved_question": episode["central_question"],
        },
        "continuity_ledger": {
            "time_window": f"{EPISODE_ID} / M{hook['sequence']:02d}; 精确钟点 DEFERRED-UNTIL-EPISODE-GATE",
            "weather": "惊蛰雷雨后；若正式分场改变天气，必须回写 Episode Gate。",
            "location_ids": episode["city_evidence"]["location_ids"],
            "wardrobe_state": "E01 春季工作状态；服装连续性以 v6 Costume Standard 为硬约束。",
            "props_and_marks": "沿用 Season Ledger 已锁定物件；不得在本卡凭空新增关键道具。",
            "information_state": "禁止角色跨越本章 evidence_or_relationship_action 直接知道后续真相。",
            "handoff": hook["next_chase"],
        },
        "episode_bindings": {
            "activity": {
                "binding_id": activity["binding_id"],
                "activity_id": activity["activity_id"],
                "activity": activity["activity"],
                "relationship_delta": activity["relationship_delta"],
                "state_transfer": activity["state_transfer"],
                "placement_status": "DEFERRED-UNTIL-EPISODE-GATE",
            },
            "humor": {
                "humor_id": humor["humor_id"],
                "speaker": humor["speaker"],
                "humor_type": humor["humor_type"],
                "surface_line": humor["surface_line"],
                "listener_reaction": humor["listener_reaction"],
                "recovery": humor["emotional_recovery"],
                "placement_status": "DEFERRED-UNTIL-EPISODE-GATE",
            },
        },
        "production_control": {
            "asset_recipe": {
                "recipe_id": "recipe.linanspringletter.microchapter-production-card",
                "version": "1.0.0",
                "mode": "planning-only",
                "deterministic_inputs": [
                    hook["chapter_id"],
                    "story/season/season-causal-ledger.json",
                    "story/season/short-chapter-hook-map.json",
                    "qa/relationship-evidence.json",
                ],
                "task_graph": [
                    "resolve-canonical-character",
                    "compile-story-card",
                    "compile-character-state",
                    "compile-emotion-action",
                    "compile-relationship-delta",
                    "compile-continuity-ledger",
                    "defer-dialogue-shot-and-provider-execution",
                ],
                "assembly_policy": "one deterministic card per microchapter; no provider call and no generated contact sheet",
            },
            "control_channels": {
                "hard": [
                    {"channel": "canonical_identity", "fallback": {"action": "block"}},
                    {"channel": "behavior_logic", "fallback": {"action": "block"}},
                    {"channel": "relationship_boundary", "fallback": {"action": "block"}},
                    {"channel": "continuity_knowledge_state", "fallback": {"action": "block"}},
                ],
                "soft": ["expression_path", "gesture_intensity", "voice_pace"],
                "advisory": ["era_texture", "modern_emotional_entry", "humor_timing"],
            },
            "evidence_bundle": {
                "bundle_id": f"EVID-{hook['chapter_id']}",
                "items": evidence_items,
                "city_sources": ["story/season/season-causal-ledger.json", "story/season/short-chapter-hook-map.json"],
            },
            "license_profile": {
                "ref": "license://linan-world/project-canon",
                "status": "PROJECT-CANON-ONLY",
                "external_identity_rights": "UNRESOLVED-BY-DESIGN",
                "action": "block_external_execution_until_explicit_asset_rights",
            },
            "capability_gate": {
                "status": "PLANNING-ONLY",
                "resolved": ["canonical_roster_lookup", "deterministic_card_assembly", "continuity_field_compilation"],
                "unresolved_hard_capabilities": ["provider_adapter", "final_dialogue_render", "shot_execution", "verified_output_receipt"],
                "action": "block_external_execution",
            },
            "provider_calls": 0,
            "execution_request": "DEFERRED-UNTIL-EPISODE-GATE",
        },
        "qa_gate": {
            "status": "PENDING-EPISODE-GATE",
            "threshold": 90,
            "dimensions": {
                key: {"score": None, "status": "PENDING"}
                for key in (
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
                )
            },
        },
    }


def build_packet() -> dict:
    roster = read_json("qa/character-roster.json")
    canonical_names = {item["id"]: item["name"] for item in roster["named_characters"]}
    ledger = read_json("story/season/season-causal-ledger.json")
    episode = next(item for item in ledger["episodes"] if item["episode_id"] == EPISODE_ID)
    hooks = [item for item in read_json("story/season/short-chapter-hook-map.json")["entries"] if item["episode_id"] == EPISODE_ID]
    if len(hooks) != 18:
        raise SystemExit(f"expected 18 hooks for {EPISODE_ID}, found {len(hooks)}")
    activity = next(item for item in read_json("story/season/song-life-activity-matrix.json")["entries"] if item["episode_id"] == EPISODE_ID)
    humor = next(item for item in read_json("story/season/humor-register-matrix.json")["entries"] if item["episode_id"] == EPISODE_ID)
    evidence_by_id = {
        snapshot["evidence_id"]: snapshot
        for relation in read_json("qa/relationship-evidence.json")["relationships"]
        for snapshot in relation["snapshots"]
    }
    for hook in hooks:
        if canonical_names.get(hook["pov_id"]) != hook["pov_name"]:
            raise SystemExit(f"non-canonical POV identity: {hook['chapter_id']}")
    cards = [build_card(hook, episode, activity, humor, evidence_by_id) for hook in hooks]
    return {
        "schema_version": 1,
        "status": "P3-02-SCAFFOLD-DRAFT",
        "scope": "P3-02 S1-E01 deterministic microchapter production cards",
        "episode_id": EPISODE_ID,
        "episode_gate_status": "OPEN",
        "chapter_total": len(cards),
        "duration_seconds_target": [120, 180],
        "source_manifest": source_manifest(),
        "cards": cards,
        "deferred_boundary": {
            "final_dialogue": "DEFERRED-UNTIL-EPISODE-GATE",
            "shot_ids": "DEFERRED-UNTIL-EPISODE-GATE",
            "activity_scene_placement": "DEFERRED-UNTIL-EPISODE-GATE",
            "humor_scene_placement": "DEFERRED-UNTIL-EPISODE-GATE",
            "u_unique_identity": "DEFERRED-UNTIL-EPISODE-GATE",
            "bg_microchapter_and_extension_bindings": "DEFERRED-UNTIL-EPISODE-GATE",
        },
        "execution_policy": "NO_PROVIDER_CALLS; external execution remains blocked until immutable Episode Gate approval and rights/capability resolution.",
        "next_gate": "Episode Gate: formal scene/dialogue, blocking, storyboard, AIGC asset binding and ten-dimension QA.",
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    packet = build_packet()
    OUTPUT_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    README_PATH.write_text(
        """# S1-E01 生产卡（P3-02）

本目录是 Episode Gate 前的确定性生产卡，不是最终剧本或成片。

- `episode-production-cards.json`：18 个微短章的机器可读生产卡。
- 每卡包含 Character State、Emotion & Action、Relationship Delta、Continuity Ledger、CineWeave Production 控制与十项 QA 占位。
- 最终对白、镜头 ID、活动/幽默的具体场次、U/BG 绑定均保持 `DEFERRED-UNTIL-EPISODE-GATE`。
- 未调用任何外部生成服务；能力、版权和输出回执未解析前，外部执行保持阻断。

下一步：逐章补正式场景与对白，完成 blocking/storyboard/AIGC 资产绑定，再运行 Episode Gate。
""",
        encoding="utf-8",
    )
    print(f"materialized {EPISODE_ID} production cards={len(packet['cards'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
