import json
import logging
from pathlib import Path
from typing import Dict, List
import sys

# Ensure project root is in sys.path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from src.utils.markdown_parser import parse_markdown

class EconomicHunterSnapshotViewerGenerator:
    """
    Generates a static HTML viewer for Economic Hunter Cognitive Snapshots.
    This viewer is strictly READ-ONLY and designed for operator observation.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.snapshots_dir = base_dir / "data" / "snapshots"
        self.output_dir = base_dir / "dashboard" / "snapshot"
        self.logger = logging.getLogger("EconomicHunterSnapshotViewerGenerator")

    def generate(self) -> Path:
        """
        Scans snapshots, builds data map, and generates the static HTML viewer.
        """
        self.logger.info("Generating Snapshot Viewer...")
        
        # 1. Load Snapshots
        snapshots_map = self._load_snapshots()
        
        # 2. Prepare Output Directory
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
        # 3. Generate HTML
        html_content = self._build_html(snapshots_map)
        
        # 4. Save File
        output_file = self.output_dir / "index.html"
        output_file.write_text(html_content, encoding="utf-8")
        self.logger.info(f"Snapshot Viewer generated at: {output_file}")
        
        return output_file

    def _load_snapshots(self) -> Dict[str, str]:
        """
        Scans data/snapshots/*.md and returns { 'YYYY-MM-DD': 'Markdown Content' }
        """
        data = {}
        if not self.snapshots_dir.exists():
            return data
            
        for file_path in self.snapshots_dir.glob("*.md"):
            try:
                # Filename format: YYYY-MM-DD_top1_snapshot.md or snapshot_YYYY-MM-DD.md
                # We prioritize the daily YYYY-MM-DD extraction
                name = file_path.stem
                # Extract date roughly (looking for 202X-XX-XX)
                date_part = name.split("_")[0] # Assuming YYYY-MM-DD is prefix or part of it
                
                # If strict format "YYYY-MM-DD_top1_snapshot", take first part
                # Verify length
                if len(date_part) != 10:
                     # Try finding date in string if naming convention varies
                     import re
                     match = re.search(r'\d{4}-\d{2}-\d{2}', name)
                     if match:
                         date_part = match.group(0)
                     else:
                         continue

                content = file_path.read_text(encoding="utf-8")
                data[date_part] = content
            except Exception as e:
                self.logger.warning(f"Failed to read snapshot {file_path}: {e}")
                
        # Sort by date descending
        sorted_keys = sorted(data.keys(), reverse=True)
        return {k: data[k] for k in sorted_keys}

    def _build_html(self, snapshots_map: Dict[str, str]) -> str:
        """
        Builds the static HTML with embedded JSON data.
        """
        # Convert Markdown to HTML for each snapshot to avoid heavy client-side parsing if possible,
        # OR just embed raw markdown and use simple replacer.
        # User requested "Markdown rendering". Let's use our parse_markdown util on server side.
        
        rendered_map = {}
        for date, raw_md in snapshots_map.items():
            rendered_map[date] = parse_markdown(raw_md)
            
        snapshot_dates = list(rendered_map.keys())
        latest_date = snapshot_dates[0] if snapshot_dates else ""
        
        json_data = json.dumps(rendered_map, ensure_ascii=False)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Economic Hunter - Cognitive Snapshot</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --panel-bg: #1e293b;
            --border-color: #334155;
            --accent-color: #38bdf8;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }}
        .container {{
            width: 100%;
            max-width: 800px;
        }}
        .header {{
            margin-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .title {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: var(--text-primary);
        }}
        .subtitle {{
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .controls select {{
            background: var(--panel-bg);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }}
        .viewer {{
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 40px;
            min-height: 500px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .empty-state {{
            text-align: center;
            color: var(--text-secondary);
            padding-top: 100px;
            font-style: italic;
        }}
        
        /* Markdown Styles */
        h3 {{ color: var(--accent-color); font-size: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; margin-top: 30px; }}
        h4 {{ color: #cbd5e1; font-size: 14px; margin-top: 20px; }}
        p {{ line-height: 1.7; font-size: 15px; color: #cbd5e1; }}
        ul {{ color: #cbd5e1; }}
        li {{ margin-bottom: 6px; line-height: 1.6; }}
        strong {{ color: white; font-weight: 600; }}
        
        .raw-badge {{
            display: inline-block;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            background: #334155;
            color: #94a3b8;
            margin-left: 10px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="title">SYSTEM COGNITIVE SNAPSHOT <span class="raw-badge">OPERATOR VIEW ONLY</span></div>
                <div class="subtitle">Not a Report / Not a Recommendation</div>
            </div>
            <div class="controls">
                <select id="dateSelect" onchange="renderSnapshot(this.value)">
                    <!-- Options will be populated by JS -->
                </select>
            </div>
        </div>
        
        <div id="viewer" class="viewer">
            <!-- Content goes here -->
        </div>
    </div>

    <script>
        // Embedded Data
        const SNAPSHOTS = {json_data};
        const DATES = {json.dumps(snapshot_dates)};
        
        function init() {{
            const select = document.getElementById('dateSelect');
            const viewer = document.getElementById('viewer');
            
            if (DATES.length === 0) {{
                select.disabled = true;
                viewer.innerHTML = '<div class="empty-state">No Snapshots Available</div>';
                return;
            }}
            
            // Populate Dropdown
            DATES.forEach(date => {{
                const option = document.createElement('option');
                option.value = date;
                option.text = date;
                select.appendChild(option);
            }});
            
            // Select Latest (Today)
            select.value = DATES[0];
            renderSnapshot(DATES[0]);
        }}
        
        function renderSnapshot(date) {{
            const viewer = document.getElementById('viewer');
            const content = SNAPSHOTS[date];
            
            if (!content) {{
                viewer.innerHTML = '<div class="empty-state">No Snapshot Generated for ' + date + '</div>';
                return;
            }}
            
            viewer.innerHTML = content;
        }}
        
        // Run
        init();
    </script>
</body>
</html>"""

if __name__ == "__main__":
    generator = EconomicHunterSnapshotViewerGenerator(Path("."))
    generator.generate()
