import os
import json
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.dashboard.build_dashboard import DashboardBuilder
from src.issuesignal.dashboard.models import DecisionCard

def verify_is29():
    base_dir = Path(".")
    output_dir = base_dir / "data" / "dashboard" / "issuesignal"
    
    print("--- IS-29 Verification Start ---")
    
    # 1. Clean up or ensure directories
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Trigger Build
    builder = DashboardBuilder(base_dir)
    html_path = builder.build()
    
    # 3. Assertions
    assert html_path.exists(), "index.html missing"
    
    unified_json = output_dir / "unified_dashboard.json"
    assert unified_json.exists(), "unified_dashboard.json missing"
    
    # 4. Check Content Integrity
    with open(unified_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "hoin_evidence" in data, "hoin_evidence missing in JSON"
        assert "link_view" in data, "link_view missing in JSON"
        print(f"Verified Unified JSON: {len(data['hoin_evidence'])} evidence items, {len(data['link_view'])} links.")

    # 5. Check HTML for Tab structure
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        assert 'id="issuesignal"' in html, "Tab 'issuesignal' missing"
        assert 'id="hoinevidence"' in html, "Tab 'hoinevidence' missing"
        assert 'id="linkview"' in html, "Tab 'linkview' missing"
        assert 'UnifiedLinkRow' not in html, "Dataclass leaking into HTML"
        print("Verified HTML Tab structure and safety.")

    print("--- IS-29 Verification SUCCESS ---")

if __name__ == "__main__":
    try:
        verify_is29()
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
