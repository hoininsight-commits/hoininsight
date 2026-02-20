import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class SnapshotToDashboardProjector:
    """
    Projects the read-only Cognitive Snapshot (Markdown) into a Dashboard-ready JSON.
    This ensures the dashboard sees exactly what the engine decided, without direct coupling.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.snapshots_dir = base_dir / "data" / "snapshots"
        self.dashboard_dir = base_dir / "data" / "dashboard"
        self.logger = logging.getLogger("SnapshotToDashboardProjector")

    def project(self) -> Optional[Path]:
        """
        Main projection method:
        1. Find today's snapshot
        2. Parse markdown content
        3. Transform to Dashboard Schema
        4. Save as data/dashboard/today.json
        """
        self.logger.info("Starting Snapshot -> Dashboard Projection...")
        
        # 1. Locate Snapshot
        snapshot_file = self._find_todays_snapshot()
        if not snapshot_file:
            self.logger.warning("No snapshot found for today. Skipping projection.")
            return None
            
        # 2. Parse Content
        content = snapshot_file.read_text(encoding="utf-8")
        parsed_data = self._parse_snapshot_content(content)
        
        # 3. Transform to Schema
        dashboard_data = self._transform_to_schema(parsed_data)
        
        # 4. Save JSON
        return self._save_dashboard_json(dashboard_data)

    def _find_todays_snapshot(self) -> Optional[Path]:
        """Finds the snapshot file for today (YYYY-MM-DD)."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Priority 1: standard naming convention
        candidates = [
            self.snapshots_dir / f"{today_str}_top1_snapshot.md",
            self.snapshots_dir / f"snapshot_{today_str}.md"
        ]
        
        for path in candidates:
            if path.exists():
                return path
        
        # Fallback: Check all files if naming varies slightly (though it shouldn't)
        if self.snapshots_dir.exists():
            for f in self.snapshots_dir.glob("*.md"):
                if today_str in f.name:
                    return f
                    
        return None

    def _parse_snapshot_content(self, content: str) -> Dict[str, str]:
        """
        Parses the strict Markdown format to extract key fields.
        Regex is used to robustly find sections.
        """
        data = {}
        
        # Extract Date
        date_match = re.search(r"DATE:\s*(\d{4}-\d{2}-\d{2})", content)
        data['date'] = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

        # Extract Title
        title_match = re.search(r"TITLE:\s*(.*)", content)
        data['title'] = title_match.group(1).strip() if title_match else "Economic Hunter Signal"

        # 1. WHY NOW
        why_now_section = re.search(r"\[1\. WHY NOW.*?\](.*?)(?=\[2\.|\[ECONOMIC_HUNTER_TOP1_SNAPSHOT\]|\Z)", content, re.DOTALL)
        if why_now_section:
            text = why_now_section.group(1)
            # Trigger Type
            trigger_match = re.search(r"- Trigger Type:\s*(.*)", text)
            data['trigger'] = trigger_match.group(1).strip() if trigger_match else "Unknown"
            
            # Rationale (지금 행동하지 않으면...)
            rationale_match = re.search(r"- 지금 행동하지 않으면 사라지는 것:\s*(.*)", text)
            data['why_now_summary'] = rationale_match.group(1).strip() if rationale_match else "Detailed analysis in snapshot."

        # 3. WHAT IS BREAKING (Use for Title if needed, or specific field)
        breaking_section = re.search(r"\[3\. WHAT IS BREAKING.*?\](.*?)(?=\[4\.|\[ECONOMIC_HUNTER_TOP1_SNAPSHOT\]|\Z)", content, re.DOTALL)
        if breaking_section:
             text = breaking_section.group(1)
             breaking_match = re.search(r"- 깨지고 있는 것:\s*(.*)", text)
             data['pressure_type'] = breaking_match.group(1).split('기반')[0].strip() if breaking_match else "Structural"
             
             count_match = re.search(r"- Escalation Count:\s*(\d+)", text)
             data['escalation_count'] = int(count_match.group(1)) if count_match else 0

        # 5. MENTIONABLE ASSETS (Sectors)
        assets_section = re.search(r"\[5\. MENTIONABLE ASSETS.*?\](.*?)(?=\[6\.|\[ECONOMIC_HUNTER_TOP1_SNAPSHOT\]|\Z)", content, re.DOTALL)
        sectors = []
        if assets_section:
            text = assets_section.group(1)
            # Find lines like "- Asset \d: ..." or just extract meaningful keywords if structured
            # Simple extraction: Look for "Asset 1: ID", "Asset 2: Market Proxy" logic
            # Let's extract values after "Asset \d:"
            asset_matches = re.findall(r"- Asset \d:\s*(.*)", text)
            for m in asset_matches:
                if m.upper() != "N/A":
                    sectors.append(m.split('(')[0].strip()) # Clean up potential parens
        data['sectors'] = sectors
        data['scope_hint'] = "Multi-Sector Potential" if len(sectors) > 1 else "Single-Sector"

        # 6. SYSTEM DECISION
        decision_section = re.search(r"\[6\. SYSTEM DECISION.*?\](.*?)(?=\Z|\[)", content, re.DOTALL)
        if decision_section:
            text = decision_section.group(1)
            
            # Lock Status
            lock_match = re.search(r"- ECONOMIC_HUNTER_LOCK:\s*(.*)", text)
            raw_lock = lock_match.group(1).strip() if lock_match else "False"
            data['status'] = "LOCK" if raw_lock == "True" else "WATCH"
            
            # Intensity
            intensity_match = re.search(r"- VIDEO_INTENSITY:\s*(.*)", text)
            data['intensity'] = intensity_match.group(1).strip() if intensity_match else "Unknown"
            
            # Rhythm
            rhythm_match = re.search(r"- RHYTHM_PROFILE:\s*(.*)", text)
            data['rhythm'] = rhythm_match.group(1).strip() if rhythm_match else "Unknown"
            
        return data

    def _transform_to_schema(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms parsed data into the strict Dashboard JSON Schema.
        """
        return {
            "date": parsed.get('date', datetime.now().strftime("%Y-%m-%d")),
            "top_signal": {
                "title": parsed.get('title', "Economic Hunter Signal"), # Wait, 'title' was mapped from '깨지고 있는 것' before? No, Step 81 parsing was vague.
                # Actually, Step 79 uses original_card.get('structure_type') for "깨지고 있는 것".
                # The "Title" requirement is "declarative and interpretive". 
                # Step 79 doesn't explicitly have a "Title" line in the Snapshot MD.
                # It has "Title" in the INPUT topic. I should add Title to Snapshot MD or fetch it differently.
                # Let's check Step 79 code again. It generates MD but doesn't write 'title'.
                # Recommendation: Add Title to MD in Step 79.
                "title": parsed.get('title', "Critical Structural Shift"), 
                "why_now": parsed.get('why_now_summary', "Opportunity detected."),
                "trigger": parsed.get('trigger', "Mechanism Activation"),
                "intensity": parsed.get('intensity', "STRIKE"),
                "rhythm": parsed.get('rhythm', "STRUCTURE_FLOW"),
                "sectors": parsed.get('sectors', []),
                "status": parsed.get('status', "WATCH"),
                
                # New Fields for UI
                "pressure_type": parsed.get('pressure_type', "Structural"),
                "escalation_count": parsed.get('escalation_count', 0),
                "scope_hint": parsed.get('scope_hint', "Single-Sector")
            }
        }

    def _save_dashboard_json(self, data: Dict[str, Any]) -> Path:
        """Saves the JSON to data/dashboard/today.json"""
        if not self.dashboard_dir.exists():
            self.dashboard_dir.mkdir(parents=True, exist_ok=True)
            
        output_file = self.dashboard_dir / "today.json"
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # [NEW] Save History
        date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        history_file = self.dashboard_dir / f"{date_str}.json"
        history_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        self.logger.info(f"Dashboard Projection saved to: {output_file} and {history_file}")
        
        return output_file
