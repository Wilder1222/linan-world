from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER_PATH = ROOT / "qa/character-roster.json"


def load_roster() -> dict:
    return json.loads(ROSTER_PATH.read_text(encoding="utf-8"))


def materialize_units(roster: dict) -> dict:
    unit = roster["unit_slots"]
    relation_ids = [f"REL-{number:03d}" for number in range(1, 17)] + ["REL-G01"]
    records = []
    for range_index, item in enumerate(unit["ranges"]):
        for number in range(item["start"], item["end"] + 1):
            ordinal = number - item["start"] + 1
            stable_id = f'{unit["prefix"]}{number:03d}'
            # Keep candidate pools distributed across all four categories.
            pov_candidate = ordinal <= 11
            natural_return = ordinal <= 10
            pov_slot_limits = (6, 6, 5, 5)
            pov_slot = ordinal <= pov_slot_limits[range_index]
            records.append({
                "id": stable_id,
                "category": item["category"],
                "window": item["window"],
                "pov_candidate": pov_candidate,
                "pov_slot": pov_slot,
                "natural_return_candidate": natural_return,
                "relation_slot": relation_ids[(number - 1) % len(relation_ids)],
                "eligible_profession_families": [item["category"], "neighborhood-support"],
                "status": "RESERVED",
            })
    return {
        "schema_version": "1.0",
        "purpose": "Unit character slots are reserved production capacity, not named characters.",
        "pov_slot_count": sum(1 for record in records if record["pov_slot"]),
        "pov_candidate_count": sum(1 for record in records if record["pov_candidate"]),
        "natural_return_candidate_count": sum(1 for record in records if record["natural_return_candidate"]),
        "slots": records,
    }


def materialize_background(roster: dict) -> dict:
    background = roster["background_archetypes"]
    records = []
    age_bands = ["child", "youth", "adult", "older-adult", "elder"]
    class_bands = ["working-poor", "stable-working", "small-owner", "clerical", "itinerant"]
    family_states = ["single", "paired", "parenting", "extended-household", "widowed-care"]
    active_times = ["dawn", "morning", "midday", "afternoon", "dusk", "night"]
    for item in background["ecosystem_ranges"]:
        for number in range(item["start"], item["end"] + 1):
            index = number - 1
            stable_id = f'{background["prefix"]}{number:03d}'
            location_id = f'LOC-{((number - 1) % 18) + 1:02d}'
            records.append({
                "id": stable_id,
                "ecosystem": item["ecosystem"],
                "age_band": age_bands[index % len(age_bands)],
                "occupation_family": item["ecosystem"],
                "class_band": class_bands[index % len(class_bands)],
                "region": f"district-{((number - 1) % 6) + 1}",
                "family_state": family_states[index % len(family_states)],
                "active_time": active_times[index % len(active_times)],
                "materials": ["纸灯", "竹篾", "布包"] if index % 3 == 0 else ["木箱", "麻绳", "油纸"],
                "eligible_location_ids": [location_id],
                "eligible_time_windows": ["ARC1-ARC2", "ARC3-ARC4", "ARC5-ARC6"],
                "eligible_work_states": ["normal", "rain", "crowded", "relief"],
                "microchapter_ids": [],
                "extension_ids": [],
                "static_decoration_record": False,
                "status": "RESERVED",
            })
    return {
        "schema_version": "1.0",
        "purpose": "Background people are traceable ecosystem archetypes; each use must be bound to a location, time and work state.",
        "minimum_count": background["minimum_count"],
        "static_decoration_records": 0,
        "archetypes": records,
    }


def main() -> int:
    roster = load_roster()
    (ROOT / "qa/unit-slots.json").write_text(json.dumps(materialize_units(roster), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "qa/background-usage.json").write_text(json.dumps(materialize_background(roster), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("qa/unit-slots.json")
    print("qa/background-usage.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
