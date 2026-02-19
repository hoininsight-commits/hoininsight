import sys
import os
from pathlib import Path
import subprocess

def verify_ref014():
    print("=== REF-014 VERIFICATION START ===")
    root = Path(os.getcwd())
    
    # 1. Existence of Scaffolding
    expected_dirs = [
        "src/hoin/engine",
        "src/hoin/interpreters",
        "src/hoin/contracts",
        "src/hoin/reporting",
        "src/hoin/ops",
        "src/legacy_shims"
    ]
    for d in expected_dirs:
        if not (root / d).exists():
            print(f"❌ Scaffolding missing: {d}")
            sys.exit(1)
    print("✅ Scaffolding structure verified.")

    # 2. Check for Deletions (git status)
    # We strictly forbid deletion or renaming of existing files.
    status = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8")
    for line in status.splitlines():
        if line.startswith(" D") or line.startswith("R "):
            print(f"❌ VIOLATION: File deletion or rename detected:\n{line}")
            sys.exit(1)
    print("✅ No deletions or renames detected.")
    
    # 3. Import Check (Simple)
    try:
        from src.hoin.engine import orchestrator
        print("✅ New orchestrator importable.")
    except ImportError as e:
        print(f"❌ New orchestrator import failed: {e}")
        sys.exit(1)

    print("=== REF-014 INTERNAL STRUCTURE VERIFIED ===")

if __name__ == "__main__":
    verify_ref014()
