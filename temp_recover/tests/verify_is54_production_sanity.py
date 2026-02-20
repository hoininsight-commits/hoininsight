import sys
import subprocess
from pathlib import Path

def test_production_sanity():
    print("[TEST] Verifying IS-54 Production Sanity Checklist...")
    try:
        # Call the actual sanity check module
        subprocess.check_call([sys.executable, "-m", "src.ops.production_sanity_check"])
        print("[PASS] IS-54 Sanity Check passed.")
    except subprocess.CalledProcessError:
        print("[FAIL] IS-54 Sanity Check failed. Mock/Test artifacts detected.")
        sys.exit(1)

if __name__ == "__main__":
    test_production_sanity()
