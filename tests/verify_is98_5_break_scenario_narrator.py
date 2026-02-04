import os
import json
import yaml
import unittest
import shutil
from pathlib import Path
from src.topics.narrator.break_scenario_narrator import BreakScenarioNarrator

class TestBreakScenarioNarrator(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is98_5")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.decision_dir = self.base_dir / "data" / "decision"
        self.registry_dir = self.base_dir / "registry" / "templates"
        self.export_dir = self.base_dir / "exports"
        
        self.decision_dir.mkdir(parents=True, exist_ok=True)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy real templates (with my appends) to temp registry
        real_templates = Path("registry/templates/script_templates_v1.yml")
        if real_templates.exists():
            shutil.copy(real_templates, self.registry_dir / "script_templates_v1.yml")
        else:
            # Fallback dummy
            dummy = {
                "break_scenario_shorts": [{"content": "{PREMISE_TEXT}\n{HOLD_TEXT}\n{WHAT_BREAKS_FIRST}\n{WINNERS_TEXT}"}],
                "break_scenario_long": [{"content": "{RELATIONSHIP}\n{PREMISE_TEXT}\n{WHAT_BREAKS_FIRST}\n{SECOND_ORDER_EFFECTS}\n{PICKAXE_DETAILS}"}]
            }
            (self.registry_dir / "script_templates_v1.yml").write_text(yaml.dump(dummy))

        # Dummy mentionables
        mentionables = {
            "top": [
                {"name": "SK Hynix", "role": "HBM", "why_must": "Exclusive HBM3E supply", "citations": ["E1", "E2"]},
                {"name": "TSMC", "role": "FOUNDRY", "why_must": "CoWoS bottleneck", "citations": ["E3"]},
                {"name": "Vertiv", "role": "COOLING", "why_must": "Liquid cooling dominance", "citations": ["E4"]}
            ]
        }
        (self.decision_dir / "mentionables_ranked.json").write_text(json.dumps(mentionables))

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_ready_scenario(self):
        # HIGH risk, 2 sources -> READY
        units = [
            {
                "interpretation_id": "UNIT-001",
                "interpretation_key": "RELATIONSHIP_BREAK_RISK",
                "target_sector": "STRATEGIC_ALLIANCE",
                "structural_narrative": "NVIDIA와 OpenAI 사이의 공급 루프 균열",
                "derived_metrics_snapshot": {
                    "stress_score": 0.85,
                    "signals": {"capital_loop": {"present": True}},
                    "reliability": 0.9
                },
                "hypothesis_jump": {
                    "status": "READY",
                    "independent_sources_count": 2
                },
                "why_now": ["Signal A", "Signal B"]
            }
        ]
        (self.decision_dir / "interpretation_units.json").write_text(json.dumps(units))
        
        # Set Hero
        hero = {
            "status": "LOCKED",
            "hero_topic": {
                "topic_id": "SYNTH-001",
                "source_units": ["UNIT-001"]
            }
        }
        (self.decision_dir / "hero_topic_lock.json").write_text(json.dumps(hero))
        
        narrator = BreakScenarioNarrator(self.base_dir)
        narrator.run()
        
        self.assertTrue((self.decision_dir / "break_scenario.json").exists())
        self.assertTrue((self.export_dir / "final_script_break_scenario_shorts.txt").exists())
        
        content = (self.export_dir / "final_script_break_scenario_shorts.txt").read_text()
        self.assertIn("NVIDIA와 OpenAI", content)
        self.assertIn("SK Hynix", content)
        # Should NOT contain HOLD text
        self.assertNotIn("아직 확정이 아닙니다", content)

    def test_hold_scenario(self):
        # MED risk -> HOLD
        units = [
            {
                "interpretation_id": "UNIT-002",
                "interpretation_key": "RELATIONSHIP_BREAK_RISK",
                "target_sector": "STRATEGIC_ALLIANCE",
                "structural_narrative": "NVIDIA와 OpenAI 사이의 미묘한 기류",
                "derived_metrics_snapshot": {
                    "stress_score": 0.6,
                    "signals": {"supplier_dependency": {"present": True}},
                    "reliability": 0.5
                },
                "hypothesis_jump": {
                    "status": "HOLD",
                    "independent_sources_count": 1
                }
            }
        ]
        (self.decision_dir / "interpretation_units.json").write_text(json.dumps(units))
        
        # No hero today, check hold queue
        (self.decision_dir / "hero_topic_lock.json").write_text(json.dumps({"status": "NO_HERO"}))
        hold_queue = [{"source_units": ["UNIT-002"]}]
        (self.decision_dir / "hold_queue.json").write_text(json.dumps(hold_queue))

        narrator = BreakScenarioNarrator(self.base_dir)
        narrator.run()
        
        content = (self.export_dir / "final_script_break_scenario_long.txt").read_text()
        self.assertIn("아직 확정이 아닙니다", content)
        self.assertIn("트리거를 기다리겠습니다", content)

    def test_guard_no_signal(self):
        (self.decision_dir / "interpretation_units.json").write_text(json.dumps([]))
        
        narrator = BreakScenarioNarrator(self.base_dir)
        narrator.run()
        
        self.assertFalse((self.decision_dir / "break_scenario.json").exists())
        self.assertFalse((self.export_dir / "final_script_break_scenario_shorts.txt").exists())

if __name__ == "__main__":
    unittest.main()
