from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "qa/project-manifest.json"
REPORT = ROOT / "qa/reviews/canon-production-quality.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def add_missing(findings: list[dict], code: str, value: str, path: str) -> None:
    findings.append({"code": code, "value": value, "path": path})


def audit() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = manifest["required_paths"]["canon"]
    findings: list[dict] = []
    texts: dict[str, str] = {}
    for relative in paths:
        path = ROOT / relative
        text = read(path)
        texts[relative] = text
        if not text.strip():
            add_missing(findings, "missing_or_empty_canon", relative, relative)
        for match in re.finditer(r"\b(?:TODO|TBD|FIXME|待补|占位)\b", text, flags=re.I):
            add_missing(findings, "placeholder_in_canon", match.group(0), relative)

    city_index_path = "canon/city/00-city-index.md"
    city_index = texts.get(city_index_path, "")
    expected_locations = [f"LOC-{index:03d}" for index in range(1, 19)]
    city_ids = sorted(set(re.findall(r"LOC-\d{3}", city_index)))
    for identifier in expected_locations:
        if identifier not in city_ids:
            add_missing(findings, "missing_location_id", identifier, city_index_path)
    travel = texts.get("canon/city/09-travel-time-matrix.md", "")
    if "LOC-001` 至 `LOC-018" not in travel or travel.count("|") < 19:
        add_missing(findings, "location_travel_matrix_incomplete", "18 主场景/路线覆盖声明缺失", "canon/city/09-travel-time-matrix.md")

    water_path = "canon/city/02-waterways-drainage-and-floodworks.md"
    water = texts.get(water_path, "")
    expected_observations = [f"OBS-W-{index:03d}" for index in range(1, 11)]
    for identifier in expected_observations:
        if identifier not in water:
            add_missing(findings, "missing_water_observation", identifier, water_path)

    causal_path = "canon/institutions/05-y0-crisis-causal-chain.md"
    causal = texts.get(causal_path, "")
    expected_events = [f"EVT-Y0-{index:03d}" for index in range(1, 11)]
    causal_rows: dict[str, list[str]] = {}
    for line in causal.splitlines():
        if not line.startswith("| EVT-Y0-"):
            continue
        columns = [item.strip() for item in line.strip().strip("|").split("|")]
        if columns:
            causal_rows[columns[0]] = columns
    for identifier in expected_events:
        row = causal_rows.get(identifier)
        if not row:
            add_missing(findings, "missing_causal_event", identifier, causal_path)
        elif len(row) < 8 or any(not value for value in row[1:8]):
            add_missing(findings, "incomplete_causal_event", identifier, causal_path)

    registry_path = "canon/00-id-and-terms-registry.md"
    registry = texts.get(registry_path, "")
    required_terms = ["微短章", "母集", "篇", "春信", "疑报", "合报", "无春", "公信案", "私情簿", "非常令"]
    for term in required_terms:
        if term not in registry:
            add_missing(findings, "missing_registered_term", term, registry_path)

    timeline_path = "canon/04-history-and-timeline.md"
    timeline = texts.get(timeline_path, "")
    registry_timeline = texts.get(registry_path, "")
    required_anchors = [
        "PRE-Y13", "Y-13", "Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END",
        "ARC4-END", "ARC5-END", "ARC6-END", "ENDING", "Y+1",
    ]
    for anchor in required_anchors:
        if anchor not in registry_timeline:
            add_missing(findings, "missing_timeline_anchor", anchor, registry_path)
    for anchor in ("Y-13", "Y0", "Y+1"):
        if anchor not in timeline:
            add_missing(findings, "timeline_missing_story_anchor", anchor, timeline_path)

    channel_path = "canon/system/01-five-channel-observation.md"
    channel = texts.get(channel_path, "")
    expected_channels = ["香通道", "曲通道", "图通道", "水通道", "客通道"]
    for name in expected_channels:
        if name not in channel:
            add_missing(findings, "missing_observation_channel", name, channel_path)

    summary = {
        "canon_files": len(paths),
        "location_total": len(expected_locations),
        "water_observation_total": len(expected_observations),
        "causal_event_total": len(expected_events),
        "timeline_anchor_total": len(required_anchors),
        "observation_channel_total": len(expected_channels),
        "registered_term_total": len(required_terms),
    }
    return {
        "schema_version": 1,
        "status": "REVIEWED-PASS" if not findings else "OPEN",
        "scope": "P0 Canon production-quality semantic audit",
        "summary": summary,
        "checks": {
            "canon_inputs_present": not any(item["code"] == "missing_or_empty_canon" for item in findings),
            "no_placeholders": not any(item["code"] == "placeholder_in_canon" for item in findings),
            "locations_and_travel_bound": not any(item["code"].startswith("location_") or item["code"] == "missing_location_id" for item in findings),
            "water_observations_bound": not any(item["code"] == "missing_water_observation" for item in findings),
            "causal_chain_complete": not any(item["code"].endswith("causal_event") for item in findings),
            "terms_registered": not any(item["code"] == "missing_registered_term" for item in findings),
            "timeline_anchors_registered": not any(item["code"] == "missing_timeline_anchor" for item in findings),
            "five_channels_registered": not any(item["code"] == "missing_observation_channel" for item in findings),
        },
        "findings": findings,
        "notes": "该审计只验证 Canon 的可生产结构与跨文件锚点；人物选择、关系证据与 36 集因果仍由 Character/Season Gate 负责。",
    }


def main() -> int:
    report = audit()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["findings"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
