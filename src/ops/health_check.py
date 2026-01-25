import json
import os
from pathlib import Path
from datetime import datetime

class HealthCheck:
    """Generates a health summary for the daily run."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
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
                "topics_count": {"READY": 0, "HOLD": 0, "DROP": 0}
            },
            "missing_files": [],
            "schema_errors": []
        }
        
        if lock_file.exists():
            try:
                data = json.loads(lock_file.read_text(encoding="utf-8"))
                cards = data.get("cards", [])
                summary = data.get("summary", {})
                
                health_data["metrics"]["topics_count"] = summary
                health_data["status"] = "SUCCESS" if summary.get("READY", 0) > 0 else "PARTIAL"
                
                # Best-effort counts
                health_data["metrics"]["anomalies_count"] = len(cards)
            except Exception as e:
                health_data["status"] = "FAIL"
                health_data["schema_errors"].append(str(e))
        else:
            health_data["status"] = "FAIL"
            health_data["missing_files"].append(str(lock_file.relative_to(self.base_dir)))
            
        self.health_path.write_text(json.dumps(health_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Health report generated: {self.health_path}")

if __name__ == "__main__":
    import sys
    base = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    HealthCheck(base).run(ymd)