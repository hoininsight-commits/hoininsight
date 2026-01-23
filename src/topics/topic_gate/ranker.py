from __future__ import annotations
from typing import List
from .types import Candidate, RankFeatures

class Ranker:
    def rank(self, candidates: List[Candidate]) -> List[Candidate]:
        ranked: List[Candidate] = []
        for c in candidates:
            hook_score = self._hook_score(c)
            number_score = 0.0  # validator가 numbers 붙이면 가산 가능
            timeliness_score = 1.0  # 기본값. 이벤트/실적 당일이면 가산 가능
            explainability_score = 1.0  # 기본값. evidence_refs 2개 이상이면 가산 가능

            if len(c.evidence_refs) >= 2:
                explainability_score += 0.5

            final = hook_score + number_score + timeliness_score + explainability_score
            c.rank_features = RankFeatures(
                hook_score=hook_score,
                number_score=number_score,
                timeliness_score=timeliness_score,
                explainability_score=explainability_score,
                final_score=final,
            )
            ranked.append(c)

        ranked.sort(key=lambda x: x.rank_features.final_score, reverse=True)
        return ranked

    def pick_top1(self, ranked: List[Candidate]) -> Candidate:
        # "없음" 선택 금지
        if not ranked:
            raise RuntimeError("TopicGate: ranked candidates empty (should never happen)")
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
