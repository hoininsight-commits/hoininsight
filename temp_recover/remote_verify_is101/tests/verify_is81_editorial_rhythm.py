import os
import json
import shutil
from pathlib import Path
import subprocess

def verify_is81_final():
    print("=== [IS-81] Final E2E Verification Start ===")
    
    base_dir = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
    intel_dir = base_dir / "data" / "intelligence"
    today_json = base_dir / "data" / "dashboard" / "today.json"
    
    # 1. Clear Intelligence data to simulate "Zero Data"
    print("[1] Clearing Intelligence data to force Rhythm Layer supplementation...")
    if intel_dir.exists():
        shutil.rmtree(intel_dir)
    intel_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Run IssueSignal Pipeline
    print("[2] Running IssueSignal Pipeline (run_issuesignal.py) with HOIN_SKIP_CONNECTORS=true...")
    try:
        # We need to make sure we don't have existing candidates in pool
        # For simplicity, we assume pool is empty or we run in a way that forces it.
        env = os.environ.copy()
        env["HOIN_SKIP_CONNECTORS"] = "true"
        result = subprocess.run(["python3", "src/issuesignal/run_issuesignal.py"], 
                                capture_output=True, text=True, cwd=base_dir, env=env)
        if result.returncode != 0:
            print("Pipeline failed!")
            print(result.stdout)
            print(result.stderr)
            return
            
    except Exception as e:
        print(f"Execution failed: {e}")
        return

    # 3. Check today.json
    print("[3] Verifying today.json...")
    if not today_json.exists():
        print("FAIL: today.json missing")
        return
        
    data = json.loads(today_json.read_text(encoding='utf-8'))
    candidates = data.get("blocks", {}).get("editorial_candidates", [])
    print(f"Total candidates in JSON: {len(candidates)}")
    
    if len(candidates) >= 3:
        print("PASS: Quota 3 met.")
    else:
        print(f"FAIL: Only {len(candidates)} candidates.")

    # 4. Trigger Global Dashboard Generator (for docs/index.html)
    print("[4] Updating Global Dashboard (dashboard_generator.py)...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(base_dir)
    subprocess.run(["python3", "src/dashboard/dashboard_generator.py"], cwd=base_dir, env=env)

    # 5. Check both HTML files
    html_targets = [
        base_dir / "data" / "dashboard" / "issuesignal" / "index.html",
        base_dir / "docs" / "index.html"
    ]
    
    for path in html_targets:
        if path.exists():
            content = path.read_text(encoding='utf-8')
            print(f"[5] Checking {path.name}...")
            # Check for Flow summary
            if "콘텐츠" in content and "흐름" in content or "필진" in content:
                 print(f"PASS: Content Flow section found in {path.name}")
            else:
                 print(f"FAIL: Content Flow section missing in {path.name}")
                 
            # Check for Supplement reason
            if "콘텐츠 리듬 유지를 위해 자동 생성됨" in content:
                 print(f"PASS: Supplement reason found in {path.name}")
            else:
                 print(f"FAIL: Supplement reason missing in {path.name}")
        else:
            print(f"FAIL: {path} not found")

    print("=== [IS-81] Verification Complete ===")

if __name__ == "__main__":
    verify_is81_final()
