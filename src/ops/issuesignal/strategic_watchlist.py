import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("StrategicWatchlist")

class StrategicWatchlistEngine:
    """
    IS-74: Strategic Watchlist Layer
    확정된 사실(HARD_FACT)과 명확한 주체(Actor)를 기반으로 구조적 감시 대상을 선정합니다.
    """

    @staticmethod
    def evaluate(candidates: List[Dict[str, Any]], official_facts: List[Dict[str, Any]], corporate_facts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        입력 조건: HARD_FACT >= 1, Actor 명확
        출력: Strategic Watchlist 데이터 또는 None
        """
        # 1. HARD_FACT 존재 여부 확인 (Official 또는 Corporate)
        hard_facts = [f for f in official_facts + corporate_facts if f.get("evidence_grade") == "HARD_FACT"]
        
        if not hard_facts:
            return None

        # 2. 명확한 Actor를 가진 후보 필터링
        # (run_issuesignal.py에서 이미 top_candidates를 제공하므로 이를 활용)
        watchlist_subjects = []
        for cand in candidates:
            details = cand.get("details", {})
            actor_name = details.get("actor_name_ko")
            actor_type = details.get("actor_type", "없음")
            
            # Actor가 명확하고 종목(Entities) 정보가 있을 때 우선 고려
            if actor_name and actor_name != "없음" and (details.get("ticker") or details.get("ticker_path")):
                watchlist_subjects.append(cand)

        if not watchlist_subjects:
            return None

        # 3. 최상위 후보 선정
        primary = watchlist_subjects[0]
        details = primary.get("details", {})
        
        # entities 추출 (ticker_path 사용)
        entities = []
        ticker = details.get("ticker")
        if ticker: entities.append(ticker)
        
        tp = details.get("ticker_path", {})
        if tp.get("ticker"): entities.append(tp["ticker"])
        entities = list(set(entities)) # 중복 제거

        return {
            "layer": "STRATEGIC_WATCHLIST",
            "status": "WATCH",
            "title": "전략적 감시 대상",
            "disclaimer": "확정 아님 / 투자 판단 아님",
            "actor": details.get("actor_name_ko", "알 수 없는 주체"),
            "entities": entities,
            "reason": details.get("actor_reason_ko") or primary.get("why_now") or "구조적 변화 감지에 따른 지속 관찰 필요",
            "confidence": "MEDIUM" if details.get("actor_confidence", 0) >= 80 else "LOW",
            "source_facts": [f.get("fact_text", "")[:50] for f in hard_facts[:2]]
        }
