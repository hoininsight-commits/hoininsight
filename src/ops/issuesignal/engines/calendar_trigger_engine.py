from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from src.collectors.calendar.event_calendar_compiler import EventCalendarCompiler

class CalendarTriggerEngine:
    """
    (IS-88) Calendar Trigger Engine.
    Generates PREVIEW narrative candidates based on compiled calendar events.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.compiler = EventCalendarCompiler(base_dir)

    def process(self) -> str:
        """
        Run the engine: Compile events, save JSON, generate Candidates.
        Returns path to calendar_events JSON.
        """
        # 1. Compile Events
        events = self.compiler.compile()
        ymd = datetime.now().strftime("%Y-%m-%d")
        
        # Save Calendar JSON
        out_dir = self.base_dir / "data" / "calendar"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"calendar_events_{ymd}.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "date": ymd,
                "events": events,
                "count": len(events)
            }, f, indent=4, ensure_ascii=False)
            
        return str(out_path)

    def get_candidates(self) -> List[Dict[str, Any]]:
        """
        Converts top events into Narrative Candidates (PREVIEW type).
        """
        candidates = []
        ymd = datetime.now().strftime("%Y-%m-%d")
        
        # Load from file to ensure consistency with what was saved
        out_path = self.base_dir / "data" / "calendar" / f"calendar_events_{ymd}.json"
        if not out_path.exists():
            self.process()
            
        try:
            data = json.loads(out_path.read_text(encoding="utf-8"))
            events = data.get("events", [])
            
            # Convert top events (D-7 or D-14) to Candidates
            for evt in events:
                # Only urgent enough events
                # Heuristic: D-7 or High Impact
                window = evt.get("window", "")
                days_left = 100
                if "D-" in window:
                    try:
                        days_left = int(window.replace("D-", ""))
                    except: pass
                
                if days_left <= 14:
                    candidates.append({
                        "id": f"NC-CAL-{evt['id']}",
                        "source_mix": ["schedule"],
                        "dominant_type": "PREVIEW",
                        "theme": f"[{evt['window']}] {evt['title']} 사전 점검",
                        "why_now": f"지금 시점에서 {evt.get('why_now_hint', '일정이 임박했습니다.')}",
                        "confidence_level": "HIGH",
                        "promotion_hint": "DAILY_LONG" if days_left <= 3 else "WEEKLY_STRUCTURE",
                        "status": "CANDIDATE"
                    })
        except Exception as e:
            print(f"Error generating calendar candidates: {e}")
            
        return candidates
