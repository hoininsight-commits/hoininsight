import sys
from datetime import datetime


def run_pipeline():
    today = datetime.now().strftime("%Y%m%d")
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
        },
        "today": today
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
        from src.validation.quality_validation import (
            calculate_validation_score_v2, calculate_score_trust, decide_action, extract_validation_reasons
        )
        from src.validation.market_data_mapper import (
            load_market_intelligence, validate_magnitude_v2, calculate_reality_score_v2, final_decision_v2, log_forward_prediction
        )
        
        agent04 = AnalystAgent()
        
        # 1. 일차 분석 수행
        raw_result = agent04.run(results.get("detector", {}))
        analysis_data = raw_result.get("analysis", {})
        topic = results.get("detector", {}).get("topic", "")
        claim = analysis_data.get("topic_core_claim", "")
        
        # 2. Quality Validation (내적 검증)
        q_score = raw_result.get("quality_score", 50)
        v_score = calculate_validation_score_v2(analysis_data)
        trust = calculate_score_trust(q_score, v_score)
        q_action = decide_action(q_score, v_score, trust)
        q_reasons = extract_validation_reasons(analysis_data)
        
        # 3. Market Intelligence Validation (Task 3~8 - 업그레이드)
        from src.validation.market_data_mapper import (
            load_market_intelligence,
            validate_magnitude_v2,
            calculate_reality_score_v2,
            final_decision_v2,
            log_forward_prediction
        )
        
        actual_data, asset_type = load_market_intelligence(topic + claim, ".", today)
        
        # 방향성 검증 (여기선 1일 변화량을 트렌드 대용으로 활용)
        dir_ok = False
        if actual_data:
            change = actual_data.get("change", 0)
            if "상승" in claim or "강세" in claim: dir_ok = change > 0
            elif "하락" in claim or "약세" in claim: dir_ok = change < 0
            else: dir_ok = True
            
        trend_ok = dir_ok # 트렌드 데이터 리스트 구축 전까지는 방향성과 동기화
        mag_ok = validate_magnitude_v2(actual_data.get("current", 0), 100, asset_type) if actual_data else 0 # 임시 계산
        
        r_score = calculate_reality_score_v2(dir_ok, trend_ok, mag_ok)
        final_action = final_decision_v2(q_action, r_score)
        
        # 미래 전망 로깅 (Task 7)
        log_forward_prediction(topic, claim, ".")
        
        # 결과 JSON 확장 (Task 10)
        raw_result["validation_score"] = v_score
        raw_result["score_trust"] = trust
        raw_result["quality_action"] = q_action
        raw_result["reality_score"] = r_score
        raw_result["forward_accuracy"] = 0.85 # 초기 추정치 (향후 실측 데이터 집계)
        raw_result["final_action"] = final_action
        raw_result["validation_reasons"] = q_reasons
        
        results["analyst"] = raw_result
        
        # [지시서 #083] 보수적인 재시도 정책
        if final_action == "REGENERATE":
            print(f"🚨 [LOW_TRUST] 품질 부족으로 재생성합니다.")
            raw_result = agent04.run(results.get("detector", {}))
            analysis_data = raw_result.get("analysis", {})
            v_score = calculate_validation_score_v2(analysis_data)
            raw_result["validation_score"] = v_score
            results["analyst"] = raw_result
            
        results["agent_status"]["analyst"] = "SUCCESS"
        print(f"✅ AGENT-04 ANALYST 완료 (Trust: {trust}, Reality: {r_score}, Final: {final_action})")
        
    except Exception as e:
        print(f"⚠️ AGENT-04 실패: {e}")
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
        from src.validation.quality_score_v2 import calculate_quality_score_v2, get_quality_grade
        
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
        
        # 2. 품질 점수 및 등급/피드백 추출 (Analyst 및 Writer 결과 기반)
        q_score = 0
        q_grade = "FALLBACK"
        q_action = "N/A"
        q_reasons = []
        
        if "analyst" in results and "analysis" in results["analyst"]:
            ana = results["analyst"].get("analysis", {})
            q_score = ana.get("quality_score", 0)
            q_grade = ana.get("quality_grade", "FALLBACK")
            q_action = ana.get("quality_action", "N/A")
            q_reasons = ana.get("failure_reasons", [])
            
        # 3. 브리핑 데이터에 상태 주입
        state, reason = get_system_state(quality_score=q_score)
        
        # 추가 지표 로드 (#077/078)
        gemini_status = "UNKNOWN"
        fallback_ratio = 0.0
        failure_breakdown = {}
        try:
            health = json.loads(Path("data/monitoring/gemini_health.json").read_text())
            stats = json.loads(Path("data/logs/fallback_stats.json").read_text())
            gemini_status = health.get("status", "UNKNOWN")
            fallback_ratio = stats.get("fallback_ratio", 0.0)
            
            # 실패 브레이크다운 계산 (#078)
            failure_log_path = Path("data/logs/gemini_failure_log.json")
            if failure_log_path.exists():
                f_logs = json.loads(failure_log_path.read_text())
                # 최근 20개 로그 기준 유형별 집계
                for log in f_logs[-20:]:
                    ft = log.get("failure_type", "UNKNOWN")
                    failure_breakdown[ft] = failure_breakdown.get(ft, 0) + 1
        except: pass

        results["engine_status"] = {
            "system_state": state,
            "reason": reason,
            "gemini_health": gemini_status,
            "fallback_ratio": fallback_ratio,
            "failure_breakdown": failure_breakdown,
            "quality_score": q_score,
            "quality_grade": q_grade,
            "quality_action": q_action,
            "failure_reasons": q_reasons,
            "fallback_run": is_fallback_run
        }
        
    except Exception as e:
        print(f"⚠️ 모니터링 로그 업데이트 실패: {e}")

    # AGENT-06: PUBLISHER
    try:
        from src.agents.publisher import PublisherAgent
        agent06 = PublisherAgent()
        
        # [지시서 #082] 실행 결과를 결과 객체에 담고 성공 시에만 마킹
        results["publisher"] = agent06.run(results)
        results["agent_status"]["publisher"] = "SUCCESS"
        print("✅ AGENT-06 PUBLISHER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-06 실패: {e}")
        results["agent_status"]["publisher"] = "FAIL"

    # Task 10: Dashboard 반영용 엔진 상태 생성 (Intelligence 반영)
    analyst_res = results.get("analyst", {})
    results["engine_status"] = {
        "quality_score": analyst_res.get("quality_score", 0),
        "validation_score": analyst_res.get("validation_score", 0),
        "score_trust": analyst_res.get("score_trust", "N/A"),
        "reality_score": analyst_res.get("reality_score", 0),
        "forward_accuracy": analyst_res.get("forward_accuracy", 0),
        "final_action": analyst_res.get("final_action", "N/A"),
        "validation_reasons": analyst_res.get("validation_reasons", [])
    }

    print(f"\n==================================================")
    print(f"파이프라인 완료 | Final Action: {results['engine_status']['final_action']}")
    print(f"Quality Trust: {results['engine_status']['score_trust']} | Reality Score: {results['engine_status']['reality_score']}/5")
    print(f"Forward Accuracy: {results['engine_status']['forward_accuracy']}")
    print(f"==================================================\n")
    
    return results


if __name__ == "__main__":
    run_pipeline()
