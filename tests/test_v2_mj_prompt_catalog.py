import json
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
        for record in catalog["records"]:
            prompt = record["prompt"]["mj_text"]
            self.assertIn("--v 8.2", prompt)
            self.assertIn("VIS-LW-V2", prompt)
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
            "production/style/v2-visual-qa.md",
            "production/style/v2-reference-policy.md",
            "production/style/v2-world-reference-atoms.md",
            "production/style/v2-world-asset-visual-registry.json",
        }
        for record in catalog["records"]:
            authority_paths = {entry["path"] for entry in record["authority_refs"]}
            self.assertTrue(required.issubset(authority_paths), record["prompt_id"])
            self.assertFalse(any("/archive/" in path for path in authority_paths))

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
            self.assertTrue(any(record["target_key"] == target for record in hero_records), target)

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
                "BLOCKED_UNTIL_CHARACTER_VISUAL_ANCHOR",
            )
            checks = " ".join(record["acceptance_checks"])
            self.assertIn("Cannot be used as Canon identity", checks)

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
