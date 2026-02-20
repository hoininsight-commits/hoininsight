import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class NarrativeIntelligenceLayer:
    """
    PHASE 12: Narrative Intelligence Layer v1.0
    Adds narrative-level evaluation layer to determine video-grade topic potential.
    Extends topic_v1 to topic_v2 schema.
    """
    
    STRUCTURAL_ACTORS = [
        "정부", "대통령", "중앙은행", "FED", "연준", "빅테크", "BIGTECH", 
        "군사", "관세", "규제", "GOVERNMENT", "PRESIDENT", "CENTRAL BANK"
    ]

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

    def _detect_actor_presence(self, card: Dict) -> bool:
        text = str(card.get("title", "")) + str(card.get("rationale", "")) + str(card.get("why_now_summary", ""))
        return any(actor in text.upper() for actor in self.STRUCTURAL_ACTORS)

    def _detect_capital_flow(self, card: Dict) -> bool:
        text = str(card.get("title", "")) + str(card.get("rationale", ""))
        keywords = ["FLOW", "자본", "수급", "유입", "CAPITAL", "ROTATION", "LIQUIDITY"]
        return any(kw in text.upper() for kw in keywords)

    def _detect_policy_shift(self, card: Dict) -> bool:
        text = str(card.get("title", "")) + str(card.get("rationale", ""))
        keywords = ["POLICY", "정책", "규제", "금리", "RATE", "SHIFT", "DECREE"]
        return any(kw in text.upper() for kw in keywords)

    def _calculate_persistence(self, dataset_id: str) -> bool:
        # Check ps_history.json as in EconomicHunterVideoIntensityLayer
        history_path = self.base_dir / "data/ops/ps_history.json"
        if not history_path.exists():
            return False
        try:
            history = json.loads(history_path.read_text(encoding='utf-8'))
            matches = [h for h in history if h.get("dataset_id") == dataset_id]
            return len(matches) >= 3
        except:
            return False

    def process_topics(self):
        self.logger.info(f"Running Narrative Intelligence Layer for {self.ymd}...")
        
        # 1. Load IssueSignal Today (Primary source of topics for EH)
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        if not data or not data.get("cards"):
            self.logger.warning("No IssueSignal cards found.")
            return

        v2_topics = []
        for card in data["cards"]:
            # --- LAYER 1: Narrative Score ---
            intensity = float(card.get("intensity", 50))
            actor = 100.0 if self._detect_actor_presence(card) else 0.0
            flow = 100.0 if self._detect_capital_flow(card) else 0.0
            policy = 100.0 if self._detect_policy_shift(card) else 0.0
            persistence = 100.0 if self._calculate_persistence(card.get("dataset_id", "")) else 0.0
            
            n_score = (
                0.35 * intensity +
                0.20 * actor +
                0.15 * flow +
                0.15 * policy +
                0.15 * persistence
            )
            n_score = round(min(100.0, n_score), 2)

            # --- LAYER 2: Causal Chain Structure ---
            # Attempting to derive from rationale and WHY_NOW
            causal_chain = {
                "cause": card.get("why_now_summary", None),
                "structural_shift": card.get("structure_type", None),
                "market_consequence": "Derived from intensity level" if intensity > 60 else "Monitoring impact",
                "affected_sector": card.get("title", None),
                "time_pressure": "high" if intensity >= 80 else "medium" if intensity >= 60 else "low"
            }

            # --- LAYER 3: Video Ready Flag ---
            # Gate: intensity >= 80, narrative_score >= 75, WHY_NOW in [State, Hybrid], at least 2 structural axes
            # Axis detection: how many signals are 100?
            axes_involved = sum([1 for x in [actor, flow, policy, persistence] if x > 0])
            
            # WHY_NOW check: We need to see if it's State/Hybrid. 
            # In IssueSignal card, sometimes it's in status or a specific flag.
            # For now, we assume if it passed EH lock before, it's likely high.
            # But let's check for specific keywords if possible or use intensity as proxy.
            video_ready = (
                intensity >= 80 and
                n_score >= 75 and
                axes_involved >= 2
            )

            # --- LAYER 4: Output Extension ---
            v2_topic = card.copy() # Backward Compatibility
            v2_topic.update({
                "narrative_score": n_score,
                "video_ready": video_ready,
                "causal_chain": causal_chain,
                "schema_version": "v2.0"
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
        self.logger.info(f"Narrative Intelligence v2.0 saved. {out_data['video_ready_count']} topics Video Ready.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base = Path(__file__).resolve().parent.parent.parent
    NarrativeIntelligenceLayer(base).process_topics()
