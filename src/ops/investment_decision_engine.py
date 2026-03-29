import json
from pathlib import Path
from datetime import datetime

class InvestmentDecisionEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.paths = {
            "core": "data/operator/core_theme_state.json",
            "evolution": "data/theme/top_theme_evolution.json",
            "momentum": "data/theme/top_theme_momentum.json",
            "early": "data/theme/top_early_theme.json",
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
            print(f"[DecisionEngine] Error loading {rel_path}: {e}")
            return {}

    def build_decision(self):
        core = self._load(self.paths["core"])
        evo = self._load(self.paths["evolution"])
        mom = self._load(self.paths["momentum"])
        early = self._load(self.paths["early"])
        topic = self._load(self.paths["topic"])

        if not core:
            return {"theme": "N/A", "decision": {"action": "WATCH", "timing": "UNKNOWN", "confidence": 0}}

        theme = core.get("core_theme", "N/A")
        stage = evo.get("stage", "UNKNOWN")
        momentum_state = mom.get("momentum_state", "UNKNOWN")
        momentum_score = mom.get("momentum_score", mom.get("score", 0))
        early_conf = early.get("score", early.get("confidence", 0))
        pressure = topic.get("topic_pressure", topic.get("pressure", 0))

        action = self.decide_action(stage, momentum_state)
        timing = self.decide_timing(stage)
        confidence = self.calculate_confidence(momentum_score, early_conf, pressure)

        decision_obj = {
            "theme": theme,
            "decision": {
                "action": action,
                "action_reason": f"Stage: {stage}, Momentum: {momentum_state}",
                "action_evidence": [f"stage={stage}", f"momentum={momentum_state}"],
                
                "timing": timing,
                "timing_reason": f"Timing derived from {stage} stage mapping.",
                "timing_evidence": [f"stage={stage}"],
                
                "confidence": confidence,
                "confidence_reason": "Weighted sum of momentum, early signals, and topic pressure.",
                "confidence_evidence": [
                    f"momentum_score={momentum_score}",
                    f"early_score={early_conf}",
                    f"pressure={pressure}"
                ]
            },
            "metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine": "InvestmentDecisionEngine-v1.1"
            }
        }
        
        print(f"[DecisionEngine] Action: {action}, Timing: {timing}, Confidence: {confidence}")
        return decision_obj

    def decide_action(self, stage, momentum):
        if stage == "PRE-STORY":
            return "WATCH"

        if stage == "EMERGING":
            if momentum == "ACCELERATING":
                return "EARLY_ENTRY"
            return "WATCH"

        if stage == "EXPANSION":
            if momentum == "ACCELERATING":
                return "ACCUMULATE"
            return "HOLD"

        if stage == "PEAK" or stage == "MAINSTREAM":
            return "DISTRIBUTE"

        if stage == "EXHAUSTION":
            return "EXIT"
            
        return "WATCH"

    def decide_timing(self, stage):
        mapping = {
            "PRE-STORY": "TOO_EARLY",
            "EMERGING": "EARLY",
            "EXPANSION": "IDEAL",
            "PEAK": "LATE",
            "MAINSTREAM": "LATE",
            "EXHAUSTION": "TOO_LATE"
        }
        return mapping.get(stage, "UNKNOWN")

    def calculate_confidence(self, momentum, early, pressure):
        # score = (momentum * 0.5 + early * 0.2 + pressure * 0.3)
        score = (momentum * 0.5) + (early * 0.2) + (pressure * 0.3)
        return round(min(score, 1.0), 2)

if __name__ == "__main__":
    import os
    root = Path(__file__).parent.parent.parent
    engine = InvestmentDecisionEngine(root)
    print(json.dumps(engine.build_decision(), indent=2))
