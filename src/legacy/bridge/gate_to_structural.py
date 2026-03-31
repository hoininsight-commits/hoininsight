from __future__ import annotations
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class GateToStructuralBridge:
    def __init__(self, mappings_path: str, rules_path: str):
        self.mappings = yaml.safe_load(Path(mappings_path).read_text(encoding="utf-8"))
        self.rules = yaml.safe_load(Path(rules_path).read_text(encoding="utf-8"))
        self.params = self.rules.get("parameters", {})

    def process(self, topic: Dict[str, Any], history: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], events_index: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Evaluates a single topic (Candidate from Gate) and returns an observation candidate if eligible.
        """
        topic_id = topic.get("candidate_id", "unknown")
        as_of_date = topic.get("as_of_date", datetime.now().strftime("%Y-%m-%d"))
        
        # 1. Eligibility Check
        eligible, path, reasons = self._check_eligibility(topic, history, anomalies, events_index or {})
        
        result = {
            "topic_id": topic_id,
            "as_of_date": as_of_date,
            "eligibility": "ELIGIBLE" if eligible else "NOT_ELIGIBLE",
            "eligibility_reason_codes": reasons,
            "rule_path": path,
            "timestamp": datetime.now().isoformat()
        }
        
        if eligible:
            # 2. Mapping to Axes
            matched_axes = self._map_to_axes(topic)
            result["matched_axes"] = matched_axes
            result["evidence_summary"] = self._summarize_evidence(topic)
            
        return result

    def _check_eligibility(self, topic: Dict[str, Any], history: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], events_index: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        reasons = []
        
        # C_Trust check: Lookup highest trust score among linked events
        trust_score = 0.5 # Default
        requires_conf = False
        
        found_event = False
        for ref in topic.get("evidence_refs", []):
            if ref.startswith("events:"):
                parts = ref.split(":")
                if len(parts) >= 3:
                    e_id = parts[2]
                    event = events_index.get(e_id)
                    if event:
                        # Normalize if it's an object (GateEvent) or dict
                        e_trust = getattr(event, "trust_score", 0.5) if hasattr(event, "trust_score") else event.get("trust_score", 0.5)
                        e_conf = getattr(event, "requires_confirmation", False) if hasattr(event, "requires_confirmation") else event.get("requires_confirmation", False)
                        
                        # Keep highest trust for eligibility
                        if not found_event or e_trust > trust_score:
                            trust_score = e_trust
                        if e_conf:
                            requires_conf = True
                        found_event = True

        trust_ok = (trust_score >= self.params.get("min_trust_score", 0.8)) and (not requires_conf)
        if not trust_ok:
            reasons.append("LOW_TRUST" if trust_score < 0.8 else "REQUIRES_CONFIRMATION")

        # B_Evidence_Strength check
        evidence_count = len(topic.get("numbers", []))
        evidence_ok = (evidence_count >= self.params.get("min_evidence_count", 1))
        if not evidence_ok:
            reasons.append("INSUFFICIENT_EVIDENCE")

        # A_Repetition check
        event_type = topic.get("category", "other")
        recent_count = sum(1 for h in history if h.get("category") == event_type)
        repetition_ok = (recent_count >= self.params.get("repetition_min_count", 2))
        
        # D_Concurrency check
        has_anomaly = any(a.get("severity") in ["MEDIUM", "HIGH"] for a in anomalies)
        concurrency_ok = has_anomaly

        # Decision Policy
        # Primary Path: Trust AND Evidence AND Repetition
        if trust_ok and evidence_ok and repetition_ok:
            return True, "PRIMARY", []
        
        # Boost Path: Trust AND Evidence AND Concurrency
        if trust_ok and evidence_ok and concurrency_ok:
            return True, "BOOST", reasons # reasons might contain 'LOW_REPETITION' but still ok via boost

        # Final Fail
        if trust_ok and evidence_ok:
            reasons.append("NO_SYSTEMIC_SIGNAL")
            
        return False, "NONE", list(set(reasons))

    def _map_to_axes(self, topic: Dict[str, Any]) -> List[str]:
        event_type = topic.get("category", "other")
        matched = []
        for m in self.mappings.get("mappings", []):
            if m.get("event_type") == event_type:
                matched.extend(m.get("mapped_axes", []))
        return list(set(matched))

    def _summarize_evidence(self, topic: Dict[str, Any]) -> str:
        numbers = topic.get("numbers", [])
        if not numbers:
            return "No numerical evidence."
        summary = ", ".join([f"{n.get('label')}: {n.get('value')} {n.get('unit')}" for n in numbers])
        return summary
