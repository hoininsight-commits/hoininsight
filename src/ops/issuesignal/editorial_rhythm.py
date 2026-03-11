import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("EditorialRhythm")

class EditorialRhythmLayer:
    """
    IS-81: Editorial Rhythm Layer
    매일 최소 3개의 콘텐츠가 대시보드에 생성되도록 강제합니다.
    """
    
    MIN_QUOTA = 3

    @staticmethod
    def enforce_minimum_output(existing_candidates: List[Dict[str, Any]], rotation_verdict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        기존 후보가 3개 미만인 경우, 부족한 유형을 자동으로 생성하여 보충합니다.
        """
        if len(existing_candidates) >= EditorialRhythmLayer.MIN_QUOTA:
            return existing_candidates

        logger.info(f"[IS-81] Current candidates count ({len(existing_candidates)}) is below quota ({EditorialRhythmLayer.MIN_QUOTA}). Supplementing...")
        
        final_list = list(existing_candidates)
        existing_types = [c.get("content_type") for c in final_list]
        
        # Priority types to supplement
        needed_types = ["STRUCTURE", "PREVIEW", "SCENARIO"]
        
        # Macro context for fallback
        macro_state = rotation_verdict.get("macro_state", {})
        rate_regime = macro_state.get("rate_regime", "UNKNOWN")
        
        supplement_reason = "콘텐츠 리듬 유지를 위해 자동 생성됨"
        
        for t in needed_types:
            if len(final_list) >= EditorialRhythmLayer.MIN_QUOTA:
                break
                
            if t not in existing_types:
                supplement = EditorialRhythmLayer._create_fallback_card(t, rate_regime, supplement_reason)
                final_list.append(supplement)
                existing_types.append(t)
        
        # If still not enough (though unlikely with 3 types), force fill with STRUCTURE
        while len(final_list) < EditorialRhythmLayer.MIN_QUOTA:
            final_list.append(EditorialRhythmLayer._create_fallback_card("STRUCTURE", rate_regime, supplement_reason))
            
        return final_list

    @staticmethod
    def _create_fallback_card(content_type: str, rate_regime: str, reason: str) -> Dict[str, Any]:
        """
        유형별 기본 폴백 카드를 생성합니다.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        if content_type == "STRUCTURE":
            title = f"시장 자본 흐름의 구조적 관찰 ({rate_regime} 환경)"
            fact_text = f"현재 {rate_regime} 금리 환경에서 자본은 상대적 수익성이 높은 자산군으로 구조적 이동을 지속하고 있습니다. 이는 단순한 가격 변동이 아닌 판의 변화입니다."
            why_now = "금리 체제와 유동성 환경이 맞물리는 지점입니다."
            disclaimer = "시장 구조 해석을 위한 콘텐츠이며 확정된 투자 판단이 아닙니다."
        elif content_type == "PREVIEW":
            title = "주요 매크로 일정 및 선행 지표 예고"
            fact_text = "다가오는 통계 발표 및 정책 회의는 시장의 방향성을 결정짓는 핵심 분기점이 될 예정입니다. 선제적 시나리오 점검이 필요한 시점입니다."
            why_now = "예정된 이벤트가 시장의 가격 결정을 강제하는 시점입니다."
            disclaimer = "예정된 일정 기반의 해석이며 실제 결과는 달라질 수 있습니다."
        else: # SCENARIO
            title = "시장 대응 시나리오 분기점 분석"
            fact_text = f"매크로 지표가 상단 저항선에 도달함에 따라, 돌파 시 자금 유입 가속화와 이탈 시 방어적 포지션 전환이라는 양방향 시나리오 분석이 요구됩니다."
            why_now = "가격 지지선과 저항선이 충돌하는 기술적 구조 단계입니다."
            disclaimer = "시나리오 기반 해석이며 결과는 상황에 따라 달라질 수 있습니다."

        return {
            "index": 99, # Special index for supplemented cards
            "title": title,
            "full_text": fact_text,
            "status": "EDITORIAL_CANDIDATE",
            "content_type": content_type,
            "permission_granted": True,
            "why_now": why_now,
            "disclaimer": disclaimer,
            "is_supplementary": True,
            "supplement_reason": reason,
            "score": 60,
            "details": {
                "ticker": None,
                "actor_type": "시장 전체",
                "actor_name_ko": "Macro Market",
                "actor_confidence": 100,
                "ticker_path": {}
            },
            "script": {
                "long_form": f"1. 정의 (Signal)\n{fact_text}\n\n2. 표면 해석 (Surface)\n단순한 변동성으로 보이나 내부 구조는 변화 중입니다.\n\n3. 결론 (Conclusion)\n리듬 유지가 필요한 구간입니다.\n\n---\n{disclaimer}\n({reason})"
            }
        }
