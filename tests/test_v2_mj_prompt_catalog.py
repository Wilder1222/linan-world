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
            "--draft",
            "--hd",
            "::",
        )
        for record in catalog["records"]:
            prompt = record["prompt"]["mj_text"]
            self.assertIn("--v 8.2", prompt)
            self.assertIn("--raw", prompt)
            self.assertIn("VIS-LW-V2", prompt)
            self.assertLessEqual(len(prompt), 6000)
            self.assertNotIn("<", prompt)
            self.assertNotIn(">", prompt)
            for token in forbidden:
                self.assertNotIn(token, prompt)
            for authority in record["authority_refs"]:
                self.assertNotIn("/archive/", authority["path"])

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
            "production/style/v2-world-asset-visual-registry.json",
        }
        for record in catalog["records"]:
            authority_paths = {entry["path"] for entry in record["authority_refs"]}
            self.assertTrue(required.issubset(authority_paths), record["prompt_id"])
            self.assertFalse(any("/archive/" in path for path in authority_paths))

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
