import os
import sys
import re
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

def verify_is48_ui_reads_ssot():
    print("Testing IS-48: UI reads SSOT...")
    base_dir = Path(".")
    
    # 1. Check loader logic (loader.py)
    loader_path = base_dir / "src/issuesignal/dashboard/loader.py"
    if loader_path.exists():
        content = loader_path.read_text(encoding="utf-8")
        if "latest_index.json" in content:
            print("✅ loader.py references latest_index.json")
        else:
            print("❌ loader.py does NOT reference latest_index.json")
            return False
    
    # 2. Check renderer logic for Korean labels
    renderer_path = base_dir / "src/issuesignal/dashboard/renderer.py"
    if renderer_path.exists():
        content = renderer_path.read_text(encoding="utf-8")
        if "오늘의 확정 인텔리전스" in content and "사전 트리거 감시망" in content:
            print("✅ renderer.py localized to Korean")
        else:
            print("❌ renderer.py localization check failed")
            return False
            
    print("✅ UI SSOT Reference Passed")
    return True

if __name__ == "__main__":
    import sys
    if verify_is48_ui_reads_ssot():
        sys.exit(0)
    else:
        sys.exit(1)
