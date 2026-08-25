from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEASON_DIR = ROOT / "story/season"
UNIT_PATH = ROOT / "qa/unit-slots.json"
HOOK_PATH = SEASON_DIR / "short-chapter-hook-map.json"
LEDGER_PATH = SEASON_DIR / "season-causal-ledger.json"
OUTPUT_PATH = SEASON_DIR / "u-candidate-selection.json"

WINDOWS = {
    "ARC1-ARC2": (1, 12),
    "ARC2-ARC3": (7, 18),
    "ARC3-ARC5": (13, 30),
    "ARC4-ARC6": (19, 36),
}

POV_EPISODES = {
    "life-visitors": [1, 3, 5, 7, 9, 11],
    "professional-problems": [7, 9, 11, 13, 15, 17],
    "crisis-bearers": [13, 17, 21, 25, 29],
    "moral-choice-triggers": [19, 23, 27, 31, 35],
}

RETURN_EPISODES = {
    "life-visitors": ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    "professional-problems": ([7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]),
    "crisis-bearers": ([13, 14, 15, 16, 17, 18, 19, 20, 21, 22], [18, 19, 20, 21, 22, 23, 24, 25, 26, 27]),
    "moral-choice-triggers": ([19, 20, 21, 22, 23, 24, 25, 26, 27, 28], [25, 26, 27, 28, 29, 30, 31, 32, 33, 34]),
}

FUNCTIONS = {
    "life-visitors": "生活观察与邻里基线",
    "professional-problems": "职业验证与制度摩擦",
    "crisis-bearers": "受影响者选择与求生反馈",
    "moral-choice-triggers": "道德选择触发与纠错反馈",
}

RETURN_REASONS = {
    "life-visitors": "同一生活圈再次求助或回报上次选择，让生活基线产生可比较的变化。",
    "professional-problems": "职业流程再次经过同一节点，带回新的限制，迫使主线重新估算代价。",
    "crisis-bearers": "危机扩大或转向后，上次承诺的人重新出现，要求兑现或修正原方案。",
    "moral-choice-triggers": "曾被制度或关系推开的行动者进入新的选择点，主动返回并改变责任分配。",
}

REPLACEMENT_RULE = "可由同 category、window 与 relation_slot 兼容的未选 U 槽位替换；不改变该章已锁定的因果责任、活动/幽默功能或关系 Delta。"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ep_id(number: int) -> str:
    return f"S1-E{number:02d}"


def chapter_index(entries: list[dict]) -> dict[str, dict]:
    return {item["chapter_id"]: item for item in entries}


def chapter_ref(entries_by_id: dict[str, dict], episode_number: int, sequence: int) -> dict:
    chapter_id = f"{ep_id(episode_number)}-M{sequence:02d}"
    item = entries_by_id[chapter_id]
    return {
        "episode_id": item["episode_id"],
        "chapter_id": item["chapter_id"],
        "context_pov_id": item["pov_id"],
        "context_function": item["function"],
        "context_tail_hook_type": item["tail_hook_type"],
        "traceability": {
            "ledger_ref": f"story/season/season-causal-ledger.json#/episodes/{episode_number - 1}",
            "hook_ref": f"story/season/short-chapter-hook-map.json#/entries/{(episode_number - 1) * 18 + sequence - 1}",
        },
    }


def role_spec(slot: dict) -> dict:
    return {
        "category": slot["category"],
        "window": slot["window"],
        "relation_slot": slot["relation_slot"],
        "eligible_profession_families": slot["eligible_profession_families"],
        "candidate_function": FUNCTIONS[slot["category"]],
        "named_identity": None,
    }


def source_slot(slot: dict, roles: list[str], selection_status: str, contexts: list[dict]) -> dict:
    return {
        "slot_id": slot["id"],
        "source_category": slot["category"],
        "source_window": slot["window"],
        "source_relation_slot": slot["relation_slot"],
        "source_pov_candidate": slot["pov_candidate"],
        "source_pov_slot": slot["pov_slot"],
        "source_natural_return_candidate": slot["natural_return_candidate"],
        "source_status": slot["status"],
        "selection_roles": roles,
        "selection_status": selection_status,
        "binding_status": "RESERVED-UNTIL-SEASON-GATE",
        "named_identity": None,
        "candidate_context_refs": contexts,
        "scene_id": None,
        "dialogue_id": None,
        "shot_id": None,
    }


def build() -> dict:
    units = load(UNIT_PATH)
    hooks = load(HOOK_PATH)
    ledger = load(LEDGER_PATH)
    entries = hooks["entries"]
    entries_by_id = chapter_index(entries)
    slots = units["slots"]

    pov_slots = [slot for slot in slots if slot["pov_slot"]]
    pov_alternates = [slot for slot in slots if slot["pov_candidate"] and not slot["pov_slot"]]
    return_slots = [slot for slot in slots if slot["natural_return_candidate"]]
    if len(pov_slots) != units["pov_slot_count"]:
        raise ValueError("POV slot registry count does not match source registry")
    if len(return_slots) != units["natural_return_candidate_count"]:
        raise ValueError("natural return registry count does not match source registry")

    pov_selections = []
    pov_by_category = {}
    for slot in pov_slots:
        pov_by_category.setdefault(slot["category"], []).append(slot)
    for category, category_slots in pov_by_category.items():
        for index, slot in enumerate(category_slots):
            episode_number = POV_EPISODES[category][index]
            sequence = 2 + ((index * 5 + 2) % 15)
            context = chapter_ref(entries_by_id, episode_number, sequence)
            pov_selections.append({
                "slot_id": slot["id"],
                "selection_status": "SELECTED-POV-CANDIDATE",
                "role_spec": role_spec(slot),
                "candidate_context": context,
                "candidate_reason": f"在 {context['episode_id']} 的 {context['chapter_id']} 提供{FUNCTIONS[category]}，只锁定可替换的观察位置，不锁定姓名或最终对白。",
                "replacement_rule": REPLACEMENT_RULE,
                "binding_status": "RESERVED-UNTIL-SEASON-GATE",
                "named_identity": None,
            })

    return_selections = []
    return_by_slot = {}
    by_category = {}
    for slot in return_slots:
        by_category.setdefault(slot["category"], []).append(slot)
    for category, category_slots in by_category.items():
        first_eps, return_eps = RETURN_EPISODES[category]
        for index, slot in enumerate(category_slots):
            first_sequence = 3 + ((index * 3) % 12)
            return_sequence = 8 + ((index * 5) % 9)
            first_context = chapter_ref(entries_by_id, first_eps[index], first_sequence)
            return_context = chapter_ref(entries_by_id, return_eps[index], return_sequence)
            item = {
                "slot_id": slot["id"],
                "selection_status": "SELECTED-NATURAL-RETURN-CANDIDATE",
                "role_spec": role_spec(slot),
                "first_appearance_context": first_context,
                "return_appearance_context": return_context,
                "return_reason": RETURN_REASONS[category],
                "state_transfer": f"首次出现留下一个可回收的生活/职业/危机/道德承诺；回场时必须带回该承诺的结果或修正，不能只重复功能。",
                "replacement_rule": REPLACEMENT_RULE,
                "binding_status": "RESERVED-UNTIL-SEASON-GATE",
                "named_identity": None,
            }
            return_selections.append(item)
            return_by_slot[slot["id"]] = item

    pov_by_slot = {item["slot_id"]: item for item in pov_selections}
    slots_output = []
    for slot in slots:
        roles = []
        contexts = []
        if slot["pov_candidate"] and not slot["pov_slot"]:
            roles.append("POV-ALTERNATE")
        if slot["id"] in pov_by_slot:
            roles.append("POV")
            contexts.append(pov_by_slot[slot["id"]]["candidate_context"])
        if slot["id"] in return_by_slot:
            roles.append("NATURAL-RETURN")
            contexts.extend([
                return_by_slot[slot["id"]]["first_appearance_context"],
                return_by_slot[slot["id"]]["return_appearance_context"],
            ])
        if slot["id"] in pov_by_slot or slot["id"] in return_by_slot:
            status = "SELECTED-CANDIDATE"
        elif "POV-ALTERNATE" in roles:
            status = "RESERVED-ALTERNATE-POV"
        else:
            status = "RESERVED"
        slots_output.append(source_slot(slot, roles, status, contexts))

    return {
        "schema_version": 1,
        "status": "SEASON-DRAFT",
        "scope": "P2 S2-06 U candidate selection and natural return boundary",
        "source_refs": [
            "qa/unit-slots.json",
            "story/season/season-causal-ledger.json",
            "story/season/short-chapter-hook-map.json",
            "qa/reviews/u-bg-boundary-audit.json",
        ],
        "slot_total": len(slots),
        "pov_slot_count": units["pov_slot_count"],
        "pov_candidate_count": units["pov_candidate_count"],
        "natural_return_candidate_count": units["natural_return_candidate_count"],
        "selected_pov_count": len(pov_selections),
        "selected_natural_return_count": len(return_selections),
        "selected_slot_count": len({item["slot_id"] for item in pov_selections} | {item["slot_id"] for item in return_selections}),
        "alternate_pov_count": len(pov_alternates),
        "pov_alternate_pool": [item["id"] for item in pov_alternates],
        "pov_selections": sorted(pov_selections, key=lambda item: item["slot_id"]),
        "natural_return_selections": sorted(return_selections, key=lambda item: item["slot_id"]),
        "slots": slots_output,
        "boundary_rules": {
            "source_registry_unchanged": True,
            "selected_rows_are_candidates_not_final_identities": True,
            "named_identity_assignment": "DEFERRED-UNTIL-SEASON-GATE",
            "scene_dialogue_shot_assignment": "DEFERRED-UNTIL-EPISODE-GATE",
            "bg_microchapter_binding": "FORBIDDEN-UNTIL-EPISODE-GATE",
            "unselected_u_status": "RESERVED",
            "candidate_contexts_are_traceability_refs_not_final_bindings": True,
            "replacement_policy": REPLACEMENT_RULE,
        },
        "next_gate": "Season Gate 前保留 U 可替换；Episode Gate 前不绑定 BG microchapter_ids 或 extension_ids。",
        "ledger_episode_count": len(ledger["episodes"]),
        "hook_chapter_count": len(entries),
    }


def main() -> int:
    data = build()
    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"materialized S2-06 slots={data['slot_total']} pov={data['selected_pov_count']} returns={data['selected_natural_return_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
