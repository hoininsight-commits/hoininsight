from typing import List, Dict, Any
from enum import Enum

class EntityState(Enum):
    OBSERVE = "OBSERVE"
    TRACK = "TRACK"
    PRESSURE = "PRESSURE"
    RESOLUTION = "RESOLUTION"

class EntityStateClassifier:
    """
    Step 84: Interprets "Entity + Structual Context" into "Action State".
    Does NOT give advice. Only classifies key phases.
    """
    
    @staticmethod
    def classify_entities(entities: List[Dict[str, Any]], topic_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enriches entity dicts with 'state' and 'justification'.
        """
        classified_entities = []
        
        # Context Extraction
        intensity = topic_context.get("top_signal", {}).get("intensity", "FLASH")
        escalation_count = topic_context.get("top_signal", {}).get("escalation_count", 0)
        is_shock = "SHOCK" in topic_context.get("top_signal", {}).get("rhythm", "")
        
        for e in entities:
            role = e.get("role", "")
            constraints = e.get("constraints", [])
            
            # Default State
            state = EntityState.OBSERVE
            justification = ["1. 초기 구조적 노출 단계입니다.", "2. 아직 임계치 미만입니다.", "3. 모니터링이 필요합니다."]
            
            # Logic Branching
            
            # 1. RESOLUTION Logic (Highest Priority)
            # If intensity is extremely high or it's a known resolution event
            if intensity == "DEEP_HUNT" and escalation_count >= 5:
                state = EntityState.RESOLUTION
                justification = [
                    "1. 구조적 압력이 정점에 도달하여 해소 국면에 진입했습니다.",
                    "2. 가격/변동성이 이미 이벤트를 반영 중입니다.",
                    "3. 사후 검증(Post-Mortem) 단계로 전환될 수 있습니다."
                ]
            
            # 2. PRESSURE Logic
            # Bottlenecks or Victims in High Intensity scenarios
            elif state == EntityState.OBSERVE: # Only if not yet resolved
                if "BOTTLENECK" in role or "VICTIM" in role:
                    if intensity in ["STRIKE", "DEEP_HUNT"] or escalation_count >= 3:
                        state = EntityState.PRESSURE
                        justification = [
                            f"1. {intensity} 강도의 구조적 제약이 실제로 작동 중입니다.",
                            "2. 물리적/자본적 병목이 가격 결정의 주도권을 가집니다.",
                            "3. 이 압력이 해소되지 않는 한 변동성은 지속됩니다."
                        ]
                elif "HEDGE" in role and is_shock:
                     state = EntityState.PRESSURE
                     justification = [
                        "1. 시장 충격(Shock)에 대한 기계적 헷지 수요가 급증하는 구간입니다.",
                        "2. 펀더멘털이 아닌 공포(Fear) 비용이 가격을 정당화합니다.",
                        "3. 충격이 진정되기 전까지는 오버슈팅 가능성이 열려 있습니다."
                    ]

            # 3. TRACK Logic
            # Scheduled events or policy locks, or Observes that are heating up
            if state == EntityState.OBSERVE:
                if "SCHEDULE_LOCKED" in constraints or "POLICY_LOCKED" in constraints:
                    state = EntityState.TRACK
                    justification = [
                        "1. 확정된 일정/정책 이벤트가 다가오고 있습니다.",
                        "2. 시간표(Timeline)가 가장 중요한 제약 조건입니다.",
                        "3. 일정이 도래하면 즉시 Pressure/Resolution으로 전이됩니다."
                    ]
                elif escalation_count >= 1:
                    state = EntityState.TRACK
                    justification = [
                        "1. 단발성 이슈를 넘어 구조화 조짐이 관찰됩니다.",
                        "2. 시장의 관심도가 증가하며 유동성이 유입되는 초기 단계입니다.",
                        "3. 추가적인 Trigger 발생 시 Pressure로 격상됩니다."
                    ]
            
            # Enrich
            e_out = e.copy()
            e_out["state"] = state.value
            e_out["state_justification"] = justification
            classified_entities.append(e_out)
            
        # Sort Rule: RESOLUTION > PRESSURE > TRACK > OBSERVE
        priority_map = {
            "RESOLUTION": 0,
            "PRESSURE": 1,
            "TRACK": 2,
            "OBSERVE": 3
        }
        
        classified_entities.sort(key=lambda x: priority_map.get(x["state"], 99))
        
        return classified_entities
