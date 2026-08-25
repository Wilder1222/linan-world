from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class GateError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _gate_key(gate: str) -> str:
    # Gate IDs may use hyphens for file names (character-foundation), while
    # production-status uses stable JSON keys with underscores.
    return f"{gate.replace('-', '_')}_gate"


def _certificate_path(root: Path, gate: str) -> Path:
    return root / f"qa/gates/{gate}-gate.json"


def validate_status_integrity(root: Path) -> list[str]:
    path = root / "qa/production-status.json"
    if not path.exists():
        return ["missing_path=qa/production-status.json"]
    data = _read_json(path)
    allowed = {"OPEN", "LOCKED"}
    errors: list[str] = []
    for key, value in data.items():
        if key == "baseline":
            if value != "APPROVED":
                errors.append(f"baseline_status_invalid={value}")
        elif key.endswith("_gate") and value not in allowed:
            errors.append(f"gate_status_invalid={key}:{value}")
    for key, value in data.items():
        if not key.endswith("_gate") or value != "LOCKED":
            continue
        gate_key = key[:-5]
        gate = gate_key.replace("_", "-")
        cert = _certificate_path(root, gate)
        if not cert.exists():
            # Preserve compatibility with gate IDs that never contained a
            # hyphen (for example canon).
            gate = gate_key
            cert = _certificate_path(root, gate)
        if not cert.exists():
            errors.append(f"locked_without_valid_certificate={gate}")
            continue
        try:
            certificate = _read_json(cert)
        except json.JSONDecodeError:
            errors.append(f"locked_without_valid_certificate={gate}")
            continue
        if certificate.get("status") != "LOCKED" or certificate.get("gate") != gate:
            errors.append(f"locked_without_valid_certificate={gate}")
    return errors


def _scope_definition(root: Path, gate: str) -> dict[str, Any]:
    path = root / f"qa/gates/scope-definitions/{gate}.json"
    if not path.exists():
        raise GateError(f"missing scope definition={path.relative_to(root)}")
    return _read_json(path)


def _check_prerequisites(root: Path, definition: dict[str, Any]) -> None:
    for prerequisite in definition.get("prerequisites", []):
        if not _certificate_path(root, prerequisite).exists():
            raise GateError(f"missing prerequisite certificate={prerequisite}")


def prepare_gate(
    root: Path,
    gate: str,
    scope: str,
    validation_runner: Callable[[str, str], None] | None = None,
) -> Path:
    definition = _scope_definition(root, gate)
    _check_prerequisites(root, definition)
    items = definition.get("items", [])
    declared = definition.get("declared_frozen_items", [])
    actual = [item.get("id") for item in items]
    if declared != actual:
        raise GateError("declared_frozen_items mismatch")
    manifest_path = root / "qa/project-manifest.json"
    if manifest_path.exists():
        project_manifest = _read_json(manifest_path)
        required_paths = set(project_manifest.get("required_paths", {}).get(scope, []))
        defined_paths = {item.get("path") for item in items}
        missing_paths = sorted(required_paths - defined_paths)
        if missing_paths:
            raise GateError("scope definition missing required paths=" + ",".join(missing_paths))
    if len(actual) != len(set(actual)):
        raise GateError("scope definition contains duplicate item IDs")
    item_paths = [item.get("path") for item in items]
    if len(item_paths) != len(set(item_paths)):
        raise GateError("scope definition contains duplicate input paths")
    projections: list[dict[str, Any]] = []
    for item in items:
        path = root / item["path"]
        if not path.exists():
            raise GateError(f"missing frozen input={item['path']}")
        projections.append({
            "id": item["id"],
            "path": item["path"],
            "mode": item.get("mode", "whole_file"),
            "projection_sha256": sha256_file(path),
        })
    manifest = {
        "schema_version": 1,
        "gate": gate,
        "scope": scope,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": projections,
    }
    path = root / f"qa/gates/input-manifests/{gate}.json"
    _write_json(path, manifest)
    if validation_runner is not None:
        validation_runner(gate, scope)
    else:
        from scripts.validate_project import validate_scope
        errors = validate_scope(scope, True, root=root)
        if errors:
            raise GateError("validation failed: " + "; ".join(errors))
    return path


def _review_fields(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\A\+\+\+\s*\n(.*?)\n\+\+\+", text, re.S)
    if not match:
        raise GateError(f"review front matter missing={path}")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition("=")
        if separator:
            fields[key.strip()] = value.strip().strip('"')
    return fields


def _input_manifest_hash(path: Path) -> str:
    return sha256_file(path)


def lock_gate(
    root: Path,
    gate: str,
    scope: str,
    reviews: list[Path],
    validation_runner: Callable[[str, str], None] | None = None,
) -> Path:
    # CLI callers commonly pass review paths relative to the repository root;
    # normalize them before reading or recording them in the certificate.
    reviews = [path if path.is_absolute() else root / path for path in reviews]
    manifest_path = root / f"qa/gates/input-manifests/{gate}.json"
    if not manifest_path.exists():
        raise GateError("input manifest missing; run prepare first")
    manifest_hash = _input_manifest_hash(manifest_path)
    definition = _scope_definition(root, gate)
    for item in definition.get("items", []):
        path = root / item["path"]
        if not path.exists() or sha256_file(path) != next(
            entry["projection_sha256"] for entry in _read_json(manifest_path)["items"] if entry["id"] == item["id"]
        ):
            raise GateError("input projection changed")
    if len(reviews) != 2:
        raise GateError("exactly two reviews are required")
    parsed = [_review_fields(path) for path in reviews]
    ids = [item.get("reviewer_id") for item in parsed]
    if len(set(ids)) != len(ids):
        raise GateError("reviewer_id values must be distinct")
    for fields in parsed:
        if fields.get("status") != "PASS" or fields.get("reviewed_input_manifest_sha256") != manifest_hash:
            raise GateError("review does not match input manifest")
    if validation_runner is not None:
        validation_runner(gate, scope)
    else:
        from scripts.validate_project import validate_scope
        errors = validate_scope(scope, True, root=root)
        if errors:
            raise GateError("validation failed: " + "; ".join(errors))
    certificate = {
        "schema_version": 1,
        "gate": gate,
        "scope": scope,
        "status": "LOCKED",
        "input_manifest_sha256": manifest_hash,
        "reviews": [path.relative_to(root).as_posix() for path in reviews],
        "locked_at": datetime.now(timezone.utc).isoformat(),
    }
    cert_path = _certificate_path(root, gate)
    _write_json(cert_path, certificate)
    status_path = root / "qa/production-status.json"
    status = _read_json(status_path)
    status[_gate_key(gate)] = "LOCKED"
    _write_json(status_path, status)
    return cert_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--lock", action="store_true")
    parser.add_argument("--review", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.prepare:
            path = prepare_gate(Path.cwd(), args.gate, args.scope)
            print(f"PREPARED {path}")
        elif args.lock:
            path = lock_gate(Path.cwd(), args.gate, args.scope, [Path(item) for item in args.review])
            print(f"LOCKED {path}")
        else:
            parser.error("choose --prepare or --lock")
    except GateError as exc:
        print(f"FAIL {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
