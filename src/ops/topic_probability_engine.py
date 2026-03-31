import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class TopicProbabilityEngine:
    """
    Step-11: Topic Probability Engine
    Evaluates Radar signals and assigns a probability score for content conversion.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("TopicProbabilityEngine")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        
    def _load_json(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return {}

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def calculate_probability(self, candidate: Dict, context: Dict) -> Dict:
        """
        Calculates probability_score (0-100) based on 6 factors.
        """
        score = 0
        supporting_factors = []
        risk_factors = []
        
        # 1. Radar Strength (20%)
        strength_map = {"HIGH": 100, "MEDIUM": 70, "LOW": 40}
        strength = candidate.get("signal_strength", "LOW")
        radar_score = strength_map.get(strength, 40)
        score += 0.20 * radar_score
        if radar_score >= 70:
            supporting_factors.append(f"Radar strong signal ({strength})")

        # 2. Why Now (20%)
        why_now_text = candidate.get("why_now", "").lower()
        critical_keywords = ["쇼크", "급락", "돌파", "폭락", "속보", "전쟁", "합병"]
        why_now_score = 50 # Base
        if any(kw in why_now_text for kw in critical_keywords):
            why_now_score = 100
            supporting_factors.append("Critical 'Why Now' keywords detected")
        score += 0.20 * why_now_score

        # 3. Convertibility (20%)
        # Simple heuristic: potential_topic length and clarity
        potential_topic = candidate.get("potential_topic", "")
        convertibility_score = 70 # Default
        if len(potential_topic) > 20:
            convertibility_score = 90
            supporting_factors.append("Rich context for narrative generation")
        score += 0.20 * convertibility_score

        # 4. Mentionable (15%)
        # Check if theme matches known themes in mentionables
        mentionables = context.get("mentionables", [])
        theme = candidate.get("theme", "")
        mentionable_score = 50
        for m in mentionables:
            if any(theme.lower() in str(val).lower() for val in m.values()):
                mentionable_score = 100
                supporting_factors.append(f"Direct alignment with existing mentionables ({theme})")
                break
        if mentionable_score == 50:
            risk_factors.append("No active mentionable linkage found")
        score += 0.15 * mentionable_score

        # 5. Structural Alignment (15%)
        # Matches against Regime/Timing
        regime = context.get("regime", {})
        timing = context.get("timing", {})
        alignment_score = 60 # Base
        
        # Logic: If Macro Shock and Tightening, align
        if "Macro" in theme and regime.get("regime", {}).get("liquidity_state") == "TIGHTENING":
            alignment_score = 100
            supporting_factors.append("Market regime alignment (Tightening & Macro)")
        elif timing.get("timing_gear", {}).get("level", 0) >= 4:
            alignment_score = 90
            supporting_factors.append("High pressure timing synchronicity")
        
        score += 0.15 * alignment_score

        # 6. Evidence Density (10%)
        # Check if topic appears in fact_first lane multiple times or in pool
        density_score = 50
        if "Investing.com" in why_now_text or "연합인포맥스" in why_now_text:
            density_score = 100
            supporting_factors.append("High-authority source density")
        score += 0.10 * density_score

        return {
            "signal_id": candidate.get("signal_id"),
            "theme": candidate.get("theme"),
            "potential_topic": candidate.get("potential_topic"),
            "probability_score": round(score, 1),
            "rank": 0, # Will be set during sorting
            "why_now": candidate.get("why_now"),
            "supporting_factors": supporting_factors,
            "risk_factors": risk_factors
        }

    def run(self):
        self.logger.info(f"Running TopicProbabilityEngine for {self.ymd}...")
        
        # 1. Load Inputs
        radar_path = self.base_dir / "data/ops/economic_hunter_radar.json"
        radar_data = self._load_json(radar_path)
        candidates = radar_data.get("radar_candidates", [])
        
        regime_path = self.base_dir / "data/ops/regime_state.json"
        timing_path = self.base_dir / "data/ops/timing_state.json"
        mentionables_path = self.base_dir / "data/decision/mentionables.json"
        
        context = {
            "regime": self._load_json(regime_path),
            "timing": self._load_json(timing_path),
            "mentionables": self._load_json(mentionables_path)
        }
        
        # 2. Evaluate Candidates
        ranked_candidates = []
        for cand in candidates:
            eval_res = self.calculate_probability(cand, context)
            ranked_candidates.append(eval_res)
            
        # 3. Sort by Score
        ranked_candidates.sort(key=lambda x: x["probability_score"], reverse=True)
        for i, cand in enumerate(ranked_candidates):
            cand["rank"] = i + 1
            
        # 4. Prepare Final Output
        output = {
            "generated_at": datetime.now().isoformat(),
            "top_topic_probability": ranked_candidates[0] if ranked_candidates else None,
            "ranked_candidates": ranked_candidates
        }
        
        output_path = self.base_dir / "data/ops/topic_probability_ranking.json"
        self._save_json(output_path, output)
        self.logger.info(f"Generated ranking with {len(ranked_candidates)} candidates at {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    TopicProbabilityEngine(Path(__file__).resolve().parent.parent.parent).run()
