import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
from src.memory.narrative_memory_store import NarrativeMemoryStore

class ThemeEvolutionEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.store = NarrativeMemoryStore(base_dir)
        self.logger = logging.getLogger("ThemeEvolution")
        self.output_path = base_dir / "data" / "memory" / "theme_evolution.json"
        
        # Integration with Ontology
        try:
            from src.ontology.ontology_resolver import OntologyResolver
            from src.ontology.ontology_store import OntologyStore
            store = OntologyStore(base_dir)
            self.resolver = OntologyResolver(store)
        except ImportError:
            self.resolver = None

    def run_analysis(self):
        """Analyzes how themes evolve into each other over time."""
        history = self.store.load_history()
        if not history:
            self.logger.warning("No history to analyze evolution.")
            return

        # 1. Sort history by date
        sorted_history = sorted(history, key=lambda x: x["date"])
        
        # 2. Map transitions (Theme A -> Theme B)
        transitions = defaultdict(list)
        theme_appearances = defaultdict(list)
        
        last_theme = None
        for entry in sorted_history:
            # Resolve theme if missing (Legacy support)
            theme = entry.get("theme")
            if not theme and self.resolver:
                resolved = self.resolver.resolve(entry.get("title", ""))
                theme = resolved.get("theme")
            
            if not theme: continue
            
            theme_appearances[theme].append(datetime.strptime(entry["date"], "%Y-%m-%d"))
            
            if last_theme and last_theme != theme:
                transitions[last_theme].append(theme)
            
            last_theme = theme

        # 3. Calculate evolution metrics per theme
        evolution_data = []
        for theme, successors in transitions.items():
            successor_counts = Counter(successors)
            total_transitions = len(successors)
            
            # Dominant Successor
            most_common = successor_counts.most_common(3)
            dominant = most_common[0][0] if most_common else "None"
            
            # Stages Logic
            # ORIGIN: First few appearances, few successors
            # EXPANDING: Many successors, high frequency
            # BRIDGING: Transitioning to new clusters
            # SATURATING: Repeatedly looping or fading
            
            freq = len(theme_appearances[theme])
            unique_successors = len(successor_counts)
            
            if freq <= 2:
                stage = "ORIGIN"
            elif unique_successors >= 3:
                stage = "DIVERGING"
            elif total_transitions >= 5 and unique_successors == 1:
                stage = "SATURATING"
            elif total_transitions >= 4:
                stage = "BRIDGING"
            else:
                stage = "EXPANDING"

            successor_list = []
            for s_theme, count in successor_counts.items():
                strength = round(count / total_transitions, 2)
                successor_list.append({
                    "theme": s_theme,
                    "transition_frequency": count,
                    "evolution_strength": strength
                })
            
            # Sort successors by count
            successor_list.sort(key=lambda x: x["transition_frequency"], reverse=True)

            evolution_data.append({
                "theme": theme,
                "current_evolution_stage": stage,
                "successor_themes": successor_list,
                "dominant_successor": dominant,
                "next_likely_theme": dominant,
                "total_transitions": total_transitions
            })

        # 4. Final output sort
        evolution_data.sort(key=lambda x: x["total_transitions"], reverse=True)

        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(evolution_data, indent=2, ensure_ascii=False), encoding="utf-8")
            self.logger.info(f"Theme Evolution analysis completed for {len(evolution_data)} themes.")
        except Exception as e:
            self.logger.error(f"Failed to save evolution data: {e}")

        return evolution_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ThemeEvolutionEngine(Path("."))
    engine.run_analysis()
