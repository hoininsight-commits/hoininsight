from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict, List
import uuid

from .types import Candidate, RankFeatures

def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

class CandidateGenerator:
    """
    Candidate는 '콘텐츠 훅(인지부조화)' 중심으로 만든다.
    - Gate 단계에서는 L레벨/Z-score/Anomaly logic 금지.
    - numbers는 여기서 억지로 만들지 않아도 됨(validator에서 붙임).
    """

    def generate(self, as_of_date: str, snapshot: Dict[str, Any], events: List[Dict[str, Any]] | None = None) -> List[Candidate]:
        events = events or []
        candidates: List[Candidate] = []

        # 1) Earnings up but price down (가능하면)
        if self._has(snapshot, ["earnings", "price"]):
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="왜 실적이 좋았는데도 주가가 하락했나?",
                category="earnings",
                hook_signals=["earnings_up_price_down"],
                evidence_refs=["snapshot:earnings", "snapshot:price"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        # 2) Index up but sector down (가능하면)
        if self._has(snapshot, ["index", "sectors"]):
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="왜 지수는 오르는데 특정 섹터만 하락하나?",
                category="rotation",
                hook_signals=["index_up_sector_down"],
                evidence_refs=["snapshot:index", "snapshot:sectors"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        # 3) Policy/event inverse (events 있으면)
        if events:
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="왜 정책/이벤트 발표 이후 시장 반응이 기대와 반대로 움직였나?",
                category="policy",
                hook_signals=["policy_announced_market_inverse"],
                evidence_refs=["events:policy_or_event"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        # 4) Fallback candidate (일반형 훅) — 부족하면 채움
        while len(candidates) < 3:
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="오늘 시장에서 사람들이 가장 헷갈리는 지점은 무엇인가?",
                category="other",
                hook_signals=["other"],
                evidence_refs=["snapshot:generic"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        return candidates

    def _has(self, snapshot: Dict[str, Any], keys: List[str]) -> bool:
        # 스냅샷 실제 구조에 맞게 안티그래피티가 조정
        return True
