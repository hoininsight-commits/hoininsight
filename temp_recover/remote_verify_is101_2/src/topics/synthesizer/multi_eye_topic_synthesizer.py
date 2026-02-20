"""
IS-96-7 Multi-Eye Topic Synthesizer
Synthesizes multiple independent signal types into ONE high-conviction topic.
"""
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import List, Dict, Set, Any
from collections import defaultdict

class EyeType(Enum):
    PRICE = "PRICE"
    POLICY = "POLICY"
    CAPITAL = "CAPITAL"
    LABOR = "LABOR"
    AUTHORITY = "AUTHORITY"
    SCHEDULE = "SCHEDULE"
    EVENT = "EVENT"
    UNKNOWN = "UNKNOWN"

class TopicType(Enum):
    STRUCTURAL_SHIFT = "STRUCTURAL_SHIFT"
    REGIME_ACCELERATION = "REGIME_ACCELERATION"
    CAPITAL_REPRICING = "CAPITAL_REPRICING"
    BOTTLENECK_REVEAL = "BOTTLENECK_REVEAL"
    UNKNOWN = "UNKNOWN"

class MultiEyeTopicSynthesizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.decision_dir = self.base_dir / "data" / "decision"

    def map_eye_type(self, unit: Dict[str, Any]) -> EyeType:
        """Determines Eye Type based on interpretation key and tags."""
        key = unit.get("interpretation_key", "")
        tags = unit.get("evidence_tags", [])
        
        if key == "PRICE_MECHANISM_SHIFT" or "PRICE_RIGIDITY" in tags:
            return EyeType.PRICE
        if "LABOR_SHIFT" in key or "LABOR" in tags:
            return EyeType.LABOR
        if "POLICY" in tags or "KR_POLICY" in tags:
            return EyeType.POLICY
        if "CAPITAL" in tags or "CAPEX" in tags or "ETF" in tags:
            return EyeType.CAPITAL
        if "AUTHORITY" in tags or "CEO" in tags:
            return EyeType.AUTHORITY
        if "SCHEDULE" in tags or "EARNINGS" in tags or "IPO" in tags:
            return EyeType.SCHEDULE
        if "EVENT" in tags or "MERGER" in tags:
            return EyeType.EVENT
            
        # Fallback based on content (simplification)
        return EyeType.UNKNOWN

    def classify_topic(self, eyes: Set[EyeType]) -> TopicType:
        """Classifies the synthesized topic based on Eye composition."""
        if {EyeType.PRICE, EyeType.LABOR, EyeType.POLICY}.issubset(eyes):
            return TopicType.STRUCTURAL_SHIFT
        if {EyeType.AUTHORITY, EyeType.SCHEDULE, EyeType.CAPITAL}.issubset(eyes):
            return TopicType.REGIME_ACCELERATION
        if {EyeType.PRICE, EyeType.CAPITAL, EyeType.EVENT}.issubset(eyes):
            return TopicType.CAPITAL_REPRICING
        if {EyeType.PRICE, EyeType.AUTHORITY, EyeType.LABOR}.issubset(eyes):
            return TopicType.BOTTLENECK_REVEAL
            
        # Default logic
        if EyeType.PRICE in eyes and EyeType.POLICY in eyes:
            return TopicType.STRUCTURAL_SHIFT
            
        return TopicType.UNKNOWN

    def synthesize(self):
        # Load Units
        in_path = self.decision_dir / "interpretation_units.json"
        if not in_path.exists():
            print("[SYNTHESIZER] No input file.")
            return

        try:
            units = json.loads(in_path.read_text())
        except Exception as e:
            print(f"[SYNTHESIZER] Load error: {e}")
            return

        # Group by Sector
        groups = defaultdict(list)
        for u in units:
            sector = u.get("target_sector", "UNKNOWN")
            groups[sector].append(u)

        synthesized_topics = []
        
        for sector, group_units in groups.items():
            eyes_present = set()
            eye_details = {}  # One detail per eye for Why-Now
            
            for u in group_units:
                eye = self.map_eye_type(u)
                if eye != EyeType.UNKNOWN:
                    eyes_present.add(eye)
                    # Pick best detail (simplification: last one)
                    eye_details[eye.value] = u.get("structural_narrative", "No detail")

            unique_eyes_count = len(eyes_present)
            
            # Gating Rule: Min 3 Eyes
            if unique_eyes_count >= 3:
                topic_type = self.classify_topic(eyes_present)
                
                # Construct Topic
                topic = {
                    "topic_id": f"SYNTH-{datetime.now().strftime('%Y%m%d')}-{sector}",
                    "sector": sector,
                    "topic_type": topic_type.value,
                    "confidence_score": 0.8 + (unique_eyes_count * 0.05), # Base 0.8 for surviving the gate
                    "eyes_used": [e.value for e in eyes_present],
                    "dominant_eye": EyeType.PRICE.value if EyeType.PRICE in eyes_present else list(eyes_present)[0].value,
                    "why_now_bundle": {
                        "why_now_1": eye_details.get("PRICE", list(eye_details.values())[0]),
                        "why_now_2": eye_details.get("POLICY", list(eye_details.values())[1] if len(eye_details)>1 else ""),
                        "why_now_3": f"Confluence of {unique_eyes_count} structural signals."
                    },
                    "source_units": [u.get("interpretation_id") for u in group_units]
                }
                synthesized_topics.append(topic)
                print(f"[SYNTH] Created Topic for {sector} (Eyes: {topic['eyes_used']})")
            else:
                print(f"[SYNTH] Dropped {sector} (Only {unique_eyes_count} Eyes: {[e.value for e in eyes_present]})")

        # Save Output
        out_path = self.decision_dir / "synthesized_topics.json"
        with open(out_path, "w") as f:
            json.dump(synthesized_topics, f, indent=2, ensure_ascii=False)
        print(f"[SYNTH] Processed {len(groups)} sectors. Survivors: {len(synthesized_topics)}")

if __name__ == "__main__":
    synth = MultiEyeTopicSynthesizer()
    synth.synthesize()
