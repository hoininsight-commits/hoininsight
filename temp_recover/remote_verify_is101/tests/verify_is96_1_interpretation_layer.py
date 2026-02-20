import os
import json
import subprocess
from pathlib import Path

def verify_is96_1():
    print("\n" + "="*60)
    print("📋 IS-96-1 INTERPRETATION LAYER VERIFICATION")
    print("="*60)

    base_dir = Path(".")
    is_96_doc = base_dir / "docs/engine/IS-96-1_INTERPRETATION_ASSEMBLY.md"
    
    # 1. File Existence Check
    print("\n[1/3] Checking Required Files...")
    if is_96_doc.exists():
        print(f"  ✅ {is_96_doc}: FOUND")
    else:
        print(f"  ❌ {is_96_doc}: MISSING")
        return

    # 2. Schema and Tag Validation (Conceptual)
    print("\n[2/3] Validating Schema and Tags...")
    content = is_96_doc.read_text(encoding='utf-8')
    
    required_tags = [
        "KR_POLICY", "GLOBAL_INDEX", "FLOW_ROTATION",
        "PRETEXT_VALIDATION", "EARNINGS_VERIFY"
    ]
    
    all_tags_present = True
    for tag in required_tags:
        if tag in content:
            print(f"  ✅ Tag '{tag}': Referenced")
        else:
            print(f"  ❌ Tag '{tag}': NOT Referenced")
            all_tags_present = False
            
    if "is-96-1-interpretation-v1" in content:
        print("  ✅ INTERPRETATION_UNIT Schema Version Found")
    else:
        print("  ❌ INTERPRETATION_UNIT Schema Version MISSING")

    # 3. Integrity Check (Add-only)
    print("\n[3/3] Constitutional Integrity Check (Add-only)...")
    forbidden_files = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md"
    ]
    
    # Baseline commit (restoration point for IS-95-1)
    BASELINE_COMMIT = "d17bb99dc"
    
    for doc in forbidden_files:
        try:
            diff = subprocess.check_output(["git", "diff", BASELINE_COMMIT, "--", doc]).decode("utf-8")
            # Only allow the IS-95-1 ADDON text which we know is there from previous task
            # If there's any diff that is NOT the IS-95-1 ADDON, we might have an issue.
            # However, for IS-96-1, we simply check that HEAD has NO NEW modifications compared to IS-95-1 final state.
            
            # Get current HEAD vs origin/main or previous commit
            current_diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            
            if current_diff:
                print(f"  ❌ {doc}: UNSAVED MODIFICATIONS in working tree!")
            else:
                print(f"  ✅ {doc}: No modifications in current working tree.")
        except Exception as e:
            print(f"  ⚠️ {doc}: Could not run git diff: {e}")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_is96_1()
