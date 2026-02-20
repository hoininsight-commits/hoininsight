import json
from pathlib import Path
from typing import Any, Dict, List

class ContentSpeakMapBuilder:
    """
    IS-97-1: Content Speak Map Layer
    Deterministically decides content production strategy based on IS-96 outputs.
    """

    def __init__(self, data_dir: str = "data/decision"):
        self.data_dir = Path(data_dir)
        self.output_path = self.data_dir / "content_speak_map.json"

    def _load_json(self, filename: str) -> Any:
        path = self.data_dir / filename
        if not path.exists():
            return {} if filename.endswith(".json") else []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build(self) -> List[Dict[str, Any]]:
        # 1. Load Input Assets
        units = self._load_json("interpretation_units.json")
        decisions = self._load_json("speakability_decision.json")
        skeletons = self._load_json("narrative_skeleton.json")

        speak_maps = []

        # 2. Process each interpretation unit
        for unit in units:
            topic_id = unit.get("interpretation_id", "unknown")
            decision = decisions.get(topic_id, {})
            skeleton = skeletons.get(topic_id, {})
            
            flag = decision.get("speakability_flag", "DROP")
            metrics = unit.get("derived_metrics_snapshot", {})
            tags = unit.get("evidence_tags", [])
            
            # Initialize map entry
            entry = {
                "topic_id": topic_id,
                "speakability": flag,
                "content_mode": "HOLD",
                "content_count": 0,
                "primary_angle": "",
                "supporting_angles": [],
                "why_now_hook": "",
                "blocked_reason": None
            }

            # Rule A: Speakability Binding (DROP)
            if flag == "DROP":
                entry["content_mode"] = "HOLD"
                entry["content_count"] = 0
                entry["blocked_reason"] = skeleton.get("drop_note", "Topic dropped by gate.")
                speak_maps.append(entry)
                continue

            # Rule C: HOLD Routing
            if flag == "HOLD":
                entry["content_mode"] = "HOLD"
                entry["content_count"] = 1
                entry["primary_angle"] = "관찰 중: 트리거 대기"
                entry["supporting_angles"] = [skeleton.get("hold_trigger", "Trigger data pending")]
                entry["why_now_hook"] = unit.get("why_now_type", "Unknown Trigger")
                speak_maps.append(entry)
                continue

            # Rule B: READY Routing
            if flag == "READY":
                pretext_score = metrics.get("pretext_score", 0.0)
                execution_gap = metrics.get("policy_execution_gap", 0.0)
                
                # Default to SHORT
                entry["content_mode"] = "SHORT"
                entry["content_count"] = 1
                
                # Check for LONG condition (Multiple units/sectors or logic-driven)
                # In this deterministic rule, we check for pretext_score and flag
                if pretext_score >= 0.9 and execution_gap <= 0.2:
                    entry["content_mode"] = "LONG" # Upgrade or specify both? 
                    # According to instructions: SHORT + LONG
                    entry["content_count"] = 2
                elif "FLOW_ROTATION" in tags and pretext_score >= 0.85:
                    entry["content_mode"] = "SHORT"
                    entry["content_count"] = 1

                # Rule D: Angle Construction
                entry["primary_angle"] = f"구조적 {unit.get('interpretation_key', 'SHIFT')}: {unit.get('target_sector', 'SECTOR')}"
                entry["supporting_angles"] = skeleton.get("evidence_3", [])
                
                # Why Now Hook
                why_now = unit.get("why_now_type", "Schedule")
                entry["why_now_hook"] = f"{why_now} 기반 {tags[0] if tags else 'DATA'} 변곡점 포착"

            speak_maps.append(entry)

        # 3. Save Output
        self.save(speak_maps)
        return speak_maps

    def save(self, data: List[Dict[str, Any]]):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved Content Speak Map to {self.output_path}")

def run_content_speak_map():
    builder = ContentSpeakMapBuilder()
    return builder.build()

if __name__ == "__main__":
    run_content_speak_map()
