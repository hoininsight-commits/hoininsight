import json
import os
from datetime import datetime
from pathlib import Path

class EngineValidationAudit:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.ledger_path = self.project_root / "data" / "ops" / "outcome_ledger.json"
        self.summary_path = self.project_root / "data" / "ops" / "outcome_summary.json"
        self.metrics_path = self.project_root / "data" / "ops" / "confidence_metrics.json"
        self.report_path = self.project_root / "data" / "ops" / "validation_audit_report.json"

    def run_audit(self):
        """
        Runs the full Engine Validation Audit [STEP-H].
        """
        print("[Audit] Starting Engine Validation Audit...")
        
        ledger = self._load_json(self.ledger_path, [])
        metrics = self._load_json(self.metrics_path, [])
        
        if not ledger:
            print("[Audit] ⚠️ Outcome ledger empty. Skipping audit.")
            return None

        report = {
            "generated_at": datetime.now().isoformat(),
            "period": f"Last {len(ledger)} runs",
            "failure_distribution": self.analyze_failure_distribution(ledger),
            "confidence_stability": self.analyze_confidence_stability(metrics),
            "outcome_alignment": self.analyze_outcome_alignment(ledger),
            "causality_validity": self.analyze_causality_validity(ledger)
        }

        # Determine PASS/FAIL status based on NON-NEGOTIABLE rules
        report["status"] = self._compute_status(report)
        
        self._save_json(self.report_path, report)
        print(f"[Audit] ✅ Audit report saved to {self.report_path}")
        return report

    def analyze_failure_distribution(self, ledger):
        """
        Analyzes the distribution of failure types in the ledger.
        """
        if not ledger: return {}
        counter = {}
        for entry in ledger:
            eval_data = entry.get("evaluation", {})
            f_type = eval_data.get("failure_type", "SUCCESS" if eval_data.get("hit_ratio", 0) > 0.5 else "UNKNOWN")
            counter[f_type] = counter.get(f_type, 0) + 1
        
        total = len(ledger)
        return {k: round(v / total, 2) for k, v in counter.items()}

    def analyze_confidence_stability(self, metrics):
        """
        Analyzes the stability (volatility) of confidence scores over time.
        """
        if not metrics:
            return {"min": 0, "max": 0, "avg": 0, "volatility": 0}
            
        values = []
        for c in metrics:
            if isinstance(c, dict) and "final_confidence" in c:
                values.append(c["final_confidence"])
            elif isinstance(c, (int, float)):
                values.append(c)
        
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "volatility": 0}

        return {
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "avg": round(sum(values) / len(values), 3),
            "volatility": round(max(values) - min(values), 3)
        }

    def analyze_outcome_alignment(self, ledger):
        """
        Checks if confidence levels align with actual outcomes (Hit Ratio).
        """
        if not ledger: return 0.0
        aligned = 0
        for entry in ledger:
            # Handle structured confidence or legacy float
            conf_data = entry.get("decision", {}).get("confidence", {})
            conf = conf_data.get("value", 0.5) if isinstance(conf_data, dict) else conf_data
            
            hit = entry.get("evaluation", {}).get("hit_ratio", 0.0)
            
            # Simple alignment check: both high or both low
            if (conf >= 0.5 and hit >= 0.5) or (conf < 0.5 and hit < 0.5):
                aligned += 1
        
        return round(aligned / len(ledger), 2)

    def analyze_causality_validity(self, ledger):
        """
        Validates the structural explainability (Causality Chain).
        """
        if not ledger: return 0.0
        valid = 0
        for entry in ledger:
            # If the failure wasn't due to structural mismatch, we consider causality valid
            if entry.get("evaluation", {}).get("failure_type") != "CAUSALITY_MISMATCH":
                valid += 1
        
        return round(valid / len(ledger), 2)

    def _compute_status(self, report):
        """
        Applies PASS/FAIL criteria.
        """
        dist = report["failure_distribution"]
        stab = report["confidence_stability"]
        align = report["outcome_alignment"]
        causal = report["causality_validity"]

        # FAIL criteria
        if any(v > 0.5 for v in dist.values() if v > 0): return "FAIL (Bias Detected)"
        if stab["volatility"] > 0.5: return "FAIL (Unstable Confidence)"
        if align < 0.5: return "FAIL (No Outcome Correlation)"
        if causal < 0.6: return "FAIL (Invalid Causality)"
        
        # PASS criteria
        if stab["volatility"] < 0.3 and align > 0.6 and causal > 0.7:
            return "PASS"
            
        return "DEGRADED"

    def _load_json(self, path, default):
        if not path.exists(): return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
