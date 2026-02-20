import sys
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def main():
    print("=== [VERIFY] IS-73 Main Dashboard Opening Sentence ===")
    
    docs_index = ROOT_DIR / "docs" / "index.html"
    if not docs_index.exists():
        print(f"[FAIL] docs/index.html does not exist")
        sys.exit(1)
        
    content = docs_index.read_text(encoding="utf-8")
    
    # 1. Check for IS-73 Header
    is73_markers = [
        "오늘의 핵심 한 문장",
        "📌 오늘의 핵심 한 문장 (Operator Decision)",
        "opening-sentence-container" 
    ]
    
    found_marker = False
    for m in is73_markers:
        if m in content:
            print(f"[PASS] Found IS-73 marker: '{m}'")
            found_marker = True
            break
            
    if not found_marker:
        print("[FAIL] No IS-73 Opening Sentence marker found in docs/index.html")
        # Print snippet for debugging
        print("--- CONTENT SNIPPET ---")
        print(content[:500])
        print("-----------------------")
        sys.exit(1)
        
    # 2. Check for IS-84 markers (optional but good to have)
    if "Long-form Script" in content:
        print("[PASS] Found IS-84 Script marker")
    else:
        print("[WARN] IS-84 Script marker not found (Check if data exists)")

    print("\n✅ IS-73 Dashboard Verification Complete!")

if __name__ == "__main__":
    main()
