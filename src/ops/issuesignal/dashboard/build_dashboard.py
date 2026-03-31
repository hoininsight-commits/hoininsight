import os
import json
import dataclasses
from pathlib import Path
from datetime import datetime
from .loader import DashboardLoader
from .renderer import DashboardRenderer

class DashboardBuilder:
    """
    (IS-27) Orchestrates the dashboard build process.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "dashboard" / "issuesignal"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self):
        ymd = datetime.now().strftime("%Y-%m-%d")
        print(f"[{datetime.now()}] Building IssueSignal Dashboard for {ymd}...")
        
        # 1. Load Data
        loader = DashboardLoader(self.base_dir)
        summary = loader.load_today_summary(ymd)
        
        # 2. Render HTML
        renderer = DashboardRenderer()
        html = renderer.render(summary)
        
        # 3. Save Files
        html_path = self.output_dir / "index.html"
        json_path = self.output_dir / "dashboard.json"
        unified_json_path = self.output_dir / "unified_dashboard.json"
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        summary_dict = dataclasses.asdict(summary)
        
        with open(json_path, "w", encoding="utf-8") as f:
            # Backward compatibility
            json.dump({"date": ymd, "status": "BUILT", "counts": summary.counts}, f)

        with open(unified_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_dict, f, ensure_ascii=False, indent=2)
            
        print(f"Dashboard Built: {html_path}")
        print(f"Unified JSON: {unified_json_path}")
        return html_path

if __name__ == "__main__":
    # Allow running as standalone: python -m src.issuesignal.dashboard.build_dashboard
    # Requires base_dir to be set correctly. 
    # For standalone test, use current dir.
    builder = DashboardBuilder(Path("."))
    builder.build()
