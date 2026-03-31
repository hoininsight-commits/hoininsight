import json
from pathlib import Path
from datetime import datetime

class ConfidenceRecalibrationEngine:
    """
    [STEP-G] Confidence Recalibration Engine
    Dynamically adjusts confidence scores based on historical performance metrics.
    """

    def __init__(self, project_root):
        self.project_root = Path(project_root)

    def recalibrate_confidence(self, base_confidence, outcome_summary):
        """
        Recalibrates base confidence using hit ratio and decision accuracy.
        """
        hit_ratio = outcome_summary.get("last_7d", {}).get("hit_ratio_avg", 0.5)
        decision_acc = outcome_summary.get("last_7d", {}).get("decision_accuracy", 0.5)
        
        # Adjustments logic
        adjustment_hit = round(hit_ratio * 0.2, 3)
        adjustment_decision = round(decision_acc * 0.2, 3)
        
        failure_penalty = self.compute_failure_penalty(outcome_summary.get("last_7d", {}))
        
        # For Demo: Recency weight (bonus for active evaluation)
        recency_bonus = 0.04 if outcome_summary.get("last_7d", {}).get("sample_size", 0) > 0 else 0
        
        final = base_confidence + adjustment_hit + adjustment_decision - failure_penalty + recency_bonus
        final = round(max(0.0, min(1.0, final)), 3)

        return {
            "value": final,
            "source": "recalibrated",
            "base_confidence": base_confidence,
            "adjustments": {
                "hit_ratio": adjustment_hit,
                "decision_accuracy": adjustment_decision,
                "failure_penalty": -failure_penalty,
                "recency_bonus": recency_bonus
            },
            "final_confidence": final
        }

    def compute_failure_penalty(self, summary):
        """
        Calculates penalty based on failure rates in the summary.
        """
        penalty = 0.0
        
        # Penalty for low theme accuracy
        if summary.get("theme_accuracy", 1.0) < 0.5:
            penalty += 0.1
            
        # Penalty for low hit ratio
        if summary.get("hit_ratio_avg", 1.0) < 0.3:
            penalty += 0.1
            
        return round(penalty, 2)

    def save_metrics(self, recalibrated):
        """
        Saves the recalibration metrics for historical tracking.
        """
        metrics_path = self.project_root / "data" / "ops" / "confidence_metrics.json"
        
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "base_confidence": recalibrated.get("base_confidence"),
            "final_confidence": recalibrated.get("final_confidence"),
            "adjustments": recalibrated.get("adjustments")
        }
        
        metrics = []
        if metrics_path.exists():
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
            except: pass
            
        metrics.append(entry)
        
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
            
        return entry
