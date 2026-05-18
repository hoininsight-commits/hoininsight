
import subprocess
import json
import os
import sys
from pathlib import Path

def run_ci_minimal():
    """
    Runs ONLY the core constitutional tests.
    """
    core_tests = [
        "tests/verify_architecture_guards.py",
        "tests/test_registry_ssot_exists.py"
    ]
    
    print("=== [CI MINIMAL] Running Core Constitutional Tests ===")
    
    # We run each test file individual or together
    cmd = ["python3", "-m", "pytest", "-v"] + core_tests
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
        
    exit_code = result.returncode
    
    summary = {
        "tests_run": core_tests,
        "exit_code": exit_code,
        "status": "PASSED" if exit_code == 0 else "FAILED"
    }
    
    # Output dir
    out_dir = Path("data_outputs/ops")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "ci_minimal_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    if exit_code != 0:
        print(f"❌ Core Tests Failed (Exit Code {exit_code})")
        sys.exit(exit_code)
    else:
        print("✅ Core Tests Passed")

if __name__ == "__main__":
    run_ci_minimal()
