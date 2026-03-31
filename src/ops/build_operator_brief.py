import json
import os
from pathlib import Path
from datetime import datetime

class OperatorBriefBuilder:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.output_path = self.project_root / "data" / "ops" / "today_operator_brief.json"

    def _load_json(self, relative_path):
        full_path = self.project_root / relative_path
        if not full_path.exists():
            return {}
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {relative_path}: {e}")
            return {}

    def build(self):
        print("[BriefBuilder] Aggregating engine outputs...")
        
        # 1. Market Radar Data
        early_theme = self._load_json("data/theme/top_early_theme.json")
        evolution = self._load_json("data/theme/top_theme_evolution.json")
        momentum = self._load_json("data/theme/top_theme_momentum.json")
        
        # 2. Narrative Brief Data
        narrative = self._load_json("data/theme/theme_narrative.json")
        story = self._load_json("data/story/today_story.json")
        
        # 3. Impact Map Data
        mentionables = self._load_json("data/story/impact_mentionables.json")
        
        # 4. Content Studio Data
        topic = self._load_json("data/topic/top_topic.json")
        script = self._load_json("data/content/today_video_script.json")
        
        brief = {
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0-OPERATOR"
            },
            "market_radar": {
                "theme": early_theme.get("theme", "N/A"),
                "early_signal_score": early_theme.get("score", 0),
                "evolution_stage": evolution.get("stage", "PRE-STORY"),
                "evolution_hint": evolution.get("action_hint", "MONITOR"),
                "momentum_state": momentum.get("momentum_state", "STABLE"),
                "momentum_score": momentum.get("momentum_score", 0),
                "momentum_drivers": momentum.get("why_momentum", [])
            },
            "narrative_brief": {
                "title": story.get("title", "Market Narrative Missing"),
                "summary": story.get("summary", "No story generated for today."),
                "featured_theme": story.get("featured_theme", early_theme.get("theme", "N/A")),
                "explanation": narrative.get("explanation", ""),
                "situation": narrative.get("situation", ""),
                "contradiction": narrative.get("contradiction", ""),
                "sector_impact": narrative.get("sector_impact", "")
            },
            "impact_map": {
                "theme": early_theme.get("theme", "N/A"),
                "mentionable_stocks": [
                    {
                        "ticker": s.get("stock", "N/A"),
                        "name": s.get("stock", "N/A"),
                        "relevance_score": s.get("score", 0) / 100.0 if s.get("score", 0) > 1 else s.get("score", 0),
                        "rationale": s.get("reason", "No rationale provided")
                    } for s in mentionables.get("mentionable_stocks", [])
                ],
                "sector_status": { s: "ACTIVE" for s in mentionables.get("affected_sectors", []) }
            },
            "content_studio": {
                "selected_topic": topic.get("selected_topic", "N/A"),
                "topic_pressure": topic.get("topic_pressure", 0),
                "pressure_drivers": topic.get("drivers", []),
                "script": {
                    "hook": script.get("hook", ""),
                    "core_message": script.get("core_message", ""),
                    "operator_action": script.get("operator_action", "WATCH")
                }
            }
        }
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
            
        print(f"[BriefBuilder] Success: {self.output_path}")
        return brief

if __name__ == "__main__":
    # Project root is 2 levels up from src/ops/
    root = Path(__file__).parent.parent.parent
    builder = OperatorBriefBuilder(root)
    builder.build()
