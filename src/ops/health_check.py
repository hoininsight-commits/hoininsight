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
        lock_file = report_dir / "daily_lock.json"
        
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
            "missing_files": [],
            "schema_errors": []
        }
        
        # 1. Check Decision Dashboard
        if (report_dir / "decision_dashboard.md").exists():
            health_data["decision_dashboard_exists"] = True

        # 2. Check Lock File and Metrics
        if lock_file.exists():
            try:
                data = json.loads(lock_file.read_text(encoding="utf-8"))
                cards = data.get("cards", [])
                summary = data.get("summary", {})
                
                health_data["metrics"]["topics_count"] = summary
                # Gate candidates are those in ranked list
                health_data["metrics"]["gate_candidates_count"] = len(cards)
                health_data["status"] = "SUCCESS" if summary.get("READY", 0) > 0 else "PARTIAL"
                
                # Best-effort counts
                health_data["metrics"]["anomalies_count"] = len(cards) # Simplified
            except Exception as e:
                health_data["status"] = "FAIL"
                health_data["schema_errors"].append(str(e))
        else:
            health_data["status"] = "FAIL"
            health_data["missing_files"].append("daily_lock.json")

        # 3. File Counts (Scripts)
        topics_dir = self.base_dir / "data" / "topics" / year / month / day
        if topics_dir.exists():
            health_data["metrics"]["scripts_md_count"] = len(list(topics_dir.glob("script_v*md")))
            health_data["metrics"]["script_quality_json_count"] = len(list(topics_dir.glob("*.quality.json")))
            
        self.health_path.write_text(json.dumps(health_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Health report generated: {self.health_path}")

if __name__ == "__main__":
    import sys
    base = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
    # Try to find latest run date if not provided
    ymd = sys.argv[1] if len(sys.argv) > 1 else None
    if not ymd:
        from dashboard_manifest import DashboardManifest
        ymd = DashboardManifest(base).find_latest_run()
        
    if ymd:
        HealthCheck(base).run(ymd)
    else:
        print("No run date found for health check.")