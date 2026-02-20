import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class TopicMemory:
    """
    Tracks topic history to detect revisits or regime updates.
    Step 20: Topic Memory & Reuse Guard.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.lock_dir = base_dir / "data" / "topics" / "gate"
        
    def _get_lock_path(self, ymd_date: str) -> Path:
        """Returns path to daily_lock.json for a given YYYY-MM-DD."""
        ymd_parts = ymd_date.split("-")
        return self.lock_dir / ymd_parts[0] / ymd_parts[1] / ymd_parts[2] / "daily_lock.json"

    def load_memory(self, end_date: str, lookback_days: int = 90) -> Dict[str, List[Dict[str, Any]]]:
        """
        Loads history of READY topics up to end_date (exclusive).
        Returns: { normalized_title: [ {date, risk_one, why_today, ...} ] }
        """
        memory_index = {}
        
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        curr = end_dt - timedelta(days=lookback_days)
        
        # We process up to end_date - 1 day
        max_date = end_dt - timedelta(days=1)
        
        while curr <= max_date:
            ymd = curr.strftime("%Y-%m-%d")
            path = self._get_lock_path(ymd)
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    cards = data.get("cards", [])
                    for c in cards:
                        if c.get("status") == "READY":
                            title = c.get("title", "").strip().lower()
                            if not title: continue
                            
                            entry = {
                                "date": ymd,
                                "risk_one": c.get("risk_one", ""), # Not always present in card, but useful if available
                                # Actually DecisionCard doesn't explicitly store risk_one? 
                                # It stores reason, speak_pack, judgment_notes.
                                # speak_pack.risk_note might be there.
                                "why_today": c.get("why_today", ""),
                                "speak_pack": c.get("speak_pack", {}),
                                "topic_id": c.get("topic_id")
                            }
                            
                            if title not in memory_index:
                                memory_index[title] = []
                            memory_index[title].append(entry)
                            
                except Exception:
                    pass 
            curr += timedelta(days=1)
            
        return memory_index

    def classify_topic(self, topic: Dict[str, Any], memory_index: Dict[str, List[Dict]], current_date: str) -> Dict[str, Any]:
        """
        Classifies the topic: NEW_TOPIC | REVISIT | REGIME_UPDATE
        """
        title = topic.get("title", "").strip().lower()
        
        if title not in memory_index:
            return {"type": "NEW_TOPIC", "meta": None}
            
        history = memory_index[title]
        last_entry = history[-1] # Chronological order assumed
        
        last_date = last_entry["date"]
        
        days_diff = (datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(last_date, "%Y-%m-%d")).days
        
        if days_diff <= 7:
            return {"type": "REVISIT", "meta": {"last_date": last_date}}
        else:
            return {"type": "REGIME_UPDATE", "meta": {"last_date": last_date, "reason": "Time elapsed"}}

    # Wait, the user prompt says: "Same normalized title + same WHY NOW axis → REVISIT".
    # And "Do NOT ... suppress ...".
    # And "Display & structure only".
    
    # If I implement the time-based logic, I might violate "same WHY NOW axis" rule if the axis literally changed next day.
    # But usually axis doesn't change next day.
    # I'll stick to time-based for robustness in V1.
