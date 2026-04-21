import sys
from datetime import datetime


def run_pipeline():
    today = datetime.now().strftime("%Y%m%d")
    print(f"\n{'='*50}")
    print(f"HOIN Insight v3.0 파이프라인 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # [지시서 #087] Content Tier 변환용 가이드 로드
    from src.content.content_tier import map_action_to_tier
    from src.content.script_generator import generate_tiered_script

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
        "content_pack": {
            "TIER_1": [],
            "TIER_2": [],
            "TIER_3": []
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
            load_market_intelligence, calculate_reality_score_v2, log_forward_prediction
        )
        
        agent04 = AnalystAgent()
        
        # [지시서 #081-R] 파이프라인 입력 연동 최적화 (Multi-Topic Content Pack)
        detector_out = results.get("detector", {})
        candidates = detector_out.get("candidates", [])
        
        # [지시서 #081-R] 불리언/비딕셔너리 데이터 방어
        if not isinstance(candidates, list):
            candidates = []
        
        # 만약 후보가 없으면 현재 선정된 토픽(selected)이라도 활용
        if not candidates and isinstance(detector_out.get("selected"), dict):
            candidates = [detector_out.get("selected")]
            
        print(f"\n🚀 총 {len(candidates[:4])}개의 후보 컨텐츠 분석 시작...")
        
        analyst_results = []
        if isinstance(candidates, list):
            for i, cand in enumerate(candidates[:4]):
                # [DEFENSE] 비정상 데이터 타입 필더링
                if not isinstance(cand, dict):
                    continue
                    
                target_topic = cand.get("topic", "N/A")
                print(f"  [{i+1}/{len(candidates[:4])}] 분석 대상: {target_topic[:30]}...")
                
                # 1. 개별 분석 수행
                raw_res = agent04.run(cand)
                analysis_data = raw_res.get("analysis", {})
                q_score = raw_res.get("quality_score", 50)
                
                # 2. 검증 (내적/외적 합산)
                v_score = calculate_validation_score_v2(analysis_data)
                trust = calculate_score_trust(q_score, v_score)
                
                from src.validation.market_data_mapper import final_decision_v3
                actual_data, asset_type = load_market_intelligence(target_topic + analysis_data.get("topic_core_claim", ""), ".", today)
                reality_score = calculate_reality_score_v2(analysis_data, actual_data, asset_type) if actual_data else 0
                
                final_act = final_decision_v3(q_score, v_score, reality_score, trust)
                
                # [Task 7] 미래 전망 로깅
                log_forward_prediction(target_topic, analysis_data.get("topic_core_claim", ""), ".")
                
                # 3. Tier 매핑 및 데이터 구성
                tier = map_action_to_tier(final_act)
                
                # 가공된 데이터 생성
                processed = {
                    "topic": target_topic,
                    "core_claim": analysis_data.get("topic_core_claim", target_topic),
                    "why_now": analysis_data.get("why_now", cand.get("why_now", "분석 중")),
                    "structural_truth": analysis_data.get("structural_truth", "인과관계 분석 중"),
                    "level2_chain": analysis_data.get("level2_chain", []),
                    "quality_score": q_score,
                    "reality_score": reality_score,
                    "score_trust": trust,
                    "final_action": final_act,
                    "content_tier": tier
                }
                
                # 4. 스크립트 생성
                processed["script"] = generate_tiered_script(processed, tier)
                
                # 팩에 추가
                results["content_pack"][tier].append(processed)
                analyst_results.append(processed)
                
                print(f"     -> Result: {final_act} ({tier}) | Reality: {reality_score}")

        results["analyst"] = analyst_results[0] if analyst_results else {}
        results["agent_status"]["analyst"] = "SUCCESS"
        print("✅ AGENT-04 ANALYST (Multi-Pack) 완료")
        
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


    print(f"\n==================================================")
    print(f"파이프라인 완료")
    print(f"==================================================\n")
    
    return results

    
    return results


if __name__ == "__main__":
    run_pipeline()
