import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ActorBridge")

class ActorBridgeEngine:
    """
    IS-68: Macro → Actor Bridge Engine
    매크로 신호를 분석하여 구체적인 주체(Actor)를 도출하고 에디토리얼 후보로 승격시킵니다.
    """

    # 매핑 규칙 정의 (Rule-based)
    MACRO_ACTOR_RULES = {
        "US10Y": {
            "actor_type": "자본주체",
            "actor_name_ko": "미국 장기채",
            "actor_tag": "회피",
            "reason_template": "국채 금리 급등으로 인해 {name} 시장의 자본 이동이 필연적으로 발생하고 있습니다."
        },
        "US02Y": {
            "actor_type": "자본주체",
            "actor_name_ko": "미국 단기 자금",
            "actor_tag": "회피",
            "reason_template": "금리 변동성이 확대되면서 {name} 중심의 안전 자산 선호가 강제되고 있습니다."
        },
        "WTI": {
            "actor_type": "섹터",
            "actor_name_ko": "에너지 섹터",
            "actor_tag": "수혜",
            "reason_template": "원유 가격의 구조적 상승으로 인해 {name} 내 기업들의 수익성 개선이 필연적입니다."
        },
        "DXY": {
            "actor_type": "자본주체",
            "actor_name_ko": "글로벌 달러 자본",
            "actor_tag": "대체",
            "reason_template": "강달러 기조가 강화되면서 {name} 흐름이 여타 자산에서 달러로 집중되고 있습니다."
        },
        "GOLD": {
             "actor_type": "자본주체",
             "actor_name_ko": "안전 자산(금)",
             "actor_tag": "회피",
             "reason_template": "인플레이션 및 지정학적 리스크로 인한 {name} 매수세가 강력하게 포착되었습니다."
        }
    }

    @staticmethod
    def bridge(macro_facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        매크로 팩트를 분석하여 Actor 정보가 포함된 후보 리스트를 반환합니다.
        """
        candidates = []
        
        for fact in macro_facts:
            ticker = fact.get("details", {}).get("ticker")
            rule = ActorBridgeEngine.MACRO_ACTOR_RULES.get(ticker)
            
            if not rule:
                continue

            # 신뢰도 계산 (Evidence Scoring)
            confidence = 50
            grade = fact.get("evidence_grade", "TEXT_HINT")
            
            if grade == "HARD_FACT":
                confidence += 30
            elif grade == "MEDIUM":
                confidence += 15
            else:
                confidence += 5

            # 변동성 가중치 (0.5% 이상 변동 시 추가 점수)
            change_pct = abs(fact.get("details", {}).get("change_pct", 0))
            if change_pct >= 0.5:
                confidence += 10
            
            confidence = min(confidence, 100)

            # 70점 미만이면 주체 도출 실패로 간주
            if confidence < 70:
                logger.debug(f"Confidence {confidence} for {ticker} is too low. Skipping bridge.")
                continue

            # Actor 객체 생성
            actor_data = {
                "actor_type": rule["actor_type"],
                "actor_name_ko": rule["actor_name_ko"],
                "actor_tag": rule["actor_tag"],
                "actor_reason_ko": rule["reason_template"].format(name=rule["actor_name_ko"]),
                "actor_confidence": confidence,
                "actor_evidence": [
                    {
                        "title": fact.get("fact_text", "매크로 지표 변동"),
                        "source": fact.get("source", "Market Data"),
                        "grade": ActorBridgeEngine._map_grade_to_ko(grade),
                        "url": fact.get("source_ref", ""),
                        "ts": fact.get("source_date", "")
                    }
                ]
            }

            # 후보 토픽 생성 (IssueSignal 호환 포맷)
            candidate = {
                "fact_text": fact.get("fact_text"),
                "source": fact.get("source"),
                "details": {
                    **fact.get("details", {}),
                    "actor_type": actor_data["actor_type"],
                    "actor_name_ko": actor_data["actor_name_ko"],
                    "actor_tag": actor_data["actor_tag"],
                    "actor_reason_ko": actor_data["actor_reason_ko"],
                    "actor_confidence": actor_data["actor_confidence"],
                    "actor_evidence": actor_data["actor_evidence"]
                },
                "why_now": actor_data["actor_reason_ko"],
                "is_macro_promotion": True
            }
            candidates.append(candidate)
            
        logger.info(f"Actor Bridge: {len(candidates)} candidates promoted from macro facts.")
        return candidates

    @staticmethod
    def _map_grade_to_ko(grade: str) -> str:
        if grade == "HARD_FACT": return "✅증거"
        if grade == "MEDIUM": return "🟡보통"
        return "🔍단서"
