# src/engine.py
# HOIN Insight Pipeline Entry Point (Loop Protection & Timeout v1.1)

import time
import sys, os
from src.pipeline import run_pipeline

# Phase 3 Task 5: Pipeline 재진입 차단 가드
EXECUTION_GUARD = set()
START_TIME = time.time()
TIMEOUT_SECONDS = 600 # 10분 하드 리밋

def run_guarded_pipeline():
    stage = "PIPELINE_MAIN"
    
    # Phase 5 Task 6: 중복 진입 체크 (경고 후 리턴)
    if stage in EXECUTION_GUARD:
        print(f"⚠️ [LOOP_DETECTED] Stage '{stage}' already executed. Skipping to prevent recursion.")
        return
    
    EXECUTION_GUARD.add(stage)
    
    print(f"🚀 파이프라인 엔진 가동 (타임아웃: {TIMEOUT_SECONDS}s)")
    
    try:
        # 실행 시간 체크용 래퍼 (심플 버전)
        run_pipeline()
        
        # 전체 실행 시간 검증
        elapsed = time.time() - START_TIME
        if elapsed > TIMEOUT_SECONDS:
            print(f"❌ [TIMEOUT] Pipeline exceeded {TIMEOUT_SECONDS}s limit ({elapsed:.1f}s)")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ [ENGINE_CRITICAL] {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_guarded_pipeline()
