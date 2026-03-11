import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ScenarioInterpreter")

class ScenarioInterpreter:
    """
    IS-75: Scenario Interpretation Layer
    확정된 사실을 구조적 시나리오로 해석합니다 (예측 배제).
    """

    @staticmethod
    def interpret(watchlist_data: Optional[Dict[str, Any]], hard_facts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        입력 조건: HARD_FACT >= 1, Actor 존재, IS-74 활성 또는 구조적 신호 감지
        출력: Scenario Interpretation 데이터 또는 None
        """
        if not watchlist_data and not hard_facts:
            return None

        # 시나리오 생성 로직 (Rule-based / Template-based)
        scenarios = []
        
        if watchlist_data:
            actor = watchlist_data.get("actor")
            entities = ", ".join(watchlist_data.get("entities", []))
            
            if "정부" in actor or "연방" in actor:
                scenarios.append(f"{actor}의 직접적인 지배력이 특정 공급망으로 확산될 경우, 해당 섹터 내 자본 집중 현상이 심화될 수 있습니다.")
                scenarios.append(f"국가 전략 자산으로서의 가치가 강조될 경우, {entities} 등 관련 기업들의 구조적 지위가 재편되는 시나리오가 가능합니다.")
            else:
                scenarios.append(f"{actor} 주도의 대규모 자본 이동이 발생할 경우, 기존 시장의 밸류체인 내 병목 구간에서 강력한 변동성이 나타날 수 있습니다.")
                scenarios.append(f"구조적 신호가 실질적인 공급망 통제로 이어질 경우, 특정 섹터의 독점적 지위가 강화될 것으로 해석될 수 있습니다.")
        
        # 팩트 기반 추가 시나리오
        for hf in hard_facts[:1]:
            scenarios.append(f"'{hf.get('fact_text', '')[:30]}...' 관련 공시가 실질적인 계약으로 구체화될 경우, 자본의 질적 전환이 가속화될 수 있습니다.")

        if not scenarios:
            return None

        return {
            "layer": "SCENARIO_INTERPRETATION",
            "status": "SCENARIO",
            "title": "가능한 구조적 시나리오",
            "disclaimer": "확정된 사실 아님 / 시나리오 해석",
            "scenarios": scenarios[:2], # 최대 2개만 노출
            "confidence": "LOW",
            "based_on": ["HARD_FACT", "STRUCTURAL_SIGNAL"]
        }
