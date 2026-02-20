from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

class EarningsCalendarConnector:
    """
    (IS-88) Earnings Calendar Connector.
    Collects Earnings Release schedules.
    Strictly forbids Mock/Random data. Reads from raw real data files or configured real events.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def fetch_upcoming(self, days: int = 14) -> List[Dict[str, Any]]:
        """
        Fetch earnings events for the next N days.
        Returns list of dicts: {title, entity, event_date, source_url, grade}
        """
        # In a full live system, this would call an API (e.g. FMP, Yahoo).
        # For IS-88 Strict Mode, we load from a manually verified 'seed' or 'raw' file
        # to ensure we don't hallucinate fake companies.
        
        raw_path = self.base_dir / "data" / "raw" / "calendar" / "earnings_snapshot.json"
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
                        "id": f"EARN-{item.get('ticker')}-{evt_date_str}",
                        "type": "EARNINGS",
                        "title": f"{item.get('name')} ({item.get('ticker')}) 실적 발표",
                        "entity": item.get("name"),
                        "ticker": item.get("ticker"),
                        "event_date": evt_date_str,
                        "window": f"D-{ (evt_date - today).days }",
                        "source_url": item.get("source", "Official IR"),
                        "evidence_grade": "HARD_FACT",
                        "why_now_hint": f"{item.get('name')} 실적이 시장 방향성을 결정할 수 있습니다."
                    })
            return events
        except Exception as e:
            print(f"Error loading earnings snapshot: {e}")
            return []
