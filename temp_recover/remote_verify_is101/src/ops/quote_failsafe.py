from pathlib import Path
from typing import List, Dict, Any, Optional
from src.ops.quote_evidence_collector import QuoteEvidenceCollector
from src.ops.quote_source_verifier import QuoteSourceVerifier

class QuoteFailsafe:
    """
    IS-31: QUOTE_FAILSAFE
    Orchestrates quote processing and enforces demotion logic.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.collector = QuoteEvidenceCollector()
        self.verifier = QuoteSourceVerifier()

    def process_ranked_topics(self, ranked_topics: List[Dict[str, Any]], events_index: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes ranked topics, attaches quote evidence, and demotes if necessary.
        """
        for topic in ranked_topics:
            trigger_type = topic.get("trigger_type")
            if trigger_type not in self.collector.IN_SCOPE_TRIGGERS:
                continue

            # 1. Find trigger event
            # Ranked topics often have 'candidate_id' or 'source_candidates'
            # We need to find the event that triggered it
            # For simplicity in this implementation, we look for matches in events_index
            trigger_event = self._find_trigger_event(topic, events_index)
            if not trigger_event:
                topic["quote_verdict"] = "REJECT"
                topic["quote_reason_code"] = "NO_TRIGGER_EVENT_FOUND"
                self._demote_topic(topic)
                continue

            # 2. Collect Quote
            quote_pack = self.collector.collect_quote(trigger_event)
            if not quote_pack:
                topic["quote_verdict"] = "REJECT"
                topic["quote_reason_code"] = "QUOTE_COLLECTION_FAILED"
                self._demote_topic(topic)
                continue

            # 3. Verify Quote
            # Note: For now, we pass the trigger event as the only source for simplicity
            # but ideally we'd pass all sources from candidate.
            verdict_res = self.verifier.verify_quote(quote_pack, [trigger_event])
            
            topic["trigger_quote"] = quote_pack
            topic["quote_verdict"] = verdict_res["verdict"]
            topic["quote_reason_code"] = verdict_res["reason_code"]

            # 4. Failsafe: Demote if not PASS
            if verdict_res["verdict"] != "PASS":
                self._demote_topic(topic)

        return ranked_topics

    def _find_trigger_event(self, topic: Dict[str, Any], events_index: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Heuristic: find the first event in events_index that matches the trigger requirements
        # or use topic's source_candidates
        source_ids = topic.get("source_candidates", []) or [topic.get("candidate_id")]
        for sid in source_ids:
            if sid in events_index:
                return events_index[sid]
        return None

    def _demote_topic(self, topic: Dict[str, Any]):
        """Demotes READY (TRUST_LOCKED) to HOLD."""
        # Note: In this system, 'status' is often determined later in script quality gate,
        # but if it's already set or being prepared, we flag it.
        # We add a specific flag to ensure Validator/Ranker/Dashboard respects it.
        topic["is_quote_demoted"] = True
        
        # If status is already "READY", force it to "HOLD"
        if topic.get("status") == "READY":
             topic["status"] = "HOLD"
             topic["demotion_reason"] = "QUOTE_MISSING_OR_WEAK"
