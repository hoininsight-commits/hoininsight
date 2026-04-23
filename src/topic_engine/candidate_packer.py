import hashlib
from typing import List, Dict

class CandidatePacker:
    """[TASK #102.4] 후보군 통합 및 유효성 검증 (v1.1)"""

    def __init__(self):
        pass

    def pack_all(self, enriched_events: List[Dict], signals: List[Dict]) -> List[Dict]:
        all_candidates = []
        
        # 1. Event 후보 패키징 (이미 필터링과 데이터 연결이 완료된 상태)
        for ev in enriched_events:
            c_id = self._generate_id(ev["event"])
            
            assets = ev.get("related_market_data", {}).get("assets", [])
            
            # [VALIDATION RULE]
            # 1. entity 존재 (Builder에서 걸러짐)
            # 2. 관련 데이터 존재 (Enricher에서 2개 이상으로 걸러짐)
            # 3. 필터 통과 (Filter에서 걸러짐)
            
            all_candidates.append({
                "candidate_id": c_id,
                "candidate_type": "HYBRID",
                "event": ev["event"],
                "entity": ev["entity"],
                "core_facts": assets,
                "expected_paths": ["안정적 흐름 유지"],
                "actual_paths": [ev["event_type"]],
                "recency_score": ev["recency_score"],
                "evidence_score": 0.8 # 데이터가 매핑되었으므로 고점 부여
            })
            
        # 2. Data 후보 패키징
        for sig in signals:
            c_id = self._generate_id(sig["signal"])
            
            core_facts = []
            for name, val in sig.get("current", {}).items():
                core_facts.append({
                    "name": name,
                    "value": val,
                    "change": sig["change"].get(name),
                    "z_score": sig.get("z_scores", {}).get(name, 0.0)
                })
                
            all_candidates.append({
                "candidate_id": c_id,
                "candidate_type": "DATA",
                "event": sig["signal"],
                "entity": ["Market"], # Data 시그널은 예외적으로 Market 허용 (혹은 지수명으로 대체 가능)
                "core_facts": core_facts,
                "expected_paths": ["평균 회귀"],
                "actual_paths": [sig["signal_type"]],
                "recency_score": 0.9,
                "evidence_score": 1.0
            })
            
        return all_candidates

    def _generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:8]
