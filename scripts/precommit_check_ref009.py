import subprocess
import sys
import os
from pathlib import Path

def run_precommit():
    print("--- REF-009 Pre-commit Guard ---")
    
    # Run the scanner
    # In a real hook, we'd check 'git diff --cached'
    # For now, we run the full verify script as a mandatory check
    res = subprocess.run(["python3", "tests/verify_ref009_no_new_legacy.py"])
    
    if res.returncode != 0:
        print("\n❌ Commit Rejected: New legacy patterns detected in non-legacy files.")
        sys.exit(1)
        
    print("✅ Pre-commit Check Passed.")

if __name__ == "__main__":
    run_precommit()
