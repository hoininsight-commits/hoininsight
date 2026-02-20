import unittest
import json
import os
from pathlib import Path
from src.topics.multi_topic_priority_engine import MultiTopicPriorityEngine

class TestIS107MultiTopicPriority(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(".")
        self.output_path = self.base_dir / "data" / "decision" / "multi_topic_priority.json"
        
        # Run engine
        engine = MultiTopicPriorityEngine(self.base_dir)
        engine.run()

    def test_output_exists(self):
        self.assertTrue(self.output_path.exists())

    def test_strict_schema(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        required_keys = ["date", "long", "shorts", "metadata"]
        for key in required_keys:
            self.assertIn(key, data)

    def test_long_constraints(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        # LONG can be 0 (if no candidates) or 1
        if data["long"]:
            self.assertIsInstance(data["long"], dict)
            self.assertIn("topic_id", data["long"])
            self.assertTrue(len(data["long"]["axes"]) >= 2)

    def test_shorts_constraints(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        self.assertIsInstance(data["shorts"], list)
        self.assertTrue(len(data["shorts"]) <= 4)
        for s in data["shorts"]:
            self.assertIn("topic_id", s)
            self.assertTrue(len(s["axes"]) >= 1)

    def test_no_overlap(self):
        data = json.loads(self.output_path.read_text(encoding='utf-8'))
        if data["long"] and data["shorts"]:
            long_id = data["long"]["topic_id"]
            short_ids = [s["topic_id"] for s in data["shorts"]]
            self.assertNotIn(long_id, short_ids)

    def test_no_undefined_literals(self):
        content = self.output_path.read_text(encoding='utf-8')
        self.assertNotIn("undefined", content.lower())
        # null is okay for "long" if empty, but we check for string literal "null" as mistake
        self.assertNotIn('"null"', content.lower())

if __name__ == "__main__":
    unittest.main()
