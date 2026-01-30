from __future__ import annotations
from typing import List
import uuid
from .types import Candidate, GateOutput, NumberItem, SpeakEligibility
from .speak_eligibility import SpeakEligibilityCheck

class OutputBuilder:
    def build(self, as_of_date: str, top1: Candidate, ranked: List[Candidate], events: List[Any] = None) -> GateOutput:
        title = self._make_title(top1)
        why_confused = self._why_confused(top1)
        reasons = self._reasons(top1)
        risk = self._risk_one(top1)

        # Step 10-4: Speak Eligibility Check (Hardened)
        checker = SpeakEligibilityCheck()
        # Pass raw event dicts for artifact validation (G2)
        event_dicts = [e.__dict__ if hasattr(e, "__dict__") else e for e in (events or [])]
        
        # Merge top1 data with generated text for keyword analysis
        eval_data = top1.__dict__.copy() if hasattr(top1, "__dict__") else top1.copy()
        eval_data.update({
            "why_people_confused": why_confused,
            "key_reasons": reasons
        })
        speak_elig = checker.evaluate(eval_data, evidence_pool=event_dicts)

        return GateOutput(
            as_of_date=as_of_date,
            topic_id=f"gate_{uuid.uuid4().hex[:10]}",
            title=title,
            question=top1.question,
            why_people_confused=why_confused,
            key_reasons=reasons,
            numbers=top1.numbers[:3],
            risk_one=risk,
            confidence=top1.confidence,
            handoff_to_structural=False,
            handoff_reason="",
            source_candidates=[c.candidate_id for c in ranked[:5]],
            speak_eligibility=speak_elig
        )

    def _make_title(self, c: Candidate | dict) -> str:
        # 질문을 짧은 제목으로
        category = c.category if hasattr(c, "category") else c.get("category")
        if category == "earnings":
            return "실적은 좋은데 주가는 왜 빠졌나"
        if category == "rotation":
            return "지수 상승 속 섹터 하락의 이유"
        if category in ("policy", "geopolitics"):
            return "정책/이벤트 발표 이후 시장 반응이 왜 반대였나"
        return "오늘 시장의 핵심 혼란 포인트"

    def _why_confused(self, c: Candidate | dict) -> str:
        hooks = c.hook_signals if hasattr(c, "hook_signals") else c.get("hook_signals", [])
        if "earnings_up_price_down" in hooks:
            return "좋은 실적=상승이라는 상식과, 실제 주가 하락이 충돌한다."
        if "index_up_sector_down" in hooks:
            return "지수 흐름과 섹터 흐름이 분리돼 체감이 엇갈린다."
        if "policy_announced_market_inverse" in hooks:
            return "정책/이벤트의 방향과 시장 가격 반응이 반대로 나타난다."
        return "시장의 직관과 데이터가 같은 방향으로 움직이지 않는다."

    def _reasons(self, c: Candidate | dict) -> List[str]:
        # 최소 2개, 최대 3개
        category = c.category if hasattr(c, "category") else c.get("category")
        base = [
            "시장 참여자들이 '다음 분기/다음 국면'을 더 중요하게 본다.",
            "자금이 특정 스타일/섹터로 회전하며 상대적 약세가 발생한다.",
        ]
        if category in ("policy", "geopolitics"):
            base.append("정책은 즉시 실적이 아니라 '기대 경로'를 바꿔 반응이 지연/왜곡될 수 있다.")
        return base[:3]

    def _risk_one(self, c: Candidate) -> str:
        return "추가 확인 데이터(가이던스/자금흐름)가 나오면 해석이 급변할 수 있다."
