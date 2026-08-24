from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PRODUCTION_ROOTS = ("canon", "characters", "story", "episodes", "extensions")
SCOPE_ROOTS = {
    "manifest": (),
    "canon": ("canon",),
    "character-foundation": ("characters",),
    "characters": ("characters",),
    "story": ("story",),
    "season": ("story",),
    "episodes": ("episodes", "story"),
    "extensions": ("extensions",),
    "content": PRODUCTION_ROOTS,
    "delivery": (),
    "all": PRODUCTION_ROOTS,
}
SCAN_SUFFIXES = {".md", ".json", ".jsonl", ".csv", ".txt"}
FORBIDDEN_PATTERNS = (
    ("unfinished_latin", re.compile(r"\b(?:tbd|todo|fixme|xxx|placeholder)\b", re.IGNORECASE)),
    ("unfinished_cn", re.compile(r"待定|以后再说|某角色|暂略|同上")),
    ("question_mark_run", re.compile(r"\?{3,}")),
    ("dummy_latin", re.compile(r"lorem\s+ipsum", re.IGNORECASE)),
)
FACT_FIELDS = {
    "fact_id", "value", "authority_path", "authority_anchor", "priority",
    "effective_from", "effective_until", "status", "change_id",
}
FACT_STATUSES = {"ACTIVE", "RETIRED"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    story = data["story_counts"]
    microchapters = story["microchapters"]
    calculated = story["episodes"] * story["microchapters_per_episode"]
    if calculated != microchapters:
        errors.append(f"episode_product={calculated} expected={microchapters}")
    pov_total = sum(data["pov_quotas"].values())
    if pov_total != microchapters:
        errors.append(f"pov_total={pov_total} expected={microchapters}")
    function_total = sum(data["primary_function_quotas"].values())
    if function_total != microchapters:
        errors.append(f"function_total={function_total} expected={microchapters}")
    named_total = sum(data["character_counts"].values())
    if named_total != 204:
        errors.append(f"named_character_total={named_total} expected=204")
    if story["arcs"] != 6 or story["episodes"] != 36 or story["extension_cards"] != 120:
        errors.append("story_counts_do_not_match_locked_spec")
    return errors


def validate_required_paths(data: dict[str, Any], scope: str, root: Path = ROOT) -> list[str]:
    return [
        f"missing_path={relative}"
        for relative in data.get("required_paths", {}).get(scope, [])
        if not (root / relative).exists()
    ]


def scan_forbidden(scope: str, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for root_name in SCOPE_ROOTS[scope]:
        scan_root = root / root_name
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8")
            for rule_id, pattern in FORBIDDEN_PATTERNS:
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    relative = path.relative_to(root).as_posix()
                    errors.append(f"forbidden_rule={rule_id} path={relative} line={line}")
    return errors


def expected_priority(authority_path: str) -> int | None:
    path = authority_path.replace("\\", "/")
    if path in {"project-approved-spec.md", "canon/00-canon-index.md"}:
        return 0
    for prefix, priority in (
        ("canon/", 1), ("characters/", 2), ("story/", 3),
        ("episodes/", 4), ("extensions/", 5),
    ):
        if path.startswith(prefix):
            return priority
    return None


def canonical_value(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def intervals_overlap(first_start: int, first_end: int, second_start: int, second_end: int) -> bool:
    return first_start < second_end and second_start < first_end


def validate_canon_facts(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("fact_registry_schema_version_must_equal_1")
    timeline = data.get("timeline_order")
    if not isinstance(timeline, list) or not timeline:
        return errors + ["timeline_order_must_be_nonempty_list"]
    if any(not isinstance(anchor, str) or not anchor for anchor in timeline):
        return errors + ["timeline_anchor_must_be_nonempty_string"]
    if len(set(timeline)) != len(timeline):
        return errors + ["timeline_order_contains_duplicate_anchor"]
    positions = {anchor: index for index, anchor in enumerate(timeline)}
    facts = data.get("facts")
    if not isinstance(facts, list):
        return errors + ["facts_must_be_list"]
    normalized: list[dict[str, Any]] = []
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            errors.append(f"fact[{index}]_must_be_object")
            continue
        missing = sorted(FACT_FIELDS - set(fact))
        if missing:
            errors.append(f"fact[{index}]_missing_fields={','.join(missing)}")
            continue
        authority_path = fact["authority_path"]
        required_priority = expected_priority(authority_path) if isinstance(authority_path, str) else None
        if required_priority is None:
            errors.append(f"fact[{index}].unknown_authority_path={authority_path}")
        elif fact["priority"] != required_priority:
            errors.append(
                f"fact[{index}].priority={fact['priority']} expected={required_priority} "
                f"authority_path={authority_path}"
            )
        if fact["status"] not in FACT_STATUSES:
            errors.append(f"fact[{index}].invalid_status={fact['status']}")
        start_anchor = fact["effective_from"]
        end_anchor = fact["effective_until"]
        if start_anchor not in positions:
            errors.append(f"fact[{index}].unknown_effective_from={start_anchor}")
            continue
        if end_anchor is not None and end_anchor not in positions:
            errors.append(f"fact[{index}].unknown_effective_until={end_anchor}")
            continue
        start = positions[start_anchor]
        end = len(timeline) if end_anchor is None else positions[end_anchor]
        if end <= start:
            errors.append(f"fact[{index}].effective_interval_is_empty_or_reversed")
            continue
        normalized.append({
            "index": index, "fact_id": fact["fact_id"], "value": canonical_value(fact["value"]),
            "priority": fact["priority"], "start": start, "end": end,
        })
    for position, first in enumerate(normalized):
        for second in normalized[position + 1:]:
            if first["fact_id"] != second["fact_id"] or first["value"] == second["value"]:
                continue
            if not intervals_overlap(first["start"], first["end"], second["start"], second["end"]):
                continue
            if first["priority"] == second["priority"]:
                errors.append(
                    f"fact_conflict=fact_id={first['fact_id']} first={first['index']} second={second['index']}"
                )
            else:
                high, low = sorted((first, second), key=lambda item: item["priority"])
                errors.append(
                    f"lower_priority_override=fact_id={first['fact_id']} high={high['index']} low={low['index']}"
                )
    return sorted(errors)


def validate_scope(scope: str, strict: bool, root: Path = ROOT) -> list[str]:
    manifest = load_json(root / "qa/project-manifest.json")
    errors = validate_manifest(manifest)
    from scripts.lock_gate import validate_status_integrity
    errors.extend(validate_status_integrity(root))
    if scope in {"delivery", "all"}:
        errors.append("delivery_validator_not_installed")
    if scope in manifest.get("required_paths", {}):
        errors.extend(validate_required_paths(manifest, scope, root=root))
    if scope in {"canon", "content", "all"}:
        registry_path = root / "qa/canon-fact-registry.json"
        if registry_path.exists():
            try:
                errors.extend(validate_canon_facts(load_json(registry_path)))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid_json=qa/canon-fact-registry.json line={exc.lineno}")
        else:
            errors.append("missing_path=qa/canon-fact-registry.json")
    if strict:
        errors.extend(scan_forbidden(scope, root=root))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=tuple(SCOPE_ROOTS), default="manifest")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    errors = validate_scope(args.scope, args.strict)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"FAIL scope={args.scope} errors={len(errors)}")
        return 1
    if args.scope in {"canon", "content", "all"}:
        print("PASS fact_conflicts=0")
    if args.strict:
        print("PASS placeholder_matches=0")
    print(f"PASS scope={args.scope} errors=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
