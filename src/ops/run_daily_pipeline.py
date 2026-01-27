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
from src.ops.fact_first_input_loader import load_fact_first_input

def run_collection():
    """Run all data collectors."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1: DATA COLLECTION STARTED")
    
    # 0. Fact-First Input Loader (Operator Seed)
    try:
        print("[Pipeline] Running Fact-First Input Loader...")
        # Use KST date for consistency with loader logic
        # For simplicity in this env, we assume system time or standardizing to KST
        # The loader expects YYYY-MM-DD string.
        # Ensure we pass the correct date string.
        from src.utils.date_utils import get_kst_ymd
        kst_ymd = get_kst_ymd()
    except ImportError:
        # Fallback if date_utils not present
        kst_ymd = datetime.now().strftime("%Y-%m-%d")
        
    try:
        res = load_fact_first_input(project_root, kst_ymd)
        print(f"[Pipeline] Loaded {res['count']} operator facts.")
    except Exception as e:
        print(f"[Pipeline] ⚠️ Fact Loader failed (Soft-Fail): {e}")

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


def run_narrative_engine():
    """Run the Narrative Engine (Phase 1.5)."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.5: NARRATIVE ENGINE STARTED")
    try:
        from src.ops.run_narrative_engine import main as narrative_main
        narrative_main()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.5: NARRATIVE ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Critical Error running Narrative Engine: {e}")
        traceback.print_exc()
        return False


def run_structural_engine():
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
        # Run src/engine.py with project root in PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        result = subprocess.run(
            [sys.executable, str(main_script)],
            cwd=project_root,
            capture_output=True,
            text=True,
            env=env
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

def run_topic_synthesis():
    """Run Topic Synthesis Layer (Phase 2.5)."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 2.5: TOPIC SYNTHESIS STARTED")
    try:
        from src.synthesis.topic_synthesizer import TopicSynthesizer
        synth = TopicSynthesizer(project_root)
        res = synth.run()
        print(f"[Pipeline] Synthesized Topic: {res.get('content_topic', {}).get('title', 'None')}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 2.5: TOPIC SYNTHESIS COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Critical Error running Topic Synthesis: {e}")
        traceback.print_exc()
        return False

def run_hoin_signal():
    """Step 61-g: HOIN Signal Judgement (Parallel Layer)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 2.6: HOIN SIGNAL JUDGEMENT STARTED")
    try:
        from src.ops.hoin_signal_judger import HoinSignalJudger
        judger = HoinSignalJudger(project_root)
        target_date = os.environ.get("HOIN_TARGET_DATE")
        ymd = target_date if target_date else datetime.now().strftime("%Y-%m-%d")
        res = judger.run_judgement(ymd)
        print(f"[Pipeline] Signal Judgement Complete. Found {len(res)} signals.")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 2.6: HOIN SIGNAL JUDGEMENT COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Error running HOIN Signal: {e}")
        return False

def main():
    print(f"=== HOIN DAILY PIPELINE: {datetime.now().strftime('%Y-%m-%d')} ===\n")
    
    # Step 1: Collect Data
    run_collection()
    
    # Step 2: Run Engine
    # 2.1 Narrative Engine (NEW)
    run_narrative_engine()
    
    # 2.2 Structural Engine (Legacy)
    success = run_structural_engine()

    # 2.3 Topic Synthesis (NEW)
    # Merges Event Gate and Structural Output
    run_topic_synthesis()

    # 2.4 HOIN Signal (NEW)
    run_hoin_signal()
    
    # Step 3: Generate Dashboard
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 3: DASHBOARD GENERATION STARTED")
    try:
        from src.dashboard.dashboard_generator import generate_dashboard
        html = generate_dashboard(project_root)
        
        # Write to dashboard/index.html
        dash_out = project_root / "dashboard" / "index.html"
        dash_out.parent.mkdir(parents=True, exist_ok=True)
        dash_out.write_text(html, encoding="utf-8")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 3: DASHBOARD GENERATION COMPLETED ({dash_out})")
    except Exception as e:
        print(f"[Pipeline] ⚠️ Dashboard generation failed: {e}")
        traceback.print_exc()

    if success:
        print("\n=== PIPELINE SUCCESS ===")
        sys.exit(0)
    else:
        print("\n=== PIPELINE FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
