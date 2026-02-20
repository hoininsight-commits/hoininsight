import json
import os
from pathlib import Path
from datetime import datetime
from src.ops.event_input_truth import diagnose

class HealthCheck:
    """Generates a health summary for the daily run."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # [Step 25-2] Standardize to data/dashboard/ for GitHub Pages deployment
        self.health_path = base_dir / "data" / "dashboard" / "health_today.json"
        self.health_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self, ymd: str):
        year, month, day = ymd.split("-")
        report_dir = self.base_dir / "data" / "reports" / year / month / day
        events_dir = self.base_dir / "data" / "events" / year / month / day
        anomalies_dir = self.base_dir / "data" / "features" / "anomalies" / year / month / day
        topics_dir = self.base_dir / "data" / "topics" / year / month / day
        candidates_file = self.base_dir / "data" / "topics" / "candidates" / year / month / day / "topic_candidates.json"
        contents_dir = self.base_dir / "data" / "content"
        
        health_data = {
            "run_date": ymd,
            "checked_at": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "metrics": {
                "events_count": 0,
                "anomalies_count": 0,
                "gate_candidates_count": 0,
                "scripts_md_count": 0,
                "script_quality_json_count": 0,
                "topics_count": {"READY": 0, "HOLD": 0, "DROP": 0}
            },
            "decision_dashboard_exists": False,
            "event_coverage_path": "data/dashboard/event_coverage_today.json",
            "errors": [],
            "missing_files": []
        }
        
        # 1. Check Decision Dashboard
        if (report_dir / "decision_dashboard.md").exists():
            health_data["decision_dashboard_exists"] = True
        else:
            health_data["errors"].append("decision_dashboard.md missing")

        # 2. Real Artifact Counts (Read-Only)
        try:
            # Events
            if events_dir.exists():
                count = len(list(events_dir.glob("*.json")))
                health_data["metrics"]["events_count"] = count
                if count == 0:
                    diag = diagnose(ymd, self.base_dir)
                    health_data["input_root_cause_code"] = diag.get("root_cause_code")
                    health_data["input_details"] = diag.get("details")
                    health_data["errors"].append(f"events_count is 0: {diag.get('root_cause_code')}")
            else:
                diag = diagnose(ymd, self.base_dir)
                health_data["input_root_cause_code"] = diag.get("root_cause_code")
                health_data["input_details"] = diag.get("details")
                health_data["missing_files"].append(str(events_dir))
                health_data["errors"].append(f"events_dir missing: {diag.get('root_cause_code')}")
            
            # Anomalies
            if anomalies_dir.exists():
                count = len(list(anomalies_dir.glob("*.json")))
                health_data["metrics"]["anomalies_count"] = count
                if count == 0:
                    health_data["errors"].append(f"anomalies_count is 0 in {anomalies_dir}")
            else:
                health_data["missing_files"].append(str(anomalies_dir))
                health_data["errors"].append(f"anomalies_dir missing: {anomalies_dir}")
            
            # Gate Candidates (from JSON)
            if candidates_file.exists():
                try:
                    c_data = json.loads(candidates_file.read_text(encoding="utf-8"))
                    count = len(c_data.get("candidates", []))
                    health_data["metrics"]["gate_candidates_count"] = count
                    if count == 0:
                        health_data["errors"].append(f"gate_candidates_count is 0 in {candidates_file}")
                except Exception as e:
                    health_data["errors"].append(f"Error parsing candidates: {e}")
            else:
                health_data["missing_files"].append(str(candidates_file))
                health_data["errors"].append(f"candidates_file missing: {candidates_file}")

            # Scripts (MD and Quality)
            # Scripts are stored by date path too now?
            # src/engine.py: gate_pipeline_main(run_ymd)
            # and DecisionDashboard uses gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
            gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
            if gate_dir.exists():
                health_data["metrics"]["scripts_md_count"] = len(list(gate_dir.glob("script_v1_*.md")))
                health_data["metrics"]["script_quality_json_count"] = len(list(gate_dir.glob("*.quality.json")))
            else:
                health_data["errors"].append(f"gate_dir missing: {gate_dir}")
            
            # Topics Summary (from daily_lock.json if exists)
            lock_file = report_dir / "daily_lock.json"
            if lock_file.exists():
                try:
                    data = json.loads(lock_file.read_text(encoding="utf-8"))
                    health_data["metrics"]["topics_count"] = data.get("summary", {"READY": 0, "HOLD": 0, "DROP": 0})
                except Exception as e:
                    health_data["errors"].append(f"Error parsing lock_file: {e}")
            else:
                health_data["errors"].append(f"daily_lock.json missing in {report_dir}")

            # Check READY count for closure signal (Step 32-3)
            ready_count = health_data["metrics"]["topics_count"].get("READY", 0)
            events_count = health_data["metrics"]["events_count"]
            if ready_count == 0:
                if events_count > 0:
                    health_data["ready_root_cause_code"] = "QUALITY_ELIGIBILITY"
                    health_data["ready_details"] = "Events present but none reached READY state (failed scoring or filters)."
                    health_data["errors"].append("topics_count.READY is 0: QUALITY_ELIGIBILITY")
                else:
                    # Already handled by input_root_cause_code
                    pass

            health_data["status"] = "SUCCESS" if not health_data["errors"] else "PARTIAL"
            
        except Exception as e:
            health_data["status"] = "FAIL"
            health_data["errors"].append(f"General health check error: {e}")
            
        self.health_path.write_text(json.dumps(health_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Health report generated: {self.health_path}")


if __name__ == "__main__":
    import sys
    # Use current working directory instead of hardcoded path for GitHub Actions compatibility
    base = Path.cwd()
    # Try to find latest run date if not provided
    ymd = sys.argv[1] if len(sys.argv) > 1 else None
    if not ymd:
        from src.ops.dashboard_manifest import DashboardManifest
        ymd = DashboardManifest(base).find_latest_run()
        
    if ymd:
        HealthCheck(base).run(ymd)
    else:
        print("No run date found for health check.")