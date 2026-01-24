from __future__ import annotations
from typing import List
from .types import Candidate, RankFeatures

class Ranker:
    def rank(self, candidates: List[Candidate], events_index: Dict[str, Any] | None = None) -> List[Candidate]:
        ranked: List[Candidate] = []
        events_index = events_index or {}
        
        for c in candidates:
            hook_score = self._hook_score(c)
            
            # 1) Number score: 정량적 증거가 많을수록 가산
            number_score = len(c.numbers) * 0.5
            
            # 2) Evidence quality score: 이벤트 연동 여부 및 출처 신뢰도 반영
            evidence_quality_score = 0.0
            linked_event_req_conf = False
            
            for ref in c.evidence_refs:
                if ref.startswith("events:"):
                    parts = ref.split(":")
                    if len(parts) >= 3:
                        e_id = parts[2]
                        event_data = events_index.get(e_id)
                        if event_data:
                            # Use trust_score from Event (0.0~1.0)
                            t_score = getattr(event_data, "trust_score", 0.5)
                            evidence_quality_score += (t_score * 1.5) # Trust 가중치
                            if getattr(event_data, "requires_confirmation", False):
                                linked_event_req_conf = True
                        else:
                            evidence_quality_score += 1.0  # fallback
                
                if "snapshot" in ref:
                    evidence_quality_score += 0.2  # 스냅샷 기초 데이터 가점

            timeliness_score = 1.0
            explainability_score = 1.0
            if len(c.evidence_refs) >= 2:
                explainability_score += 0.5

            final = hook_score + number_score + timeliness_score + explainability_score + evidence_quality_score
            
            # Metadata for Top1 filtering
            c.requires_confirmation = linked_event_req_conf
            
            c.rank_features = RankFeatures(
                hook_score=hook_score,
                number_score=number_score,
                timeliness_score=timeliness_score,
                explainability_score=explainability_score,
                evidence_quality_score=evidence_quality_score,
                final_score=final,
            )
            ranked.append(c)

        ranked.sort(key=lambda x: x.rank_features.final_score, reverse=True)
        return ranked

    def pick_top1(self, ranked: List[Candidate]) -> Candidate:
        # "없음" 선택 금지
        if not ranked:
            raise RuntimeError("TopicGate: ranked candidates empty (should never happen)")
        
        # 신뢰도가 낮아 교차 검증(confirmation)이 필요한 이벤트 기반 후보는 TOP1에서 제외
        for cand in ranked:
            if not getattr(cand, "requires_confirmation", False):
                return cand
        
        # 모든 후보가 requires_confirmation인 경우 (거의 없겠지만), 
        # 안전을 위해 fallback(generic)을 찾거나 첫번째를 반환 (비즈니스 룰에 따라)
        # 여기서는 가장 점수 높은 것을 반환하되, 경고성으로 첫번째 반환
        return ranked[0]

    def _hook_score(self, c: Candidate) -> float:
        # 단순 룰: 인지부조화 타입에 가중치
        hooks = set(c.hook_signals)
        score = 0.0
        if "earnings_up_price_down" in hooks: score += 2.0
        if "index_up_sector_down" in hooks: score += 1.5
        if "policy_announced_market_inverse" in hooks: score += 1.5
        if "good_news_price_down" in hooks: score += 2.0
        if "bad_news_price_up" in hooks: score += 2.0
        if score == 0.0: score = 1.0
        return score
