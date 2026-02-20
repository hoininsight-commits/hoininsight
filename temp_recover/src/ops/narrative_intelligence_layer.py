import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class NarrativeIntelligenceLayer:
    """
    PHASE 12.7: Conflict & Tension Layer v1.0
    Detects structural conflict, expectation gaps, and tension signals.
    Extends TopicV2 to TopicV3.
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

    # Conflict Pattern Keywords
    CONFLICT_KEYWORDS = {
        "Tightening": ["TIGHTENING", "HAWKISH", "RATE HIKE", "금리 인상", "긴축"],
        "Easing": ["EASING", "DOVISH", "RATE CUT", "금리 인하", "완화"],
        "Inflow": ["INFLOW", "유입", "매수", "BUY", "SURGE"],
        "Drain": ["DRAIN", "OUTFLOW", "유출", "매도", "SELL", "DROP"],
        "SupplyExp": ["SUPPLY EXPANSION", "생산 확대", "증설", "CAPEX"],
        "DemandWeak": ["DEMAND WEAKNESS", "수요 둔화", "부진", "WEAK"],
        "StrongEarnings": ["EARNINGS SURPRISE", "어닝 서프라이즈", "실적 호조", "PROFIT"],
        "PriceDecline": ["PRICE DECLINE", "하락", "폭락", "CRASH", "BEAR"],
        "RegPressure": ["REGULATION", "규제", "압박", "제재", "BAN"],
        "InvSurge": ["INVESTMENT", "투자", "유치", "유입"],
        "GeoRisk": ["WAR", "CONFLICT", "전쟁", "분쟁", "RISK"],
        "AssetRally": ["RALLY", "상승", "급등", "BULL", "SURGE"]
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

    def _get_history(self, dataset_id: str) -> List[Dict]:
        history_path = self.base_dir / "data/ops/ps_history.json"
        if not history_path.exists():
            return []
        try:
            history = json.loads(history_path.read_text(encoding='utf-8'))
            matches = [h for h in history if h.get("dataset_id") == dataset_id]
            matches.sort(key=lambda x: x.get("ts_utc", ""), reverse=True)
            return matches
        except:
            return []

    def _check_escalation(self, card: Dict, matches: List[Dict]) -> bool:
        intensity = float(card.get("intensity", 0))
        if not matches:
            return False
            
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
                    
        return False

    def _detect_conflict(self, card: Dict, matches: List[Dict], is_escalated: bool) -> bool:
        text = (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper()
        intensity = float(card.get("intensity", 50))
        
        def has(keys): return any(k in text for k in self.CONFLICT_KEYWORDS[keys])

        patterns = [
            has("Tightening") and has("Inflow"),                          # 1
            has("Easing") and has("Drain"),                               # 2
            has("SupplyExp") and has("DemandWeak"),                       # 3
            has("StrongEarnings") and has("PriceDecline"),                # 4
            has("RegPressure") and has("InvSurge"),                       # 5
            has("GeoRisk") and has("AssetRally")                          # 6
        ]
        
        # 7. High Persistence (count >= 3) + Sudden Intensity Drop (delta <= -15)
        if len(matches) >= 3:
            last_intensity = float(matches[0].get("intensity", 0))
            if intensity <= (last_intensity - 15):
                patterns.append(True)
                
        # 8. Low Intensity + Escalation Flag True
        if intensity < 50 and is_escalated:
            patterns.append(True)
            
        return any(patterns)

    def _get_expectation_gap(self, card: Dict, matches: List[Dict], n_score_jump: float) -> Tuple[int, str]:
        intensity = float(card.get("intensity", 50))
        
        # Calculate scores
        gap_score = 0
        
        if matches:
            # delta from 7-day avg (if history long enough)
            recent_i = [float(m.get("intensity", 0)) for m in matches[:7]]
            avg_i = sum(recent_i) / len(recent_i)
            if abs(intensity - avg_i) >= 15: gap_score += 2
            
            # jump >= +12
            if intensity >= (float(matches[0].get("intensity", 0)) + 12): gap_score += 2
            
            # persistence >= 3 with sudden shift (delta >= 10 in either direction)
            if len(matches) >= 3 and abs(intensity - float(matches[0].get("intensity", 0))) >= 10:
                gap_score += 2
                
        # n_score_jump >= +10
        if n_score_jump >= 10: gap_score += 1
        
        level = "none"
        if gap_score >= 6: level = "strong"
        elif gap_score >= 3: level = "moderate"
        
        return gap_score, level

    def process_topics(self):
        self.logger.info(f"Running Narrative Intelligence Phase 12.7 (Conflict & Tension) for {self.ymd}...")
        
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        if not data or not data.get("cards"):
            self.logger.warning("No IssueSignal cards found.")
            return

        v3_topics = []
        for card in data["cards"]:
            intensity = float(card.get("intensity", 50))
            matches = self._get_history(card.get("dataset_id", ""))
            
            # --- Base Metrics (PHASE 12.5) ---
            actor_tier_score = self._get_actor_tier_score(card)
            axis_count, axis_multiplier = self._get_cross_axis_metrics(card)
            is_escalated = self._check_escalation(card, matches)
            escalation_bonus = 5.0 if is_escalated else 0.0
            
            # Derived factors
            actor_weight_score = actor_tier_score * 100.0
            flow_score = 100.0 if any(kw in (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper() for kw in ["FLOW", "자본", "수급", "유입", "CAPITAL", "LIQUIDITY", "ROTATION"]) else 0.0
            policy_score = 100.0 if any(kw in (str(card.get("title", "")) + str(card.get("rationale_natural", ""))).upper() for kw in ["POLICY", "정책", "규제", "금리", "RATE", "SHIFT", "DECREE"]) else 0.0
            persistence_score = 100.0 if is_escalated else 0.0
            
            base_weighted_sum = (
                0.28 * intensity +
                0.22 * actor_weight_score +
                0.18 * flow_score +
                0.17 * policy_score +
                0.15 * persistence_score
            )
            
            # Intermediate n_score for jump calculation?
            # Requirement says "Narrative_score jump >= +10". We compare with last recorded n_score in history.
            last_n_score = float(matches[0].get("narrative_score", 0)) if matches else 0.0
            pre_multiplier_score = (base_weighted_sum * axis_multiplier) + escalation_bonus
            n_score_jump = pre_multiplier_score - last_n_score if matches else 0.0

            # --- PHASE 12.7 Scopes ---
            # Step 1: Conflict Flag
            conflict_flag = self._detect_conflict(card, matches, is_escalated)
            
            # Step 2: Expectation Gap
            gap_score, gap_level = self._get_expectation_gap(card, matches, n_score_jump)
            
            # Step 3: Tension Multiplier
            tension_mult = 1.12 if conflict_flag else 1.0
            final_n_score = pre_multiplier_score * tension_mult
            if gap_level == "strong":
                final_n_score += 4.0
            
            final_n_score = round(min(100.0, max(0.0, final_n_score)), 2)

            # --- Step 4: Video Ready Logic Adjustment (v12.7) ---
            video_ready = (
                (final_n_score >= 80 and actor_tier_score >= 0.75) or
                (conflict_flag == True and final_n_score >= 75) or
                (is_escalated == True and gap_level != "none")
            )

            # --- Output Construction (v3.0) ---
            v3_topic = card.copy()
            v3_topic.update({
                "narrative_score": pre_multiplier_score, # Preserve v2 value
                "final_narrative_score": final_n_score,
                "video_ready": video_ready,
                "actor_tier_score": actor_tier_score,
                "cross_axis_count": axis_count,
                "cross_axis_multiplier": axis_multiplier,
                "escalation_flag": is_escalated,
                "conflict_flag": conflict_flag,
                "expectation_gap_score": gap_score,
                "expectation_gap_level": gap_level,
                "tension_multiplier_applied": tension_mult > 1.0 or gap_level == "strong",
                "causal_chain": {
                    "cause": card.get("why_now_summary", None),
                    "structural_shift": card.get("structure_type", None),
                    "market_consequence": "Derived from final_n_score" if final_n_score > 70 else "Monitoring friction",
                    "affected_sector": card.get("title", None),
                    "time_pressure": "high" if intensity >= 80 else "medium" if intensity >= 60 else "low"
                },
                "schema_version": "v3.0"
            })
            v3_topics.append(v3_topic)

        # Save Results
        out_data = {
            "date": self.ymd,
            "total_topics": len(v3_topics),
            "video_ready_count": len([t for t in v3_topics if t["video_ready"]]),
            "topics": v3_topics
        }
        
        out_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        self._save_json(out_path, out_data)
        self.logger.info(f"Narrative Intelligence v3.0 (Conflict/Tension) completed. {out_data['video_ready_count']} topics Video Ready.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base = Path(__file__).resolve().parent.parent.parent
    ni = NarrativeIntelligenceLayer(base)
    ni.process_topics()
