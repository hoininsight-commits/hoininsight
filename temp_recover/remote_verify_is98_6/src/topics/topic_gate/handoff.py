from __future__ import annotations
from typing import Dict, Any, List
from .types import GateOutput, Candidate

class HandoffDecider:
    def decide(self, output: GateOutput, top1: Candidate | dict, snapshot: Dict[str, Any]) -> GateOutput:
        # 간단한 handoff 조건:
        # - evidence_refs가 서로 다른 축 2개 이상
        # - numbers 2개 이상
        evidence_refs = top1.evidence_refs if hasattr(top1, "evidence_refs") else top1.get("evidence_refs", [])
        numbers = top1.numbers if hasattr(top1, "numbers") else top1.get("numbers", [])
        
        distinct_axes = set([ref.split(":")[0] for ref in evidence_refs]) if evidence_refs else set()
        if len(distinct_axes) >= 2 and len(numbers) >= 2:
            output.handoff_to_structural = True
            output.handoff_reason = "복수 데이터 축 결합 + 설명 숫자 2개 이상 확보됨(승격 아님, 후보 전달)."
        else:
            output.handoff_to_structural = False
            output.handoff_reason = "콘텐츠 후보로는 충분하나, Structural 엔진에 넘길 만큼 축 결합/증거가 부족."
        return output
