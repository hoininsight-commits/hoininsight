import sys
import os
from pathlib import Path

project_root = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
sys.path.append(str(project_root))

from src.dashboard.dashboard_generator import generate_dashboard

try:
    print("Testing dashboard generation...")
    html = generate_dashboard(project_root)
    
    # Write to a test file
    test_out = project_root / "dashboard" / "test_index.html"
    test_out.parent.mkdir(parents=True, exist_ok=True)
    test_out.write_text(html, encoding="utf-8")
    
    print(f"Success! Test dashboard generated at {test_out}")
    print(f"HTML size: {len(html)} characters.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
