from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from src.events.source_trust import score_event

def normalize_event(raw_event: dict, as_of_date: str) -> dict:
    """
    Transforms RawEvent -> events_gate_v1 schema.
    """
    # 1. Map event_type from source source/keywords (simplified for Step 9)
    # Defaulting based on collector context passed by build_events if needed, 
    # but for now we look at source clues or raw_text.
    
    # In Step 9, we trust the collector's intent. 
    # We will pass the type hint from build_events.py
    e_type = raw_event.get("_type_hint", "other")
    
    # 2. Basic Fields
    event_id = f"ev_{e_type}_{uuid.uuid4().hex[:8]}"
    
    evidence = []
    for n in raw_event.get("numbers", []):
        evidence.append({
            "label": n.get("context", "Extracted Data"),
            "value": n.get("value"),
            "unit": n.get("unit", ""),
            "context": f"Source: {raw_event.get('source')} | {raw_event.get('title')}"
        })
        
    start_date = raw_event.get("published_at", as_of_date)
    # Default window: 7 days
    try:
        dt = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        dt = datetime.strptime(as_of_date, "%Y-%m-%d")
        
    end_date = (dt + timedelta(days=7)).strftime("%Y-%m-%d")
    
    normalized = {
        "event_id": event_id,
        "event_type": e_type,
        "title": raw_event.get("title", "Untitled Event"),
        "source": {
            "publisher": raw_event.get("source", "Unknown"),
            "url": raw_event.get("url", "#")
        },
        "effective_window": {
            "start_date": start_date,
            "end_date": end_date
        },
        "evidence": evidence
    }
    
    # 3. Integrate Trust (MUST use source_trust.py mapping)
    score, req_conf, tier = score_event(normalized, as_of_date)
    
    normalized["trust_score"] = score
    normalized["trust_tier"] = tier
    normalized["requires_confirmation"] = req_conf
    
    return normalized
