#!/usr/bin/env python3
"""
STEP-18: Narrative Propagation Engine
Predicts how market topics will spread through various channels.
Scores based on: Narrative Strength + Media Compatibility + Social Spread + Market Sensitivity.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("NarrativePropagation")

class NarrativePropagationEngine:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_path = self.base_dir / "data/ops/narrative_propagation.json"

    def _load_json(self, path: Path):
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _calculate_propagation_score(self, topic: Dict, ranking: Dict, regime: Dict) -> Dict[str, Any]:
        """
        Scoring Model (Max 100):
        1. Narrative Strength (30): Based on signal strength and top ranking status.
        2. Media Compatibility (25): Based on why_now text richness.
        3. Social Spread Potential (25): Based on theme's retail appeal.
        4. Market Sensitivity (20): Based on regime alignment.
        """
        # 1. Narrative Strength
        strength_score = 15  # Base
        if topic.get("signal_strength") == "HIGH" or topic.get("prediction_score", 0) > 80:
            strength_score = 30
        
        # 2. Media Compatibility
        reason = topic.get("prediction_reason", topic.get("why_now", ""))
        media_score = 10
        if len(reason) > 50:
            media_score = 25
        elif len(reason) > 20:
            media_score = 18

        # 3. Social Spread Potential
        theme = topic.get("theme", "").lower()
        social_score = 15
        if any(k in theme for k in ["crypto", "ai", "nvidia", "코인", "반도체"]):
            social_score = 25
        elif any(k in theme for k in ["shock", "war", "전쟁", "긴급"]):
            social_score = 22

        # 4. Market Sensitivity
        regime_alignment = 10
        current_regime = regime.get("current_regime", "").lower()
        if any(k in current_regime for k in ["긴축", "유동성", "tightening"]):
            regime_alignment = 20
        
        total_score = round(strength_score + media_score + social_score + regime_alignment, 2)
        
        return {
            "total_score": min(total_score, 100),
            "breakdown": {
                "narrative_strength": strength_score,
                "media_compatibility": media_score,
                "social_spread": social_score,
                "market_sensitivity": regime_alignment
            }
        }

    def _analyze_channels(self, score: float, theme: str) -> List[Dict]:
        channels = [
            {"channel": "News Media", "probability": 0.5, "speed": "MEDIUM"},
            {"channel": "YouTube / Video", "probability": 0.4, "speed": "MEDIUM"},
            {"channel": "Social Media", "probability": 0.3, "speed": "FAST"},
            {"channel": "Institutional Research", "probability": 0.2, "speed": "SLOW"}
        ]
        
        theme_l = theme.lower()
        for ch in channels:
            # Adjust probabilities based on score and theme
            ch["probability"] = min(ch["probability"] * (score / 60), 0.95)
            
            if ch["channel"] == "News Media" and any(k in theme_l for k in ["policy", "reg", "정부"]):
                ch["probability"] += 0.2
                ch["speed"] = "FAST"
            if ch["channel"] == "YouTube / Video" and any(k in theme_l for k in ["ai", "crypto", "반도체"]):
                ch["probability"] += 0.3
                ch["speed"] = "FAST"
            if ch["channel"] == "Social Media" and any(k in theme_l for k in ["shock", "vix", "공포"]):
                ch["probability"] += 0.4
                ch["speed"] = "INSTANT"

        return sorted(channels, key=lambda x: x["probability"], reverse=True)

    def run(self):
        logger.info("Running Narrative Propagation Engine...")
        
        # Load inputs
        predictions = self._load_json(self.base_dir / "data/ops/topic_predictions.json")
        radar = self._load_json(self.base_dir / "data/ops/economic_hunter_radar.json")
        regime = self._load_json(self.base_dir / "data/ops/regime_state.json")
        
        # Collect topics from predictions primarily
        topics_to_analyze = []
        if predictions and "predictions" in predictions:
            topics_to_analyze.extend(predictions["predictions"])
        
        if not topics_to_analyze and radar:
            # Fallback to radar if no predictions
            topics_to_analyze.extend(radar.get("radar_candidates", [])[:3])

        propagation_results = []
        for topic in topics_to_analyze:
            p_score_data = self._calculate_propagation_score(topic, {}, regime or {})
            score = p_score_data["total_score"]
            channels = self._analyze_channels(score, topic.get("theme", "Unknown"))
            
            result = {
                "topic_id": topic.get("topic_id", topic.get("signal_id")),
                "theme": topic.get("theme", "Unknown"),
                "propagation_score": score,
                "spread_channels": [c["channel"] for c in channels if c["probability"] > 0.5],
                "detailed_channels": channels,
                "spread_speed": "FAST" if any(c["speed"] == "FAST" for c in channels[:2]) else "MEDIUM",
                "market_sensitivity": "HIGH" if score > 80 else "MEDIUM",
                "score_breakdown": p_score_data["breakdown"]
            }
            propagation_results.append(result)

        # Sort and Save
        propagation_results.sort(key=lambda x: x["propagation_score"], reverse=True)
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "results": propagation_results
            }, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Generated propagation analysis for {len(propagation_results)} topics.")

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    engine = NarrativePropagationEngine(base_dir)
    engine.run()

if __name__ == "__main__":
    main()
