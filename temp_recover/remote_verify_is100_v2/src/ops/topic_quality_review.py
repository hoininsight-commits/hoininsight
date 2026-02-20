from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class TopicQualityReview:
    """
    Evaluates topic quality based on deterministic rules (facts, timing, fit).
    Generates data/ops/topic_quality_review_today.json and .md.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_json = base_dir / "data" / "ops" / "topic_quality_review_today.json"
        self.output_md = base_dir / "data" / "ops" / "topic_quality_review_today.md"
        self.output_json.parent.mkdir(parents=True, exist_ok=True)

    def run(self, ymd: str, topics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs the quality review process for the given topics.
        """
        review_data = {
            "run_date": ymd,
            "counts": {
                "fact_anchor": {"STRONG": 0, "MEDIUM": 0, "WEAK": 0},
                "timing_edge": {"EARLY": 0, "ON_TIME": 0, "LATE": 0},
                "narration_fit": {"GOOD": 0, "FAIR": 0, "POOR": 0}
            },
            "topics": []
        }

        if not topics:
            self._write_empty_artifacts(ymd)
            return review_data

        for t in topics:
            review = self._evaluate_topic(t)
            review_data["topics"].append(review)
            
            # Update counts
            review_data["counts"]["fact_anchor"][review["fact_anchor"]] += 1
            review_data["counts"]["timing_edge"][review["timing_edge"]] += 1
            review_data["counts"]["narration_fit"][review["narration_fit"]] += 1

        # Save artifacts
        self.output_json.write_text(json.dumps(review_data, indent=2, ensure_ascii=False), encoding="utf-8")
        self._export_markdown(review_data)
        
        return review_data

    def _evaluate_topic(self, t: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic evaluation of a single topic.
        """
        status = t.get("status", "DROP")
        evidence_count = t.get("evidence_count", 0)
        level = t.get("narration_level", 1)
        impact = t.get("impact_window", "LONG")
        saturation = t.get("saturation_level", "NORMAL")
        flags = t.get("flags", [])

        # 1. Fact Anchor
        if status == "READY" and evidence_count >= 3:
            fact_anchor = "STRONG"
        elif status == "READY" and evidence_count >= 1:
            fact_anchor = "MEDIUM"
        else:
            fact_anchor = "WEAK"

        # 2. Timing Edge
        if saturation in ["DENSE", "SATURATED"]:
            timing_edge = "LATE"
        elif impact in ["MID", "LONG"]:
            timing_edge = "EARLY"
        else:
            timing_edge = "ON_TIME"

        # 3. Narration Fit
        if level >= 3:
            narration_fit = "GOOD"
        elif level == 2:
            narration_fit = "FAIR"
        else:
            narration_fit = "POOR"

        # 4. Stock Linkability
        stock_linkable = "LINKABLE" if level >= 3 else "NOT_LINKABLE"

        # 5. Operator Hint (Logic Mapping)
        hint = "Standard Observation"
        if timing_edge == "EARLY" and fact_anchor in ["STRONG", "MEDIUM"]:
            hint = "High preemption candidate"
        elif timing_edge == "LATE":
            hint = "Avoid repetition"
        elif level < 3 and "TITLE_MISMATCH" not in flags:
            # If it's not Level 3, it usually lacks direct beneficiary proof
            hint = "Need beneficiary proof"

        return {
            "topic_id": t.get("topic_id", "unknown"),
            "title": t.get("title", "Untitled"),
            "fact_anchor": fact_anchor,
            "timing_edge": timing_edge,
            "narration_fit": narration_fit,
            "stock_linkability": stock_linkable,
            "hint": hint,
            "flags": flags,
            "why_now": t.get("why_today") or t.get("why_now") or "(not specified)",
            "ceiling": t.get("narration_ceiling") or "(no ceiling)",
            "missing_to_upgrade": self._get_missing_to_upgrade(level),
            "lane": t.get("lane") or "ANOMALY" if not t.get("is_fact_driven") else "FACT"
        }

    def _get_missing_to_upgrade(self, current_level: int) -> str:
        if current_level >= 3:
            return "Full visibility achieved"
        if current_level == 2:
            return "Direct company-level capital signal or contract disclosure"
        return "Industry sector linkage and quantitative trend stability"

    def _write_empty_artifacts(self, ymd: str):
        content = {
            "run_date": ymd,
            "status": "No topics to review today",
            "counts": {},
            "topics": []
        }
        self.output_json.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
        
        md_content = f"# TOPIC QUALITY REVIEW (RUN_DATE: {ymd})\n\nNo topics to review today."
        self.output_md.write_text(md_content, encoding="utf-8")

    def _export_markdown(self, data: Dict[str, Any]):
        ymd = data["run_date"]
        lines = [f"# TOPIC QUALITY REVIEW (RUN_DATE: {ymd})", ""]
        
        for t in data["topics"]:
            lines.append(f"## {t['title']} ({t['topic_id']})")
            lines.append(f"- **Lane**: {t['lane']}")
            lines.append("- **Review**:")
            lines.append(f"  - Fact Anchor: {t['fact_anchor']}")
            lines.append(f"  - Frame Clarity: GOOD (Implicit)")
            lines.append(f"  - Timing Edge: {t['timing_edge']}")
            lines.append(f"  - Narration Fit: {t['narration_fit']}")
            lines.append(f"  - Stock Linkability: {t['stock_linkability']}")
            lines.append(f"  - Flags: {', '.join(t['flags']) if t['flags'] else 'None'}")
            lines.append("- **Explain**:")
            lines.append(f"  - WHY NOW: {t['why_now']}")
            lines.append(f"  - Ceiling: {t['ceiling']}")
            lines.append(f"  - Missing to Upgrade: {t['missing_to_upgrade']}")
            lines.append("")

        self.output_md.write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    # Smoke test
    reviewer = TopicQualityReview(Path("."))
    reviewer.run(datetime.now().strftime("%Y-%m-%d"), [])
