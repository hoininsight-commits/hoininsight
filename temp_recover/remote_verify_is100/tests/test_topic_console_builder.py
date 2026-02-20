import unittest
import json
import shutil
from pathlib import Path
from typing import Any
from src.ops.topic_console_builder import TopicConsoleBuilder

class TestTopicConsoleBuilder(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path("test_console_tmp")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.ops_dir = self.base_dir / "data" / "ops"
        self.ops_dir.mkdir(parents=True, exist_ok=True)
        self.ymd = "2026-01-26"
        self.ymd_path = self.ymd.replace("-", "/")
        
        self.builder = TopicConsoleBuilder(self.base_dir)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def _write_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def test_deterministic_join(self):
        """1) Verify deterministic join by topic_id and asset detection."""
        # Setup inputs
        view = {"sections": {"ready": [{"topic_id": "T1", "title": "Topic One", "lane": "FACT"}]}}
        quality = {"topics": [{"topic_id": "T1", "fact_anchor": "STRONG"}]}
        speak = {"verdicts": [{"topic_id": "T1", "speakability": "SPEAKABLE_NOW"}]}
        
        bundle_dir = self.base_dir / "data" / "ops" / "bundles" / self.ymd_path
        bundle = {"topics": [{"topic_id": "T1", "title": "Topic One"}]}
        
        script_dir = self.base_dir / "data" / "topics" / "gate" / self.ymd_path
        script_dir.mkdir(parents=True, exist_ok=True)
        script_file = script_dir / "script_v1_gate_t1.md"
        script_file.write_text("Script for T1\nID: T1", encoding="utf-8")

        self._write_json(self.ops_dir / "topic_view_today.json", view)
        self._write_json(self.ops_dir / "topic_quality_review_today.json", quality)
        self._write_json(self.ops_dir / "topic_speakability_today.json", speak)
        self._write_json(bundle_dir / "speak_bundle.json", bundle)

        # Run
        res = self.builder.run(self.ymd)
        t = res["topics"][0]
        
        self.assertEqual(t["topic_id"], "T1")
        self.assertEqual(t["speakability"], "SPEAKABLE_NOW")
        self.assertTrue(t["script_assets"]["script_md_path"].endswith("script_v1_gate_t1.md"))
        self.assertTrue(t["script_assets"]["speak_bundle_md_path"].endswith("speak_bundle.md"))
        self.assertEqual(len(t["script_assets"]["missing_assets"]), 0)

    def test_missing_assets(self):
        """2) Missing assets are recorded."""
        view = {"sections": {"ready": [{"topic_id": "T2", "title": "Empty"}]}}
        self._write_json(self.ops_dir / "topic_view_today.json", view)
        
        res = self.builder.run(self.ymd)
        t = res["topics"][0]
        self.assertIn("script_md", t["script_assets"]["missing_assets"])
        self.assertIn("speak_bundle", t["script_assets"]["missing_assets"])

    def test_markdown_output(self):
        """3) Verify markdown generation."""
        view = {"sections": {"ready": [{"topic_id": "T1", "title": "Test MD"}]}}
        self._write_json(self.ops_dir / "topic_view_today.json", view)
        
        self.builder.run(self.ymd)
        md_content = (self.base_dir / "data" / "ops" / "topic_console_today.md").read_text(encoding="utf-8")
        
        self.assertIn("# TOPIC CONSOLE", md_content)
        self.assertIn("## Test MD", md_content)
        self.assertIn("### 1) Why Selected", md_content)
        self.assertIn("### 2) Fact Anchors & Evidence", md_content)
        self.assertIn("### 3) Script / Speak Material", md_content)

if __name__ == "__main__":
    unittest.main()
