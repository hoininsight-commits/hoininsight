# scripts/run_multi_validation.py
# HOIN Insight Multi-Run Validation Orchestrator (지시서 #081)

import subprocess
import json
import time
from pathlib import Path
from src.validation.multi_run_analysis import analyze_runs, final_system_state_calc

RUNS = 2
DASHBOARD_DATA_PATH = Path("docs/today_data.json")

def load_engine_status():
    """docs/today_data.json에서 현재 엔진 상태 로드"""
    if DASHBOARD_DATA_PATH.exists():
        try:
            data = json.loads(DASHBOARD_DATA_PATH.read_text())
            return data.get("today", {}).get("engine_status", {})
        except:
            pass
    return {}

def run_multi_validation():
    print(f"🚀 [MULTI-RUN] Starting {RUNS} validation runs...")
    
    run_results = []
    
    for i in range(RUNS):
        print(f"\n{'='*30}")
        print(f"  RUN {i+1} / {RUNS}")
        print(f"{'='*30}\n")
        
        # 엔진 실행
        subprocess.run(["python3", "-m", "src.engine"], check=False)
        
        # 결과 취합
        status = load_engine_status()
        if status:
            run_results.append(status)
            print(f"  -> Score: {status.get('quality_score')} | Fallback: {status.get('fallback_ratio')}")
        
        time.sleep(2) # API Rate Limit 방지

    if not run_results:
        print("❌ No results collected. Multi-run validation failed.")
        return

    # 통계 분석
    analysis = analyze_runs(run_results)
    final_state = final_system_state_calc(analysis)
    analysis["final_state"] = final_state

    print(f"\n📊 [VALIDATION REPORT]")
    print(f"  Avg Score: {analysis['avg_score']}")
    print(f"  Variance:  {analysis['variance']}")
    print(f"  Avg FB:    {analysis['avg_fallback']}")
    print(f"  FINAL STATE: {final_state}")

    # 대시보드 반영 (Task 6)
    if DASHBOARD_DATA_PATH.exists():
        data = json.loads(DASHBOARD_DATA_PATH.read_text())
        data["today"]["engine_validation"] = analysis
        DASHBOARD_DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"\n✅ Multi-run results attached to dashboard.")

if __name__ == "__main__":
    run_multi_validation()
