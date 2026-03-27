import json
import os
from pathlib import Path
from datetime import datetime

# Import individual aligners
from src.ops.core_theme_selector import CoreThemeSelector
from src.ops.align_narrative import align_narrative
from src.ops.align_topic import align_topic
from src.ops.align_impact import align_impact
from src.ops.align_script import align_script

class ConsistencyEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.selector = CoreThemeSelector(self.project_root)
        self.brief_path = self.project_root / "data" / "ops" / "today_operator_brief.json"
        
    def _load_json(self, rel_path):
        p = self.project_root / rel_path
        if not p.exists():
            return {}
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self):
        print("[ConsistencyEngine] Starting SSOT alignment...")
        
        # 1. Select Core Theme
        core = self.selector.select_core_theme()
        core_theme = core["core_theme"]
        
        # 2. Load and Align components
        narrative_data = self._load_json("data/theme/theme_narrative.json")
        aligned_narrative = align_narrative(self.project_root, core_theme, narrative_data)
        
        topic_data = self._load_json("data/topic/top_topic.json")
        aligned_topic = align_topic(self.project_root, core_theme, topic_data)
        
        impact_data = self._load_json("data/story/impact_mentionables.json")
        aligned_impact = align_impact(self.project_root, core_theme, impact_data)
        
        script_data = self._load_json("data/content/today_video_script.json")
        aligned_script = align_script(self.project_root, core_theme, script_data)
        
        # 3. Save Core Theme State
        state_path = self.project_root / "data" / "operator" / "core_theme_state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(core, f, indent=2, ensure_ascii=False)
            
        # 4. Update Operator Brief
        self.update_brief(core_theme, aligned_narrative, aligned_topic, aligned_impact, aligned_script)
        
        print(f"[ConsistencyEngine] Finished. Core Theme: {core_theme}")
        return core

    def update_brief(self, core_theme, narrative, topic, impact, script):
        if not self.brief_path.exists():
            print("[ConsistencyEngine] ⚠️ Brief not found. Skipping update.")
            return
            
        with open(self.brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
            
        # Add core_theme and display_title
        brief["core_theme"] = core_theme
        brief["display_title"] = narrative.get("title", f"Insight: {core_theme}")
        
        # Update components with aligned data
        # Note: mapping keys to match today_operator_brief.json structure
        
        # Market Radar update (theme only)
        if "market_radar" in brief:
            brief["market_radar"]["theme"] = core_theme
            
        # Narrative Brief update
        if "narrative_brief" in brief:
            brief["narrative_brief"]["title"] = narrative.get("title", f"Insight: {core_theme}")
            brief["narrative_brief"]["featured_theme"] = core_theme
            brief["narrative_brief"]["explanation"] = narrative.get("explanation", "")
            brief["narrative_brief"]["situation"] = narrative.get("situation", "")
            brief["narrative_brief"]["contradiction"] = narrative.get("contradiction", "")
            brief["narrative_brief"]["sector_impact"] = ", ".join(narrative.get("sector_impact", [])) if isinstance(narrative.get("sector_impact"), list) else narrative.get("sector_impact", "")

        # Impact Map update
        if "impact_map" in brief:
            brief["impact_map"]["theme"] = core_theme
            brief["impact_map"]["mentionable_stocks"] = []
            for s in impact.get("mentionable_stocks", []):
                # Standardize field names for UI (ticker, name, relevance_score, rationale)
                brief["impact_map"]["mentionable_stocks"].append({
                    "ticker": s.get("stock", "N/A"),
                    "name": s.get("stock", "N/A"),
                    "relevance_score": s.get("score", 0) / 100.0 if s.get("score", 0) > 1 else s.get("score", 0),
                    "rationale": s.get("reason", ["No rationale"]) # Now a list
                })

        # Content Studio update
        if "content_studio" in brief:
            brief["content_studio"]["selected_topic"] = topic.get("selected_topic", "N/A")
            brief["content_studio"]["topic_pressure"] = topic.get("topic_pressure", 0)
            if "script" in brief["content_studio"]:
                brief["content_studio"]["script"]["hook"] = script.get("hook", "")
                brief["content_studio"]["script"]["core_message"] = script.get("core_message", script.get("title", ""))

        # Metadata update
        brief["metadata"]["consistency_aligned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.brief_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
        print(f"[ConsistencyEngine] today_operator_brief.json updated for {core_theme}")

if __name__ == "__main__":
    import sys
    # Add project root to path for imports to work
    root_dir = Path(__file__).parent.parent.parent
    sys.path.append(str(root_dir))
    
    engine = ConsistencyEngine(root_dir)
    engine.run()
