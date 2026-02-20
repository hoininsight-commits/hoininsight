import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class NarrativeIntelligenceLayer:
    """
    PHASE 12.5: Narrative Score Precision Refinement
    Refines narrative evaluation with actor tiers, multipliers, and escalation bonuses.
    """
    
    TIER_1_ACTORS = ["FEDERAL RESERVE", "FED", "연준", "IMF", "BIS", "중앙은행", "CENTRAL BANK", "G7", "정부"]
    TIER_2_ACTORS = ["BIG TECH", "빅테크", "APPLE", "MICROSOFT", "GOOGLE", "AMAZON", "META", "NVIDIA", "JPMORGAN", "GS", "HSBC", "BOFA", "CITI", "SOVEREIGN WEALTH FUND"]
    TIER_3_ACTORS = ["MINISTRY", "기획재정부", "산업통상자원부", "국토교통부", "삼성전자", "SAMSUNG", "HYUNDAI", "현대차", "SK", "LG"]
    TIER_4_ACTORS = ["CORPORATION", "COMPANY", "기업", "업체"]

    AXES_KEYWORDS = {
        "Policy": ["POLICY", "정책", "규제", "DECREE", "GOV"],
        "Capital Flow": ["FLOW", "자본", "수급", "유입", "CAPITAL", "LIQUIDITY", "ROTATION"],
        "Supply Chain": ["CHAIN", "SUPPLY", "공급망", "물류", "SEMICONDUCTOR", "CHIP"],
        "Structural Capital": ["STRUCTURAL", "구조적", "ASSET", "CAPITAL", "EQUITY"],
        "Liquidity": ["LIQUIDITY", "유동성", "M2", "MONEY"],
        "Geopolitical": ["GEOPOLITICAL", "지정학", "WAR", "군사", "TENSION", "CONFLICT"]
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("NarrativeIntelligenceLayer")
        self.ymd = datetime.now().strftime("%Y-%m-%d")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return None

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def _get_actor_tier_score(self, card: Dict) -> float:
        text = str(card.get("title", "")) + str(card.get("rationale_natural", "")) + str(card.get("why_now_summary", ""))
        text_up = text.upper()
        
        if any(actor in text_up for actor in self.TIER_1_ACTORS): return 1.00
        if any(actor in text_up for actor in self.TIER_2_ACTORS): return 0.90
        if any(actor in text_up for actor in self.TIER_3_ACTORS): return 0.75
        if any(actor in text_up for actor in self.TIER_4_ACTORS): return 0.55
        
        return 0.0

    def _get_cross_axis_metrics(self, card: Dict) -> Tuple[int, float]:
        text = (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper()
        count = 0
        for axis, keywords in self.AXES_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                count += 1
        
        multiplier = 1.0
        if count >= 3:
            multiplier = 1.15
        elif count >= 2:
            multiplier = 1.08
            
        return count, multiplier

    def _check_escalation(self, card: Dict) -> bool:
        dataset_id = card.get("dataset_id", "")
        intensity = float(card.get("intensity", 0))
        
        history_path = self.base_dir / "data/ops/ps_history.json"
        if not history_path.exists():
            return False
            
        try:
            history = json.loads(history_path.read_text(encoding='utf-8'))
            matches = [h for h in history if h.get("dataset_id") == dataset_id]
            matches.sort(key=lambda x: x.get("ts_utc", ""), reverse=True)
            
            # Rule 1: intensity increase for 2 consecutive days
            if len(matches) >= 2:
                recent_intensities = [float(matches[0].get("intensity", 0)), float(matches[1].get("intensity", 0))]
                if intensity > recent_intensities[0] > recent_intensities[1]:
                    return True
            
            # Rule 2: persistence >= 3 days
            if len(matches) >= 3:
                return True
                
            # Rule 3: intensity delta >= +10 from prior occurrence
            if len(matches) >= 1:
                if intensity >= (float(matches[0].get("intensity", 0)) + 10):
                    return True
                    
        except:
            pass
            
        return False

    def process_topics(self):
        self.logger.info(f"Running Narrative Intelligence Precision Refinement for {self.ymd}...")
        
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        if not data or not data.get("cards"):
            self.logger.warning("No IssueSignal cards found.")
            return

        v2_topics = []
        for card in data["cards"]:
            # --- PHASE 12.5 Scopes ---
            intensity = float(card.get("intensity", 50))
            
            # Step 2: Actor Tier
            actor_tier_score = self._get_actor_tier_score(card)
            
            # Step 3: Cross-Axis
            axis_count, axis_multiplier = self._get_cross_axis_metrics(card)
            
            # Step 4: Escalation
            is_escalated = self._check_escalation(card)
            escalation_bonus = 5.0 if is_escalated else 0.0
            
            # Derived factors for weighted sum
            actor_weight_score = actor_tier_score * 100.0
            
            # Re-using binary detection for simpler weights if precision not needed for every sub-axis
            # Using defaults from Step 1 rules:
            flow_score = 100.0 if any(kw in (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper() for kw in ["FLOW", "자본", "수급", "유입", "CAPITAL", "LIQUIDITY", "ROTATION"]) else 0.0
            policy_score = 100.0 if any(kw in (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper() for kw in ["POLICY", "정책", "규제", "금리", "RATE", "SHIFT", "DECREE"]) else 0.0
            persistence_score = 100.0 if self._check_escalation(card) else 0.0 # Re-using escalation check for persistence
            
            # Step 1 & 5: Revised Score Formula
            base_weighted_sum = (
                0.28 * intensity +
                0.22 * actor_weight_score +
                0.18 * flow_score +
                0.17 * policy_score +
                0.15 * persistence_score
            )
            
            n_score = (base_weighted_sum * axis_multiplier) + escalation_bonus
            n_score = round(min(100.0, max(0.0, n_score)), 2)

            # --- Step 6: Video Ready Logic Adjustment ---
            # Condition A: (narrative_score >= 78 AND intensity >= 75 AND actor_tier_score >= 0.75)
            # Condition B: (escalation_flag == TRUE AND narrative_score >= 72)
            video_ready = (
                (n_score >= 78 and intensity >= 75 and actor_tier_score >= 0.75) or
                (is_escalated and n_score >= 72)
            )

            # Causal Chain (Step 2.0 Maintenance)
            causal_chain = {
                "cause": card.get("why_now_summary", None),
                "structural_shift": card.get("structure_type", None),
                "market_consequence": "Derived from intensity level" if intensity > 60 else "Monitoring impact",
                "affected_sector": card.get("title", None),
                "time_pressure": "high" if intensity >= 80 else "medium" if intensity >= 60 else "low"
            }

            # --- LAYER 4: Output Extension ---
            v2_topic = card.copy()
            v2_topic.update({
                "narrative_score": n_score,
                "video_ready": video_ready,
                "causal_chain": causal_chain,
                "actor_tier_score": actor_tier_score,
                "cross_axis_count": axis_count,
                "cross_axis_multiplier": axis_multiplier,
                "escalation_flag": is_escalated,
                "schema_version": "v2.5"
            })
            v2_topics.append(v2_topic)

        # Save Results
        out_data = {
            "date": self.ymd,
            "total_topics": len(v2_topics),
            "video_ready_count": len([t for t in v2_topics if t["video_ready"]]),
            "topics": v2_topics
        }
        
        out_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        self._save_json(out_path, out_data)
        self.logger.info(f"Narrative Intelligence v2.5 refined. {out_data['video_ready_count']} topics Video Ready.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base = Path(__file__).resolve().parent.parent.parent
    ni = NarrativeIntelligenceLayer(base)
    ni.process_topics()
