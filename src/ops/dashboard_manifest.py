import json
import os
from pathlib import Path
from datetime import datetime

class DashboardManifest:
    """Generates a manifest file to point the dashboard to the latest run."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # [Step 25-2] Standardize to data/dashboard/ for GitHub Pages deployment
        self.manifest_path = base_dir / "data" / "dashboard" / "latest_run.json"
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def find_latest_run(self) -> str:
        """Finds the most recent YYYY-MM-DD run folder."""
        reports_root = self.base_dir / "data" / "reports"
        dates = []
        for y_dir in reports_root.glob("20*"):
            if not y_dir.is_dir(): continue
            for m_dir in y_dir.glob("??"):
                if not m_dir.is_dir(): continue
                for d_dir in m_dir.glob("??"):
                    if not d_dir.is_dir(): continue
                    dates.append(f"{y_dir.name}-{m_dir.name}-{d_dir.name}")
        
        return sorted(dates, reverse=True)[0] if dates else None

    def generate(self, ymd: str = None):
        """Creates latest_run.json. Auto-detects if ymd is None."""
        if not ymd:
            ymd = self.find_latest_run()
        
        if not ymd:
            print("No runs detected.")
            return

        year, month, day = ymd.split("-")
        rel_dir = f"data/reports/{year}/{month}/{day}"
        abs_dir = self.base_dir / rel_dir
        
        # Verify required files and log missing
        required = {
            "report_md": "daily_brief.md",
            "decision_md": "decision_dashboard.md", # Point to the new decision dashboard
            "daily_lock_json": "daily_lock.json"
        }
        
        paths = {}
        missing = []
        for key, filename in required.items():
            if (abs_dir / filename).exists():
                paths[key] = f"{rel_dir}/{filename}"
            else:
                missing.append(filename)

        # Flattened Manifest Structure (Step 28-3)
        manifest_data = {
            "run_date": ymd,
            "run_ts": datetime.now().isoformat(),
            "report_md": paths.get("report_md"),
            "decision_md": paths.get("decision_md"), 
            "daily_lock": paths.get("daily_lock"),
            "health_json": f"data/dashboard/health_today.json",
            "auto_priority_json": "data/ops/auto_priority_today.json",
            "missing": missing
        }
        
        self.manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Manifest generated: {self.manifest_path} for {ymd}")


if __name__ == "__main__":
    import sys
    # Use current working directory instead of hardcoded path for GitHub Actions compatibility
    base = Path.cwd()
    ymd = sys.argv[1] if len(sys.argv) > 1 else None
    DashboardManifest(base).generate(ymd)