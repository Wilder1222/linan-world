from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "qa/project-manifest.json"
OUTPUT = ROOT / "qa/gates/scope-definitions/character-foundation.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = list(manifest["required_paths"]["character-foundation"])
    for directory in (
        "characters/central",
        "characters/important",
        "characters/recurring",
        "characters/relations/core",
        "characters/emotional-spines",
    ):
        paths.extend(
            path.relative_to(ROOT).as_posix()
            for path in sorted((ROOT / directory).glob("*.md"))
        )
    items = []
    for index, relative in enumerate(paths, start=1):
        path = ROOT / relative
        if path.is_dir():
            raise SystemExit(f"character-foundation scope cannot freeze directory: {relative}")
        if not path.exists():
            raise SystemExit(f"missing character-foundation input: {relative}")
        items.append({"id": f"CHARFOUND-{index:03d}", "path": relative, "mode": "whole_file"})
    definition = {
        "schema_version": 1,
        "gate": "character-foundation",
        "scope": "character-foundation",
        "prerequisites": ["canon"],
        "declared_frozen_items": [item["id"] for item in items],
        "items": items,
        "reserved_until": {
            "U": "season-gate",
            "BG_microchapter_ids": "episode-gate",
            "BG_extension_ids": "delivery-gate",
        },
    }
    OUTPUT.write_text(json.dumps(definition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{OUTPUT.relative_to(ROOT)} items={len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
