#!/usr/bin/env python3
"""
[NO-DUP-LOCK] CI Guard: Enforce SSOT for run_publish_ui_decision_assets.py
Ensures there is exactly 1 implementation file and at most 1 wrapper shim.
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("[CI Guard] Checking for duplicate run_publish_ui_decision_assets.py scripts...")
    
    # 1. Find all files with the exact name using git ls-files to respect repo tracked files
    try:
        result = subprocess.run(
            ["git", "ls-files", "*/run_publish_ui_decision_assets.py"],
            capture_output=True, text=True, check=True
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error querying git ls-files: {e}")
        sys.exit(1)
        
    print(f"Found {len(files)} files matching 'run_publish_ui_decision_assets.py'.")
    for f in files:
        print(f"  - {f}")
        
    impl_count = 0
    shim_count = 0
    ssot_path = Path("src/ui/run_publish_ui_decision_assets.py")
    
    for f_path in files:
        path = Path(f_path)
        if not path.exists():
            continue
            
        content = path.read_text(encoding="utf-8")
        
        # A shim is defined as a file that explicitly imports the SSOT instead of implementing logic.
        exact_shim_text = 'from src.ui.run_publish_ui_decision_assets import main\nif __name__ == "__main__":\n    main()'
        # Normalize newlines and strip whitespace for precise comparison
        normalized_content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])
        normalized_target = "\n".join([line.strip() for line in exact_shim_text.splitlines() if line.strip()])

        if normalized_content == normalized_target:
            print(f"[{f_path}] -> Identified as EXACT WRAPPER SHIM")
            shim_count += 1
        elif path == ssot_path:
            print(f"[{f_path}] -> Identified as AUTHORITATIVE SSOT")
            impl_count += 1
        else:
            print(f"[{f_path}] -> ERROR: UNKNOWN IMPLEMENTATION / INVALID SHIM CONTENT")
            print(f"Content found:\n{content}")
            impl_count += 1
            
    print("-" * 50)
    print(f"Total SSOT Implementations: {impl_count} (Expected: 1)")
    print(f"Total Wrapper Shims: {shim_count} (Expected: 0 or 1)")
    
    if impl_count > 1:
        print("❌ ERROR: Duplicate publisher implementations detected!")
        print("There must be exactly one logic implementation (src/ui/run_publish_ui_decision_assets.py).")
        sys.exit(1)
        
    if impl_count == 0:
        print("❌ ERROR: Main publisher SSOT not found at expected path (src/ui/run_publish_ui_decision_assets.py).")
        sys.exit(1)
        
    if shim_count > 1:
        print("❌ ERROR: Too many wrapper shims detected. Maintain at most one.")
        sys.exit(1)
        
    print("✅ [OK] SSOT Publisher lock validated. No duplicates found.")
    sys.exit(0)

if __name__ == "__main__":
    main()
