from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "qa/gates/scope-definitions/season.json"
MANIFEST_PATH = ROOT / "qa/gates/input-manifests/season.json"
CERTIFICATE_PATH = ROOT / "qa/gates/season-gate.json"
STATUS_PATH = ROOT / "qa/production-status.json"
REQUIRED_REPORTS = [
    "qa/reviews/season-causal-ledger-review.json",
    "qa/reviews/season-s2c-review.json",
    "qa/reviews/season-u-boundary-review.json",
    "qa/reviews/season-mystery-review.json",
    "qa/reviews/season-activity-review.json",
    "qa/reviews/season-humor-review.json",
    "qa/reviews/season-gate-causal-mystery-review.json",
    "qa/reviews/season-gate-relationship-life-humor-review.json",
    "qa/reviews/season-gate-exception-ledger.json",
]
FROZEN_PATHS = [
    "story/season/season-causal-ledger.schema.json",
    "story/season/season-causal-ledger.json",
    "story/season/mystery-reversal-matrix.schema.json",
    "story/season/mystery-reversal-matrix.json",
    "story/season/song-life-activity-matrix.schema.json",
    "story/season/song-life-activity-matrix.json",
    "story/season/humor-register-matrix.schema.json",
    "story/season/humor-register-matrix.json",
    "story/season/short-chapter-hook-map.schema.json",
    "story/season/short-chapter-hook-map.json",
    "story/season/u-candidate-selection.schema.json",
    "story/season/u-candidate-selection.json",
    "qa/relationship-slots.json",
    "qa/relationship-evidence.json",
    "qa/emotional-spines.json",
    "qa/unit-slots.json",
    "qa/background-usage.json",
    *REQUIRED_REPORTS,
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scope_definition() -> dict:
    items = [{"id": f"SEASON-{index:02d}", "path": path, "mode": "whole_file"} for index, path in enumerate(FROZEN_PATHS, 1)]
    return {
        "schema_version": 1,
        "gate": "season",
        "scope": "season",
        "prerequisites": ["canon", "character-foundation"],
        "declared_frozen_items": [item["id"] for item in items],
        "items": items,
    }


def validate_inputs() -> list[str]:
    errors: list[str] = []
    for relative in FROZEN_PATHS:
        if not (ROOT / relative).exists():
            errors.append(f"missing_input={relative}")
    if not (ROOT / "qa/gates/canon-gate.json").exists() or read_json(ROOT / "qa/gates/canon-gate.json").get("status") != "LOCKED":
        errors.append("canon_prerequisite_not_locked")
    if not (ROOT / "qa/gates/character-foundation-gate.json").exists() or read_json(ROOT / "qa/gates/character-foundation-gate.json").get("status") != "LOCKED":
        errors.append("character_foundation_prerequisite_not_locked")
    for relative in REQUIRED_REPORTS:
        path = ROOT / relative
        if not path.exists():
            continue
        data = read_json(path)
        if data.get("status") != "REVIEWED-SEASON-PASS":
            errors.append(f"review_not_pass={relative}")
        if data.get("findings"):
            errors.append(f"review_has_findings={relative}")
    status = read_json(STATUS_PATH)
    if status.get("season_gate") not in {"OPEN", "LOCKED"}:
        errors.append(f"season_gate_status_invalid={status.get('season_gate')}")
    return errors


def prepare() -> Path:
    errors = validate_inputs()
    if errors:
        raise RuntimeError("; ".join(errors))
    definition = scope_definition()
    write_json(SCOPE_PATH, definition)
    projections = [
        {
            "id": item["id"],
            "path": item["path"],
            "mode": item["mode"],
            "projection_sha256": sha256_file(ROOT / item["path"]),
        }
        for item in definition["items"]
    ]
    write_json(MANIFEST_PATH, {
        "schema_version": 1,
        "gate": "season",
        "scope": "season",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": projections,
    })
    return MANIFEST_PATH


def lock() -> Path:
    errors = validate_inputs()
    if errors:
        raise RuntimeError("; ".join(errors))
    if not MANIFEST_PATH.exists() or not SCOPE_PATH.exists():
        raise RuntimeError("season scope or input manifest missing; run --prepare first")
    definition = read_json(SCOPE_PATH)
    manifest = read_json(MANIFEST_PATH)
    if definition.get("declared_frozen_items") != [item.get("id") for item in definition.get("items", [])]:
        raise RuntimeError("season scope declared_frozen_items mismatch")
    expected = {item["id"]: item for item in manifest.get("items", [])}
    for item in definition.get("items", []):
        path = ROOT / item["path"]
        if not path.exists() or sha256_file(path) != expected.get(item["id"], {}).get("projection_sha256"):
            raise RuntimeError(f"season input projection changed={item['path']}")
    certificate = {
        "schema_version": 1,
        "gate": "season",
        "scope": "season",
        "status": "LOCKED",
        "input_manifest_sha256": sha256_file(MANIFEST_PATH),
        "reviews": REQUIRED_REPORTS,
        "exception_ledger": "qa/reviews/season-gate-exception-ledger.json",
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "deferred_boundary": "DEFERRED-UNTIL-EPISODE-GATE",
    }
    write_json(CERTIFICATE_PATH, certificate)
    status = read_json(STATUS_PATH)
    status["season_gate"] = "LOCKED"
    write_json(STATUS_PATH, status)
    return CERTIFICATE_PATH


def audit() -> dict:
    errors = validate_inputs()
    certificate = read_json(CERTIFICATE_PATH) if CERTIFICATE_PATH.exists() else {}
    manifest = read_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else {}
    if not CERTIFICATE_PATH.exists():
        errors.append("season_certificate_missing")
    if not MANIFEST_PATH.exists() or not SCOPE_PATH.exists():
        errors.append("season_scope_or_manifest_missing")
    if certificate.get("status") != "LOCKED" or certificate.get("gate") != "season":
        errors.append("season_certificate_not_locked")
    if certificate.get("input_manifest_sha256") != sha256_file(MANIFEST_PATH) if MANIFEST_PATH.exists() else True:
        errors.append("season_certificate_manifest_hash_mismatch")
    status = read_json(STATUS_PATH)
    if status.get("season_gate") != "LOCKED":
        errors.append("production_status_season_gate_not_locked")
    return {
        "schema_version": 1,
        "status": "REVIEWED-SEASON-PASS" if not errors else "OPEN",
        "scope": "P2 SG-04 Season Gate decision and rebuildability review",
        "certificate": "qa/gates/season-gate.json",
        "input_manifest": "qa/gates/input-manifests/season.json",
        "scope_definition": "qa/gates/scope-definitions/season.json",
        "input_item_total": len(manifest.get("items", [])),
        "findings": [{"code": error, "severity": "BLOCKING"} for error in errors],
        "deferred_boundary": "DEFERRED-UNTIL-EPISODE-GATE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--lock", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare:
            print(f"PREPARED {prepare()}")
        if args.lock:
            print(f"LOCKED {lock()}")
        if args.audit or not (args.prepare or args.lock):
            result = audit()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] == "REVIEWED-SEASON-PASS" else 1
        return 0
    except RuntimeError as error:
        print(f"OPEN {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
