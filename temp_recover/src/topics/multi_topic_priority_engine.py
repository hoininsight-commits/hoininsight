import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class MultiTopicPriorityEngine:
    """
    [IS-107] Multi-Topic Priority Engine
    Categorizes topics into LONG (TIER-1) and SHORT (TIER-2) roles.
    """
    
    AXIS_MAPPING = {
        "KR_POLICY": "POLICY",
        "FLOW_ROTATION": "CAPITAL",
        "RELATIONSHIP_BREAK_RISK": "RELATIONSHIP",
        "EARNINGS_VERIFY": "EARNINGS",
        "US_MA_RUMOR": "CAPITAL",
        "MACRO_SHOCK": "SCHEDULE",
        "STRUCTURAL_ROUTE_FIXATION": "STRUCTURAL"
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.decision_dir = base_dir / "data" / "decision"
        self.logger = logging.getLogger("MultiTopicPriorityEngine")

    def load_json(self, path: Path) -> Any:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def run(self):
        # 1. Load Inputs
        units = self.load_json(self.decision_dir / "interpretation_units.json")
        citations = self.load_json(self.decision_dir / "evidence_citations.json")

        if not isinstance(units, list): units = []
        if not isinstance(citations, list): citations = []

        # 2. Categorize and Filter
        long_candidate = None
        short_candidates = []

        # Sort by confidence just in case we need a tie-breaker, but rules are primary
        units.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)

        for u in units:
            tags = u.get("evidence_tags", [])
            axes = set()
            for t in tags:
                if t in self.AXIS_MAPPING:
                    axes.add(self.AXIS_MAPPING[t])
            
            # Special check for interpretation_key/theme
            key = (u.get("interpretation_key") or "") + "_" + (u.get("theme") or "")
            for tag, axis in self.AXIS_MAPPING.items():
                if tag in key:
                    axes.add(axis)

            has_why_now = len(u.get("why_now", [])) > 0 or u.get("why_now_type") is not None
            has_numbers = self._check_numbers(u, citations)

            # TIER-1 (LONG) Rule
            # 1. Structural/Capital/Relationship signal
            # 2. Why Now trigger exists
            # 3. Overlap of at least 2 Axes
            if not long_candidate:
                if any(a in axes for a in ["STRUCTURAL", "CAPITAL", "RELATIONSHIP"]) and \
                   has_why_now and \
                   len(axes) >= 2:
                    long_candidate = {
                        "topic_id": u.get("interpretation_id"),
                        "title": u.get("structural_narrative", "제목 없음")[:50] + "...",
                        "axes": list(axes),
                        "confidence": u.get("confidence_score", 0.0)
                    }
                    continue

            # TIER-2 (SHORT) Rule
            # 1. At least 1 axis
            # 2. Must have numbers/evidence
            if has_numbers and len(axes) >= 1:
                short_candidates.append({
                    "topic_id": u.get("interpretation_id"),
                    "title": u.get("structural_narrative", "제목 없음")[:50] + "...",
                    "axes": list(axes),
                    "confidence": u.get("confidence_score", 0.0)
                })

        # Final Priority Result
        priority = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "long": long_candidate,
            "shorts": short_candidates[:4], # Limit to 4 for UI stability but logic handles any
            "metadata": {
                "total_candidates": len(units),
                "engine_version": "is107_v1"
            }
        }

        # 3. Save Asset
        output_path = self.decision_dir / "multi_topic_priority.json"
        output_path.write_text(json.dumps(priority, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[PRIORITY] Generated {output_path}")

    def _check_numbers(self, unit: Dict, citations: List) -> bool:
        # Check narrative or why_now
        texts = [unit.get("structural_narrative", "")] + unit.get("why_now", [])
        for t in texts:
            if re.search(r'\d', t):
                return True
        
        # Check citations
        tid = unit.get("interpretation_id")
        topic_citations = next((c for c in citations if c.get("topic_id") == tid), None)
        if topic_citations:
            for c in topic_citations.get("citations", []):
                for s in c.get("sources", []):
                    if re.search(r'\d', s):
                        return True
        
        # Check metrics
        metrics = unit.get("derived_metrics_snapshot", {})
        if isinstance(metrics, dict) and metrics:
            return True # If snapshot exists, it usually contains numbers

        return False

if __name__ == "__main__":
    engine = MultiTopicPriorityEngine(Path("."))
    engine.run()
