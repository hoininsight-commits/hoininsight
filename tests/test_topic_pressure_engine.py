import unittest
import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.topics.topic_pressure_engine import TopicPressureEngine

class TestTopicPressureEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TopicPressureEngine(project_root)

    def test_pressure_calculation(self):
        topic = {"theme": "AI Infrastructure", "prediction_score": 80}
        signal = {"strength": 90}
        flow = {"top_capital_flow_theme": {"impact_direction": "POSITIVE"}}
        story = {"featured_theme": "AI Infrastructure"}
        
        res = self.engine._calculate_pressure(topic, signal, flow, story)
        # 0.4 * 0.9 + 0.3 * 0.9 + 0.2 * 0.8 + 0.1 * 0.8 = 0.36 + 0.27 + 0.16 + 0.08 = 0.87
        self.assertAlmostEqual(res["total"], 0.87)

if __name__ == "__main__":
    unittest.main()
