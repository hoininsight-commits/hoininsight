import os
import json
import yaml
import unittest
from pathlib import Path
from src.collectors.relationship_stress_collector import RelationshipStressCollector
from src.decision.relationship_break_interpreter import RelationshipBreakInterpreter

class TestRelationshipStress(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is96_8")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup paths
        self.ops_dir = self.base_dir / "data" / "ops"
        self.decision_dir = self.base_dir / "data" / "decision"
        self.registry_dir = self.base_dir / "registry" / "sources"
        
        self.ops_dir.mkdir(parents=True, exist_ok=True)
        self.decision_dir.mkdir(parents=True, exist_ok=True)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy registry
        registry = {
            "sources": [
                {"id": "tier1_source", "reliability": 0.9},
                {"id": "tier2_source", "reliability": 0.6}
            ]
        }
        (self.registry_dir / "source_registry_v1.yml").write_text(yaml.dump(registry))

    def tearDown(self):
        import shutil
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_high_risk_scenario(self):
        # 1. HIGH risk: 2 sources, reliability>=0.7, deal_reprice + divergence -> HIGH
        catalyst = [
            {
                "event_id": "e1",
                "source_id": "tier1_source",
                "title": "NVIDIA and OpenAI talks stalled over reprice",
                "entities": ["NVIDIA", "OpenAI"],
                "as_of_date": "2026-02-04"
            },
            {
                "event_id": "e2",
                "source_id": "tier1_source",
                "title": "OpenAI exploring switch supplier for next cluster",
                "entities": ["NVIDIA", "OpenAI"],
                "as_of_date": "2026-02-04"
            }
        ]
        (self.ops_dir / "catalyst_events.json").write_text(json.dumps(catalyst))
        
        collector = RelationshipStressCollector(self.base_dir)
        collector.collect()
        
        stress_path = self.decision_dir / "relationship_stress.json"
        self.assertTrue(stress_path.exists())
        
        data = json.loads(stress_path.read_text())
        rel = data["relationships"][0]
        
        # deal_reprice (0.35) + statement_divergence (0.25) [talks] + supply_dependency (0.20) [switch supplier] = 0.8
        self.assertEqual(rel["break_risk"], "HIGH")
        self.assertGreaterEqual(rel["stress_score"], 0.75)
        
        # Test interpreter
        interpreter = RelationshipBreakInterpreter(self.base_dir)
        interpreter.interpret()
        
        unit_path = self.decision_dir / "interpretation_units.json"
        self.assertTrue(unit_path.exists())
        units = json.loads(unit_path.read_text())
        
        found = any(u["interpretation_key"] == "RELATIONSHIP_BREAK_RISK" and u["hypothesis_jump"]["status"] == "READY" for u in units)
        self.assertTrue(found)

    def test_med_risk_scenario(self):
        # 2. MED risk: single source -> HOLD eligible
        catalyst = [
            {
                "event_id": "e3",
                "source_id": "tier2_source",
                "title": "Rumors of NVIDIA reprice talks",
                "entities": ["NVIDIA", "OpenAI"],
                "as_of_date": "2026-02-04"
            }
        ]
        (self.ops_dir / "catalyst_events.json").write_text(json.dumps(catalyst))
        
        collector = RelationshipStressCollector(self.base_dir)
        collector.collect()
        
        data = json.loads((self.decision_dir / "relationship_stress.json").read_text())
        rel = data["relationships"][0]
        
        # stress_score = deal_reprice (0.35) or statement_divergence (0.25)? 
        # Title "reprice talks" matches both in my heuristic. -> 0.6
        self.assertEqual(rel["break_risk"], "MED")
        
        interpreter = RelationshipBreakInterpreter(self.base_dir)
        interpreter.interpret()
        
        units = json.loads((self.decision_dir / "interpretation_units.json").read_text())
        found = any(u["interpretation_key"] == "RELATIONSHIP_BREAK_RISK" and u["hypothesis_jump"]["status"] == "HOLD" for u in units)
        self.assertTrue(found)

    def test_low_risk_scenario(self):
        # 3. LOW risk: weak signals -> no interpretation emitted
        catalyst = [
            {
                "event_id": "e4",
                "source_id": "tier2_source",
                "title": "NVIDIA and OpenAI dinner party",
                "entities": ["NVIDIA", "OpenAI"],
                "as_of_date": "2026-02-04"
            }
        ]
        (self.ops_dir / "catalyst_events.json").write_text(json.dumps(catalyst))
        
        collector = RelationshipStressCollector(self.base_dir)
        collector.collect()
        
        data = json.loads((self.decision_dir / "relationship_stress.json").read_text())
        # If no keywords match and no manual seed, relationships should be empty
        self.assertEqual(len(data["relationships"]), 0)
        
        interpreter = RelationshipBreakInterpreter(self.base_dir)
        interpreter.interpret()
        
        unit_path = self.decision_dir / "interpretation_units.json"
        if unit_path.exists():
            units = json.loads(unit_path.read_text())
            found = any(u["interpretation_key"] == "RELATIONSHIP_BREAK_RISK" for u in units)
            self.assertFalse(found)

if __name__ == "__main__":
    unittest.main()
