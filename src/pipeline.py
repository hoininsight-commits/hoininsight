import sys
from datetime import datetime


def run_pipeline():
    print(f"\n{'='*50}")
    print(f"HOIN Insight v3.0 파이프라인 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    results = {}

    # AGENT-01: COLLECTOR
    try:
        from src.agents.collector import CollectorAgent
        agent01 = CollectorAgent()
        results["collector"] = agent01.run()
        print("✅ AGENT-01 COLLECTOR 완료")
    except Exception as e:
        print(f"❌ AGENT-01 실패: {e}")
        sys.exit(1)

    # AGENT-03: DETECTOR
    try:
        from src.agents.detector import DetectorAgent
        agent03 = DetectorAgent()
        results["detector"] = agent03.run(results.get("collector", {}))
        print("✅ AGENT-03 DETECTOR 완료")
    except Exception as e:
        print(f"❌ AGENT-03 실패: {e}")
        sys.exit(1)

    # AGENT-04: ANALYST
    try:
        from src.agents.analyst import AnalystAgent
        agent04 = AnalystAgent()
        results["analyst"] = agent04.run(results.get("detector", {}))
        print("✅ AGENT-04 ANALYST 완료")
    except ImportError as e:
        print(f"⚠️ AGENT-04 패키지 없음 (건너뜀): {e}")
    except Exception as e:
        print(f"⚠️ AGENT-04 실패 (계속 진행): {e}")

    # AGENT-05: WRITER
    try:
        from src.agents.writer import WriterAgent
        agent05 = WriterAgent()
        results["writer"] = agent05.run(results.get("analyst", {}))
        print("✅ AGENT-05 WRITER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-05 실패 (계속 진행): {e}")

    # AGENT-05.5: FACT_CHECKER (NEW)
    try:
        from src.agents.fact_checker import FactCheckerAgent
        agent055 = FactCheckerAgent()
        results["fact_checker"] = agent055.run(results.get("writer", {}))
        
        if results["fact_checker"].get("status") == "FAIL":
            print("🛑 AGENT-05.5 팩트체크 실패. 퍼블리싱을 중단합니다.")
            return # 중단
            
        print("✅ AGENT-05.5 FACT_CHECKER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-05.5 실패 (계속 진행): {e}")

    # AGENT-06: PUBLISHER
    try:
        from src.agents.publisher import PublisherAgent
        agent06 = PublisherAgent()
        results["publisher"] = agent06.run(results)
        print("✅ AGENT-06 PUBLISHER 완료")
    except Exception as e:
        print(f"⚠️ AGENT-06 실패 (계속 진행): {e}")

    print(f"\n{'='*50}")
    print("파이프라인 완료")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_pipeline()
