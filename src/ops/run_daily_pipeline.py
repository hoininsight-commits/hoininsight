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
    
    import subprocess
    
    try:
        # Run src.engine as a module with project root in PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        print("[Pipeline] Executing: python3 -m src.engine")
        result = subprocess.run(
            [sys.executable, "-m", "src.engine"],
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
        from src.ops.synthesis.topic_synthesizer import TopicSynthesizer
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

def run_issue_signal():
    """Step 88-92: Issue Signal (Economic Hunter Production Line)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 2.7: ISSUE SIGNAL (EH LINE) STARTED")
    try:
        import subprocess
        is_script = project_root / "src" / "ops" / "issuesignal" / "run_issuesignal.py"
        if not is_script.exists():
            print(f"[Pipeline] ❌ Error: run_issuesignal.py not found at {is_script}")
            return False
            
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        result = subprocess.run(
            [sys.executable, str(is_script)],
            cwd=project_root,
            capture_output=True,
            text=True,
            env=env
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[Pipeline] ❌ IssueSignal run failed with code {result.returncode}")
            print(result.stderr)
            return False
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 2.7: ISSUE SIGNAL (EH LINE) COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Error running IssueSignal: {e}")
        traceback.print_exc()
        return False

def run_agent(agent_module: str, description: str):
    """Generic wrapper to run an agent as a module."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> {description} STARTED")
    import subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    try:
        print(f"[Pipeline] Executing: python3 -m {agent_module}")
        result = subprocess.run(
            [sys.executable, "-m", agent_module],
            cwd=project_root,
            capture_output=True,
            text=True,
            env=env
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[Pipeline] ❌ {agent_module} failed with code {result.returncode}")
            print(result.stderr)
            return False
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< {description} COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Error running {agent_module}: {e}")
        return False

def run_memory_update():
    """PHASE Memory Update: Record topics and detect patterns."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE Memory Update: NARRATIVE MEMORY STARTED")
    try:
        from src.memory.narrative_memory_engine import NarrativeMemoryEngine
        from src.memory.narrative_pattern_detector import NarrativePatternDetector
        from src.utils.date_utils import get_kst_ymd
        
        engine = NarrativeMemoryEngine(project_root)
        detector = NarrativePatternDetector(project_root)
        
        target_date = os.environ.get("HOIN_TARGET_DATE")
        ymd = target_date if target_date else get_kst_ymd()
        
        print(f"[Pipeline] Recording topics for {ymd}...")
        engine.record_today_topics(ymd)
        
        print("[Pipeline] Running pattern detection...")
        detector.run_analysis()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE Memory Update: NARRATIVE MEMORY COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Error running Narrative Memory: {e}")
        traceback.print_exc()
        return False

def main():
    print(f"=== HOIN DAILY PIPELINE: {datetime.now().strftime('%Y-%m-%d')} ===\n")
    
    # Step 1: Collect Data
    run_collection()
    
    # Step 2: Run Engine Components
    # 2.1 Narrative Engine (Legacy/Phase 1.5)
    run_narrative_engine()
    
    # 2.2 Core Engine (Structural + Signal Detection)
    # This calls python -m src.engine which covers A1 (redundant but safe) + A2
    success = run_structural_engine()
    
    # 2.3 [A3] Narrative Intelligence Agent (Structural Layers: Regime, Timing, OS)
    # This is critical for generating regime_state.json, investment_os_state.json, etc.
    run_agent("src.ops.agents.narrative_agent", "PHASE 2.3: NARRATIVE AGENT (A3)")

    # 2.4 Topic Synthesis
    run_topic_synthesis()

    # 2.5 HOIN Signal
    run_hoin_signal()
    
    # 2.6 Issue Signal (EH Production Line)
    run_issue_signal()
    
    # 2.7 [A4] Decision Agent (Approval & Final Decision Card)
    run_agent("src.ops.agents.decision_agent", "PHASE 2.7: DECISION AGENT (A4)")
    
    # 2.8 [A5] Video Agent (Script & Stock Linkage)
    run_agent("src.ops.agents.video_agent", "PHASE 2.8: VIDEO AGENT (A5)")

    # 2.9 [STEP-20] Portfolio Relevance Engine (Priority Stock Basket)
    run_agent("src.ops.portfolio_relevance_engine", "PHASE 2.9: PORTFOLIO RELEVANCE ENGINE (STEP-20)")

    # 2.10 [STEP-24] Narrative Memory Engine
    run_memory_update()

    # Step 3: Generate Dashboard & Publishing
    # 3.1 [A6] Publish Agent (SSOT & Delivery)
    run_agent("src.ops.agents.publish_agent", "PHASE 3.1: PUBLISH AGENT (A6)")
    
    # 3.6 System Health Generation
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 3.6: SYSTEM HEALTH GENERATION STARTED")
    try:
        from src.ops.system_health_generator import generate_health_data
        generate_health_data()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 3.6: SYSTEM HEALTH GENERATION COMPLETED")
    except Exception as e:
        print(f"[Pipeline] ⚠️ System Health generation failed: {e}")
        traceback.print_exc()

    # Step 4: Final UI Sync & Contract Verification
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 4: FINAL UI SYNC STARTED")
    try:
        from src.ui.ui_contracts.publish import run_publish
        run_publish(project_root)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 4: UI SYNC COMPLETED")
    except Exception as e:
        print(f"[Pipeline] ⚠️ UI Sync failed (Soft-Fail): {e}")

    if success:
        print("\n=== PIPELINE SUCCESS ===")
        sys.exit(0)
    else:
        print("\n=== PIPELINE FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
