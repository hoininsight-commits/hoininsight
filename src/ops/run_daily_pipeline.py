"""
Daily Hoin Engine Pipeline Runner
Orchestrates the daily data collection and topic selection process.
Designed to be run by GitHub Actions cron job.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.collectors.ecos_collector import ECOSCollector
from src.collectors.fred_collector import FREDCollector
# Import other collectors as needed or rely on main.py to handle some?
# Actually, main.py usually does "Selection + Insight". Collection is often separate.
# But for a robust daily pipeline, we should ensure collection happens first.

def run_collection():
    """Run all data collectors."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1: DATA COLLECTION STARTED")
    
    # 1. ECOS (Bank of Korea)
    try:
        print("[Pipeline] Running ECOS Collector...")
        ecos = ECOSCollector()
        ecos.collect_all()
    except Exception as e:
        print(f"[Pipeline] ⚠️ ECOS Collector failed (Soft-Fail): {e}")

    # 2. FRED (US Fed)
    try:
        print("[Pipeline] Running FRED Collector...")
        fred = FREDCollector()
        fred.collect_all()
    except Exception as e:
        print(f"[Pipeline] ⚠️ FRED Collector failed (Soft-Fail): {e}")
        
    # 3. Policy (Mock/Static)
    # Import locally to avoid top-level failures if file issues
    try:
        from src.collectors.policy_collector import run_collector as run_policy
        print("[Pipeline] Running Policy Collector...")
        run_policy()
    except Exception as e:
        print(f"[Pipeline] ⚠️ Policy Collector failed (Soft-Fail): {e}")
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1: DATA COLLECTION COMPLETED\n")


def run_engine():
    """Run the main Hoin Engine (Selection -> Insight)."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 2: ENGINE EXECUTION STARTED")
    
    # We call main.py's functionality. 
    # Best way is to import the engine or run it as a subprocess to ensure clean state.
    # Given the complexity, subprocess is safer to avoid polluting the global namespace 
    # or mock-imports from main.py interfering here.
    
    import subprocess
    
    main_script = project_root / "src" / "engine.py"
    if not main_script.exists():
        print(f"[Pipeline] ❌ Error: engine.py not found at {main_script}")
        return False
        
    try:
        # Run src/engine.py
        # You might want to pass specific flags if your main.py supports them (e.g. --auto)
        result = subprocess.run(
            [sys.executable, str(main_script)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Print output for logs
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"[Pipeline] ❌ Engine run failed with code {result.returncode}")
            print("Errors:")
            print(result.stderr)
            return False
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 2: ENGINE EXECUTION COMPLETED")
        return True
        
    except Exception as e:
        print(f"[Pipeline] ❌ Critical Error running Engine: {e}")
        traceback.print_exc()
        return False

def main():
    print(f"=== HOIN DAILY PIPELINE: {datetime.now().strftime('%Y-%m-%d')} ===\n")
    
    # Step 1: Collect Data
    run_collection()
    
    # Step 2: Run Engine
    success = run_engine()
    
    if success:
        print("\n=== PIPELINE SUCCESS ===")
        sys.exit(0)
    else:
        print("\n=== PIPELINE FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
