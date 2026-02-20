import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class AutoPrioritizer:
    """
    Step 43: Auto Prioritization Layer (Pre-pick Engine).
    Surfaces top 3-5 candidates based on deterministic priority scoring.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(self, ymd: str, ready_candidates: List[Dict], shadow_candidates: List[Dict]) -> Dict[str, Any]:
        """
        Evaluates topics and produces auto_priority_today.json.
        """
        all_evals = []
        
        # Step 43-2: Define candidate pool
        # 1. READY topics
        for c in ready_candidates:
            all_evals.append(self._evaluate_topic(c, "READY"))
            
        # 2. NEARLY_READY topics (if total < 3)
        if len(all_evals) < 3:
            nearly_ready = [s for s in shadow_candidates if s.get("readiness", {}).get("readiness_bucket") == "NEARLY_READY"]
            for c in nearly_ready:
                all_evals.append(self._evaluate_topic(c, "NEARLY_READY"))
                
        # 3. SHADOW_READY_TO_PROMOTE topics (if still < 3)
        if len(all_evals) < 3:
            ready_to_promote = [s for s in shadow_candidates if s.get("readiness", {}).get("readiness_bucket") == "READY_TO_PROMOTE"]
            for c in ready_to_promote:
                # Avoid duplicate if already added via READY (though shadow vs ready should be distinct)
                all_evals.append(self._evaluate_topic(c, "READY_TO_PROMOTE"))

        # Sort by score desc, then stable title
        all_evals.sort(key=lambda x: (-x["priority_score"], x["title"]))
        
        # Pick top 3-5
        top_candidates = all_evals[:5]

        result = {
            "run_date": ymd,
            "candidates": all_evals,
            "top_candidates": top_candidates
        }

        # Save to data/ops/auto_priority_today.json
        out_path = self.base_dir / "data" / "ops" / "auto_priority_today.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return result

    def _evaluate_topic(self, topic: Dict[str, Any], pool_type: str) -> Dict[str, Any]:
        """
        Step 43-1: Sum fixed weights for priority scoring.
        """
        score = 0
        factors = []
        
        # +3 if impact_tag == TIME-SENSITIVE
        impact_tag = topic.get("impact_window")
        if impact_tag == "IMMEDIATE" or impact_tag == "NEAR": # mapping impact_tag to internal windows
             # In DecisionDashboard._determine_impact_window mapping
             pass
        
        # Let's check for specific "TIME-SENSITIVE" tag in the topic's own metadata or keywords
        # Re-reading prompt: "if impact_tag == TIME-SENSITIVE"
        # We'll treat "IMMEDIATE" as TIME-SENSITIVE based on Step 17 nomenclature
        if impact_tag == "IMMEDIATE":
            score += 3
            factors.append("TIME-SENSITIVE")

        # +2 if narration_level == 3
        level = topic.get("level", 1)
        if level >= 3:
            score += 2
            factors.append("NARRATION_LEVEL_3")

        # +2 if FACT-DRIVEN == true
        if topic.get("is_fact_driven"):
            score += 2
            factors.append("FACT-DRIVEN")

        # +1 if numeric_evidence exists
        if topic.get("numbers") or topic.get("evidence_count", 0) > 0:
            score += 1
            factors.append("NUMERIC_EVIDENCE")

        # +1 if WHY_NOW mentions policy / earnings / regulation
        why_now = str(topic.get("selection_rationale", [])).lower() + " " + str(topic.get("why_not_speak", "")).lower()
        if any(keyword in why_now for keyword in ["policy", "earnings", "regulation", "fed", "bok"]):
            score += 1
            factors.append("WHY_NOW_POLICY")

        # +1 if shadow_readiness == READY_TO_PROMOTE
        if topic.get("readiness", {}).get("readiness_bucket") == "READY_TO_PROMOTE":
            score += 1
            factors.append("READY_TO_PROMOTE")

        # -1 if narrative_saturation == SATURATED
        if topic.get("saturation_level") == "SATURATED":
            score -= 1
            factors.append("SATURATED_PENALTY")

        # -2 if ceiling_reason exists
        if "CEILING" in str(topic.get("failure_codes", [])):
            score -= 2
            factors.append("CEILING_PENALTY")

        return {
            "topic_id": topic.get("topic_id", topic.get("candidate_id")),
            "title": topic.get("title", "Untitled"),
            "priority_score": score,
            "impact_tag": impact_tag,
            "narration_level": level,
            "fact_driven": topic.get("is_fact_driven", False),
            "reason_factors": factors,
            "pool_type": pool_type
        }
