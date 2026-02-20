import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class SilenceLayer:
    """
    (IS-16) Enforces a daily speech cap of 3 Decision Cards.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.log_path = base_dir / "data" / "issuesignal" / "speech_log.json"
        self._ensure_log()
        
    def _ensure_log(self):
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "w") as f:
                json.dump({}, f)

    def can_speak(self) -> bool:
        """
        Checks if the daily cap (3) has been reached.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_path, "r") as f:
            data = json.load(f)
            
        count = data.get(today, 0)
        return count < 3

    def record_speech(self):
        """
        Increments the daily speech count.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_path, "r") as f:
            data = json.load(f)
            
        data[today] = data.get(today, 0) + 1
        with open(self.log_path, "w") as f:
            json.dump(data, f)

    def select_top_triggers(self, triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks triggers by Capital Force, Time Pressure, Irreversibility.
        Only allows progress if within daily cap.
        """
        if not triggers:
            return []
            
        # 1. Ranking logic (re-uses priority scores if available)
        ranked = sorted(triggers, key=lambda x: x.get("priority_score", 0), reverse=True)
        
        # 2. Check remaining quota
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_path, "r") as f:
            data = json.load(f)
        remaining = 3 - data.get(today, 0)
        
        if remaining <= 0:
            return []
            
        return ranked[:remaining]
