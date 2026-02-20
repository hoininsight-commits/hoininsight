from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class EditorialSpeakabilityGate:
    """
    Final pre-speak gate providing binary verdicts: SPEAKABLE_NOW or NOT_SPEAKABLE_YET.
    Deterministic and read-only.
    """

    SPEAKABLE_NOW = "SPEAKABLE_NOW"
    NOT_SPEAKABLE_YET = "NOT_SPEAKABLE_YET"

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_json = base_dir / "data" / "ops" / "topic_speakability_today.json"
        self.output_md = base_dir / "data" / "ops" / "topic_speakability_today.md"
        self.output_json.parent.mkdir(parents=True, exist_ok=True)

    def run(self, ymd: str) -> Dict[str, Any]:
        """
        Runs the speakability gate.
        Inputs: topic_view_today.json, topic_quality_review_today.json
        """
        view_path = self.base_dir / "data" / "ops" / "topic_view_today.json"
        quality_path = self.base_dir / "data" / "ops" / "topic_quality_review_today.json"

        view_data = {}
        quality_data = {}

        if view_path.exists():
            try:
                view_data = json.loads(view_path.read_text(encoding="utf-8"))
            except: pass
        if quality_path.exists():
            try:
                quality_data = json.loads(quality_path.read_text(encoding="utf-8"))
            except: pass

        # Map quality review by topic_id for easy lookup
        quality_map = {t["topic_id"]: t for t in quality_data.get("topics", [])}

        results = []
        counts = {self.SPEAKABLE_NOW: 0, self.NOT_SPEAKABLE_YET: 0}

        # Consolidate all topics from sections for review
        # The prompt says "For each topic in TODAY TOPIC VIEW"
        # dashboard_manifest links topic_view_today.json.
        # Let's iterate over consolidated topics from quality review if it exists, or from view.
        # Quality review has more mapping info.
        
        all_topics = quality_data.get("topics", [])
        if not all_topics and view_data.get("sections"):
            # Fallback to view sections if quality review missed some
            seen = set()
            for sect in view_data["sections"].values():
                for t in sect:
                    if t.get("topic_id") not in seen:
                        all_topics.append(t)
                        seen.add(t.get("topic_id"))

        for t in all_topics:
            topic_id = t.get("topic_id", "unknown")
            quality = quality_map.get(topic_id, {})
            
            verdict = self._decide_speakability(t, quality)
            results.append(verdict)
            counts[verdict["speakability"]] += 1

        output = {
            "run_date": ymd,
            "counts": counts,
            "verdicts": results
        }

        # Save artifacts
        self.output_json.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        self._export_markdown(output)

        return output

    def _decide_speakability(self, topic: Dict[str, Any], quality: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decision Rules:
        1) Anchor: STRONG or (FACT-FIRST & >= 1 verified fact)
        2) Timing: EARLY or ON_TIME (NOT LATE)
        3) Fit: narrative_fit != LOW (POOR) & hypothesis_confidence != LOW
        4) Risk: No HARD_RISK flags & ceiling does NOT block narration
        5) Visibility: In TODAY TOPIC VIEW & quality_review exists
        """
        blocking_reasons = []
        basis = {
            "anchor": quality.get("fact_anchor", "UNKNOWN"),
            "timing": quality.get("timing_edge", "UNKNOWN"),
            "fit": quality.get("narration_fit", "UNKNOWN"),
            "risk": "CLEAR"
        }

        # 1. Fact Anchor
        anchor_strength = quality.get("fact_anchor")
        lane = topic.get("lane")
        is_fact_first = lane == "FACT_FIRST"
        evidence_cnt = topic.get("evidence_count", 0)

        anchor_ok = (anchor_strength == "STRONG") or (is_fact_first and evidence_cnt >= 1)
        if not anchor_ok:
            blocking_reasons.append("INSUFFICIENT_ANCHOR_STRENGTH")

        # 2. Timing
        timing_state = quality.get("timing_edge")
        timing_ok = timing_state in ["EARLY", "ON_TIME"]
        if not timing_ok:
            blocking_reasons.append("TIMING_INVALID_OR_LATE")

        # 3. Narrative Fit
        fit_state = quality.get("narration_fit")
        # hypothesis_confidence checked if available in topic or quality
        # TopicQualityReview doesn't explicitly store hypothesis_confidence yet, but let's check flags
        flags = topic.get("flags", [])
        fit_ok = (fit_state != "POOR") and ("WEAK_HYPOTHESIS" not in flags)
        if not fit_ok:
            blocking_reasons.append("LOW_NARRATIVE_FIT")

        # 4. Risk Ceiling
        hard_risk = any("RISK" in f for f in flags)
        ceiling = topic.get("ceiling", "(no ceiling)")
        # If ceiling contains "block", it might be blocking.
        # Rules say: "ceiling does NOT block narration at current level"
        # Narrative ceiling is usually "Industry sector linkage..." etc for Level 1.
        # Logic: If it has a ceiling that says "NOT SPEAKABLE" or "INSUFFICIENT", block?
        # Actually, "narration_ceiling" text like "Evidence insufficient" is a block.
        ceiling_blocks = "NOT SPEAKABLE" in ceiling or "insufficient" in ceiling.lower()
        
        if hard_risk:
            blocking_reasons.append("HARD_RISK_DETECTED")
            basis["risk"] = "HARD_RISK"
        if ceiling_blocks:
            blocking_reasons.append("CEILING_BLOCKS_NARRATION")
            basis["risk"] = "CEILING_HIT"

        # 5. Visibility Readiness
        if not quality:
            blocking_reasons.append("QUALITY_REVIEW_MISSING")

        speakable = self.SPEAKABLE_NOW if not blocking_reasons else self.NOT_SPEAKABLE_YET

        return {
            "topic_id": topic.get("topic_id", "unknown"),
            "title": topic.get("title", "Untitled"),
            "speakability": speakable,
            "blocking_reasons": blocking_reasons,
            "decision_basis": basis
        }

    def _export_markdown(self, data: Dict[str, Any]):
        ymd = data["run_date"]
        lines = [f"# EDITORIAL SPEAKABILITY GATE (RUN_DATE: {ymd})", ""]
        
        c = data["counts"]
        lines.append(f"**SUMMARY**: 🟢 SPEAKABLE_NOW={c[self.SPEAKABLE_NOW]} | ⚪ NOT_SPEAKABLE_YET={c[self.NOT_SPEAKABLE_YET]}")
        lines.append("")

        for v in data["verdicts"]:
            status_icon = "🟢" if v["speakability"] == self.SPEAKABLE_NOW else "⚪"
            lines.append(f"## {status_icon} {v['title']} ({v['topic_id']})")
            lines.append(f"- **Speakability**: {v['speakability']}")
            if v["blocking_reasons"]:
                lines.append(f"- **Blocking Reasons**: {', '.join(v['blocking_reasons'])}")
            
            b = v["decision_basis"]
            lines.append("- **Decision Basis**:")
            lines.append(f"  - Anchor: {b['anchor']}")
            lines.append(f"  - Timing: {b['timing']}")
            lines.append(f"  - Fit: {b['fit']}")
            lines.append(f"  - Risk: {b['risk']}")
            lines.append("")

        self.output_md.write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    # Smoke test
    gate = EditorialSpeakabilityGate(Path("."))
    gate.run(datetime.now().strftime("%Y-%m-%d"))
