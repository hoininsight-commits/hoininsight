from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import random

class EntityRole(Enum):
    BENEFICIARY = "STRUCTURAL BENEFICIARY"
    VICTIM = "STRUCTURAL VICTIM"
    BOTTLENECK = "STRUCTURAL BOTTLENECK"
    HEDGE = "STRUCTURAL HEDGE"
    EXECUTOR = "STRUCTURAL EXECUTOR"

class ConstraintTag(Enum):
    SCHEDULE_LOCKED = "SCHEDULE_LOCKED"
    CAPITAL_LOCKED = "CAPITAL_LOCKED"
    POLICY_LOCKED = "POLICY_LOCKED"
    PHYSICAL_LOCKED = "PHYSICAL_LOCKED"
    NARRATIVE_LOCKED = "NARRATIVE_LOCKED"

@dataclass
class EntityCard:
    name: str
    type: str # Company, ETF, etc.
    role: EntityRole
    constraints: List[ConstraintTag]
    logic_summary: str # 4 sentences
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "role": self.role.value,
            "constraints": [c.value for c in self.constraints],
            "logic_summary": self.logic_summary
        }

class EntityMappingLayer:
    """
    Step 83: Maps Top-1 Topic to structural entities.
    Principles:
    1. No Recommendations.
    2. Structural Necessity Only.
    """
    
    @staticmethod
    def map_target_entities(top_topic: Dict[str, Any], decision_card: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main entry point.
        """
        # 1. Extract Candidate Strings
        # Try to get from decision card's top topic if available, otherwise fallback
        candidates = []
        
        # Strategy A: Use 'leader_stocks' from the matching topic in decision_card
        topic_title = top_topic.get("top_signal", {}).get("title", "")
        
        # Find matching topic in decision_card
        source_topic = None
        for t in decision_card.get("top_topics", []):
            if t.get("title") == topic_title:
                source_topic = t
                break
        
        if source_topic:
            candidates = source_topic.get("leader_stocks", [])
        
        # Fallback if no candidates found (for safety/mock)
        if not candidates and "Risk-Off" in topic_title:
            candidates = ["KODEX 200선물인버스2X", "SQQQ", "VIXY"]
        elif not candidates:
            # Generic fallback to ensure UI doesn't break
            candidates = ["Sector Leader A", "Infrastructure B", "Hedge ETF C"]

        # 2. Enrich Entities (The Core "Cognitive" Step)
        entity_cards = []
        for name in candidates:
            card = EntityMappingLayer._enrich_entity(name, top_topic)
            entity_cards.append(card)
            
        # 3. Validation (Min 3)
        # If we have fewer than 3, we might need to hallucinate structural peers (skipped for now, assuming upstream provides enough)
        
        return [c.to_dict() for c in entity_cards]

    @staticmethod
    def _enrich_entity(name: str, topic_context: Dict[str, Any]) -> EntityCard:
        """
        Determines Role, Type, and Logic based on Name and Context.
        In a real system, this would query a Knowledge Graph.
        Here, we use Heuristics based on naming conventions and topic context.
        """
        
        # 1. Type Inference
        e_type = "Company"
        if any(x in name.upper() for x in ["ETF", "ETN", "KODEX", "TIGER", "SQQQ", "TQQQ", "VIX"]):
            e_type = "ETF"
        elif any(x in name for x in ["선물", "국채", "달러"]):
            e_type = "Sovereign/Currency"
            
        # 2. Role Inference
        # Default
        role = EntityRole.EXECUTOR
        
        # Heuristics
        title = topic_context.get("top_signal", {}).get("title", "")
        pressure_type = topic_context.get("top_signal", {}).get("pressure_type", "")
        
        # Priority 0: Explicit Hedges (Inverse/VIX)
        if "인버스" in name or "SQQQ" in name or "VIX" in name:
             role = EntityRole.HEDGE
             
        # Priority 1: Infrastructure / Supply Chain (Bottlenecks)
        elif "공급망" in title or "Infrastructure" in pressure_type:
             # If it's an ETF, it's likely a beneficiary or capital lock, but if company, likely bottleneck/executor
             if e_type == "ETF":
                 role = EntityRole.BENEFICIARY 
             else:
                 role = EntityRole.BOTTLENECK

        # Priority 2: Crisis / Risk-Off (Overrides Priority 1 only for Hedges/Victims if not Infra)
        elif "Risk-Off" in title or "위기" in title or "붕괴" in title:
             role = EntityRole.VICTIM 
             
        # Correction for knowns
        if "엘컴텍" in name: role = EntityRole.HEDGE # Gold proxy
        
        # 3. Constraint Inference
        constraints = []
        if e_type == "ETF":
            constraints.append(ConstraintTag.CAPITAL_LOCKED) # ETFs receive flows
        if role == EntityRole.BOTTLENECK:
            constraints.append(ConstraintTag.PHYSICAL_LOCKED)
        if "정책" in title or "Political" in pressure_type:
            constraints.append(ConstraintTag.POLICY_LOCKED)
            
        if not constraints:
            constraints.append(ConstraintTag.NARRATIVE_LOCKED) # Default
            
        # 4. Logic Generation (The 4 Sentences)
        # Template based on Role
        logic = ""
        if role == EntityRole.HEDGE:
            logic = f"1. 이 토픽은 '자본의 긴급한 회피'라는 구조적 압력을 발생시킵니다. 2. {name}은(는) 이 압력을 흡수할 수 있는 유일한 역방향 파이프라인입니다. 3. 시장 심리가 아닌, 리스크 헷지 매커니즘(Capital Logic)에 의해 자금 유입이 강제됩니다. 4. 이 대상이 없다면 시장의 공포 비용을 정량화할 수 없습니다."
        elif role == EntityRole.BOTTLENECK:
            logic = f"1. 이 토픽은 물리적 공급망의 병목을 핵심 구조로 가집니다. 2. {name}은(는) 해당 병목을 통과하기 위해 반드시 거쳐야 할 관문입니다. 3. 대체 불가능한 물리적 인프라(Physical Constraint)에 의해 수요가 고정됩니다. 4. 이 대상을 제외하면 공급망의 구조적 결함을 설명할 수 없습니다."
        elif role == EntityRole.VICTIM:
            logic = f"1. 이 토픽은 거시적 유동성 축소라는 구조적 충격을 동반합니다. 2. {name}은(는) 해당 충격에 가장 취약한 자산 구조를 가지고 있습니다. 3. 밸류에이션이 아닌, 자금 조달 비용 상승(Rate Pressure)에 의해 하락 압력이 발생합니다. 4. 이 대상을 언급하지 않으면 위기의 전염 경로를 설명할 수 없습니다."
        else: # Executor / Beneficiary
            logic = f"1. 이 토픽은 새로운 트렌드의 실행을 요구하는 구조입니다. 2. {name}은(는) 이 트렌드를 현실화할 수 있는 실행 주체입니다. 3. 이미 시장 담론(Narrative)에 진입하여 수급의 1차 기착지가 되었습니다. 4. 이 대상을 제외하고는 이 토픽의 현재 진행형을 설명할 수 없습니다."
            
        return EntityCard(name=name, type=e_type, role=role, constraints=constraints, logic_summary=logic)
