import json
import os
from pathlib import Path
from datetime import datetime

class DashboardManifest:
    """Generates a manifest file to point the dashboard to the latest run."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.manifest_path = base_dir / "data" / "dashboard" / "latest_run.json"
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, ymd: str):
        """Creates latest_run.json for the given date."""
        year, month, day = ymd.split("-")
        
        # Consistent pathing as per reporter logic
        report_dir = f"data/reports/{year}/{month}/{day}"
        
        manifest_data = {
            "date": ymd,
            "refreshed_at": datetime.now().isoformat(),
            "paths": {
                "daily_report_md": f"{report_dir}/daily_report.md",
                "decision_dashboard_md": f"{report_dir}/decision_dashboard.md",
                "daily_lock_json": f"{report_dir}/daily_lock.json"
            }
        }
        
        self.manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Manifest generated: {self.manifest_path}")

if __name__ == "__main__":
    import sys
    base = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
    ymd = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    DashboardManifest(base).generate(ymd)