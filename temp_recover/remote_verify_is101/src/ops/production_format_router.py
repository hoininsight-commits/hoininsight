from typing import Dict, List, Any
from enum import Enum

class FormatEnum(str, Enum):
    SHORT_ONLY = "SHORT_ONLY"
    LONG_ONLY = "LONG_ONLY"
    BOTH = "BOTH"

class ProductionFormatRouter:
    """
    Step 46: Production Format Router v1.0.
    Determines optimal production format (SHORT / LONG / BOTH) based on metadata.
    """
    def route_topic(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a single topic based on deterministic rules.
        Expected topic fields: narration_level, impact_tag, speak_pack (numbers), evidence_refs, risk_note.
        """
        lvl = topic.get("narration_level", 1)
        impact = topic.get("impact_tag")
        
        sp = topic.get("speak_pack", {})
        nums_count = len(sp.get("numbers", []))
        refs_count = len(topic.get("evidence_refs", []))
        evidence_density = nums_count + refs_count
        
        risk_note = sp.get("risk_note", "").upper()
        has_complex_risk = "TRADE-OFF" in risk_note or "RISK" in risk_note or len(risk_note) > 50

        reasons = []
        
        # Rule Evaluation
        is_long = False
        is_both = False
        is_short = False
        
        # LONG_ONLY Rules (Condition sets)
        if lvl == 3:
            is_long = True
            reasons.append("LEVEL_3")
        if evidence_density >= 4:
            is_long = True
            reasons.append("EVIDENCE_DENSE")
        if has_complex_risk:
            is_long = True
            reasons.append("COMPLEX_RISK_CONTEXT")
            
        # BOTH Rules (All must pass for this set)
        if lvl == 2 and evidence_density >= 2 and impact in ["NEAR", "MID"]:
            is_both = True
            reasons.append("LEVEL_2_MID_IMPACT_DENSE")
            
        # SHORT_ONLY Rules (All must pass)
        if lvl == 1 and impact in ["IMMEDIATE", "NEAR"] and evidence_density <= 2 and not has_complex_risk:
            is_short = True
            reasons.append("HIGH_PRIORITY_BRIEF")

        # Priority Order: LONG_ONLY > BOTH > SHORT_ONLY
        if is_long:
            final_format = FormatEnum.LONG_ONLY
            final_reasons = [r for r in reasons if r in ["LEVEL_3", "EVIDENCE_DENSE", "COMPLEX_RISK_CONTEXT"]]
        elif is_both:
            final_format = FormatEnum.BOTH
            final_reasons = [r for r in reasons if r == "LEVEL_2_MID_IMPACT_DENSE"]
        else:
            final_format = FormatEnum.SHORT_ONLY
            final_reasons = reasons if is_short else ["DEFAULT_SHORT"]

        return {
            "topic_id": topic.get("topic_id"),
            "format": final_format.value,
            "routing_reason": final_reasons or ["DEFAULT_BRIEF"]
        }
