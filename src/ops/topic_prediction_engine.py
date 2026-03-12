#!/usr/bin/env python3
"""
STEP-17: Economic Hunter Topic Prediction Engine
Predicts future market topics before they become mainstream news.
Scores based on: Radar Strength + Probability Trend + Regime Alignment + Narrative Potential.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("TopicPrediction")

class TopicPredictionEngine:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_path = self.base_dir / "data/ops/topic_predictions.json"

    def _load_json(self, path: Path):
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _calculate_prediction_score(self, signal: Dict, ranking: Dict, regime: Dict) -> Dict[str, Any]:
        """
        Calculation Model (Max 100):
        1. Radar Strength (30): 10 (LOW), 20 (MEDIUM), 30 (HIGH)
        2. Probability Score (30): Normalized to 30.
        3. Regime Alignment (20): Based on context match.
        4. Narrative Potential (20): Default for new signals.
        """
        # 1. Radar Strength
        strength_map = {"HIGH": 30, "MEDIUM": 20, "LOW": 10}
        radar_score = strength_map.get(signal.get("signal_strength", "LOW"), 10)

        # 2. Probability Score
        p_score_raw = ranking.get("probability_score", 50)
        prob_score = (p_score_raw / 100) * 30

        # 3. Regime Alignment
        current_regime = regime.get("current_regime", "").lower()
        theme = signal.get("theme", "").lower()
        regime_alignment = 10  # Base
        if ("긴축" in current_regime or "tightening" in current_regime) and ("inflation" in theme or "macro" in theme):
            regime_alignment = 20
        elif ("ai" in theme or "semiconductor" in theme):
            regime_alignment = 18

        # 4. Narrative Potential
        narrative_potential = 18 # High potential for radar signals

        total_score = round(radar_score + prob_score + regime_alignment + narrative_potential, 2)
        
        return {
            "total_score": total_score,
            "breakdown": {
                "radar": radar_score,
                "probability": prob_score,
                "regime": regime_alignment,
                "narrative": narrative_potential
            }
        }

    def run(self):
        logger.info("Running Topic Prediction Engine...")
        
        # 1. Load Inputs
        radar_data = self._load_json(self.base_dir / "data/ops/economic_hunter_radar.json")
        ranking_data = self._load_json(self.base_dir / "data/ops/topic_probability_ranking.json")
        regime_data = self._load_json(self.base_dir / "data/ops/regime_state.json")
        
        if not radar_data or not ranking_data:
            logger.error("Missing required input data for prediction.")
            return

        signals = radar_data.get("radar_candidates", []) # Fixed key name
        rankings = ranking_data.get("ranked_candidates", [])
        top_ranking = ranking_data.get("top_topic_probability", {})
        
        # Merge rankings for lookup
        ranking_map = {r["signal_id"]: r for r in rankings}
        if top_ranking:
            ranking_map[top_ranking["signal_id"]] = top_ranking

        predictions = []
        for i, signal in enumerate(signals):
            signal_id = signal.get("signal_id")
            ranking = ranking_map.get(signal_id, {"probability_score": 50})
            
            p_result = self._calculate_prediction_score(signal, ranking, regime_data or {})
            
            prediction = {
                "topic_id": f"PRED_{datetime.now().strftime('%Y%m%d')}_{i+1:02d}",
                "theme": signal.get("theme", "Unknown"),
                "prediction_score": p_result["total_score"],
                "prediction_reason": f"{signal.get('theme')} Momentum + {p_result['breakdown']['regime']} Regime Alignment",
                "expected_market_impact": f"{signal.get('theme')} volatility acceleration expected",
                "expected_sector": self._detect_sector(signal.get("theme", "")),
                "breakdown": p_result["breakdown"]
            }
            predictions.append(prediction)

        # Sort and take Top 3
        predictions.sort(key=lambda x: x["prediction_score"], reverse=True)
        top_predictions = predictions[:3]

        # Save to ops
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump({"generated_at": datetime.now().isoformat(), "predictions": top_predictions}, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated {len(top_predictions)} predictions.")

        # Generate Predictive Narrative for score > 85
        high_score_predictions = [p for p in top_predictions if p["prediction_score"] > 85]
        if high_score_predictions:
            self._save_predictive_narratives(high_score_predictions)

    def _detect_sector(self, theme: str) -> str:
        theme = theme.lower()
        if "semiconductor" in theme or "chip" in theme or "ai" in theme:
            return "Semiconductors"
        if "inflation" in theme or "macro" in theme or "금리" in theme:
            return "Financials"
        if "energy" in theme or "oil" in theme:
            return "Energy"
        if "policy" in theme or "reg":
            return "Infrastructure"
        return "Broad Market"

    def _save_predictive_narratives(self, high_score_preds: List[Dict]):
        narrative_path = self.base_dir / "data/decision/predicted_narratives.json"
        
        narratives = []
        for p in high_score_preds:
            narratives.append({
                "topic_id": p["topic_id"],
                "theme": p["theme"],
                "narrative": f"예측 시그널: {p['theme']} 분야의 모멘텀이 강화되고 있습니다. {p['prediction_reason']}에 따라 단기 변동성이 확대될 것으로 보이며, {p['expected_sector']} 섹터 중심의 대응이 필요합니다."
            })
        
        with open(narrative_path, "w", encoding="utf-8") as f:
            json.dump({"generated_at": datetime.now().isoformat(), "narratives": narratives}, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(narratives)} predictive narratives.")

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    engine = TopicPredictionEngine(base_dir)
    engine.run()

if __name__ == "__main__":
    main()
