from __future__ import annotations
import json
from pathlib import Path
from typing import List
from .gate_event_schema import GateEvent, EventSource, EffectiveWindow, EventEvidence

from .source_trust import score_event

def load_gate_events(base_dir: Path, as_of_date: str) -> List[GateEvent]:
    """
    Loads events from data/events/YYYY/MM/DD/events.json and attaches trust scores.
    """
    path = base_dir / "data" / "events" / as_of_date.replace("-", "/") / "events.json"
    
    if not path.exists():
        return []
    
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        events_list = data.get("events", [])
        
        results = []
        for e in events_list:
            source = EventSource(**e["source"])
            window = EffectiveWindow(**e["effective_window"])
            evidence = [EventEvidence(**ev) for ev in e["evidence"]]
            
            # Create object mapping
            event_obj = GateEvent(
                event_id=e["event_id"],
                event_type=e["event_type"],
                title=e["title"],
                source=source,
                effective_window=window,
                evidence=evidence
            )
            
            # Calculate trust (New)
            score, req_conf, tier = score_event(event_obj, as_of_date)
            event_obj.trust_score = score
            event_obj.requires_confirmation = req_conf
            event_obj.trust_tier = tier
            
            results.append(event_obj)
        return results
    except Exception as e:
        print(f"[GateEventLoader] Error loading {path}: {e}")
        return []
