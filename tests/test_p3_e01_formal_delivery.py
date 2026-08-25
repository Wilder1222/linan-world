from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODE_DIR = ROOT / "production/episodes/S1-E01"


class P3E01FormalDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads((EPISODE_DIR / "episode-formal-delivery.json").read_text(encoding="utf-8"))
        cls.script = json.loads((EPISODE_DIR / "script-scenes.json").read_text(encoding="utf-8"))
        cls.storyboard = json.loads((EPISODE_DIR / "storyboard.json").read_text(encoding="utf-8"))
        cls.continuity = json.loads((EPISODE_DIR / "continuity-ledger.json").read_text(encoding="utf-8"))

    def test_formal_packet_is_draft_and_gate_open(self) -> None:
        self.assertEqual(self.packet["status"], "P3-03-DRAFT")
        self.assertEqual(self.packet["episode_gate_status"], "OPEN")
        self.assertEqual(self.packet["qa_policy"], {"dimensions": 10, "threshold": 90, "status": "PENDING-EPISODE-GATE"})

    def test_all_eighteen_scene_bindings_are_ordered(self) -> None:
        expected = [f"S1-E01-M{index:02d}" for index in range(1, 19)]
        self.assertEqual([scene["chapter_id"] for scene in self.packet["script_scenes"]], expected)
        self.assertEqual([scene["chapter_id"] for scene in self.packet["storyboard"]], expected)
        self.assertEqual([scene["chapter_id"] for scene in self.packet["continuity_ledger"]], expected)

    def test_each_scene_has_dialogue_and_no_camera_leak(self) -> None:
        for scene in self.packet["script_scenes"]:
            self.assertTrue(scene["beats"])
            self.assertIn("镜头", scene["dialogue_boundary"])
            for beat in scene["beats"]:
                self.assertTrue(beat["action"])
                self.assertTrue(beat["subtext"])
                self.assertTrue(beat["dialogue"])
                self.assertFalse(any(key in beat for key in ("camera", "shot_id", "storyboard")))

    def test_each_storyboard_scene_has_three_deterministic_shots(self) -> None:
        for scene in self.packet["storyboard"]:
            chapter_id = scene["chapter_id"]
            self.assertEqual([shot["shot_id"] for shot in scene["shots"]], [f"{chapter_id}-S0{index}" for index in range(1, 4)])
            for shot in scene["shots"]:
                self.assertEqual(shot["camera"]["axis_side"], "preserve")
                self.assertTrue(shot["light"]["physical_sources"])
                self.assertTrue(shot["temporal"]["start"])
                self.assertTrue(shot["temporal"]["event"])
                self.assertTrue(shot["temporal"]["end"])

    def test_continuity_matches_participants_and_defers_final_assets(self) -> None:
        for scene, ledger in zip(self.packet["script_scenes"], self.packet["continuity_ledger"]):
            self.assertEqual(set(ledger["characters"]), set(scene["participants"]))
            self.assertTrue(ledger["characters"])
            self.assertTrue(ledger["space_and_time"]["location_ids"])
            self.assertTrue(ledger["props"]["continuity_refs"])
            self.assertEqual(ledger["status"], "DRAFT-EPISODE-GATE")
        self.assertEqual(self.packet["deferred_boundary"]["u_unique_identity"], "DEFERRED-UNTIL-EPISODE-GATE")
        self.assertEqual(self.packet["deferred_boundary"]["bg_bindings"], "DEFERRED-UNTIL-EPISODE-GATE")
        self.assertEqual(self.packet["execution_policy"], "DESIGN-ONLY; no provider calls, media claims, or final render receipts.")


if __name__ == "__main__":
    unittest.main()
