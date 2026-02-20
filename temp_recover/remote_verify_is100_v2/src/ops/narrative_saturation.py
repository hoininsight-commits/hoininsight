import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class NarrativeSaturation:
    """
    Detects overuse of narrative axes to prevent editorial fatigue.
    Step 21: Narrative Saturation Guard.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.lock_dir = base_dir / "data" / "topics" / "gate"
        
    def _get_lock_path(self, ymd_date: str) -> Path:
        """Returns path to daily_lock.json for a given YYYY-MM-DD."""
        ymd_parts = ymd_date.split("-")
        return self.lock_dir / ymd_parts[0] / ymd_parts[1] / ymd_parts[2] / "daily_lock.json"

    def load_history(self, end_date: str, days: int = 14) -> Dict[str, int]:
        """
        Loads frequency of narrative axes in the rolling window (exclusive of end_date).
        Returns: { axis_key: count }
        """
        saturation_counts = {}
        
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        curr = end_dt - timedelta(days=days)
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
                            # Use helper to derive key from stored card
                            key = self._derive_axis_key(c, from_card=True)
                            saturation_counts[key] = saturation_counts.get(key, 0) + 1
                except Exception:
                    pass
            curr += timedelta(days=1)
            
        return saturation_counts

    def _derive_axis_key(self, topic: Dict[str, Any], from_card: bool = False) -> str:
        """
        Deterministically derives the narrative axis key.
        Strategy: Tags Match + Is_Fact
        """
        # "tags" might be list or string depending on where it comes from
        # In DecisionCard (and stored json), tags is List[str].
        # In raw topic dict (from gate), tags is List[str].
        
        tags = topic.get("tags", [])
        if not tags:
            # Fallback to title if no tags (weak proxy but better than nothing)
            # Or "Uncategorized"
            return f"Uncategorized | FACT:{topic.get('is_fact_driven', False)}"
            
        # Sort tags for determinism
        sorted_tags = sorted(tags)
        tags_str = "/".join(sorted_tags)
        
        # Fact status
        is_fact = topic.get("is_fact_driven", False)
        
        return f"{tags_str} | FACT:{is_fact}"

    def compute_saturation(self, topic: Dict[str, Any], history_counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Computes saturation level for the topic.
        """
        axis = self._derive_axis_key(topic)
        count = history_counts.get(axis, 0)
        
        # Thresholds: NORMAL(0-2), DENSE(3-4), SATURATED(5+)
        if count >= 5:
            level = "SATURATED"
        elif count >= 3:
            level = "DENSE"
        else:
            level = "NORMAL"
            
        return {
            "level": level,
            "count": count,
            "axis": axis
        }
