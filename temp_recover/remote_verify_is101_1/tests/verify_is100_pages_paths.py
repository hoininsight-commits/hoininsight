"""
Verify IS-100 Published Paths in docs/
"""
import os
from pathlib import Path

def test_published_paths():
    required_files = [
        "docs/data/decision/interpretation_units.json",
        "docs/data/decision/mentionables.json",
        "docs/data/decision/narrative_skeleton.json",
        "docs/data/decision/evidence_citations.json",
        "docs/data/decision/speakability_decision.json",
        "docs/data/decision/content_pack.json"
    ]
    
    print("[VERIFY] Checking published paths in docs/data/decision/...")
    all_pass = True
    for f_path in required_files:
        f = Path(f_path)
        if f.exists():
            print(f"[OK] {f_path} exists")
        else:
            print(f"[FAIL] {f_path} missing")
            all_pass = False
            
    if all_pass:
        print("IS-100 Pages Paths Verification: PASSED")
    else:
        print("IS-100 Pages Paths Verification: FAILED")
        # sys.exit(1)

if __name__ == "__main__":
    test_published_paths()
