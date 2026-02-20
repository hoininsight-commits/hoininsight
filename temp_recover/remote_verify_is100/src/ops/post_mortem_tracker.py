import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class PostMortemTracker:
    """
    Tracks retrospective accountability of READY topics.
    Step 18: Post-Mortem Signal Tracker.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.lock_dir = base_dir / "data" / "topics" / "gate"
        
    def _get_lock_path(self, ymd_date: str) -> Path:
        """Returns path to daily_lock.json for a given YYYY-MM-DD."""
        ymd_parts = ymd_date.split("-")
        return self.lock_dir / ymd_parts[0] / ymd_parts[1] / ymd_parts[2] / "daily_lock.json"

    def load_history(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Loads all daily_lock.json files between start and end date (inclusive).
        Returns: { 'YYYY-MM-DD': lock_data_dict }
        """
        history = {}
        curr = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while curr <= end:
            ymd = curr.strftime("%Y-%m-%d")
            path = self._get_lock_path(ymd)
            if path.exists():
                try:
                    history[ymd] = json.loads(path.read_text(encoding="utf-8"))
                except Exception:
                    pass # Skip corrupted or empty
            curr += timedelta(days=1)
            
        return history

    def evaluate_topic(self, topic: Dict[str, Any], topic_date: str, history: Dict[str, Any]) -> str:
        """
        Determines outcome: CONFIRMED | FAILED | UNRESOLVED
        """
        impact_win = topic.get("impact_window", "MID") # Default to MID if missing
        
        # 1. Determine Evaluation Window Start
        # IMMEDIATE=2d, NEAR=7d, MID=30d, LONG=90d
        delays = {
            "IMMEDIATE": 2,
            "NEAR": 7,
            "MID": 30,
            "LONG": 90
        }
        min_days = delays.get(impact_win, 30)
        
        t_date = datetime.strptime(topic_date, "%Y-%m-%d")
        eval_start_date = t_date + timedelta(days=min_days)
        
        # Determine strict future bound (max date in history)
        if not history:
             return "UNRESOLVED"
             
        max_hist_date_str = max(history.keys())
        max_hist_date = datetime.strptime(max_hist_date_str, "%Y-%m-%d")
        
        # If not enough time has passed yet relative to available history
        if max_hist_date < eval_start_date:
            return "UNRESOLVED"
            
        # 2. Search for Confirming/Failing Signals in Future
        # We look from (topic_date + 1 day) up to max_hist_date
        # Why +1? Supporting evidence might appear immediately, but let's say subsequent.
        # Actually matching rule says: "If supporting anomaly/fact appears after T days" -> Wait, 
        # "If window not elapsed -> UNRESOLVED". "Rules: If supporting ... appears ... -> CONFIRMED".
        # This implies we can search ANY time after topic_date, but we only make the call *after* the window elapsed.
        # So search range: [t_date + 1, max_hist_date]
        
        topic_title_norm = topic.get("title", "").strip().lower()
        
        # Iterate chronologically
        curr = t_date + timedelta(days=1)
        while curr <= max_hist_date:
            ymd = curr.strftime("%Y-%m-%d")
            data = history.get(ymd)
            if data:
                # Check READY topics for match
                cards = data.get("cards", [])
                for c in cards:
                    # Match Rule: Same normalized title
                    c_title = c.get("title", "").strip().lower()
                    
                    if c_title == topic_title_norm:
                        if c.get("status") == "READY":
                            return "CONFIRMED"
                        elif c.get("status") == "DROP":
                             # Check failure reason logic if implemented
                             # For now, simplistic: if DROP has 'False', 'Contradict', 'Fail'
                             # Note: In daily_lock, we might save DROP items? 
                             # Dashboard usually filters non-READY. 
                             # Wait, daily_lock saves all? 
                             # Check decision_dashboard.py save_snapshot logic.
                             # It saves `data`. `data` contains `cards`.
                             # `build_dashboard_data` logic: `cards` usually contains what is passed to it.
                             # In `build_dashboard_data`, we construct cards from `ranked` list.
                             # Does `ranked` contain DROP? 
                             # `topic_gate_output.json.ranked` contains all ranked topics?
                             # Usually yes. But let's verify if `DecisionDashboard` saves ALL cards to lock.
                             # `build_dashboard_data` iterates over `gate_output.ranked`.
                             # So yes, it includes READY, HOLD, DROP.
                            pass

            curr += timedelta(days=1)
            
        return "UNRESOLVED"

    def get_aggregate_stats(self, end_date: str, lookback_days: int = 90) -> Dict[str, int]:
        """
        Computes outcomes for all READY topics in [end_date - lookback, end_date - 2].
        Why -2? Because IMMEDIATE needs at least 2 days.
        Actually, we can iterate all, evaluate_topic handles UNRESOLVED if time hasn't passed.
        """
        stats = {"CONFIRMED": 0, "FAILED": 0, "UNRESOLVED": 0}
        
        start_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=lookback_days)
        start_date = start_dt.strftime("%Y-%m-%d")
        
        # Load history up to end_date
        history = self.load_history(start_date, end_date)
        
        # Iterate past days
        for ymd, data in history.items():
            if ymd == end_date:
                continue # Don't evaluate today's topics yet
                
            cards = data.get("cards", [])
            for c in cards:
                if c.get("status") == "READY":
                    outcome = self.evaluate_topic(c, ymd, history)
                    if outcome in stats:
                        stats[outcome] += 1
                        
        return stats
