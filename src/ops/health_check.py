import json
import os
from pathlib import Path
from datetime import datetime

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
            "errors": [],
            "missing_files": []
        }
        
        # 1. Check Decision Dashboard (and Daily Brief)
        if (report_dir / "daily_brief.md").exists():
            health_data["decision_dashboard_exists"] = True
        else:
            health_data["errors"].append("daily_brief.md missing")

        # 2. Real Artifact Counts (Read-Only)
        try:
            # Events
            if events_dir.exists():
                health_data["metrics"]["events_count"] = len(list(events_dir.glob("*.json")))
            
            # Anomalies
            if anomalies_dir.exists():
                health_data["metrics"]["anomalies_count"] = len(list(anomalies_dir.glob("*.json")))
            
            # Gate Candidates (from JSON)
            if candidates_file.exists():
                try:
                    c_data = json.loads(candidates_file.read_text(encoding="utf-8"))
                    health_data["metrics"]["gate_candidates_count"] = len(c_data.get("candidates", []))
                except Exception as e:
                    health_data["errors"].append(f"Error parsing candidates: {e}")

            # Scripts (MD and Quality)
            if contents_dir.exists():
                health_data["metrics"]["scripts_md_count"] = len(list(contents_dir.glob("script_v1_*.md")))
                health_data["metrics"]["script_quality_json_count"] = len(list(contents_dir.glob("*.quality.json")))
            
            # Topics Summary (from daily_lock.json if exists)
            lock_file = report_dir / "daily_lock.json"
            if lock_file.exists():
                try:
                    data = json.loads(lock_file.read_text(encoding="utf-8"))
                    health_data["metrics"]["topics_count"] = data.get("summary", {"READY": 0, "HOLD": 0, "DROP": 0})
                except Exception as e:
                    health_data["errors"].append(f"Error parsing lock_file: {e}")

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