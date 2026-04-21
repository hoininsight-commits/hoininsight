import sys
from datetime import datetime


def run_pipeline():
    print(f"\n{'='*50}")
    print(f"HOIN Insight v3.0 파이프라인 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    results = {
        "agent_status": {
            "collector": "WAITING",
            "learner": "WAITING",
            "detector": "WAITING",
            "analyst": "WAITING",
            "writer": "WAITING",
            "fact_checker": "WAITING",
            "publisher": "WAITING"
        }
    }

    # AGENT-01: COLLECTOR
    try:
        from src.agents.collector import CollectorAgent
        agent01 = CollectorAgent()
        results["collector"] = agent01.run()
        results["agent_status"]["collector"] = "SUCCESS"
        print("✅ AGENT-01 COLLECTOR 완료")
    except Exception as e:
        print(f"❌ AGENT-01 실패: {e}")
        results["agent_status"]["collector"] = "FAIL"
        sys.exit(1)

    # AGENT-02: LEARNER (YT Transcript Learning)
    try:
        from src.agents.learner import LearnerAgent
        agent02 = LearnerAgent()
        # Learner는 보통 백그라운드에서 동작하지만 여기선 상태 체크만 수행
        results["agent_status"]["learner"] = "SUCCESS"
        print("✅ AGENT-02 LEARNER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-02 실패 (건너뜀): {e}")
        results["agent_status"]["learner"] = "FAIL"

    # AGENT-03: DETECTOR
    try:
        from src.agents.detector import DetectorAgent
        agent03 = DetectorAgent()
        results["detector"] = agent03.run(results.get("collector", {}))
        results["agent_status"]["detector"] = "SUCCESS"
        print("✅ AGENT-03 DETECTOR 완료")
    except Exception as e:
        print(f"❌ AGENT-03 실패: {e}")
        results["agent_status"]["detector"] = "FAIL"
        sys.exit(1)

    # AGENT-04: ANALYST
    try:
        from src.agents.analyst import AnalystAgent
        agent04 = AnalystAgent()
        results["analyst"] = agent04.run(results.get("detector", {}))
        results["agent_status"]["analyst"] = "SUCCESS"
        print("✅ AGENT-04 ANALYST 완료")
    except ImportError as e:
        print(f"⚠️ AGENT-04 패키지 없음 (건너뜀): {e}")
        results["agent_status"]["analyst"] = "FAIL"
    except Exception as e:
        print(f"⚠️ AGENT-04 실패 (계속 진행): {e}")
        results["agent_status"]["analyst"] = "FAIL"

    # AGENT-05: WRITER
    try:
        from src.agents.writer import WriterAgent
        agent05 = WriterAgent()
        results["writer"] = agent05.run(results.get("analyst", {}))
        results["agent_status"]["writer"] = "SUCCESS"
        print("✅ AGENT-05 WRITER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-05 실패 (계속 진행): {e}")
        results["agent_status"]["writer"] = "FAIL"

    # AGENT-05.5: FACT_CHECKER (NEW)
    try:
        from src.agents.fact_checker import FactCheckerAgent
        agent055 = FactCheckerAgent()
        results["fact_checker"] = agent055.run(results.get("writer", {}))
        
        if results["fact_checker"].get("status") == "FAIL":
            print("🛑 AGENT-05.5 팩트체크 실패. 퍼블리싱을 중단합니다.")
            results["agent_status"]["fact_checker"] = "FAIL"
            return # 중단
            
        results["agent_status"]["fact_checker"] = "SUCCESS"
        print("✅ AGENT-05.5 FACT_CHECKER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-05.5 실패 (계속 진행): {e}")
        results["agent_status"]["fact_checker"] = "FAIL"

    # 시스템 상태 취합 및 로깅 (지시서 #076)
    try:
        from src.monitoring.system_state import update_fallback_stats, get_system_state
        from src.validation.quality_score import calculate_quality_score
        
        # 1. Fallback 사용 여부 판단 (에이전트별 fallback_used 플래그 확인)
        is_fallback_run = False
        if results.get("analyst") and isinstance(results["analyst"], dict):
            analysis_data = results["analyst"].get("analysis", {})
            if analysis_data.get("fallback_used"):
                is_fallback_run = True
        if results.get("writer") and isinstance(results["writer"], dict):
            if results["writer"].get("fallback_used"):
                is_fallback_run = True
                
        update_fallback_stats(is_fallback_run)
        
        # 2. 품질 점수 계산 (최종 Writer 결과물 기준)
        q_score = 0
        if "writer" in results and results["writer"]:
            q_score = calculate_quality_score(results["writer"], is_fallback=is_fallback_run)
            
        # 3. 브리핑 데이터에 상태 주입
        state, reason = get_system_state()
        
        # 추가 지표 로드 (#077)
        gemini_status = "UNKNOWN"
        fallback_ratio = 0.0
        try:
            health = json.loads(Path("data/monitoring/gemini_health.json").read_text())
            stats = json.loads(Path("data/logs/fallback_stats.json").read_text())
            gemini_status = health.get("status", "UNKNOWN")
            fallback_ratio = stats.get("fallback_ratio", 0.0)
        except: pass

        results["engine_status"] = {
            "system_state": state,
            "reason": reason,
            "gemini_health": gemini_status,
            "fallback_ratio": fallback_ratio,
            "quality_score": q_score,
            "fallback_run": is_fallback_run
        }
        
    except Exception as e:
        print(f"⚠️ 모니터링 로그 업데이트 실패: {e}")

    # AGENT-06: PUBLISHER
    try:
        from src.agents.publisher import PublisherAgent
        agent06 = PublisherAgent()
        results["agent_status"]["publisher"] = "SUCCESS"
        results["publisher"] = agent06.run(results)
        print("✅ AGENT-06 PUBLISHER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-06 실패 (건너뜀): {e}")
        results["agent_status"]["publisher"] = "FAIL"

    print(f"\n{'='*50}")
    print(f"파이프라인 완료 | 엔진 상태: {results.get('engine_status', {}).get('system_state', 'UNKNOWN')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_pipeline()
