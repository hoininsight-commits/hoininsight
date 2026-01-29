import os
import json
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
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        with open(json_path, "w", encoding="utf-8") as f:
            # Simple conversion of dataclass to dict if possible, 
            # for simulation we just dump a message
            json.dump({"date": ymd, "status": "BUILT"}, f)
            
        print(f"Dashboard Built: {html_path}")
        return html_path

if __name__ == "__main__":
    # Allow running as standalone: python -m src.issuesignal.dashboard.build_dashboard
    # Requires base_dir to be set correctly. 
    # For standalone test, use current dir.
    builder = DashboardBuilder(Path("."))
    builder.build()
