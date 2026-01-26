import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class ShadowCandidateBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _determine_impact_window(self, topic: Dict[str, Any], tags: List[str]) -> str:
        tags = tags or []
        risk_one = topic.get("risk_one", "")
        reasons = topic.get("key_reasons", [])
        combined_text = (risk_one + " " + " ".join(reasons)).lower()
        
        schedule_keywords = ["d-day", "today", "tomorrow", "scheduled", "timeline", "확정", "발표일"]
        if any(k in combined_text for k in schedule_keywords):
            return "IMMEDIATE"
            
        if any("TIME-SENSITIVE" in t for t in tags):
            return "NEAR"
            
        if any("TRENDING NOW" in t for t in tags):
             return "MID"
             
        if any("STRUCTURAL" in t for t in tags):
             return "LONG"
             
        return "MID"

    def _check_fact_driven(self, topic: Dict) -> bool:
        if topic.get("is_fact_driven") or topic.get("metadata", {}).get("is_fact_driven"):
            return True
        tags = topic.get("tags", [])
        if any(isinstance(tag, str) and tag.startswith("FACT_") for tag in tags):
            return True
        return False

    def build(self, ymd: str) -> Dict[str, Any]:
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        candidates_file = gate_dir / "topic_gate_candidates.json"
        
        if not candidates_file.exists():
            return {"run_date": ymd, "count": 0, "candidates": []}

        try:
            data = json.loads(candidates_file.read_text(encoding="utf-8"))
            all_topics = data.get("candidates", [])
        except:
            return {"run_date": ymd, "count": 0, "candidates": []}

        shadow_pool = []
        for t in all_topics:
            tid = t.get("topic_id")
            if not tid: continue

            # Load quality info
            quality_file = gate_dir / f"script_v1_{tid}.md.quality.json"
            if not quality_file.exists():
                continue

            try:
                q_data = json.loads(quality_file.read_text(encoding="utf-8"))
                quality_status = q_data.get("quality_status", "DROP")
                failure_codes = q_data.get("failure_codes", [])
            except:
                continue

            # Eligibility Rule 34-1
            if quality_status not in ["HOLD", "DROP"]:
                continue

            # Condition 1: Fact Driven / Structural / Non-Immediate
            is_fact = self._check_fact_driven(t)
            is_structural = any("STRUCTURAL" in tag for tag in t.get("tags", []))
            impact_window = self._determine_impact_window(t, t.get("tags", []))
            
            eligible_feature = is_fact or is_structural or impact_window != "IMMEDIATE"
            if not eligible_feature:
                continue

            # Condition 2: Not rejected for critical naming/placeholder issues
            if "TITLE_MISMATCH" in failure_codes:
                continue
            
            # If rejected ONLY for PLACEHOLDER_EVIDENCE, excluded? 
            # Prompt: "NOT rejected for: PLACEHOLDER_EVIDENCE only"
            # This means if codes == ["PLACEHOLDER_EVIDENCE"], skip.
            if failure_codes == ["PLACEHOLDER_EVIDENCE"]:
                continue

            # Build candidate object
            promotion_triggers = []
            if impact_window != "IMMEDIATE":
                promotion_triggers.append("issue timing window opens")
            if is_fact:
                promotion_triggers.append("additional numeric evidence appears")
            if is_structural:
                promotion_triggers.append("supporting anomaly signal confirmed")
            
            # Default triggers
            if not promotion_triggers:
                promotion_triggers.append("script quality improvement")
                promotion_triggers.append("evidence gathering complete")

            shadow_pool.append({
                "topic_id": tid,
                "title": t.get("title", "Untitled"),
                "lane": "FACT" if is_fact else "ANOMALY",
                "quality_status": quality_status,
                "why_not_speak": q_data.get("reason", "Quality standards not met"),
                "promotion_triggers": promotion_triggers,
                "impact_window": impact_window
            })

        result = {
            "run_date": ymd,
            "count": len(shadow_pool),
            "candidates": shadow_pool
        }

        output_path = self.base_dir / "data" / "ops" / "shadow_candidates.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return result

if __name__ == "__main__":
    import sys
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.utcnow().strftime("%Y-%m-%d")
    builder = ShadowCandidateBuilder(Path("."))
    builder.build(ymd)
