"""Transition Character Foundation source inputs to their post-Gate status.

This intentionally touches only the generated character profiles and the two
machine registries that describe their Foundation scope. Historical provenance
documents may continue to mention FOUNDATION-DRAFT.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD = "FOUNDATION-DRAFT"
NEW = "FOUNDATION-LOCKED"


def replace_profile_statuses() -> int:
    count = 0
    for tier in ("central", "important", "recurring"):
        for path in sorted((ROOT / "characters" / tier).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            updated = text.replace(f'status = "{OLD}"', f'status = "{NEW}"')
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                count += 1
    return count


def update_registry(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") == OLD:
        data["status"] = NEW
    for item in data.get("named_characters", []):
        if item.get("status") == OLD:
            item["status"] = NEW
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    changed = replace_profile_statuses()
    update_registry(ROOT / "qa/character-roster.json")
    update_registry(ROOT / "qa/relationship-slots.json")
    print(f"transitioned_profiles={changed} status={NEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
