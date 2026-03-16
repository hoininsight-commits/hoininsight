import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class EarlyTopicDetector:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("EarlyTopicDetector")
        self.output_path = base_dir / "data" / "ops" / "early_topic_candidates.json"
        
        # Load Data Dependencies
        self.radar = self._load_json(base_dir / "data" / "ops" / "economic_hunter_radar.json")
        self.predictions = self._load_json(base_dir / "data" / "ops" / "topic_predictions.json")
        self.history = self._load_json(base_dir / "data" / "memory" / "narrative_history.json")
        self.cycles = self._load_json(base_dir / "data" / "memory" / "narrative_cycles.json")
        self.evolution = self._load_json(base_dir / "data" / "memory" / "theme_evolution.json")
        self.resolver_data = self._load_json(base_dir / "data" / "ontology" / "topic_resolved.json")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            self.logger.warning(f"File not found: {path}")
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.error(f"Error loading {path}: {e}")
            return []

    def run_analysis(self):
        """Identifies early topic candidates by cross-referencing signals with memory and evolution."""
        candidates = []
        
        # 1. Gather all potential topics from radar and predictions
        potential_topics = []
        
        # Radar candidates
        radar_list = self.radar.get("radar_candidates", []) if isinstance(self.radar, dict) else []
        for r in radar_list:
            title = r.get("potential_topic") or r.get("title")
            if title:
                potential_topics.append({"title": title, "source": "radar", "intensity": 0.8 if r.get("signal_strength") == "HIGH" else 0.6})
        
        # Topic predictions
        pred_list = self.predictions.get("predictions", []) if isinstance(self.predictions, dict) else []
        for p in pred_list:
            title = p.get("theme") # In predictions, theme is often the primary focus
            if title:
                potential_topics.append({"title": title, "source": "prediction", "probability": p.get("prediction_score", 0) / 100.0})

        # 2. Process each topic
        processed_titles = set()
        for pt in potential_topics:
            title = pt.get("title")
            if not title or title in processed_titles: continue
            processed_titles.add(title)

            # A. Theme Mapping
            theme = "General Interest"
            if isinstance(self.resolver_data, dict) and title in self.resolver_data:
                theme = self.resolver_data[title].get("theme", "General Interest")
            
            # B. Signal Presence (0-15)
            signal_score = 10
            if pt["source"] == "radar" and pt.get("intensity", 0) > 0.7: signal_score = 15
            elif pt["source"] == "prediction" and pt.get("probability", 0) > 0.6: signal_score = 12

            # C. Memory Match (0-20)
            memory_match = 0
            appearances = [h for h in self.history if h.get("theme") == theme]
            if appearances:
                memory_match = min(20, len(appearances) * 4)
            
            # D. Cycle Match (0-20)
            cycle_score = 0
            cycle_info = next((c for c in self.cycles if c["theme"] == theme), None)
            if cycle_info:
                phase = cycle_info.get("current_phase")
                if phase == "REACTIVATION": cycle_score = 20
                elif phase == "EARLY": cycle_score = 15
                elif phase == "MID": cycle_score = 10
            
            # E. Evolution Match (0-20)
            evo_score = 0
            evo_info = next((e for e in self.evolution if e["theme"] == theme), None)
            # Or if it IS a dominant successor of a current mainstream theme
            is_successor = False
            for e in self.evolution:
                if e.get("dominant_successor") == theme:
                    is_successor = True
                    break
            
            if is_successor: evo_score = 20
            elif evo_info and evo_info.get("current_evolution_stage") == "EXPANDING": evo_score = 15
            
            # F. Narrative Potential (0-15) - Basic heuristic
            potential_score = 12 # Default for resolved topics
            
            # G. Regime Alignment (0-10) - Default
            regime_score = 8

            # Total Score
            total_score = signal_score + memory_match + cycle_score + evo_score + potential_score + regime_score
            
            # Constraints
            if signal_score < 10: total_score -= 10
            
            # Confidence
            confidence = "LOW"
            if total_score >= 80: confidence = "HIGH"
            elif total_score >= 65: confidence = "MEDIUM"
            
            # Why Early
            reasons = []
            if memory_match > 10: reasons.append(f"{theme} theme memory exists in history")
            if cycle_score >= 15: reasons.append(f"Cycle {cycle_info.get('current_phase')} phase detected")
            if is_successor: reasons.append("Successor match from Theme Evolution")
            if signal_score >= 12: reasons.append("Strong signal presence in current Radar")

            # Classification
            phase = "PRE-NARRATIVE"
            if total_score >= 80: classification = "EARLY HIGH PRIORITY"
            elif total_score >= 65: classification = "EARLY WATCH"
            else: classification = "WEAK SIGNAL"

            if total_score >= 50:
                candidates.append({
                    "theme": theme,
                    "topic_name": title,
                    "early_topic_score": total_score,
                    "signal_presence": "STRONG" if signal_score >= 12 else "MODERATE",
                    "memory_match_score": memory_match,
                    "cycle_match_score": cycle_score,
                    "evolution_match_score": evo_score,
                    "narrative_potential_score": potential_score,
                    "regime_alignment_score": regime_score,
                    "current_phase": phase,
                    "classification": classification,
                    "why_early": reasons,
                    "next_theme_path": [title, theme],
                    "confidence": confidence
                })

        # 3. Sort and Save
        candidates.sort(key=lambda x: x["early_topic_score"], reverse=True)
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(candidates, indent=2, ensure_ascii=False), encoding="utf-8")
            self.logger.info(f"Early Topic Detection completed: {len(candidates)} candidates found.")
        except Exception as e:
            self.logger.error(f"Failed to save early topic candidates: {e}")
            
        return candidates

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = EarlyTopicDetector(Path("."))
    engine.run_analysis()
