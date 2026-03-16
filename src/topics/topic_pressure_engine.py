import os
import json
from pathlib import Path
from datetime import datetime

class TopicPressureEngine:
    """
    Evaluates multiple narrative topics and selects the TOP 1 based on a weighted 
    "Topic Pressure" score (Anomaly + Flow + Spread + Persistence).
    """

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.predictions_path = self.project_root / "data" / "ops" / "topic_predictions.json"
        self.story_path = self.project_root / "data" / "story" / "today_story.json"
        self.signal_path = self.project_root / "data" / "ops" / "hoin_signal_today.json"
        self.flow_path = self.project_root / "data" / "ops" / "capital_flow_impact.json"
        self.output_path = self.project_root / "data" / "topic" / "top_topic.json"
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def run_selection(self):
        print("[TopicPressureEngine] Starting Selection Analysis...")
        
        predictions = self._load_json(self.predictions_path)
        story = self._load_json(self.story_path)
        signal = self._load_json(self.signal_path)
        flow = self._load_json(self.flow_path)
        
        if not predictions or not predictions.get("predictions"):
            print("[TopicPressureEngine] ⚠️ No topic predictions found.")
            return None

        topic_candidates = predictions["predictions"]
        evaluated_topics = []

        for topic in topic_candidates:
            pressure_data = self._calculate_pressure(topic, signal, flow, story)
            evaluated_topics.append({
                "selected_topic": topic.get("theme", "Unknown Topic"),
                "topic_id": topic.get("topic_id"),
                "topic_pressure": round(pressure_data["total"], 2),
                "components": {
                    "anomaly": round(pressure_data["anomaly"], 2),
                    "capital_flow": round(pressure_data["flow"], 2),
                    "narrative_spread": round(pressure_data["spread"], 2),
                    "persistence": round(pressure_data["persistence"], 2)
                }
            })

        # Sort by pressure and pick TOP 1
        top_topic = sorted(evaluated_topics, key=lambda x: x["topic_pressure"], reverse=True)[0]
        top_topic["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(top_topic, f, indent=2, ensure_ascii=False)

        print(f"[TopicPressureEngine] Selected Topic: {top_topic['selected_topic']} (Pressure: {top_topic['topic_pressure']})")
        return top_topic

    def _calculate_pressure(self, topic, signal, flow, story):
        # topic_pressure = 0.4 * anomaly + 0.3 * flow + 0.2 * spread + 0.1 * persistence
        
        # 1. Anomaly (0-1.0)
        anomaly_val = (signal.get("strength", 50) / 100) if signal else 0.5
        
        # 2. Capital Flow (0-1.0)
        flow_val = 0.5
        if flow:
            impact = flow.get("top_capital_flow_theme", {}).get("impact_direction", "NEUTRAL")
            if impact == "POSITIVE": flow_val = 0.9
            elif impact == "NEGATIVE": flow_val = 0.2
            
        # 3. Narrative Spread (0-1.0)
        # Using prediction_score as proxy for spread/volume (usually 0-100)
        spread_val = (topic.get("prediction_score", 50) / 100)
        
        # 4. Persistence (0-1.0)
        # Check alignment with Market Story theme
        persistence_val = 0.8 if story and story.get("featured_theme") == topic.get("theme") else 0.4
        
        total = (0.4 * anomaly_val) + (0.3 * flow_val) + (0.2 * spread_val) + (0.1 * persistence_val)
        
        return {
            "total": total,
            "anomaly": anomaly_val,
            "flow": flow_val,
            "spread": spread_val,
            "persistence": persistence_val
        }

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = TopicPressureEngine(root)
    engine.run_selection()
