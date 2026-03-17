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


def run_market_benchmark():
    """PHASE 1.2: Market Prediction Benchmark Engine (STEP-33)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.2: MARKET PREDICTION BENCHMARK STARTED")
    try:
        from src.prediction.run_prediction import PredictionRunner
        runner = PredictionRunner(project_root)
        runner.run_all()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.2: MARKET PREDICTION BENCHMARK COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Market Prediction Benchmark failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


def run_contradiction_engine():
    """PHASE 1.3: Market Contradiction Engine (STEP-34)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.3: MARKET CONTRADICTION ENGINE STARTED")
    try:
        from src.engine.contradiction_engine import MarketContradictionEngine
        engine = MarketContradictionEngine(project_root)
        engine.run_all()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.3: MARKET CONTRADICTION ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Market Contradiction Engine failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


        return False


        return False


def run_theme_early_detection_engine():
    """PHASE 1.3.9: Theme Early Detection Engine (STEP-39)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.3.9: EARLY DETECTION STARTED")
    try:
        from src.theme.theme_early_detection_engine import ThemeEarlyDetectionEngine
        engine = ThemeEarlyDetectionEngine(project_root)
        engine.run_detection()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.3.9: EARLY DETECTION COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Theme Early Detection failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


        return False


def run_theme_narrative_engine():
    """PHASE 1.3.9.5: Theme Narrative Engine (STEP-40)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.3.9.5: THEME NARRATIVE STARTED")
    try:
        from src.theme.theme_narrative_engine import ThemeNarrativeEngine
        engine = ThemeNarrativeEngine(project_root)
        engine.run_narrative_expansion()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.3.9.5: THEME NARRATIVE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Theme Narrative failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


        return False


def run_theme_evolution_engine():
    """PHASE 1.3.9.7: Theme Evolution Engine (STEP-41)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.3.9.7: THEME EVOLUTION STARTED")
    try:
        from src.theme.theme_evolution_engine import ThemeEvolutionEngine
        engine = ThemeEvolutionEngine(project_root)
        engine.run_evolution_analysis()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.3.9.7: THEME EVOLUTION COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Theme Evolution failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


        return False


def run_theme_momentum_engine():
    """PHASE 1.3.9.9: Narrative Momentum Engine (STEP-42)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.3.9.9: NARRATIVE MOMENTUM STARTED")
    try:
        from src.theme.theme_momentum_engine import NarrativeMomentumEngine
        engine = NarrativeMomentumEngine(project_root)
        engine.run_momentum_analysis()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.3.9.9: NARRATIVE MOMENTUM COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Narrative Momentum failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


def run_market_story_engine():
    """PHASE 1.4: Market Story Engine (STEP-35)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.4: MARKET STORY ENGINE STARTED")
    try:
        from src.engine.story_engine import MarketStoryEngine
        engine = MarketStoryEngine(project_root)
        engine.run_all()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.4: MARKET STORY ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Market Story Engine failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


        return False


        return False


def run_mentionables_engine():
    """PHASE 1.4.5: Impact & Mentionables Engine (STEP-36)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.4.5: MENTIONABLES ENGINE STARTED")
    try:
        from src.impact.mentionables_engine import MentionablesEngine
        engine = MentionablesEngine(project_root)
        engine.run_analysis()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.4.5: MENTIONABLES ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Mentionables Engine failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


def run_topic_pressure_engine():
    """PHASE 1.4.6: Topic Pressure & Selection Engine (STEP-38)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.4.6: TOPIC PRESSURE ENGINE STARTED")
    try:
        from src.topics.topic_pressure_engine import TopicPressureEngine
        engine = TopicPressureEngine(project_root)
        engine.run_selection()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.4.6: TOPIC PRESSURE ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Topic Pressure Engine failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


def run_script_engine():
    """PHASE 1.4.7: Story-to-Video Script Engine (STEP-37)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 1.4.7: VIDEO SCRIPT ENGINE STARTED")
    try:
        from src.content.script_engine import TodayScriptEngine
        engine = TodayScriptEngine(project_root)
        engine.run_synthesis()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 1.4.7: VIDEO SCRIPT ENGINE COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Video Script Engine failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False


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

        # [STEP-25] Topic Ontology Resolution
        print("[Pipeline] Running Topic Ontology Engine...")
        from src.ontology.topic_ontology_engine import TopicOntologyEngine
        ontology_engine = TopicOntologyEngine(project_root)
        ontology_engine.run_daily_resolution()

        # [STEP-26] Narrative Cycle Detection
        print("[Pipeline] Running Narrative Cycle Detector...")
        from src.memory.narrative_cycle_detector import NarrativeCycleDetector
        cycle_detector = NarrativeCycleDetector(project_root)
        cycle_detector.run_analysis()

        # [STEP-27] Theme Evolution Analysis
        print("[Pipeline] Running Theme Evolution Engine...")
        from src.memory.theme_evolution_engine import ThemeEvolutionEngine
        evolution_engine = ThemeEvolutionEngine(project_root)
        evolution_engine.run_analysis()

        # [STEP-28] Early Topic Detection
        print("[Pipeline] Running Early Topic Detector...")
        from src.ops.early_topic_detector import EarlyTopicDetector
        early_detector = EarlyTopicDetector(project_root)
        early_detector.run_analysis()

        # [STEP-29] Narrative Escalation Analysis
        print("[Pipeline] Running Narrative Escalation Engine...")
        from src.ops.narrative_escalation_engine import NarrativeEscalationEngine
        escalation_engine = NarrativeEscalationEngine(project_root)
        escalation_engine.run_analysis()

        # [橫-30] Operator Action Generation
        print("[Pipeline] Running Operator Action Engine...")
        from src.ops.operator_action_engine import OperatorActionEngine
        action_engine = OperatorActionEngine(project_root)
        action_engine.run_analysis()

        # [STEP-31] Auto Narrative Script Generation
        print("[Pipeline] Running Auto Script Engine...")
        from src.content.auto_script_engine import AutoScriptEngine
        script_engine = AutoScriptEngine(project_root)
        script_engine.run_analysis()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE Memory Update: NARRATIVE MEMORY COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ❌ Error running Narrative Memory: {e}")
        traceback.print_exc()
        return False

def run_operator_brief_builder():
    """PHASE 3.0: Operator Brief Builder (STEP-44)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] >>> PHASE 3.0: OPERATOR BRIEF BUILDER STARTED")
    try:
        from src.ops.build_operator_brief import OperatorBriefBuilder
        builder = OperatorBriefBuilder(project_root)
        builder.build()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] <<< PHASE 3.0: OPERATOR BRIEF BUILDER COMPLETED")
        return True
    except Exception as e:
        print(f"[Pipeline] ⚠️ Operator Brief Builder failed (Soft-Fail): {e}")
        traceback.print_exc()
        return False

def main():
    print(f"=== HOIN DAILY PIPELINE: {datetime.now().strftime('%Y-%m-%d')} ===\n")
    
    # Step 1: Collect Data
    run_collection()
    
    # Step 1.2: [STEP-33] Market Prediction Benchmark
    run_market_benchmark()
    
    # Step 1.3.5: [STEP-34] Market Contradiction Engine
    run_contradiction_engine()
    
    # Step 1.3.9: [STEP-39] Theme Early Detection Engine
    run_theme_early_detection_engine()
    
    # Step 1.3.9.5: [STEP-40] Theme Narrative Engine
    run_theme_narrative_engine()
    
    # Step 1.3.9.7: [STEP-41] Theme Evolution Engine
    run_theme_evolution_engine()
    
    # Step 1.3.9.9: [STEP-42] Narrative Momentum Engine
    run_theme_momentum_engine()
    
    # Step 1.4: [STEP-35] Market Story Engine
    run_market_story_engine()
    
    # Step 1.4.5: [STEP-36] Impact & Mentionables Engine
    run_mentionables_engine()
    
    # Step 1.4.6: [STEP-38] Topic Pressure & Selection Engine
    run_topic_pressure_engine()
    
    # Step 1.4.7: [STEP-37] Video Script Engine
    run_script_engine()
    
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
    # 3.0 [STEP-44] Operator Brief Builder
    run_operator_brief_builder()
    
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
