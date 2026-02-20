import os
import json
import unittest
import shutil
import re
from pathlib import Path
from src.ui.narrative_entry_hook_generator import NarrativeEntryHookGenerator

class TestNarrativeEntryHook(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("temp_test_is101_2")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        
        self.decision_dir.mkdir(parents=True, exist_ok=True)
        self.ui_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_hook_structural(self):
        # Mock inputs
        summary = {
            "status": "READY",
            "why_now": ["새로운 칩 발표"],
            "core_logic": ["A가 흔들리면 B가 재편된다", "논리 문장 2"]
        }
        (self.ui_dir / "hero_summary.json").write_text(json.dumps(summary))
        
        gen = NarrativeEntryHookGenerator(self.base_dir)
        gen.run()
        
        out_path = self.ui_dir / "narrative_entry_hook.json"
        self.assertTrue(out_path.exists())
        
        data = json.loads(out_path.read_text(encoding='utf-8'))
        
        self.assertEqual(data["hook_type"], "STRUCTURAL")
        self.assertEqual(data["confidence_level"], "HIGH")
        
        sentence = data["entry_sentence"]
        self.assertGreater(len(sentence), 10)
        self.assertIsNone(re.search(r'\d', sentence), "Sentence should not contain numbers")
        self.assertNotIn("?", sentence, "Sentence should not be a question")
        self.assertLessEqual(sentence.count(","), 2, "Max 2 commas allowed")

    def test_hook_warning(self):
        summary = {
            "status": "HOLD",
            "why_now": ["가격 변동성"],
            "core_logic": ["문장 1"]
        }
        (self.ui_dir / "hero_summary.json").write_text(json.dumps(summary))
        
        gen = NarrativeEntryHookGenerator(self.base_dir)
        gen.run()
        
        data = json.loads((self.ui_dir / "narrative_entry_hook.json").read_text())
        self.assertEqual(data["hook_type"], "WARNING")
        self.assertEqual(data["confidence_level"], "LOW")

    def test_hook_flow(self):
        summary = {
            "status": "READY",
            "why_now": ["자본 유입 확인"],
            "core_logic": ["문장 1"]
        }
        (self.ui_dir / "hero_summary.json").write_text(json.dumps(summary))
        
        gen = NarrativeEntryHookGenerator(self.base_dir)
        gen.run()
        
        data = json.loads((self.ui_dir / "narrative_entry_hook.json").read_text())
        self.assertEqual(data["hook_type"], "FLOW")
        self.assertEqual(data["confidence_level"], "MEDIUM")

if __name__ == "__main__":
    unittest.main()
