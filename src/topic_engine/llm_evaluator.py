import json
from typing import List, Dict
from src.core.gemini_client import GeminiClient

class TopicEvaluator:
    """[TASK #101.5] AI 기반 정성적 토픽 평가기 (Production v1.0)"""

    def __init__(self):
        # LLM 호출 제거 (v2.2)
        pass

    def evaluate_all(self, candidates: List[Dict]) -> List[Dict]:
        evaluations = []
        for cand in candidates:
            res = self.evaluate_single(cand)
            if res:
                evaluations.append(res)
        return evaluations

    def evaluate_single(self, candidate: Dict) -> Dict:
        """[HEURISTIC] Rule-based 정성 평가 (LLM 호출 금지)"""
        core_facts = candidate.get("core_facts", [])
        main_fact = core_facts[0] if core_facts else {}
        
        z_score = abs(main_fact.get("z_score", 0.0))
        change = abs(main_fact.get("change", 0.0))
        
        # 1. explainability_score 계산 (Narrative + Market Hybrid v2.0)
        # Z-score(시장)와 News Strength(데이터)를 결합
        recency = candidate.get("recency_score", 1.0)
        evidence = candidate.get("evidence_score", 0.5)
        is_mismatch = candidate.get("is_mismatch", False)
        is_preemptive = candidate.get("is_preemptive", False)
        
        # [AUTONOMOUS] 시장 지수가 조용해도 뉴스 에너지가 높으면 점수 확보
        base_score = (z_score * 0.5) + (recency * 3.0) + (evidence * 2.5)
        base_score = min(base_score, 8.5) # 최대 8.5점까지 기본 점수로 확보
        
        intensity_bonus = min(change * 0.5, 1.5) # 변동률 보너스
        
        # [NEW] Hunter Bonus
        hunter_bonus = 0.0
        if is_mismatch:
            hunter_bonus += 2.0 # 모순 상황(가격-뉴스 상충)이면 강력 가산
            
        # [v4.0 Frontier Axis Bonus]
        # 자율 발견된 축에 어울리는 이름이 붙었다면 '미지(Frontier)의 개척지' 보너스 부여
        legacy_axes = ["rates", "liquidity", "geopolitics", "supply_chain", "policy", "flow", "emerging", "unknown"]
        current_axis = candidate.get("structure_axis", "unknown")
        
        # 'emerging'이나 'unknown'이 아니라는 것은 AI가 새로운 '이름'을 붙여주었다는 뜻
        if current_axis not in legacy_axes:
            hunter_bonus += 4.5
            print(f"  ✨ Narrative Discovery Bonus (+4.5) for frontier: '{current_axis}'")
        elif recency + evidence > 2.2:
            # 발견에 실패했더라도 데이터 밀도가 매우 높다면 '잠재적 개척지'로 보고 가산
            hunter_bonus += 2.5
            print(f"  🔥 Potential Frontier Bonus (+2.5) due to high data density")

        explainability_score = round(min(base_score + intensity_bonus + hunter_bonus, 10.0), 1)
        
        # 2. Flow Type 결정
        flow_type = "NORMAL"
        if is_mismatch:
            flow_type = "MISMATCH"
        elif z_score > 3.0:
            flow_type = "ANOMALY"
        elif len(core_facts) > 1:
            flow_type = "MIXED"
            
        # 3. Selection Decision
        topic_decision = "DROP"
        if explainability_score >= 5.0:
            topic_decision = "PROMOTE"
        elif explainability_score >= 3.0:
            topic_decision = "HOLD"

        # 4. Output Schema (기존 유지)
        selection_reason = f"High intensity movement in {main_fact.get('name')} ({change}%)"
        if is_mismatch:
            selection_reason = f"🚨 Price-News Paradox detected in {main_fact.get('name')}. High strategic value."
        elif is_preemptive:
            selection_reason = f"🗓️ Preemptive theme detected (Upcoming event/schedule)."

        return {
            "candidate_id": candidate.get("candidate_id", "unknown"),
            "structure_axis": candidate.get("structure_axis", "unknown"),
            "why_now_gate": {
                "recent_change": True,
                "market_reaction_started": True,
                "not_fully_priced": True,
                "passed": True if explainability_score >= 4.0 else False
            },
            "explainability_score": explainability_score,
            "why_now_summary": f"Detected significant {candidate.get('structure_axis')} shift with Z-score {z_score:.2f}" if not is_mismatch else "Market reaction contradicts news sentiment (Strong Hunter Signal)",
            "selection_reason": selection_reason,
            "tier_decision_reason": "Hunter-v4 Priority Scoring" if is_mismatch else "Rule-based scoring",
            "sector_hints": ["Macro", "Finance"],
            "impact_scope": "Macro" if z_score > 2.5 or is_mismatch else "Sector",
            "topic_fit_score": explainability_score,
            "market_impact_score": explainability_score,
            "theme_expandability": round(explainability_score * 0.8, 1),
            "flow_type": flow_type,
            "topic_decision": topic_decision
        }
