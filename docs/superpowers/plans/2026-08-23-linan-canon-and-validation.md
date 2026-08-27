# 《临安春信》Canon 与验证基础 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立《临安春信》的唯一世界事实源、稳定 ID、城市与制度规则、历史时间轴，以及能阻止数量、路径、占位和上游依赖错误进入后续人物与剧情阶段的验证器。

**Architecture:** Markdown 保存可读 Canon，JSON 保存机器可检验的数量、路径和 Gate 状态；`scripts/validate_project.py` 只做确定性结构验证，不替代人工历史与叙事审读。Canon 顶层文件负责摘要和索引，细节文件各自拥有唯一权威范围，避免同一规则在两处维护。

**Tech Stack:** Markdown、JSON、Python 3 标准库、`unittest`、PowerShell、Git。

---

## Task 1: 建立项目清单与验证器测试

**Files:**
- Create: `qa/project-manifest.json`
- Create: `qa/production-status.json`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_validate_project.py`

- [ ] **Step 1: 写入机器可读总量清单**

`qa/project-manifest.json` 使用以下完整内容：

```json
{
  "spec": "docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md",
  "baseline_commit": "58b8385",
  "character_counts": {
    "L1": 5,
    "L2": 4,
    "L3": 3,
    "A1": 8,
    "A2": 8,
    "A3": 8,
    "B": 48,
    "U": 120
  },
  "background_archetypes_minimum": 300,
  "pov_quotas": {
    "L1": 230,
    "L2": 108,
    "L3": 72,
    "A1": 80,
    "A2": 48,
    "A3": 16,
    "B": 72,
    "U": 22
  },
  "story_counts": {
    "arcs": 6,
    "episodes": 36,
    "microchapters_per_episode": 18,
    "microchapters": 648,
    "extension_cards": 120
  },
  "primary_function_quotas": {
    "main_plot": 312,
    "character_relationship": 204,
    "daily_life": 132
  },
  "required_paths": {
    "canon": [
      "canon/00-canon-index.md",
      "canon/00-id-and-terms-registry.md",
      "canon/01-world-bible.md",
      "canon/02-linan-city-atlas.md",
      "canon/03-spring-letter-system.md",
      "canon/04-history-and-timeline.md",
      "canon/05-government-economy-and-daily-life.md",
      "canon/06-language-and-material-culture.md",
      "canon/city/00-city-index.md",
      "canon/city/01-macro-geography-and-access.md",
      "canon/city/02-waterways-drainage-and-floodworks.md",
      "canon/city/03-he-ming-lane-and-shen-shop.md",
      "canon/city/04-imperial-street-night-market-and-spring-stage.md",
      "canon/city/05-west-lake-and-xiling-circle.md",
      "canon/city/06-qiantang-docks-and-qingyao-routes.md",
      "canon/city/07-government-granaries-gates-and-three-warehouses.md",
      "canon/city/08-clinic-temple-guesthouse-and-refugee-camp.md",
      "canon/city/09-travel-time-matrix.md",
      "canon/city/10-seasonal-location-state.md",
      "canon/city/11-reusable-location-cards.md",
      "canon/system/01-five-channel-observation.md",
      "canon/system/02-evidence-levels-no-spring-and-correction.md",
      "canon/system/03-transmission-privacy-and-access.md",
      "canon/system/04-lantern-signals-and-emergency-protocol.md",
      "canon/system/05-y13-failure-and-y0-redesign.md",
      "canon/institutions/01-government-authority-matrix.md",
      "canon/institutions/02-extraordinary-order-and-signatures.md",
      "canon/institutions/03-food-medicine-trade-and-storage.md",
      "canon/institutions/04-water-sanitation-health-and-relief.md",
      "canon/institutions/05-y0-crisis-causal-chain.md",
      "canon/institutions/06-postcrisis-public-information-charter.md"
    ]
  }
}
```

- [ ] **Step 2: 写入 Gate 初始状态**

`qa/production-status.json` 使用以下完整内容：

```json
{
  "baseline": "APPROVED",
  "canon_gate": "OPEN",
  "character_foundation_gate": "OPEN",
  "season_gate": "OPEN",
  "episode_gate": "OPEN",
  "character_final_gate": "OPEN",
  "delivery_gate": "OPEN"
}
```

- [ ] **Step 3: 写失败测试**

`tests/test_validate_project.py` 首版使用以下代码：

```python
import json
import unittest
from pathlib import Path

from scripts.validate_project import validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_committed_manifest_is_internally_consistent(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_manifest(data))

    def test_pov_total_must_equal_microchapter_total(self):
        data = {
            "character_counts": {"L1": 5, "L2": 4, "L3": 3, "A1": 8, "A2": 8, "A3": 8, "B": 48, "U": 120},
            "background_archetypes_minimum": 300,
            "pov_quotas": {"L1": 1},
            "story_counts": {"arcs": 6, "episodes": 36, "microchapters_per_episode": 18, "microchapters": 648, "extension_cards": 120},
            "primary_function_quotas": {"main_plot": 312, "character_relationship": 204, "daily_life": 132},
            "required_paths": {"canon": []}
        }
        self.assertIn("pov_total=1 expected=648", validate_manifest(data))

    def test_function_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["primary_function_quotas"]["daily_life"] = 131
        self.assertIn("function_total=647 expected=648", validate_manifest(data))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: 运行测试并确认因模块不存在而失败**

Run:

```powershell
python -m unittest tests.test_validate_project -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.validate_project'`。

- [ ] **Step 5: 提交测试与清单**

Run:

```powershell
git add qa/project-manifest.json qa/production-status.json scripts/__init__.py tests/__init__.py tests/test_validate_project.py
git commit -m "test: define Linan project invariants"
```

## Task 2: 实现基础验证器

**Files:**
- Create: `scripts/validate_project.py`
- Create: `scripts/lock_gate.py`
- Create: `qa/gates/gate-scope-schema.md`
- Create: `qa/gates/scope-definitions/canon.json`
- Modify: `tests/test_validate_project.py`
- Create: `tests/test_gate_lock.py`

- [ ] **Step 1: 先把基础验证与 Gate 证书失败测试写完整**

把 `tests/test_validate_project.py` 替换为：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_project import scan_forbidden, validate_manifest, validate_scope


ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_committed_manifest_is_internally_consistent(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_manifest(data))

    def test_pov_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["pov_quotas"]["L1"] -= 1
        self.assertIn("pov_total=647 expected=648", validate_manifest(data))

    def test_function_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["primary_function_quotas"]["daily_life"] -= 1
        self.assertIn("function_total=647 expected=648", validate_manifest(data))

    def test_scanner_is_case_insensitive_and_never_scans_qa(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "canon").mkdir()
            (root / "qa").mkdir()
            (root / "canon/fact.md").write_text("ToDo", encoding="utf-8")
            (root / "qa/rule.md").write_text("TODO", encoding="utf-8")
            errors = scan_forbidden("canon", root=root)
            self.assertEqual(1, len(errors))
            self.assertIn("path=canon/fact.md", errors[0])

    def test_delivery_scope_stays_closed_until_delivery_validator_is_installed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "qa").mkdir()
            manifest = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
            (root / "qa/project-manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            status = {
                "baseline": "APPROVED",
                "canon_gate": "OPEN",
                "character_foundation_gate": "OPEN",
                "season_gate": "OPEN",
                "episode_gate": "OPEN",
                "character_final_gate": "OPEN",
                "delivery_gate": "OPEN",
            }
            (root / "qa/production-status.json").write_text(
                json.dumps(status), encoding="utf-8"
            )
            self.assertIn(
                "delivery_validator_not_installed",
                validate_scope("delivery", strict=False, root=root),
            )


if __name__ == "__main__":
    unittest.main()
```

创建 `tests/test_gate_lock.py`，完整内容如下：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.lock_gate import (
    GateError,
    lock_gate,
    prepare_gate,
    sha256_file,
    validate_status_integrity,
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def make_status() -> dict[str, str]:
    return {
        "baseline": "APPROVED",
        "canon_gate": "OPEN",
        "character_foundation_gate": "OPEN",
        "season_gate": "OPEN",
        "episode_gate": "OPEN",
        "character_final_gate": "OPEN",
        "delivery_gate": "OPEN",
    }


def make_scope(root: Path, gate: str = "canon", prerequisites: list[str] | None = None) -> None:
    (root / "canon").mkdir(parents=True, exist_ok=True)
    (root / "canon/source.md").write_text("locked fact\n", encoding="utf-8")
    write_json(root / "qa/production-status.json", make_status())
    write_json(
        root / f"qa/gates/scope-definitions/{gate}.json",
        {
            "schema_version": 1,
            "gate": gate,
            "scope": "delivery" if gate == "delivery" else gate,
            "prerequisites": prerequisites or [],
            "declared_frozen_items": ["SOURCE"],
            "items": [
                {
                    "id": "SOURCE",
                    "path": "canon/source.md",
                    "mode": "whole_file",
                }
            ],
        },
    )


def write_review(path: Path, reviewer: str, manifest_hash: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "+++\n"
        f'reviewer_id = "{reviewer}"\n'
        'status = "PASS"\n'
        f'reviewed_input_manifest_sha256 = "{manifest_hash}"\n'
        'signed_at = "2026-08-23T00:00:00+08:00"\n'
        "+++\n\nSigned review.\n",
        encoding="utf-8",
    )


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
        first = self.root / "qa/reviews/first.md"
        second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash)
        write_review(second, "reviewer-b", manifest_hash)
        (self.root / "canon/source.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "input projection changed"):
            lock_gate(
                self.root,
                "canon",
                "canon",
                [first, second],
                validation_runner=self.runner,
            )

    def test_duplicate_reviewer_id_is_rejected(self):
        make_scope(self.root)
        manifest = self.prepare()
        manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"
        second = self.root / "qa/reviews/second.md"
        write_review(first, "same-reviewer", manifest_hash)
        write_review(second, "same-reviewer", manifest_hash)
        with self.assertRaisesRegex(GateError, "reviewer_id values must be distinct"):
            lock_gate(
                self.root,
                "canon",
                "canon",
                [first, second],
                validation_runner=self.runner,
            )

    def test_missing_prerequisite_certificate_blocks_prepare(self):
        make_scope(self.root, gate="character-foundation", prerequisites=["canon"])
        with self.assertRaisesRegex(GateError, "missing prerequisite certificate"):
            self.prepare("character-foundation", "character-foundation")

    def test_delivery_prepare_and_lock_both_use_ready_validator(self):
        make_scope(self.root, gate="delivery", prerequisites=[])
        manifest = self.prepare("delivery", "delivery")
        manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"
        second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash)
        write_review(second, "reviewer-b", manifest_hash)
        lock_gate(
            self.root,
            "delivery",
            "delivery",
            [first, second],
            validation_runner=self.runner,
        )
        self.assertEqual(
            [("delivery", "delivery"), ("delivery", "delivery")], self.calls
        )

    def test_successful_lock_writes_certificate_and_status(self):
        make_scope(self.root)
        manifest = self.prepare()
        manifest_hash = sha256_file(manifest)
        first = self.root / "qa/reviews/first.md"
        second = self.root / "qa/reviews/second.md"
        write_review(first, "reviewer-a", manifest_hash)
        write_review(second, "reviewer-b", manifest_hash)
        certificate = lock_gate(
            self.root,
            "canon",
            "canon",
            [first, second],
            validation_runner=self.runner,
        )
        status = json.loads(
            (self.root / "qa/production-status.json").read_text(encoding="utf-8")
        )
        self.assertEqual("LOCKED", status["canon_gate"])
        self.assertEqual("LOCKED", json.loads(certificate.read_text())["status"])

    def test_scope_definition_must_cover_every_declared_item(self):
        make_scope(self.root)
        path = self.root / "qa/gates/scope-definitions/canon.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["declared_frozen_items"].append("MISSING")
        write_json(path, data)
        with self.assertRaisesRegex(GateError, "declared_frozen_items mismatch"):
            self.prepare()

    def test_direct_locked_status_without_certificate_is_invalid(self):
        make_scope(self.root)
        status_path = self.root / "qa/production-status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["canon_gate"] = "LOCKED"
        write_json(status_path, status)
        self.assertIn(
            "locked_without_valid_certificate=canon",
            validate_status_integrity(self.root),
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认实现尚不存在**

Run:

```powershell
python -m unittest tests.test_validate_project tests.test_gate_lock -v
```

Expected: FAIL，错误明确包含 `ModuleNotFoundError` 或缺少 `scripts.validate_project` / `scripts.lock_gate`。

- [ ] **Step 3: 实现总量、路径、占位与 Gate 状态检查**

创建 `scripts/validate_project.py`，完整内容如下：

```python
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "qa/project-manifest.json"
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


def validate_required_paths(
    data: dict[str, Any], scope: str, root: Path = ROOT
) -> list[str]:
    errors: list[str] = []
    for relative in data.get("required_paths", {}).get(scope, []):
        if not (root / relative).exists():
            errors.append(f"missing_path={relative}")
    return errors


def scan_forbidden(scope: str, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    roots = SCOPE_ROOTS[scope]
    for root_name in roots:
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
                    errors.append(
                        f"forbidden_rule={rule_id} path={path.relative_to(root)} line={line}"
                    )
    return errors


def validate_scope(scope: str, strict: bool, root: Path = ROOT) -> list[str]:
    manifest = load_json(root / "qa/project-manifest.json")
    errors = validate_manifest(manifest)
    try:
        from scripts.lock_gate import validate_status_integrity
    except ModuleNotFoundError:
        from lock_gate import validate_status_integrity

    errors.extend(validate_status_integrity(root))
    if scope in {"delivery", "all"}:
        errors.append("delivery_validator_not_installed")
    if scope in manifest.get("required_paths", {}):
        errors.extend(validate_required_paths(manifest, scope, root=root))
    if strict:
        errors.extend(scan_forbidden(scope, root=root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=("manifest", "canon", "character-foundation", "characters", "story", "season", "episodes", "extensions", "content", "delivery", "all"),
        default="manifest",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    errors = validate_scope(args.scope, args.strict)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"FAIL scope={args.scope} errors={len(errors)}")
        return 1
    print(f"PASS scope={args.scope} errors=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 实现不可手改的 Gate 证书工具**

创建 `scripts/lock_gate.py`，完整内容如下：

```python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
GATE_NAMES = (
    "canon",
    "character-foundation",
    "season",
    "episode",
    "character-final",
    "delivery",
)
STATUS_KEYS = {
    "canon": "canon_gate",
    "character-foundation": "character_foundation_gate",
    "season": "season_gate",
    "episode": "episode_gate",
    "character-final": "character_final_gate",
    "delivery": "delivery_gate",
}
ValidationRunner = Callable[[str, str], None]


class GateError(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return value


def atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def safe_relative_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise GateError(f"path escapes repository root: {relative}") from exc
    return candidate


def json_pointer(value: object, pointer: str) -> object:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise GateError(f"invalid JSON pointer: {pointer}")
    current = value
    for encoded in pointer[1:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise GateError(f"missing JSON pointer: {pointer}")
    return current


def markdown_region(text: str, region_id: str) -> str:
    start = f"<!-- LOCK:{region_id} START -->"
    end = f"<!-- LOCK:{region_id} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise GateError(f"region markers must occur exactly once: {region_id}")
    body = text.split(start, 1)[1].split(end, 1)[0]
    return body.replace("\r\n", "\n").strip() + "\n"


def project_item(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    item_id = str(item["id"])
    mode = str(item["mode"])
    result: dict[str, Any] = {"id": item_id, "mode": mode}
    if mode == "whole_file":
        path = safe_relative_path(root, str(item["path"]))
        if not path.is_file():
            raise GateError(f"missing frozen path: {item['path']}")
        result["path"] = str(item["path"])
        result["projection_sha256"] = sha256_file(path)
        return result
    if mode == "json_pointers":
        path = safe_relative_path(root, str(item["path"]))
        data = read_json(path)
        pointers = item.get("immutable_pointers")
        if not isinstance(pointers, list) or not pointers:
            raise GateError(f"json_pointers item needs immutable_pointers: {item_id}")
        projection = {str(pointer): json_pointer(data, str(pointer)) for pointer in pointers}
        result["path"] = str(item["path"])
        result["immutable_pointers"] = [str(pointer) for pointer in pointers]
        result["projection_sha256"] = sha256_bytes(canonical_json(projection))
        return result
    if mode == "markdown_regions":
        path = safe_relative_path(root, str(item["path"]))
        text = path.read_text(encoding="utf-8")
        region_ids = item.get("region_ids")
        if not isinstance(region_ids, list) or not region_ids:
            raise GateError(f"markdown_regions item needs region_ids: {item_id}")
        projection = {str(region): markdown_region(text, str(region)) for region in region_ids}
        result["path"] = str(item["path"])
        result["region_ids"] = [str(region) for region in region_ids]
        result["projection_sha256"] = sha256_bytes(canonical_json(projection))
        return result
    if mode == "manifest_paths":
        manifest_path = safe_relative_path(root, str(item["manifest_path"]))
        manifest = read_json(manifest_path)
        relative_paths = json_pointer(manifest, str(item["paths_pointer"]))
        if not isinstance(relative_paths, list) or not all(
            isinstance(value, str) for value in relative_paths
        ):
            raise GateError(f"manifest_paths pointer must resolve to string list: {item_id}")
        members = []
        for relative in relative_paths:
            path = safe_relative_path(root, relative)
            if not path.is_file():
                raise GateError(f"missing manifest member: {relative}")
            members.append({"path": relative, "sha256": sha256_file(path)})
        result["manifest_path"] = str(item["manifest_path"])
        result["paths_pointer"] = str(item["paths_pointer"])
        result["members"] = members
        result["projection_sha256"] = sha256_bytes(canonical_json(members))
        return result
    raise GateError(f"unsupported projection mode: {mode}")


def load_scope_definition(root: Path, gate: str, scope: str) -> tuple[Path, dict[str, Any]]:
    path = root / f"qa/gates/scope-definitions/{gate}.json"
    data = read_json(path)
    if data.get("schema_version") != 1:
        raise GateError("scope definition schema_version must be 1")
    if data.get("gate") != gate or data.get("scope") != scope:
        raise GateError("scope definition gate/scope mismatch")
    items = data.get("items")
    declared = data.get("declared_frozen_items")
    if not isinstance(items, list) or not isinstance(declared, list):
        raise GateError("scope definition needs items and declared_frozen_items")
    item_ids = [str(item.get("id")) for item in items if isinstance(item, dict)]
    if len(item_ids) != len(items) or len(set(item_ids)) != len(item_ids):
        raise GateError("scope item IDs must be present and unique")
    if set(map(str, declared)) != set(item_ids):
        raise GateError("declared_frozen_items mismatch")
    prerequisites = data.get("prerequisites")
    if not isinstance(prerequisites, list) or any(
        value not in GATE_NAMES for value in prerequisites
    ):
        raise GateError("invalid prerequisites")
    return path, data


def prerequisite_records(root: Path, prerequisites: list[str]) -> list[dict[str, str]]:
    records = []
    for prerequisite in prerequisites:
        relative = f"qa/gates/{prerequisite}-gate.json"
        path = root / relative
        if not path.is_file():
            raise GateError(f"missing prerequisite certificate: {prerequisite}")
        certificate = read_json(path)
        if certificate.get("gate") != prerequisite or certificate.get("status") != "LOCKED":
            raise GateError(f"invalid prerequisite certificate: {prerequisite}")
        records.append({"gate": prerequisite, "path": relative, "sha256": sha256_file(path)})
    return records


def build_snapshot(root: Path, gate: str, scope: str) -> dict[str, Any]:
    definition_path, definition = load_scope_definition(root, gate, scope)
    items = [project_item(root, item) for item in definition["items"]]
    prerequisites = prerequisite_records(root, list(definition["prerequisites"]))
    stable = {
        "schema_version": 1,
        "gate": gate,
        "scope": scope,
        "scope_definition_path": str(definition_path.relative_to(root)).replace("\\", "/"),
        "scope_definition_sha256": sha256_file(definition_path),
        "prerequisite_certificates": prerequisites,
        "items": items,
    }
    stable["aggregate_sha256"] = sha256_bytes(canonical_json(stable))
    return stable


def default_validation_runner(root: Path) -> ValidationRunner:
    def run(gate: str, scope: str) -> None:
        if gate == "delivery":
            command = [sys.executable, str(root / "scripts/build_final_gate.py"), "--verify-ready"]
        else:
            command = [
                sys.executable,
                str(root / "scripts/validate_project.py"),
                "--scope",
                scope,
                "--strict",
            ]
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
        if completed.returncode != 0:
            output = (completed.stdout + completed.stderr).strip()
            raise GateError(f"strict validation failed: {output}")

    return run


def prepare_gate(
    root: Path,
    gate: str,
    scope: str,
    validation_runner: ValidationRunner | None = None,
) -> Path:
    runner = validation_runner or default_validation_runner(root)
    runner(gate, scope)
    manifest = build_snapshot(root, gate, scope)
    manifest["prepared_at"] = datetime.now(timezone.utc).isoformat()
    path = root / f"qa/gates/input-manifests/{gate}.json"
    atomic_write_json(path, manifest)
    return path


def parse_review(path: Path, expected_manifest_hash: str) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A\+\+\+\s*\r?\n(.*?)\r?\n\+\+\+", text, re.DOTALL)
    if match is None:
        raise GateError(f"review lacks TOML front matter: {path}")
    try:
        front = tomllib.loads(match.group(1))
    except tomllib.TOMLDecodeError as exc:
        raise GateError(f"invalid review TOML: {path}: {exc}") from exc
    required = (
        "reviewer_id",
        "status",
        "reviewed_input_manifest_sha256",
        "signed_at",
    )
    if any(key not in front for key in required):
        raise GateError(f"review front matter missing required field: {path}")
    if front["status"] != "PASS":
        raise GateError(f"review status is not PASS: {path}")
    if front["reviewed_input_manifest_sha256"] != expected_manifest_hash:
        raise GateError(f"review signed a different input manifest: {path}")
    return {
        "reviewer_id": str(front["reviewer_id"]),
        "signed_at": str(front["signed_at"]),
        "path": path.as_posix(),
        "sha256": sha256_file(path),
    }


def stable_manifest_fields(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "prepared_at"}


def lock_gate(
    root: Path,
    gate: str,
    scope: str,
    review_paths: list[Path],
    validation_runner: ValidationRunner | None = None,
) -> Path:
    if len(review_paths) < 2:
        raise GateError("at least two reviews are required")
    runner = validation_runner or default_validation_runner(root)
    runner(gate, scope)
    manifest_path = root / f"qa/gates/input-manifests/{gate}.json"
    stored_manifest = read_json(manifest_path)
    current_snapshot = build_snapshot(root, gate, scope)
    if stable_manifest_fields(stored_manifest) != current_snapshot:
        raise GateError("input projection changed after prepare")
    manifest_hash = sha256_file(manifest_path)
    reviews = [parse_review(path, manifest_hash) for path in review_paths]
    reviewer_ids = [review["reviewer_id"] for review in reviews]
    if len(set(reviewer_ids)) != len(reviewer_ids):
        raise GateError("reviewer_id values must be distinct")
    certificate = {
        "schema_version": 1,
        "gate": gate,
        "scope": scope,
        "status": "LOCKED",
        "input_manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "input_manifest_sha256": manifest_hash,
        "scope_definition_sha256": stored_manifest["scope_definition_sha256"],
        "prerequisite_certificates": stored_manifest["prerequisite_certificates"],
        "reviews": reviews,
        "locked_at": datetime.now(timezone.utc).isoformat(),
    }
    certificate_path = root / f"qa/gates/{gate}-gate.json"
    atomic_write_json(certificate_path, certificate)
    status_path = root / "qa/production-status.json"
    status = read_json(status_path)
    status[STATUS_KEYS[gate]] = "LOCKED"
    atomic_write_json(status_path, status)
    return certificate_path


def validate_status_integrity(root: Path = ROOT) -> list[str]:
    status_path = root / "qa/production-status.json"
    if not status_path.is_file():
        return []
    status = read_json(status_path)
    errors: list[str] = []
    for gate, status_key in STATUS_KEYS.items():
        if status.get(status_key) != "LOCKED":
            continue
        certificate_path = root / f"qa/gates/{gate}-gate.json"
        manifest_path = root / f"qa/gates/input-manifests/{gate}.json"
        try:
            certificate = read_json(certificate_path)
            manifest = read_json(manifest_path)
            if certificate.get("gate") != gate or certificate.get("status") != "LOCKED":
                raise GateError("certificate gate/status mismatch")
            if certificate.get("input_manifest_sha256") != sha256_file(manifest_path):
                raise GateError("certificate input manifest hash mismatch")
            current = build_snapshot(root, gate, str(certificate["scope"]))
            if stable_manifest_fields(manifest) != current:
                raise GateError("locked input projection changed")
            for review in certificate.get("reviews", []):
                review_path = safe_relative_path(root, str(review["path"]))
                if sha256_file(review_path) != review.get("sha256"):
                    raise GateError("locked review hash changed")
        except (GateError, KeyError, OSError, json.JSONDecodeError):
            errors.append(f"locked_without_valid_certificate={gate}")
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True, choices=GATE_NAMES)
    parser.add_argument("--scope", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--lock", action="store_true")
    parser.add_argument("--review", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.prepare:
            path = prepare_gate(ROOT, args.gate, args.scope)
            print(f"PREPARED gate={args.gate} manifest={path.relative_to(ROOT)}")
        else:
            path = lock_gate(
                ROOT,
                args.gate,
                args.scope,
                [ROOT / value for value in args.review],
            )
            print(f"LOCKED gate={args.gate} certificate={path.relative_to(ROOT)}")
    except (GateError, OSError, KeyError, ValueError) as exc:
        print(f"FAIL gate={args.gate} error={exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`qa/gates/gate-scope-schema.md` 使用以下完整内容：

```markdown
# Gate Scope Definition Schema v1

每个 `qa/gates/scope-definitions/{gate}.json` 必须包含：

- `schema_version: 1`
- `gate` 与 `scope`
- `prerequisites`：前置 Gate 名称数组
- `declared_frozen_items`：本 Gate 声明冻结的全部 item ID
- `items`：item 数组；其 ID 必须与 `declared_frozen_items` 集合完全相等

合法 mode：

- `whole_file`：需要 `path`
- `json_pointers`：需要 `path` 与非空 `immutable_pointers`
- `markdown_regions`：需要 `path` 与非空 `region_ids`，正文使用
  `<!-- LOCK:{ID} START -->` / `<!-- LOCK:{ID} END -->`
- `manifest_paths`：需要 `manifest_path` 与 `paths_pointer`，该指针必须指向显式路径数组

所有路径必须位于仓库内。Gate 工具对规范化投影、前置证书与 scope definition
计算 SHA-256；未声明模式、缺失路径、重复 ID、未覆盖声明冻结项均立即失败。
```

`qa/gates/scope-definitions/canon.json` 使用以下完整内容：

```json
{
  "schema_version": 1,
  "gate": "canon",
  "scope": "canon",
  "prerequisites": [],
  "declared_frozen_items": [
    "APPROVED_SPEC",
    "PROJECT_CONSTRAINTS",
    "CANON_REQUIRED_PATHS",
    "CANON_FACT_REGISTRY"
  ],
  "items": [
    {
      "id": "APPROVED_SPEC",
      "path": "docs/superpowers/specs/2026-08-22-linan-spring-letter-master-design.md",
      "mode": "whole_file"
    },
    {
      "id": "PROJECT_CONSTRAINTS",
      "path": "qa/project-manifest.json",
      "mode": "json_pointers",
      "immutable_pointers": [
        "/spec",
        "/baseline_commit",
        "/character_counts",
        "/background_archetypes_minimum",
        "/pov_quotas",
        "/story_counts",
        "/primary_function_quotas",
        "/required_paths/canon"
      ]
    },
    {
      "id": "CANON_REQUIRED_PATHS",
      "mode": "manifest_paths",
      "manifest_path": "qa/project-manifest.json",
      "paths_pointer": "/required_paths/canon"
    },
    {
      "id": "CANON_FACT_REGISTRY",
      "path": "qa/canon-fact-registry.json",
      "mode": "whole_file"
    }
  ]
}
```

- [ ] **Step 5: 运行测试并确认全部通过**

Run:

```powershell
python -m unittest tests.test_validate_project -v
python -m unittest tests.test_gate_lock -v
```

Expected: 基础验证器 5 项、Gate 工具 8 项测试全部通过。

首版故意让 `--scope delivery` 与 `--scope all` 返回 `delivery_validator_not_installed`；它们只在最终交付计划接入 DOCX、渲染与后验哈希验证后才允许通过。占位扫描从一开始就不读取 `qa/`、测试、脚本、计划或报告；最终内容阶段再改为严格读取 `qa/content-source-manifest.json` 白名单。

- [ ] **Step 6: 验证清单模式**

Run:

```powershell
python scripts/validate_project.py --scope manifest
```

Expected: `PASS scope=manifest errors=0`。

- [ ] **Step 7: 提交验证器**

Run:

```powershell
git add scripts/validate_project.py scripts/lock_gate.py qa/gates/gate-scope-schema.md qa/gates/scope-definitions/canon.json tests/test_validate_project.py tests/test_gate_lock.py
git commit -m "feat: add Linan project validator"
```

## Task 3: 建立 Canon 治理、ID 与术语权威

**Files:**
- Create: `canon/00-canon-index.md`
- Create: `canon/00-id-and-terms-registry.md`
- Create: `qa/canon-fact-registry.json`
- Modify: `qa/canon-change-log.md`

- [ ] **Step 1: 创建 Canon 索引**

`canon/00-canon-index.md` 必须按顺序列出：总规格、世界、时间轴、城市、春信、制度经济、语言物质文化；每项包含稳定 ID、权威范围、依赖、状态和链接。文件开头明确 C0 内部优先级为“批准总规格与本索引 > 世界/时间轴/制度 > 36 集 > 648 章”。

- [ ] **Step 2: 创建 ID 与术语表**

`canon/00-id-and-terms-registry.md` 必须定义并举出合法实例：

```text
CHR-L1-01  中央第一主角
CHR-L2-01  城市共主角
CHR-L3-01  中央对照人物
CHR-A1-01  一级重要角色
CHR-A2-01  二级重要角色
CHR-A3-01  三级重要角色
CHR-B-001  市井常驻人物
CHR-U-001  单元人物
CHR-BG-001  背景人口原型
LOC-001     地点
ORG-001     组织
EVT-Y13-001 十三年前事件
EVT-Y0-001  当代事件
OBJ-001     物件
CLU-001     线索
REL-001     关系
CR-001      Canon 变更
```

术语表必须锁定“微短章、母集、篇、春信、疑报、合报、无春、公信案、私情簿、非常令”的唯一含义，并注明 `S1` 只表示第一季，`C0`—`C4` 只表示正史等级。

- [ ] **Step 2A: 建立机器可读事实与优先级注册表**

创建 `qa/canon-fact-registry.json`，初始完整内容如下；后续任务只允许追加经过变更日志批准的事实，不得改字段名或时间锚顺序：

```json
{
  "schema_version": 1,
  "timeline_order": [
    "PRE-Y13",
    "Y-13",
    "Y0-OPEN",
    "ARC1-END",
    "ARC2-END",
    "ARC3-END",
    "ARC4-END",
    "ARC5-END",
    "ARC6-END",
    "ENDING",
    "Y+1"
  ],
  "facts": [
    {
      "fact_id": "FORMAT.ARC_COUNT",
      "value": 6,
      "authority_path": "project-approved-spec.md",
      "authority_anchor": "叙事交付",
      "priority": 0,
      "effective_from": "Y0-OPEN",
      "effective_until": null,
      "status": "ACTIVE",
      "change_id": "CR-001"
    },
    {
      "fact_id": "FORMAT.EPISODE_COUNT",
      "value": 36,
      "authority_path": "project-approved-spec.md",
      "authority_anchor": "叙事交付",
      "priority": 0,
      "effective_from": "Y0-OPEN",
      "effective_until": null,
      "status": "ACTIVE",
      "change_id": "CR-001"
    },
    {
      "fact_id": "FORMAT.MICROCHAPTER_COUNT",
      "value": 648,
      "authority_path": "project-approved-spec.md",
      "authority_anchor": "叙事交付",
      "priority": 0,
      "effective_from": "Y0-OPEN",
      "effective_until": null,
      "status": "ACTIVE",
      "change_id": "CR-001"
    }
  ]
}
```

每条事实固定写 `fact_id`、结构化 `value`、`authority_path`、`authority_anchor`、`priority`、`effective_from`、`effective_until`、`status` 与来源变更 ID。优先级数字越小权威越高，固定映射为：批准规格/Canon 索引 `0`、专项 Canon `1`、人物/关系 `2`、季纲 `3`、微章 `4`、扩展 `5`。有效区间采用左闭右开 `[effective_from, effective_until)`；`null` 表示延续至时间轴末端。同一 `fact_id` 在重叠有效区间出现不同值、路径与声明优先级不符、或低优先级来源试图用不同值覆盖高优先级来源时验证失败。Markdown 是解释视图，跨系统连续性只从该注册表读取 C0 真值。

- [ ] **Step 3: 登记治理文件创建记录**

在 `qa/canon-change-log.md` 新增 `CR-002`，记录 ID 与术语体系建立、影响范围和状态 `APPROVED`。

- [ ] **Step 4: 检查并提交**

Run:

```powershell
git diff --check
git add canon/00-canon-index.md canon/00-id-and-terms-registry.md qa/canon-fact-registry.json qa/canon-change-log.md
git commit -m "docs: establish Linan canon governance"
```

## Task 4: 完成世界圣经与总时间轴

**Files:**
- Create: `canon/01-world-bible.md`
- Create: `canon/04-history-and-timeline.md`

- [ ] **Step 1: 写世界圣经的九个固定章节**

按以下顺序完成：作品定位；平行南宋边界；主题与伦理；临安系统性脆弱；城市人口与依赖；职业武侠边界；技术与信息边界；禁止元素；后续地域扩展原则。明确无仙法、无现代科学术语、无唯一救世主、无门派升级、无将民间协同写成无政府主义。

- [ ] **Step 2: 写三层时间轴**

`canon/04-history-and-timeline.md` 必须包含：

1. Y-13 上元惊变逐日时间轴；
2. Y-13 至 Y0 的十三年人物与机构变化；
3. Y0 惊蛰至 Y+1 春分的节气时间轴；
4. 六篇起止节气；
5. 重要人物年龄换算；
6. 每项历史事实的来源与公开程度。

- [ ] **Step 3: 人工审计父辈年龄与事件顺序**

逐项确认沈蘅 Y0 20 岁、裴九娘 Y0 31 岁、上元惊变时年龄与经历可成立；确认城务司成立晚于旧灾、周伯安放入新香丸发生于 Y0 而非 Y-13。

- [ ] **Step 4: 提交世界与时间轴**

Run:

```powershell
git add canon/01-world-bible.md canon/04-history-and-timeline.md
git commit -m "docs: define Linan world rules and timeline"
```

## Task 5: 完成城市宏观地理、水系与旅行时间

**Files:**
- Create: `canon/02-linan-city-atlas.md`
- Create: `canon/city/00-city-index.md`
- Create: `canon/city/01-macro-geography-and-access.md`
- Create: `canon/city/02-waterways-drainage-and-floodworks.md`
- Create: `canon/city/09-travel-time-matrix.md`
- Create: `canon/city/10-seasonal-location-state.md`

- [ ] **Step 1: 锁定宏观空间关系**

明确皇城、御街、鹤鸣巷、西湖、钱塘码头、城南水渠、外城门、三仓与流民安置区的相对方向；任何剧情捷径必须能在地图和旅行时间表中解释。

- [ ] **Step 2: 锁定水系与灾害机制**

逐项写明上游雨量、钱塘潮、城内河网、短堤、堵渠、分洪闸、排水滞后、水污进入生活用水的路径；对应 `EVT-Y0-001` 至 `EVT-Y0-010`。

- [ ] **Step 3: 完成旅行时间矩阵**

`canon/city/09-travel-time-matrix.md` 必须给出 18 个主场景之间的常态步行、船行、雨季与封锁状态时间；矩阵对称项若不同，必须解释上行、潮汐、查验或地形原因。

- [ ] **Step 4: 完成六篇地点状态表**

每个主场景记录六篇中的开放、封锁、破损、积水、改用与恢复状态，并锁定 E31 前已经出现的救灾能力。

- [ ] **Step 5: 提交宏观城市 Canon**

Run:

```powershell
git add canon/02-linan-city-atlas.md canon/city/00-city-index.md canon/city/01-macro-geography-and-access.md canon/city/02-waterways-drainage-and-floodworks.md canon/city/09-travel-time-matrix.md canon/city/10-seasonal-location-state.md
git commit -m "docs: map Linan geography and water system"
```

## Task 6: 完成十八个可复用场景

**Files:**
- Create: `canon/city/03-he-ming-lane-and-shen-shop.md`
- Create: `canon/city/04-imperial-street-night-market-and-spring-stage.md`
- Create: `canon/city/05-west-lake-and-xiling-circle.md`
- Create: `canon/city/06-qiantang-docks-and-qingyao-routes.md`
- Create: `canon/city/07-government-granaries-gates-and-three-warehouses.md`
- Create: `canon/city/08-clinic-temple-guesthouse-and-refugee-camp.md`
- Create: `canon/city/11-reusable-location-cards.md`

- [ ] **Step 1: 为十八个场景逐一填写地点卡**

每张地点卡固定包含：ID、所属坊区、所有者、管理者、实际使用者、相邻地点与时间、白昼/夜间、晴雨/汛期、声音、气味、光线、材质、职业活动、生活行为、六篇状态、终局功能、禁止临时出现的出口或能力。

- [ ] **Step 2: 检查五大生活圈是否都有工作与休息空间**

鹤鸣巷、春台、西泠、钱塘、停云不能只保存主线用房；每处至少记录买卖、吃饭、清洁、储物、睡眠、照料与冲突发生的位置。

- [ ] **Step 3: 检查终局能力前置**

确认公共灶、医棚、刻版、船只调度、客舍安置、寺院开仓、城门通行和灯号挂点都在 E01—E30 可被自然看见。

- [ ] **Step 4: 提交场景 Canon**

Run:

```powershell
git add canon/city
git commit -m "docs: define reusable Linan locations"
```

## Task 7: 完成春信协议

**Files:**
- Create: `canon/03-spring-letter-system.md`
- Create: `canon/system/01-five-channel-observation.md`
- Create: `canon/system/02-evidence-levels-no-spring-and-correction.md`
- Create: `canon/system/03-transmission-privacy-and-access.md`
- Create: `canon/system/04-lantern-signals-and-emergency-protocol.md`
- Create: `canon/system/05-y13-failure-and-y0-redesign.md`

- [ ] **Step 1: 定义五信观察边界**

为香信、曲信、图信、水信、客信分别写：可观察事实、不可推断事项、原始记录格式、典型误差、可交叉验证渠道、对应职业与现实能力上限。

- [ ] **Step 2: 定义三级证据与无春判定**

锁定疑报、合报、无春的进入条件、退出条件、来源标签、时刻标签、亲见/转闻/推断标签及同显眼度更正规则；给出一次误报从发现到撤销的完整实例。

- [ ] **Step 3: 定义隐私与保护档案**

明确公开民生簿、限期解密调度簿、受保护私情簿的访问边界；将裴九娘原信列为私情簿范例，既保留来源又不公开幸存者身份。

- [ ] **Step 4: 定义灯号协议**

至少覆盖道路可通、需要医生、有粮、有人被困、可安置五类信号；每类写明颜色、位置、高度、持续方式、核验者、撤销和更正方法。

- [ ] **Step 5: 对照 Y-13 失败与 Y0 重构**

逐项解释旧制为何放大恐慌，以及新制如何通过分级、来源、纠错、隐私和横向通信降低风险；不得写成“旧人愚蠢、新人正确”。

- [ ] **Step 6: 提交春信协议**

Run:

```powershell
git add canon/03-spring-letter-system.md canon/system
git commit -m "docs: specify Spring Letter protocol"
```

## Task 8: 完成官署、经济、公共卫生与危机因果

**Files:**
- Create: `canon/05-government-economy-and-daily-life.md`
- Create: `canon/institutions/01-government-authority-matrix.md`
- Create: `canon/institutions/02-extraordinary-order-and-signatures.md`
- Create: `canon/institutions/03-food-medicine-trade-and-storage.md`
- Create: `canon/institutions/04-water-sanitation-health-and-relief.md`
- Create: `canon/institutions/05-y0-crisis-causal-chain.md`
- Create: `canon/institutions/06-postcrisis-public-information-charter.md`

- [ ] **Step 1: 锁定权力矩阵**

逐项写明城务司、临安府、殿前司、行业组织、寺院和民间节点在常态与非常令下的汇总、征用、封锁、调军、开仓、救济权限；明确宋惟敬无单独调军权，曹肃只能在殿前司改令后带领所部行动。

- [ ] **Step 2: 锁定非常令流程**

写明二十四时辰自动失效、临安府副署、殿前司军令、续行见证、公开依据与事后审查；解释宋惟敬如何以选择性呈报获得合法授权。

- [ ] **Step 3: 锁定粮药供应链**

追踪新粮、陈粮、白芷和关键药材从来源、船运、三仓、批发、零售到百姓桌面的时间、成本、损耗、价格变化和控制点。

- [ ] **Step 4: 锁定水污、拥挤与冬疫链**

明确病例如何出现、如何记录、何时超出个人病范围、医棚如何分级、饮水如何处理、哪些措施合理、哪些措施越权。

- [ ] **Step 5: 写十步当代危机因果**

每一步使用独立 `EVT-Y0` ID，记录行动人、直接目的、地点、时间、预期结果、非预期结果、下一步放大机制与最终责任；自然暴雨不得替人为操纵免责。

- [ ] **Step 6: 写灾后六项制度章程**

完整落实三类档案、十二处公信案、来源与更正记录、非常令失效与续签、隐私分级、春信屋无裁决权六项结果。

- [ ] **Step 7: 提交制度 Canon**

Run:

```powershell
git add canon/05-government-economy-and-daily-life.md canon/institutions
git commit -m "docs: define Linan institutions and crisis causality"
```

## Task 9: 完成语言与物质文化

**Files:**
- Create: `canon/06-language-and-material-culture.md`

- [ ] **Step 1: 写时间、钱币、称量与距离规则**
- [ ] **Step 2: 写服饰、发式、妆容、材料与阶层差异**
- [ ] **Step 3: 写饮食、香药、医药、造纸、刻版、船运、瓦舍的真实职业流程**
- [ ] **Step 4: 写官府、市井、商旅、艺人、北客的语言层级与禁用现代措辞**
- [ ] **Step 5: 为每个职业列出可见动作、常见错误、工具、身体痕迹和能力上限**
- [ ] **Step 6: 提交物质文化 Canon**

Run:

```powershell
git add canon/06-language-and-material-culture.md
git commit -m "docs: establish Linan material culture"
```

## Task 10: 扩展验证器并锁定 Canon Gate

**Files:**
- Modify: `tests/test_validate_project.py`
- Modify: `scripts/validate_project.py`
- Modify: `qa/production-status.json`
- Create: `qa/canon-dependency-matrix.md`
- Create: `qa/gates/input-manifests/canon.json`
- Create: `qa/gates/canon-gate.json`
- Create: `qa/reviews/canon-world-review.md`
- Create: `qa/reviews/canon-narrative-review.md`

- [ ] **Step 1: 增加 Canon 路径与事实优先级失败测试**

把 `tests/test_validate_project.py` 整体替换为以下完整内容：

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_project import (
    scan_forbidden,
    validate_canon_facts,
    validate_manifest,
    validate_required_paths,
    validate_scope,
)


ROOT = Path(__file__).resolve().parents[1]
TIMELINE = [
    "PRE-Y13",
    "Y-13",
    "Y0-OPEN",
    "ARC1-END",
    "ARC2-END",
    "ARC3-END",
    "ARC4-END",
    "ARC5-END",
    "ARC6-END",
    "ENDING",
    "Y+1",
]


def make_fact(
    *,
    value: object,
    authority_path: str,
    priority: int,
    effective_from: str = "Y0-OPEN",
    effective_until: str | None = None,
) -> dict[str, object]:
    return {
        "fact_id": "WORLD.TEST_FACT",
        "value": value,
        "authority_path": authority_path,
        "authority_anchor": "测试锚点",
        "priority": priority,
        "effective_from": effective_from,
        "effective_until": effective_until,
        "status": "ACTIVE",
        "change_id": "CR-TEST",
    }


def make_registry(*facts: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "timeline_order": TIMELINE,
        "facts": list(facts),
    }


class ManifestTests(unittest.TestCase):
    def test_committed_manifest_is_internally_consistent(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_manifest(data))

    def test_pov_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["pov_quotas"]["L1"] -= 1
        self.assertIn("pov_total=647 expected=648", validate_manifest(data))

    def test_function_total_must_equal_microchapter_total(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        data["primary_function_quotas"]["daily_life"] -= 1
        self.assertIn("function_total=647 expected=648", validate_manifest(data))

    def test_scanner_is_case_insensitive_and_never_scans_qa(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "canon").mkdir()
            (root / "qa").mkdir()
            (root / "canon/fact.md").write_text("ToDo", encoding="utf-8")
            (root / "qa/rule.md").write_text("TODO", encoding="utf-8")
            errors = scan_forbidden("canon", root=root)
            self.assertEqual(1, len(errors))
            self.assertIn("path=canon/fact.md", errors[0])

    def test_delivery_scope_stays_closed_until_delivery_validator_is_installed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "qa").mkdir()
            manifest = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
            (root / "qa/project-manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
            )
            status = {
                "baseline": "APPROVED",
                "canon_gate": "OPEN",
                "character_foundation_gate": "OPEN",
                "season_gate": "OPEN",
                "episode_gate": "OPEN",
                "character_final_gate": "OPEN",
                "delivery_gate": "OPEN",
            }
            (root / "qa/production-status.json").write_text(
                json.dumps(status), encoding="utf-8"
            )
            self.assertIn(
                "delivery_validator_not_installed",
                validate_scope("delivery", strict=False, root=root),
            )


class CanonPathTests(unittest.TestCase):
    def test_all_required_canon_paths_exist(self):
        data = json.loads((ROOT / "qa/project-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_required_paths(data, "canon", root=ROOT))


class CanonFactTests(unittest.TestCase):
    def test_conflicting_fact_effective_intervals_fail(self):
        registry = make_registry(
            make_fact(
                value={"state": "open"},
                authority_path="canon/01-world-bible.md",
                priority=1,
                effective_until="ARC4-END",
            ),
            make_fact(
                value={"state": "closed"},
                authority_path="canon/02-city-atlas.md",
                priority=1,
                effective_from="ARC2-END",
            ),
        )
        errors = validate_canon_facts(registry)
        self.assertIn(
            "fact_conflict=fact_id=WORLD.TEST_FACT first=0 second=1",
            errors,
        )

    def test_lower_priority_override_fails(self):
        registry = make_registry(
            make_fact(
                value="canon-value",
                authority_path="canon/01-world-bible.md",
                priority=1,
            ),
            make_fact(
                value="season-value",
                authority_path="story/season-01.md",
                priority=3,
            ),
        )
        errors = validate_canon_facts(registry)
        self.assertIn(
            "lower_priority_override=fact_id=WORLD.TEST_FACT high=0 low=1",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行失败测试并确认新能力尚未实现**

Run:

```powershell
python -m unittest tests.test_validate_project -v
```

Expected: FAIL，导入阶段明确报告 `cannot import name 'validate_canon_facts'`；此时不得修改断言绕过失败。

- [ ] **Step 3: 实现 Canon 事实区间、优先级与 CLI 汇总验证**

把 `scripts/validate_project.py` 整体替换为以下完整内容：

```python
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
    "fact_id",
    "value",
    "authority_path",
    "authority_anchor",
    "priority",
    "effective_from",
    "effective_until",
    "status",
    "change_id",
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


def validate_required_paths(
    data: dict[str, Any], scope: str, root: Path = ROOT
) -> list[str]:
    errors: list[str] = []
    for relative in data.get("required_paths", {}).get(scope, []):
        if not (root / relative).exists():
            errors.append(f"missing_path={relative}")
    return errors


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
                    errors.append(
                        f"forbidden_rule={rule_id} path={path.relative_to(root)} line={line}"
                    )
    return errors


def expected_priority(authority_path: str) -> int | None:
    path = authority_path.replace("\\", "/")
    if path in {"project-approved-spec.md", "canon/00-canon-index.md"}:
        return 0
    prefixes = (
        ("canon/", 1),
        ("characters/", 2),
        ("story/", 3),
        ("episodes/", 4),
        ("extensions/", 5),
    )
    for prefix, priority in prefixes:
        if path.startswith(prefix):
            return priority
    return None


def canonical_value(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def intervals_overlap(
    first_start: int,
    first_end: int,
    second_start: int,
    second_end: int,
) -> bool:
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
        fact_id = fact["fact_id"]
        authority_path = fact["authority_path"]
        start_anchor = fact["effective_from"]
        end_anchor = fact["effective_until"]
        if not isinstance(fact_id, str) or not fact_id:
            errors.append(f"fact[{index}].fact_id_must_be_nonempty_string")
        if not isinstance(authority_path, str) or not authority_path:
            errors.append(f"fact[{index}].authority_path_must_be_nonempty_string")
            continue
        declared_priority = fact["priority"]
        required_priority = expected_priority(authority_path)
        if required_priority is None:
            errors.append(f"fact[{index}].unknown_authority_path={authority_path}")
        elif not isinstance(declared_priority, int) or isinstance(declared_priority, bool):
            errors.append(f"fact[{index}].priority_must_be_integer")
        elif declared_priority != required_priority:
            errors.append(
                f"fact[{index}].priority={declared_priority} expected={required_priority} "
                f"authority_path={authority_path}"
            )
        if fact["status"] not in FACT_STATUSES:
            errors.append(f"fact[{index}].invalid_status={fact['status']}")
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
        normalized.append(
            {
                "index": index,
                "fact_id": fact_id,
                "value": canonical_value(fact["value"]),
                "priority": declared_priority,
                "start": start,
                "end": end,
            }
        )

    for first_position, first in enumerate(normalized):
        for second in normalized[first_position + 1 :]:
            if first["fact_id"] != second["fact_id"]:
                continue
            if first["value"] == second["value"]:
                continue
            if not intervals_overlap(
                first["start"], first["end"], second["start"], second["end"]
            ):
                continue
            if first["priority"] == second["priority"]:
                errors.append(
                    f"fact_conflict=fact_id={first['fact_id']} "
                    f"first={first['index']} second={second['index']}"
                )
                continue
            high, low = sorted((first, second), key=lambda item: item["priority"])
            errors.append(
                f"lower_priority_override=fact_id={first['fact_id']} "
                f"high={high['index']} low={low['index']}"
            )
    return sorted(errors)


def validate_scope(scope: str, strict: bool, root: Path = ROOT) -> list[str]:
    manifest = load_json(root / "qa/project-manifest.json")
    errors = validate_manifest(manifest)
    try:
        from scripts.lock_gate import validate_status_integrity
    except ModuleNotFoundError:
        from lock_gate import validate_status_integrity

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
    if strict:
        errors.extend(scan_forbidden(scope, root=root))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scope",
        choices=(
            "manifest",
            "canon",
            "character-foundation",
            "characters",
            "story",
            "season",
            "episodes",
            "extensions",
            "content",
            "delivery",
            "all",
        ),
        default="manifest",
    )
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
```

- [ ] **Step 4: 运行测试并确认由红转绿**

Run:

```powershell
python -m unittest tests.test_validate_project tests.test_gate_lock -v
```

Expected: `tests.test_validate_project` 8 项与 `tests.test_gate_lock` 8 项，共 16 项通过。

- [ ] **Step 5: 创建依赖矩阵**

`qa/canon-dependency-matrix.md` 为每个 Canon 文件记录上游、下游、事实所有权和变更传播范围；所有顶层摘要文件必须指向细节权威，不得复制第二套规则。

- [ ] **Step 6: 执行严格检查**

Run:

```powershell
python scripts/validate_project.py --scope canon --strict
git diff --check
```

Expected: 验证器输出 `PASS scope=canon errors=0` 且包含 `fact_conflicts=0`、`placeholder_matches=0`；`git diff --check` 无输出。QA 规则、测试和报告不属于 Canon 正文扫描范围。

- [ ] **Step 7: 人工 Canon 审读**

先运行：

```powershell
python scripts/lock_gate.py --gate canon --scope canon --prepare
```

世界/制度审读者与人物/叙事审读者分别在两份审读文件的 TOML 头写同一个输入清单哈希并签署。逐项确认：空间可达、权限可行、供应链可行、危机十步闭合、春信可核验、隐私不被公开主义牺牲、终局制度能由失败自然导出。

- [ ] **Step 8: 锁定并提交**

```powershell
python scripts/lock_gate.py --gate canon --scope canon --lock --review qa/reviews/canon-world-review.md --review qa/reviews/canon-narrative-review.md
python scripts/validate_project.py --scope canon --strict
git add canon qa scripts tests
git commit -m "qa: lock Linan foundation canon"
```

Expected: `qa/gates/canon-gate.json` 存在、证书输入与两份审读哈希有效，工作区干净，Canon Gate 为 `LOCKED`。
