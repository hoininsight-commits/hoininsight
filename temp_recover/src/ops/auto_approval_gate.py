import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class AutoApprovalGate:
    """
    Step 44: Conditional Auto-Approval Gate v1.0.
    Automatically approves critical topics if they meet 8 strict conditions.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(self, ymd: str, ready_topics: List[Dict], auto_priority_data: Dict[str, Any], operator_decisions: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Evaluates topics for auto-approval.
        auto_priority_data is expected to be the content of auto_priority_today.json.
        operator_decisions is {topic_id: decision_dict} from OperatorDecisionLog.
        """
        # Map priority scores from auto_priority_data for easy lookup
        priority_map = {c["topic_id"]: c for c in auto_priority_data.get("candidates", [])}
        
        auto_approved = []
        for t in ready_topics:
            tid = t.get("topic_id")
            p_data = priority_map.get(tid, {})
            p_score = p_data.get("priority_score", 0)
            
            # Step 44-1: Eligibility Rules (ALL MUST PASS)
            reasons = []
            
            # Rule 1: status == READY (assured by input ready_topics)
            # Rule 2: auto_priority_score >= 8
            if p_score >= 8:
                reasons.append("HIGH_PRIORITY_SCORE")
            
            # Rule 3: impact_tag == TIME-SENSITIVE (mapped to IMMEDIATE in Step 43)
            # We look at the evaluated p_data which has impact_tag normalized
            if p_data.get("impact_tag") == "IMMEDIATE":
                reasons.append("TIME_SENSITIVE")
            
            # Rule 4: narration_level == 3
            if t.get("level", 1) >= 3:
                reasons.append("LEVEL_3")
                
            # Rule 5: narrative_saturation != SATURATED
            if t.get("saturation_level") != "SATURATED":
                reasons.append("NOT_SATURATED")
                
            # Rule 6: ceiling_reason == NONE
            # failure_codes usually empty for READY topics but let's be strict
            if not t.get("failure_codes"):
                reasons.append("NO_CEILING")
                
            # Rule 7: judgment_notes does NOT include HIGH RISK
            j_notes = str(t.get("judgment_notes", [])).upper()
            if "HIGH RISK" not in j_notes:
                reasons.append("LOW_NARRATIVE_RISK")
                
            # Rule 8: operator_decision NOT already recorded
            if tid not in operator_decisions:
                reasons.append("NO_OPERATOR_CONFLICT")

            # Final check - all 7 detected above + status check
            # wait, prompt says 8 rules. 
            # 1) status == READY
            # 2) score >= 8
            # 3) impact == TIME-SENSITIVE
            # 4) level == 3
            # 5) saturation != SATURATED
            # 6) ceiling == NONE
            # 7) notes != HIGH RISK
            # 8) operator_decision NOT recorded
            
            target_reasons = {
                "HIGH_PRIORITY_SCORE", "TIME_SENSITIVE", "LEVEL_3", 
                "NOT_SATURATED", "NO_CEILING", "LOW_NARRATIVE_RISK", 
                "NO_OPERATOR_CONFLICT"
            }
            
            if target_reasons.issubset(set(reasons)):
                auto_approved.append({
                    "topic_id": tid,
                    "title": t.get("title"),
                    "priority_score": p_score,
                    "approval_reason": [
                        "TIME_SENSITIVE", 
                        "LEVEL_3", 
                        "STRONG_EVIDENCE", # derived from high score/priority
                        "NO_CEILING", 
                        "LOW_NARRATIVE_RISK"
                    ]
                })

        result = {
            "run_date": ymd,
            "auto_approved": auto_approved,
            "count": len(auto_approved)
        }

        # Save to data/ops/auto_approved_today.json
        out_path = self.base_dir / "data" / "ops" / "auto_approved_today.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return result
