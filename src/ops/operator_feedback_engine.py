import json
from pathlib import Path
from datetime import datetime

class OperatorFeedbackEngine:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.log_path = self.project_root / "data" / "ops" / "operator_feedback_log.json"
        self.summary_path = self.project_root / "data" / "ops" / "operator_feedback_summary.json"

    def evaluate_outcome(self, entry):
        """
        Rule-based outcome evaluation based on hit_ratio and alignment.
        """
        hit = entry.get("hit_ratio", 0)
        align = entry.get("alignment", 0)

        if hit >= 0.5 and align >= 0.6:
            return "SUCCESS"

        if hit < 0.2:
            return "STOCK_WRONG"

        if align < 0.3:
            return "THEME_WRONG"

        return "TIMING_WRONG"

    def build_summary(self, logs):
        """
        Aggregates logs into a performance summary.
        """
        if not logs:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "failure_distribution": {},
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        total = len(logs)
        success = sum(1 for x in logs if x.get("result", {}).get("success", False))

        failure_counts = {}
        for x in logs:
            f = x.get("result", {}).get("failure_type", "UNKNOWN")
            failure_counts[f] = failure_counts.get(f, 0) + 1

        return {
            "total_runs": total,
            "success_rate": round(success / total, 2) if total else 0,
            "failure_distribution": failure_counts,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def append_log(self, entry):
        """
        Appends a new entry to the feedback log.
        """
        logs = []
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        
        # Ensure result consistency
        if "result" not in entry:
            f_type = self.evaluate_outcome(entry)
            entry["result"] = {
                "success": f_type == "SUCCESS",
                "failure_type": f_type
            }
            
        logs.append(entry)
        
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
        # Sync to docs for server check
        public_log = self.project_root / "docs" / "data" / "ops" / "operator_feedback_log.json"
        public_log.parent.mkdir(parents=True, exist_ok=True)
        with open(public_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
        return logs

    def run_feedback_loop(self, entry_data):
        """
        Complete feedback loop: evaluate -> log -> summary.
        """
        logs = self.append_log(entry_data)
        summary = self.build_summary(logs)
        
        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        # Sync to docs for server check
        public_summary = self.project_root / "docs" / "data" / "ops" / "operator_feedback_summary.json"
        public_summary.parent.mkdir(parents=True, exist_ok=True)
        with open(public_summary, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        return summary
