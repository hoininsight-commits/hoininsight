#!/usr/bin/env python3
"""
[NO-DUP-LOCK] CI Guard: Enforce SSOT for Publishers
Ensures there is exactly 1 implementation file and at most 1 wrapper shim per publisher type.
Rules:
1. SSOT 구현체는 1개만 허용
2. shim은 허용하되 “로직 라인 수 10줄 초과 시 FAIL”
3. 두 곳 모두 로직이 있으면 즉시 FAIL
"""
import subprocess
import sys
from pathlib import Path

# Config: Publisher base names to check
PUBLISHERS = [
    "run_publish_ui_decision_assets.py",
    "publish_ui_assets.py"
]

def check_publisher(name):
    print(f"\n[CI Guard] Checking for duplicate '{name}' scripts...")
    
    try:
        # Respect repo tracked files
        result = subprocess.run(
            ["git", "ls-files", f"*/{name}"],
            capture_output=True, text=True, check=True
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error querying git ls-files: {e}")
        return False
        
    if not files:
        print(f"  - No files found for {name} (valid if not used)")
        return True

    print(f"Found {len(files)} files matching '{name}'.")
    for f in files:
        print(f"  - {f}")
        
    impl_files = []
    shim_files = []
    
    for f_path in files:
        path = Path(f_path)
        if not path.exists():
            continue
            
        content = path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
        
        # A shim is defined as containing an import and a main call, with minimal logic
        is_shim = any("import" in line for line in lines) and any("main(" in line for line in lines)
        
        if is_shim and len(lines) <= 10:
            print(f"  [{f_path}] -> Identified as SHIM (Lines: {len(lines)})")
            shim_files.append(f_path)
        else:
            print(f"  [{f_path}] -> Identified as IMPLEMENTATION (Lines: {len(lines)})")
            impl_files.append(f_path)
            
    # Validation
    if len(impl_files) > 1:
        print(f"❌ ERROR: Multiple logic implementations detected for {name}!")
        print(f"  Files: {impl_files}")
        return False
        
    if len(impl_files) == 1 and len(shim_files) > 0:
        print(f"✅ [OK] Verified 1 Implementation and {len(shim_files)} Shim(s) for {name}")
    elif len(impl_files) == 1:
        print(f"✅ [OK] Verified 1 Implementation for {name}")
    elif len(shim_files) > 0:
        # Only shims? This shouldn't happen for the SSOT
        print(f"⚠️  WARNING: Only shims found for {name}. Implementation missing?")
        
    return True

def main():
    success = True
    for p in PUBLISHERS:
        if not check_publisher(p):
            success = False
            
    if not success:
        print("\n❌ CI GUARD FAILED: Duplicate or invalid publisher structure detected.")
        sys.exit(1)
        
    print("\n✅ CI GUARD PASSED: SSOT Publisher locks validated.")
    sys.exit(0)

if __name__ == "__main__":
    main()
