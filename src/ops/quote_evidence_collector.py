import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class QuoteEvidenceCollector:
    """
    IS-31: QUOTE_EVIDENCE_COLLECTOR
    Extracts 1–2 lines of verbatim quote from Speech/Policy/Calendar triggers.
    Ensures 'hard anchor' tokens exist.
    """
    
    HARD_ANCHOR_TOKENS = [
        "raise", "cut", "tariff", "approve", "sign", "implement", 
        "enforce", "hearing", "vote", "hike", "pause", "maintain",
        "restrict", "expand", "ban", "permit", "authorize"
    ]
    
    IN_SCOPE_TRIGGERS = ["SPEECH", "SPEECH_SHIFT", "POLICY", "CALENDAR"]

    def __init__(self):
        pass

    def collect_quote(self, trigger: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        trigger_type = trigger.get("trigger_type", "").upper()
        if trigger_type not in self.IN_SCOPE_TRIGGERS:
            return None

        # 1. Verification of Anchor Tokens
        full_text = trigger.get("raw_content", "").lower()
        has_anchor = any(token in full_text for token in self.HARD_ANCHOR_TOKENS)
        
        # Calendar special case: date/time can be anchor
        if trigger_type == "CALENDAR":
            if trigger.get("event_time_utc") or trigger.get("schedule_verbatim"):
                has_anchor = True

        if not has_anchor:
            return None

        # 2. Verbatim Extraction (Mocking logic for extracting best 1-2 lines)
        # In a real scenario, this would involve NLP or regex to find the most relevant context.
        quote_text = self._extract_verbatim(trigger)
        if not quote_text or len(quote_text) > 240:
            return None

        # 3. Build Pack
        pack = {
            "quote_text": quote_text,
            "speaker": trigger.get("speaker") or trigger.get("issuing_body"),
            "event_name": trigger.get("event_name"),
            "event_time_utc": trigger.get("event_time_utc") or datetime.now().isoformat(),
            "source_url": trigger.get("source_url"),
            "source_type": trigger.get("source_type"), # Expected OFFICIAL_* enum
            "retrieved_at": datetime.now().isoformat(),
            "hash": self._generate_hash(quote_text, trigger.get("event_time_utc"))
        }

        # Check required fields for pack integrity
        required = ["quote_text", "speaker", "event_name", "event_time_utc", "source_type", "hash"]
        if all(pack.get(f) for f in required):
            return pack
        
        return None

    def _extract_verbatim(self, trigger: Dict[str, Any]) -> str:
        """
        Extracts 1-2 lines. 
        Prioritizes 'quote_excerpt' or takes first 240 chars of 'raw_content'.
        """
        excerpt = trigger.get("quote_excerpt") or trigger.get("raw_content") or ""
        # Clean up whitespace and limit to ~240
        cleaned = " ".join(excerpt.split())
        return cleaned[:240]

    def _generate_hash(self, text: str, time_utc: Optional[str]) -> str:
        base = f"{text}|{time_utc or ''}"
        return hashlib.sha256(base.encode('utf-8')).hexdigest()
