import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

class NarrativeGuard:
    """
    (IS-17) Prevents repeating the same macro story within a 14-day window.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.history_path = base_dir / "data" / "issuesignal" / "narrative_history.json"
        self._ensure_history()
        
    def _ensure_history(self):
        if not self.history_path.exists():
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w") as f:
                json.dump([], f)

    def is_saturated(self, new_narrative: str) -> bool:
        """
        Checks if the narrative story is repetitive within 14 days.
        """
        cutoff = datetime.now() - timedelta(days=14)
        
        with open(self.history_path, "r") as f:
            history = json.load(f)
            
        # Clean history of old entries
        valid_history = [
            item for item in history 
            if datetime.fromisoformat(item["timestamp"]) > cutoff
        ]
        
        # Simple keyword overlap / similarity check (Mocking vector similarity)
        new_keywords = set(new_narrative.lower().split())
        
        for item in valid_history:
            old_keywords = set(item["narrative"].lower().split())
            overlap = new_keywords.intersection(old_keywords)
            
            # If > 60% overlap in non-trivial words (simplified)
            if len(overlap) / max(len(new_keywords), 1) > 0.6:
                return True
                
        return False

    def record_narrative(self, issue_id: str, narrative: str):
        """
        Saves the successful narrative to history.
        """
        with open(self.history_path, "r") as f:
            history = json.load(f)
            
        history.append({
            "issue_id": issue_id,
            "narrative": narrative,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2)
