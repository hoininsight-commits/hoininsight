from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

class PolicyCalendarConnector:
    """
    (IS-88) Policy & Macro Calendar Connector.
    Collects FOMC, BOK, CPI, Jobs Report schedules.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def fetch_upcoming(self, days: int = 21) -> List[Dict[str, Any]]:
        """
        Fetch policy/macro events.
        """
        # Similar to Earnings, strictly reads from a 'macro_calendar_snapshot.json'
        # containing verified official schedules (Fed Calendar, BLS Release Schedule).
        
        raw_path = self.base_dir / "data" / "raw" / "calendar" / "macro_snapshot.json"
        if not raw_path.exists():
             return []

        try:
            data = json.loads(raw_path.read_text(encoding="utf-8"))
            events = []
            today = datetime.now().date()
            target_end = today + timedelta(days=days)
            
            for item in data:
                evt_date_str = item.get("date")
                if not evt_date_str: continue
                
                evt_date = datetime.strptime(evt_date_str, "%Y-%m-%d").date()
                if today <= evt_date <= target_end:
                    events.append({
                        "id": f"MACRO-{item.get('code')}-{evt_date_str}",
                        "type": "POLICY",
                        "title": item.get("event"),
                        "entity": item.get("agency"),
                        "event_date": evt_date_str,
                        "window": f"D-{ (evt_date - today).days }",
                        "source_url": item.get("source", "Official Source"),
                        "evidence_grade": "HARD_FACT",
                        "why_now_hint": item.get("impact_hint", "주요 거시경제 이벤트입니다.")
                    })
            return events
        except Exception as e:
            print(f"Error loading macro snapshot: {e}")
            return []
