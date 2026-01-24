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

    def generate(self, as_of_date: str, snapshot: Dict[str, Any], events: List[Any] | None = None) -> List[Candidate]:
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
        if self._has(snapshot, ["index_spx"]):
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="왜 지수는 오르는데 내 종목은 하락하나?",
                category="rotation",
                hook_signals=["index_up_sector_down"],
                evidence_refs=["snapshot:index_spx"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        # 3) Event-based candidates (events 연동)
        for e in events:
            # e can be a dict (from older code) or GateEvent object
            e_id = getattr(e, "event_id", e.get("event_id") if isinstance(e, dict) else "unknown")
            e_type = getattr(e, "event_type", e.get("event_type") if isinstance(e, dict) else "other")
            e_title = getattr(e, "title", e.get("title") if isinstance(e, dict) else "Untitled Event")

            q = f"왜 {e_title} (이벤트)가 발생했는데 시장 반응은 기대와 다르게 움직였나?"
            category = "other"
            
            if e_type == "earnings":
                q = f"왜 이번 {e_title} 실적 발표가 향후 분기 가이던스와 충돌하고 있나?"
                category = "earnings"
            elif e_type in ["policy", "regulation"]:
                q = f"왜 {e_title} 규제가 당장의 시장 지배력보다 장기 공급망 재편에 더 결정적인가?"
                category = "policy"
            elif e_type == "flow":
                q = f"왜 {e_title} (자금 흐름) 유입이 가격 상승으로 이어지지 못하고 '출구 전략'으로 보이나?"
                category = "flows"
            elif e_type == "geopolitics":
                 q = f"왜 {e_title} 리스크에도 불구하고 시장의 공포 지수는 오히려 하락하고 있나?"
                 category = "geopolitics"

            candidates.append(Candidate(
                candidate_id=_new_id("cand_ev"),
                as_of_date=as_of_date,
                question=q,
                category=category,
                hook_signals=[f"event_trigger_{e_type}"],
                evidence_refs=[f"events:{e_type}:{e_id}"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        # 4) Fallback candidate (일반형 훅) — 부족하면 채움
        while len(candidates) < 3:
            candidates.append(Candidate(
                candidate_id=_new_id("cand"),
                as_of_date=as_of_date,
                question="오늘 시장에서 사람들이 가장 헷갈리는 지점은 무엇인가? (혼란 포인트)",
                category="other",
                hook_signals=["other"],
                evidence_refs=["snapshot:generic"],
                rank_features=RankFeatures(0,0,0,0,0),
            ))

        return candidates

    def _has(self, snapshot: Dict[str, Any], keys: List[str]) -> bool:
        # Check against daily_snapshot "datasets" list
        # keys are substrings of dataset_id that must exist and be OK
        datasets = snapshot.get("datasets", [])
        
        for key in keys:
            # Logic: At least one dataset containing 'key' must be OK
            found_ok = False
            for ds in datasets:
                if key in ds.get("dataset_id", "") and ds.get("status_today") == "OK":
                    found_ok = True
                    break
            if not found_ok:
                return False
                
        return True
