import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class NarrativeEscalationEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("NarrativeEscalation")
        self.output_path = base_dir / "data" / "ops" / "narrative_escalation.json"
        
        # Data Dependencies
        self.early_topics = self._load_json(base_dir / "data" / "ops" / "early_topic_candidates.json")
        self.radar = self._load_json(base_dir / "data" / "ops" / "economic_hunter_radar.json")
        self.predictions = self._load_json(base_dir / "data" / "ops" / "topic_predictions.json")
        self.propagation = self._load_json(base_dir / "data" / "ops" / "narrative_propagation.json")
        self.history = self._load_json(base_dir / "data" / "memory" / "narrative_history.json")
        self.cycles = self._load_json(base_dir / "data" / "memory" / "narrative_cycles.json")
        self.evolution = self._load_json(base_dir / "data" / "memory" / "theme_evolution.json")
        self.resolver_data = self._load_json(base_dir / "data" / "ontology" / "topic_resolved.json")
        
        # 보조 데이터
        self.regime = self._load_json(base_dir / "data" / "ops" / "regime_state.json")
        self.timing = self._load_json(base_dir / "data" / "ops" / "timing_state.json")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            self.logger.warning(f"File not found: {path}")
            return {} if "state" in path.name else []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.error(f"Error loading {path}: {e}")
            return {} if "state" in path.name else []

    def run_analysis(self):
        """Analyzes escalation stages for early topic candidates."""
        escalations = []
        
        if not self.early_topics:
            self.logger.info("No early topics found to escalate.")
            return []

        for candidate in self.early_topics:
            theme = candidate.get("theme")
            early_score = candidate.get("early_topic_score", 0)
            
            # 1. Signal Acceleration (0-20)
            # Simplification: Higher if intensity is HIGH or multiple radar signals
            acc_score = 12
            radar_count = sum(1 for r in self.radar.get("radar_candidates", []) if r.get("theme") == theme)
            if radar_count >= 2: acc_score = 18
            elif radar_count == 1: acc_score = 15

            # 2. Memory Reinforcement (0-15)
            # Use candidate's memory_match_score
            mem_score = min(15, candidate.get("memory_match_score", 0))

            # 3. Cycle Reactivation (0-15)
            # Use candidate's cycle_match_score
            cyc_score = min(15, candidate.get("cycle_match_score", 0))

            # 4. Evolution Alignment (0-15)
            # Use candidate's evolution_match_score
            evo_score = min(15, candidate.get("evolution_match_score", 0))

            # 5. Propagation Growth (0-15)
            # Check narrative_propagation.json for theme alignment
            prop_score = 8
            if isinstance(self.propagation, list):
                prop_item = next((p for p in self.propagation if p.get("theme") == theme), None)
                if prop_item:
                    prop_score = min(15, int(prop_item.get("propagation_score", 50) / 10 * 1.5))

            # 6. Market Alignment (0-10)
            # Use regime/timing alignment
            mkt_score = 7
            if self.regime.get("regime_group") == "STABLE_GROWTH": mkt_score += 2
            if self.timing.get("market_timing") == "OPTIMAL_ENTRY": mkt_score += 1

            # 7. Narrative Potential (0-10)
            pot_score = min(10, candidate.get("narrative_potential_score", 5))

            # Total Escalation Score
            total_score = acc_score + mem_score + cyc_score + evo_score + prop_score + mkt_score + pot_score
            
            # Stage Determination
            if total_score >= 80: stage = "DOMINANT"
            elif total_score >= 60: stage = "ESCALATING"
            elif total_score >= 40: stage = "EMERGING"
            else: stage = "WEAK_SIGNAL"

            # Reasons
            reasons = []
            if acc_score >= 15: reasons.append("Signal acceleration detected in current radar")
            if mem_score >= 12: reasons.append("Strong memory reinforcement from historical patterns")
            if cyc_score >= 12: reasons.append("Cycle reactivation confirmed")
            if evo_score >= 12: reasons.append("Evolution path alignment verified")
            if prop_score >= 12: reasons.append("Propagation potential is rising")

            escalations.append({
                "theme": theme,
                "early_topic_score": early_score,
                "escalation_score": total_score,
                "escalation_stage": stage,
                "signal_acceleration_score": acc_score,
                "memory_reinforcement_score": mem_score,
                "cycle_reactivation_score": cyc_score,
                "evolution_alignment_score": evo_score,
                "propagation_growth_score": prop_score,
                "market_alignment_score": mkt_score,
                "narrative_potential_score": pot_score,
                "why_escalating": reasons,
                "next_escalation_path": candidate.get("next_theme_path", []),
                "confidence": candidate.get("confidence", "MEDIUM")
            })

        # Sort and Save
        escalations.sort(key=lambda x: x["escalation_score"], reverse=True)
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(escalations, indent=2, ensure_ascii=False), encoding="utf-8")
            self.logger.info(f"Narrative Escalation analysis completed for {len(escalations)} candidates.")
        except Exception as e:
            self.logger.error(f"Failed to save escalation data: {e}")

        return escalations

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = NarrativeEscalationEngine(Path("."))
    engine.run_analysis()
