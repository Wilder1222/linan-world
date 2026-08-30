import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V2MidjourneyPromptCatalogTests(unittest.TestCase):
    def test_catalog_validator_passes(self) -> None:
        result = subprocess.run(
            ["node", "scripts/validate_mj_v8_2_catalog.cjs"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_direct_prompts_are_v8_2_and_resolved(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(catalog["catalog_id"], "LINAN-VIS-LW-V2-MJ8.2")
        self.assertGreaterEqual(len(catalog["records"]), 1000)
        forbidden = (
            "<STYLE_REF_URL>",
            "--oref",
            "--ow",
            "--cref",
            "--cw",
            "--q ",
            "--quality",
            "--draft",
            "--sv",
            "::",
        )
        allowed_no_atoms = {"text", "watermark", "logo"}
        negative_prose = re.compile(r"\b(?:no|not|never|without)\b|do not", re.IGNORECASE)
        for record in catalog["records"]:
            prompt = record["prompt"]["mj_text"]
            self.assertIn("--v 8.2", prompt)
            self.assertNotIn("VIS-LW-V2", prompt)
            self.assertIn("--ar ", prompt)
            self.assertIn("--s ", prompt)
            self.assertIn("--c ", prompt)
            self.assertLessEqual(len(prompt), 6000)
            self.assertNotIn("<", prompt)
            self.assertNotIn(">", prompt)
            for token in forbidden:
                self.assertNotIn(token, prompt)
            for authority in record["authority_refs"]:
                self.assertNotIn("/archive/", authority["path"])
            raw_in_prompt = "--raw" in prompt
            self.assertEqual(raw_in_prompt, record["parameters"]["raw"])
            if record["state"]["technical_lane"]:
                self.assertTrue(raw_in_prompt)
            declared_no = record["prompt"].get("negative", [])
            if declared_no:
                self.assertIn("--no ", prompt)
            else:
                self.assertNotIn("--no ", prompt)
            self.assertTrue(set(declared_no).issubset(allowed_no_atoms))
            self.assertLessEqual(len(declared_no), 2)
            self.assertIsNone(
                negative_prose.search(record["prompt"]["positive"]),
                record["prompt_id"],
            )
            self.assertIsNone(
                re.search(r"[\u3400-\u9fff]", prompt),
                record["prompt_id"],
            )

        model_contract = catalog["model_contract"]
        optional = " ".join(model_contract["optional_after_approval_only"])
        self.assertNotIn("--sv", optional)
        self.assertIn(
            "--sv",
            model_contract["not_emitted_without_target_session_verification"],
        )

    def test_active_catalog_uses_only_v2_authority_sources(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        required = {
            "production/style/v2-urban-splendor-song-style-package.md",
            "production/style/v2-scene-composition-standard.md",
            "production/style/v2-costume-construction-standard.md",
            "production/style/v2-visual-qa.md",
            "production/style/v2-reference-policy.md",
            "production/style/v2-world-reference-atoms.md",
            "production/style/v2-world-asset-visual-registry.json",
        }
        for record in catalog["records"]:
            authority_paths = {entry["path"] for entry in record["authority_refs"]}
            self.assertTrue(required.issubset(authority_paths), record["prompt_id"])
            self.assertFalse(any("/archive/" in path for path in authority_paths))

    def test_scene_composition_profiles_bind_location_city_and_calibration_records(self) -> None:
        registry = json.loads(
            (ROOT / "production/style/v2-world-asset-visual-registry.json").read_text(
                encoding="utf-8"
            )
        )
        profiles = registry["scene_composition_profiles"]
        self.assertIn("SCN-STREET-LEVEL-WATER-MARKET", profiles)
        self.assertIn("SCN-WATER-CAPITAL-ESTABLISHING", profiles)
        for profile_id, profile in profiles.items():
            self.assertTrue(profile["prompt_block"], profile_id)
            self.assertTrue(profile["acceptance_checks"], profile_id)

        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        records = catalog["records"]
        for location_id, design in registry["locations"].items():
            profile_id = design["composition_profile_id"]
            self.assertIn(profile_id, profiles, location_id)
            location_records = [
                record
                for record in records
                if record["family"] == "location"
                and record["target"]["stable_id"] == location_id
            ]
            self.assertEqual(len(location_records), 7, location_id)
            self.assertTrue(
                all(
                    record["facts_snapshot"].get("composition_profile_id")
                    == profile_id
                    for record in location_records
                ),
                location_id,
            )

        day_canal = next(
            record
            for record in records
            if record["target_key"] == "CALIBRATION:DAY-CANAL"
        )
        self.assertEqual(
            day_canal["facts_snapshot"]["composition_profile_id"],
            "SCN-STREET-LEVEL-WATER-MARKET",
        )
        city_records = [
            record for record in records if record["family"] == "city-establishing"
        ]
        self.assertTrue(city_records)
        self.assertTrue(
            all(
                record["facts_snapshot"].get("composition_profile_id")
                == "SCN-WATER-CAPITAL-ESTABLISHING"
                for record in city_records
            )
        )

    def test_three_costume_validation_prompts_are_ready_and_visually_specific(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        expected = {
            "CHR-L1-01": "fragrance-powder traces",
            "CHR-L1-02": "peacock-ink",
            "CHR-L1-04": "deck-balance",
        }
        records = [
            record
            for record in catalog["records"]
            if record["family"] == "costume-validation"
        ]
        self.assertEqual(len(records), len(expected))
        for character_id, identity_detail in expected.items():
            record = next(
                item
                for item in records
                if item["target_key"] == f"COSTUME-VALIDATION:{character_id}:001"
            )
            self.assertEqual(record["asset_lane"], "costume-validation-fullbody")
            self.assertEqual(
                record["execution_status"], "READY_FOR_USER_COSTUME_VALIDATION"
            )
            self.assertTrue(record["parameters"]["raw"])
            self.assertEqual(record["parameters"]["ar"], "2:3")
            positive = record["prompt"]["positive"]
            for phrase in (
                "crossed-collar",
                "fine pores",
                "plain",
                "studio",
                identity_detail,
            ):
                self.assertIn(phrase, positive, record["prompt_id"])
            self.assertNotRegex(
                positive,
                r"\b(?:Shen Heng|Liu Shisi|Pei Jiuniang)\b",
                record["prompt_id"],
            )

    def test_all_central_characters_have_a_hero_key_art_lane(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        roster = json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
        expected = [character for character in roster["named_characters"] if character["tier"] in {"L1", "L2", "L3"}]
        hero_records = [record for record in catalog["records"] if record["asset_lane"] == "identity-hero"]
        self.assertEqual(len(hero_records), len(expected))
        for character in expected:
            target = f"CHARACTER:{character['id']}:HERO-001"
            hero = next((record for record in hero_records if record["target_key"] == target), None)
            self.assertIsNotNone(hero, target)
            self.assertEqual(hero["parameters"]["ar"], "2:3")
            self.assertEqual(
                hero["execution_status"],
                "BLOCKED_UNTIL_APPROVED_MASTER_REFERENCE",
            )
            self.assertEqual(
                hero["reference_binding"]["status"],
                "AWAITING_USER_APPROVED_MASTER_REFERENCE",
            )
            self.assertTrue(hero["depends_on"])

    def test_central_master_references_are_the_only_first_pass_character_tasks(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        roster = json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
        central = [character for character in roster["named_characters"] if character["tier"] in {"L1", "L2", "L3"}]
        for character in central:
            record = next(
                item
                for item in catalog["records"]
                if item["target_key"] == f"CHARACTER:{character['id']}:IDENTITY-001"
            )
            self.assertEqual(
                record["execution_status"],
                "READY_FOR_V2_MASTER_REFERENCE_SELECTION",
            )
            self.assertEqual(record["parameters"]["ar"], "3:4")
            self.assertTrue(record["parameters"]["raw"])
            self.assertLessEqual(record["parameters"]["stylize"], 100)
            self.assertLessEqual(record["parameters"]["chaos"], 2)

    def test_noncentral_character_explorations_do_not_claim_canonical_identity(self) -> None:
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        roster = json.loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
        central_ids = {
            character["id"]
            for character in roster["named_characters"]
            if character["tier"] in {"L1", "L2", "L3"}
        }
        coverage = catalog["coverage_contract"]
        self.assertEqual(
            coverage["named_character_visual_anchor_tasks"],
            len(roster["named_characters"]),
        )
        self.assertEqual(
            coverage["central_character_identity_anchors"], len(central_ids)
        )
        self.assertEqual(
            coverage["noncentral_character_visual_anchor_candidates"],
            len(roster["named_characters"]) - len(central_ids),
        )
        self.assertEqual(
            coverage["noncentral_character_occupation_states"],
            len(roster["named_characters"]) - len(central_ids),
        )
        self.assertEqual(coverage["water_city_establishing_views"], 3)
        self.assertEqual(coverage["central_character_motion_studies"], 3)
        self.assertNotIn("named_character_identity_anchors", coverage)
        identity_records = [
            record
            for record in catalog["records"]
            if record["target_key"].endswith(":IDENTITY-001")
        ]
        noncentral_records = [
            record
            for record in identity_records
            if record["target"]["stable_id"] not in central_ids
        ]
        self.assertEqual(
            len(noncentral_records),
            len(roster["named_characters"]) - len(central_ids),
        )
        for record in noncentral_records:
            self.assertEqual(record["asset_lane"], "character-visual-anchor-exploration")
            self.assertEqual(
                record["execution_status"],
                "READY_FOR_V2_VISUAL_ANCHOR_SELECTION",
            )
            anchor = record["facts_snapshot"]["visual_anchor"]
            for key in ("portrait", "wardrobe", "gesture", "setting", "presentation"):
                self.assertTrue(anchor[key], f"{record['prompt_id']}: {key}")
            state_target = record["target_key"].replace("IDENTITY-001", "STATE-001")
            state = next(
                item for item in catalog["records"] if item["target_key"] == state_target
            )
            self.assertIn(
                state["asset_lane"],
                {"supporting-hero-state", "supporting-occupation-state"},
            )

    def test_shen_heng_age_is_twenty_everywhere_active(self) -> None:
        profile = (ROOT / "characters/central/chr-l1-01-shen-heng.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("age_y0 = 20", profile)
        catalog = json.loads(
            (ROOT / "production/midjourney/v2-asset-prompt-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        shen_records = [
            record
            for record in catalog["records"]
            if record["target"].get("stable_id") == "CHR-L1-01"
        ]
        self.assertTrue(shen_records)
        for record in shen_records:
            facts = record["facts_snapshot"]
            if "age_y0" in facts:
                self.assertEqual(facts["age_y0"], 20)


if __name__ == "__main__":
    unittest.main()
