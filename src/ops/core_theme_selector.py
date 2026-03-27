import json
from pathlib import Path

class CoreThemeSelector:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.paths = {
            "early": "data/theme/top_early_theme.json",
            "evolution": "data/theme/top_theme_evolution.json",
            "momentum": "data/theme/top_theme_momentum.json",
            "topic": "data/topic/top_topic.json"
        }

    def _load(self, rel_path):
        p = self.project_root / rel_path
        if not p.exists():
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Selector] Error loading {rel_path}: {e}")
            return {}

    def select_core_theme(self):
        candidates = []

        # 1. Early Signal
        early = self._load(self.paths["early"])
        if early and "theme" in early:
            # Score as confidence
            score = early.get("score", early.get("confidence", 0))
            candidates.append({
                "theme": early["theme"],
                "score": score * 0.3,
                "source": "early"
            })

        # 2. Evolution
        evo = self._load(self.paths["evolution"])
        if evo and "theme" in evo:
            stage_weight = {
                "PRE-STORY": 0.2,
                "EMERGING": 0.4,
                "EXPANSION": 0.8,
                "PEAK": 1.0,
                "MAINSTREAM": 1.0, # Map PEAK to MAINSTREAM if needed
                "EXHAUSTION": 0.3
            }
            weight = stage_weight.get(evo.get("stage"), 0.1)
            candidates.append({
                "theme": evo["theme"],
                "score": weight,
                "source": "evolution"
            })

        # 3. Momentum
        mom = self._load(self.paths["momentum"])
        if mom and "theme" in mom:
            score = mom.get("momentum_score", mom.get("score", 0))
            candidates.append({
                "theme": mom["theme"],
                "score": score,
                "source": "momentum"
            })

        # 4. Topic Pressure
        topic = self._load(self.paths["topic"])
        if topic and "selected_topic" in topic:
            # Note: topic often has a "selected_topic" but maybe not a "theme" field directly.
            # In our today_operator_brief, we mapped topic to the theme.
            # For selection, we might need to check if there's a theme associated.
            # If not, we use "theme" if present, else fallback.
            theme = topic.get("theme", topic.get("selected_topic"))
            pressure = topic.get("topic_pressure", topic.get("pressure", 0))
            candidates.append({
                "theme": theme,
                "score": pressure,
                "source": "topic"
            })

        if not candidates:
            return {"core_theme": "N/A", "score": 0, "sources": []}

        # Aggregate by theme
        aggregated = {}
        for c in candidates:
            t = c["theme"]
            if t not in aggregated:
                aggregated[t] = {"score": 0, "sources": []}
            aggregated[t]["score"] += c["score"]
            aggregated[t]["sources"].append(c["source"])

        # Select max
        top_theme = max(aggregated.items(), key=lambda x: x[1]["score"])
        
        result = {
            "core_theme": top_theme[0],
            "score": round(top_theme[1]["score"], 4),
            "sources": top_theme[1]["sources"]
        }
        
        print(f"[Selector] Selected Core Theme: {result['core_theme']} (Score: {result['score']})")
        return result

if __name__ == "__main__":
    import os
    # Assuming run from root or src/ops
    root = Path(__file__).parent.parent.parent
    selector = CoreThemeSelector(root)
    print(json.dumps(selector.select_core_theme(), indent=2))
