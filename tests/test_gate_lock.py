import json
import tempfile
import unittest
from pathlib import Path

from scripts.lock_gate import GateError, lock_gate, prepare_gate, sha256_file, validate_status_integrity


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_status() -> dict[str, str]:
    return {"baseline": "APPROVED", "canon_gate": "OPEN", "character_foundation_gate": "OPEN",
            "season_gate": "OPEN", "episode_gate": "OPEN", "character_final_gate": "OPEN", "delivery_gate": "OPEN"}


def make_scope(root: Path, gate: str = "canon", prerequisites: list[str] | None = None) -> None:
    (root / "canon").mkdir(parents=True, exist_ok=True)
    (root / "canon/source.md").write_text("locked fact\n", encoding="utf-8")
    write_json(root / "qa/production-status.json", make_status())
    write_json(root / f"qa/gates/scope-definitions/{gate}.json", {
        "schema_version": 1, "gate": gate, "scope": "delivery" if gate == "delivery" else gate,
        "prerequisites": prerequisites or [], "declared_frozen_items": ["SOURCE"],
        "items": [{"id": "SOURCE", "path": "canon/source.md", "mode": "whole_file"}],
    })


def write_review(path: Path, reviewer: str, manifest_hash: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("+++\n" + f'reviewer_id = "{reviewer}"\n' + 'status = "PASS"\n' +
                    f'reviewed_input_manifest_sha256 = "{manifest_hash}"\n' +
                    'signed_at = "2026-08-23T00:00:00+08:00"\n+++\n\nSigned review.\n', encoding="utf-8")


class GateLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.calls: list[tuple[str, str]] = []

    def tearDown(self):
        self.temp.cleanup()

    def runner(self, gate: str, scope: str) -> None:
        self.calls.append((gate, scope))

    def prepare(self, gate: str = "canon", scope: str = "canon") -> Path:
        return prepare_gate(self.root, gate, scope, validation_runner=self.runner)

    def test_prepare_writes_a_hashed_projection_manifest(self):
        make_scope(self.root)
        path = self.prepare()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("canon", data["gate"])
        self.assertEqual(1, len(data["items"]))
        self.assertEqual(64, len(data["items"][0]["projection_sha256"]))
        self.assertEqual([("canon", "canon")], self.calls)

    def test_changed_input_after_prepare_blocks_lock(self):
        make_scope(self.root)
        manifest = self.prepare()
        manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"; second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash); write_review(second, "reviewer-b", manifest_hash)
        (self.root / "canon/source.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "input projection changed"):
            lock_gate(self.root, "canon", "canon", [first, second], validation_runner=self.runner)

    def test_duplicate_reviewer_id_is_rejected(self):
        make_scope(self.root); manifest = self.prepare(); manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"; second = self.root / "qa/reviews/second.md"
        write_review(first, "same-reviewer", manifest_hash); write_review(second, "same-reviewer", manifest_hash)
        with self.assertRaisesRegex(GateError, "reviewer_id values must be distinct"):
            lock_gate(self.root, "canon", "canon", [first, second], validation_runner=self.runner)

    def test_missing_prerequisite_certificate_blocks_prepare(self):
        make_scope(self.root, gate="character-foundation", prerequisites=["canon"])
        with self.assertRaisesRegex(GateError, "missing prerequisite certificate"):
            self.prepare("character-foundation", "character-foundation")

    def test_delivery_prepare_and_lock_both_use_ready_validator(self):
        make_scope(self.root, gate="delivery"); manifest = self.prepare("delivery", "delivery")
        manifest_hash = sha256_file(manifest); first = self.root / "qa/reviews/first.md"; second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash); write_review(second, "reviewer-b", manifest_hash)
        lock_gate(self.root, "delivery", "delivery", [first, second], validation_runner=self.runner)
        self.assertEqual([("delivery", "delivery"), ("delivery", "delivery")], self.calls)

    def test_successful_lock_writes_certificate_and_status(self):
        make_scope(self.root); manifest = self.prepare(); manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"; second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash); write_review(second, "reviewer-b", manifest_hash)
        certificate = lock_gate(self.root, "canon", "canon", [first, second], validation_runner=self.runner)
        status = json.loads((self.root / "qa/production-status.json").read_text(encoding="utf-8"))
        self.assertEqual("LOCKED", status["canon_gate"])
        self.assertEqual("LOCKED", json.loads(certificate.read_text()) ["status"])

    def test_scope_definition_must_cover_every_declared_item(self):
        make_scope(self.root); path = self.root / "qa/gates/scope-definitions/canon.json"
        data = json.loads(path.read_text(encoding="utf-8")); data["declared_frozen_items"].append("MISSING"); write_json(path, data)
        with self.assertRaisesRegex(GateError, "declared_frozen_items mismatch"):
            self.prepare()

    def test_scope_definition_must_cover_manifest_required_paths(self):
        make_scope(self.root)
        write_json(
            self.root / "qa/project-manifest.json",
            {"required_paths": {"canon": ["canon/source.md", "canon/required.md"]}},
        )
        with self.assertRaisesRegex(GateError, "scope definition missing required paths"):
            self.prepare()

    def test_direct_locked_status_without_certificate_is_invalid(self):
        make_scope(self.root); status_path = self.root / "qa/production-status.json"
        status = json.loads(status_path.read_text(encoding="utf-8")); status["canon_gate"] = "LOCKED"; write_json(status_path, status)
        self.assertIn("locked_without_valid_certificate=canon", validate_status_integrity(self.root))


if __name__ == "__main__":
    unittest.main()
