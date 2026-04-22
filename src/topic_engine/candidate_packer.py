import uuid
from typing import List, Dict

class CandidatePacker:
    """[TASK #100.4] 모든 후보를 통일된 CANDIDATE PACK 구조로 변환"""

    def __init__(self):
        pass

    def pack_all(self, events: List[Dict], signals: List[Dict], hybrids: List[Dict]) -> List[Dict]:
        packs = []
        
        # 1. Pack Hybrids (Priority)
        for h in hybrids:
            packs.append(self._pack_hybrid(h))
            
        # 2. Pack Data Signals
        for s in signals:
            packs.append(self._pack_signal(s))
            
        # 3. Pack Events
        for e in events:
            packs.append(self._pack_event(e))
            
        return packs

    def _pack_hybrid(self, h: Dict) -> Dict:
        return {
            "candidate_id": str(uuid.uuid4())[:8],
            "candidate_type": "HYBRID",
            "title_seed": f"{h['event']} & {h['signal']}",
            "entity": [],
            "sector_hints": [],
            "core_facts": [], # Will be populated if linked to metrics
            "event_summary": h["event"],
            "expected_paths": ["Normal reaction"],
            "actual_paths": [h["signal"]],
            "difference_flags": [h["consistency"]],
            "recency_score": 0.9,
            "breadth_score": 0.8,
            "evidence_score": 0.9
        }

    def _pack_signal(self, s: Dict) -> Dict:
        facts = []
        for m, val in s["current"].items():
            facts.append({
                "name": m,
                "value": val,
                "previous": s["previous"].get(m),
                "change": s["change"].get(m)
            })
            
        return {
            "candidate_id": str(uuid.uuid4())[:8],
            "candidate_type": "DATA",
            "title_seed": s["signal"],
            "entity": [],
            "sector_hints": [],
            "core_facts": facts,
            "event_summary": "수치 기반 이상징후 포착",
            "expected_paths": ["Normal correlation"],
            "actual_paths": [s["signal_type"]],
            "difference_flags": [s["signal_type"]],
            "recency_score": 1.0,
            "breadth_score": 0.5,
            "evidence_score": min(1.0, abs(s.get("z_score", 0)) / 3.0)
        }

    def _pack_event(self, e: Dict) -> Dict:
        return {
            "candidate_id": str(uuid.uuid4())[:8],
            "candidate_type": "EVENT",
            "title_seed": e["event"],
            "entity": [e["entity"]],
            "sector_hints": e["sector_hint"],
            "core_facts": [], # Rule: No numbers, no candidate. I must find numbers for events.
            "event_summary": e["event"],
            "expected_paths": ["Stable operations"],
            "actual_paths": [e["event_type"]],
            "difference_flags": [e["event_type"]],
            "recency_score": e["recency_score"],
            "breadth_score": 0.6 if e["impact_scope"] == "섹터" else 0.8,
            "evidence_score": 0.5
        }
