import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TickerPathExtractor")

class TickerPathExtractor:
    """
    IS-69: Ticker Path Extractor
    매크로 주인공(Actor)을 실제 공시(HARD_FACT) 기반의 종목(Ticker)과 연결합니다.
    """

    # 정합성 검증 규칙 (Alignment Rules)
    ALIGNMENT_MAP = {
        "수혜": ["Sales", "Contract", "Supply", "Expansion", "Profit", "AGREEMENT", "ACQUISITION"],
        "피해": ["Regulation", "Lawsuit", "Loss", "Divestiture", "TERMINATION"],
        "회피": ["Regulation", "Divestiture"],
        "병목": ["Exclusive", "Patent", "Unique", "Sole", "Bottleneck"],
        "대체": ["Exclusive", "Patent", "Unique"]
    }

    @staticmethod
    def extract(actor_info: Dict[str, Any], corporate_facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        주인공 정보와 기업 공시를 분석하여 종목 도출 결과를 반환합니다.
        """
        actor_tag = actor_info.get("actor_tag", "-")
        target_keywords = TickerPathExtractor.ALIGNMENT_MAP.get(actor_tag, [])
        
        ticker_results = []
        best_bottleneck_link = "구조적 변화로 인한 수혜가 예상되는 기업입니다."

        # 최근 HARD_FACT 필터링
        hard_facts = [f for f in corporate_facts if f.get("evidence_grade") == "HARD_FACT"]
        
        for fact in hard_facts:
            details = fact.get("details", {})
            company = details.get("company", "알 수 없는 기업")
            action_type = details.get("action_type", "이벤트")
            raw_summary = details.get("raw_summary", "").upper()
            
            # 1. Alignment Check (정합성 검증)
            is_aligned = any(kw.upper() in raw_summary for kw in target_keywords) or \
                         any(kw.upper() in action_type.upper() for kw in target_keywords)
            
            if not is_aligned:
                continue

            # 2. Confidence Scoring
            confidence = 60 # HARD_FACT 기본 점수
            
            # Actor Tag 일치 가점
            if is_aligned: confidence += 15
            
            # 독점/특허 키워드 가점
            if any(kw in raw_summary for kw in ["EXCLUSIVE", "PATENT", "SOLE", "MONOPOLY", "UNIQUE"]):
                confidence += 15
            
            confidence = min(confidence, 100)
            
            # Exposure Rule
            exposure = "숨김"
            if confidence >= 80:
                exposure = "공개"
            elif confidence >= 60:
                exposure = "마스킹"

            if confidence < 60:
                continue

            # 3. Bottleneck Link Generation
            bottleneck_link = TickerPathExtractor._generate_bottleneck_link(company, action_type, raw_summary)
            if confidence >= 80:
                best_bottleneck_link = bottleneck_link

            ticker_results.append({
                "ticker": details.get("ticker", "TKR"), # 실데이터 기반 티커 (기존 구조 활용)
                "company_name_ko": company,
                "event_type": TickerPathExtractor._map_action_to_ko(action_type),
                "bottleneck_link_ko": bottleneck_link,
                "confidence": confidence,
                "evidence_url": fact.get("source_ref", ""),
                "exposure": exposure
            })

        # 결과 정렬 및 상위 3개 제한
        ticker_results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "ticker_results": ticker_results[:3],
            "global_bottleneck_ko": best_bottleneck_link
        }

    @staticmethod
    def _generate_bottleneck_link(company: str, action_type: str, summary: str) -> str:
        """병목 연결 문장 생성"""
        if "AGREEMENT" in action_type:
            return f"{company}는 대규모 공급 계약을 통해 시장의 수요 병목을 해결하는 핵심 주체로 부상하고 있습니다."
        if "ACQUISITION" in action_type:
            return f"{company}는 전략적 인수를 통해 밸류체인 내 독보적인 점유율을 확보하며 구조적 우위를 점하고 있습니다."
        if "FINANCIAL_OBLIGATION" in action_type:
            return f"{company}는 공격적인 자금 조달을 통해 미래 성장을 위한 인프라 병목을 선제적으로 해소하고 있습니다."
        return f"{company}의 이번 결정은 업계 내 공급 구조를 변화시키는 유의미한 신호입니다."

    @staticmethod
    def _map_action_to_ko(action: str) -> str:
        mapping = {
            "AGREEMENT": "계약",
            "ACQUISITION": "인수/합병",
            "FINANCIAL_OBLIGATION": "자산투자",
            "TERMINATION": "계약종료"
        }
        return mapping.get(action, "기타")
