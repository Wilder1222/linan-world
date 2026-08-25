import json
import unittest
from pathlib import Path

from scripts.audit_p3_e01_production import audit


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "production/episodes/S1-E01/episode-production-cards.json"
REPORT = ROOT / "qa/reviews/p3-e01-production-scaffold-review.json"


class P3E01ProductionTests(unittest.TestCase):
    def test_e01_scaffold_review_passes(self):
        report = audit()
        self.assertEqual("REVIEWED-P3-SCAFFOLD-PASS", report["status"])
        self.assertEqual(18, report["chapter_total"])
        self.assertTrue(report["checks"]["canonical_pov_identity"])
        self.assertTrue(report["checks"]["external_execution_blocked"])
        self.assertTrue(report["checks"]["ten_dimension_qa_pending"])

    def test_packet_keeps_episode_gate_boundary(self):
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual("P3-02-SCAFFOLD-DRAFT", packet["status"])
        self.assertEqual("OPEN", packet["episode_gate_status"])
        self.assertEqual("DEFERRED-UNTIL-EPISODE-GATE", packet["deferred_boundary"]["final_dialogue"])
        self.assertEqual(18, len(packet["cards"]))
        self.assertTrue(all(card["production_control"]["provider_calls"] == 0 for card in packet["cards"]))

    def test_report_is_rebuildable(self):
        audit()
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual("REVIEWED-P3-SCAFFOLD-PASS", report["status"])
        self.assertTrue(report["checks"]["source_manifest_current"])


if __name__ == "__main__":
    unittest.main()
