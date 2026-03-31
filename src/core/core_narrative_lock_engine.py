import os
import json
from pathlib import Path
from datetime import datetime

class CoreNarrativeLockEngine:
    """
    STEP-52: Core Narrative Lock Engine
    Forces all engine outputs to align with a single core_theme.
    Logic: Generate -> Discard -> Rebuild
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        
        # Input Paths
        self.early_theme_path = self.project_root / "data" / "theme" / "early_theme_candidates.json"
        self.evo_path = self.project_root / "data" / "theme" / "theme_evolution_state.json"
        self.mom_path = self.project_root / "data" / "theme" / "theme_momentum_state.json"
        
        # Existing Output Paths (to be discarded/neutralized)
        self.story_path = self.project_root / "data" / "story" / "today_story.json"
        self.mentionables_path = self.project_root / "data" / "story" / "impact_mentionables.json"
        self.topic_path = self.project_root / "data" / "ops" / "top_topic.json"
        self.script_path = self.project_root / "data" / "content" / "today_video_script.json"
        
        # Lock Output Path
        self.lock_output_path = self.project_root / "data" / "operator" / "locked_brief.json"
        self.lock_output_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run_lock(self):
        print("[CoreNarrativeLockEngine] Starting Lock Synchronization...")
        
        # STEP 1: Determine core_theme
        early_themes = self._load_json(self.early_theme_path)
        evolution = self._load_json(self.evo_path)
        momentum = self._load_json(self.mom_path)
        
        if not early_themes:
            print("[CoreNarrativeLockEngine] ⚠️ Warning: No early themes found. Using fallback.")
            core_theme = "Market Stability"
        else:
            # Pick the top one based on score
            top_candidate = early_themes[0]
            core_theme = top_candidate.get("theme", "Market Stability")
            
        print(f"[CoreNarrativeLockEngine] Selected Core Theme: {core_theme}")
        
        # STEP 2: Discard Existing Results (Invalidate)
        # We don't necessarily delete them yet, but we will rebuild them below.
        
        # STEP 3: Core Theme Based Rebuilding
        
        # A. Narrative Rebuild
        narrative_locked = f"Structural shift in {core_theme} is now the primary driver of market tension."
        
        # B. Topic Rebuild
        topic_locked = f"{core_theme} Frontier"
        
        # C. Script Rebuild (Hook)
        script_hook_locked = f"오늘 우리가 주목해야 할 시장의 유일한 균열, 주제는 바로 '{core_theme}'입니다."
        
        # D. Stocks Re-mapping (Placeholder for now, logic similar to Repair Engine)
        # In a real scenario, this would filter mentionables that match the theme
        original_mentionables = self._load_json(self.mentionables_path)
        stocks_locked = []
        if original_mentionables:
            # Filter or re-tag stocks based on theme alignment
            stocks_locked = original_mentionables.get("mentionable_stocks", [])
        
        # STEP 4: Output Locked Brief
        locked_brief = {
            "core_theme": core_theme,
            "narrative": narrative_locked,
            "topic": topic_locked,
            "script": script_hook_locked,
            "stocks": stocks_locked,
            "consistency": "LOCKED",
            "metadata": {
                "locked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine_version": "v1.0-LOCKED",
                "inputs": {
                    "early_theme": str(self.early_theme_path.name),
                    "evolution": str(self.evo_path.name),
                    "momentum": str(self.mom_path.name)
                }
            }
        }
        
        self._save_json(self.lock_output_path, locked_brief)
        print(f"[CoreNarrativeLockEngine] Locked Brief saved to {self.lock_output_path}")
        
        # Force align individual files to ensure consistency
        self._sync_individual_files(locked_brief)
        
        return locked_brief

    def _sync_individual_files(self, locked_data):
        """Sync the locked data back to the individual files to prevent UI divergence."""
        core_theme = locked_data["core_theme"]
        
        # Sync Top Topic
        topic_data = self._load_json(self.topic_path) or {}
        topic_data["selected_topic"] = locked_data["topic"]
        topic_data["locked_by_engine"] = True
        self._save_json(self.topic_path, topic_data)
        
        # Sync Script
        script_data = self._load_json(self.script_path) or {}
        script_data["theme"] = core_theme
        script_data["hook"] = locked_data["script"]
        self._save_json(self.script_path, script_data)
        
        # Sync Mentionables Theme
        mention_data = self._load_json(self.mentionables_path) or {}
        mention_data["featured_theme"] = core_theme
        self._save_json(self.mentionables_path, mention_data)

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    engine = CoreNarrativeLockEngine(root)
    engine.run_lock()
