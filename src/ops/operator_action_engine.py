import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class OperatorActionEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("OperatorAction")
        self.output_path = base_dir / "data" / "ops" / "operator_actions.json"
        
        # Data Dependencies
        self.escalation = self._load_json(base_dir / "data" / "ops" / "narrative_escalation.json")
        self.early_topics = self._load_json(base_dir / "data" / "ops" / "early_topic_candidates.json")
        self.propagation = self._load_json(base_dir / "data" / "ops" / "narrative_propagation.json")
        self.cycles = self._load_json(base_dir / "data" / "memory" / "narrative_cycles.json")
        self.evolution = self._load_json(base_dir / "data" / "memory" / "theme_evolution.json")
        self.regime = self._load_json(base_dir / "data" / "ops" / "regime_state.json")
        self.timing = self._load_json(base_dir / "data" / "ops" / "timing_state.json")
        self.resolver_data = self._load_json(base_dir / "data" / "ontology" / "topic_resolved.json")

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
        """Analyzes and generates operator actions based on narrative intelligence."""
        actions = []
        
        # Build lookup maps for faster scoring
        early_map = {item.get("theme"): item for item in self.early_topics}
        prop_map = {item.get("theme"): item for item in (self.propagation if isinstance(self.propagation, list) else [])}
        cycle_map = {item.get("theme"): item for item in (self.cycles if isinstance(self.cycles, list) else [])}
        evolution_map = {item.get("theme"): item for item in (self.evolution if isinstance(self.evolution, list) else [])}

        if not self.escalation:
            self.logger.info("No escalation data found. Action Engine skipping.")
            return []

        for item in self.escalation:
            theme = item.get("theme")
            esc_score = item.get("escalation_score", 0)
            esc_stage = item.get("escalation_stage", "WEAK_SIGNAL")
            
            # 1. Escalation Component (0-40) 
            # Weighted at 40% of total
            comp_esc = min(40, int(esc_score * 0.4))

            # 2. Early Signal Component (0-20)
            comp_early = 0
            early_item = early_map.get(theme)
            if early_item:
                comp_early = min(20, int(early_item.get("early_topic_score", 0) * 0.2))

            # 3. Cycle Component (0-10)
            comp_cycle = 0
            cycle_item = cycle_map.get(theme)
            if cycle_item:
                comp_cycle = min(10, int(cycle_item.get("cycle_strength", 0) * 10))

            # 4. Evolution Component (0-10)
            comp_evo = 0
            evo_item = evolution_map.get(theme)
            if evo_item:
                # evolution_strength isn't a direct field, use stage or match score proxy
                comp_evo = 8 if evo_item.get("evolution_stage") == "BRANCHING" else 5

            # 5. Propagation Component (0-10)
            comp_prop = 0
            prop_item = prop_map.get(theme)
            if prop_item:
                comp_prop = min(10, int(prop_item.get("propagation_score", 0) / 10))

            # 6. Market Alignment Component (0-10)
            comp_mkt = 5
            if self.regime.get("regime_group") == "STABLE_GROWTH": comp_mkt += 3
            if self.timing.get("market_timing") == "OPTIMAL_ENTRY": comp_mkt += 2

            # Total Action Score
            total_action_score = comp_esc + comp_early + comp_cycle + comp_evo + comp_prop + comp_mkt
            
            # Action Determination
            if total_action_score >= 80: action = "FOCUS"
            elif total_action_score >= 60: action = "TRACK"
            elif total_action_score >= 40: action = "WATCHLIST"
            else: action = "OBSERVE"

            # Recommends & Reasons
            reasons = []
            if esc_stage in ["ESCALATING", "DOMINANT"]: reasons.append(f"Escalation stage is {esc_stage}")
            if comp_cycle >= 7: reasons.append("Cycle reactivation active")
            if comp_evo >= 7: reasons.append("Evolution successor matched")
            if comp_prop >= 7: reasons.append("Narrative propagation rising")
            if comp_mkt >= 8: reasons.append("Market alignment is optimal")

            # Focus Areas from ontology
            focus_areas = []
            if theme in self.resolver_data: # this is resolver_data
                 pass # simplified for now
            
            # Try to get recommended focus from ontology or related items
            recommended_focus = []
            res_item = next((r for r in self.resolver_data if r.get("theme") == theme), None)
            if res_item:
                recommended_focus = [res_item.get("sector", "Market Context"), theme, res_item.get("macro", "Global Trend")]
            else:
                recommended_focus = [theme, "Market Intelligence"]

            actions.append({
                "theme": theme,
                "action": action,
                "action_score": total_action_score,
                "escalation_stage": esc_stage,
                "confidence": item.get("confidence", "MEDIUM"),
                "why_action": reasons if reasons else ["Sustained narrative observation"],
                "next_expected_move": "Mainstream adoption" if action == "TRACK" else "Dominant narrative potential" if action == "FOCUS" else "Escalation check",
                "recommended_focus": recommended_focus,
                "breakdown": {
                    "escalation": comp_esc,
                    "early": comp_early,
                    "cycle": comp_cycle,
                    "evolution": comp_evo,
                    "propagation": comp_prop,
                    "market": comp_mkt
                }
            })

        # Sort and Save
        actions.sort(key=lambda x: x["action_score"], reverse=True)
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(actions, indent=2, ensure_ascii=False), encoding="utf-8")
            self.logger.info(f"Operator Action analysis completed for {len(actions)} themes.")
        except Exception as e:
            self.logger.error(f"Failed to save action data: {e}")

        return actions

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = OperatorActionEngine(Path("."))
    engine.run_analysis()
