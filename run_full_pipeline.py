
import os
import sys
from pathlib import Path

# PYTHONPATH 설정 (src 모듈을 찾기 위함)
sys.path.append(str(Path(__file__).resolve().parent))
os.environ["PYTHONPATH"] = str(Path(__file__).resolve().parent)

def main():
    # [v24.4] 파이프라인 시작 시 누적 세션 비용을 0으로 초기화하여 1회 구동 비용만 측정
    try:
        import json
        from datetime import datetime
        session_path = Path("data/monitoring/session_cost.json")
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps({"session_cost": 0.0, "last_updated": datetime.now().isoformat()}))
        print(f"🧹 세션 비용 초기화 완료: {session_path}")
    except Exception as e:
        print(f"⚠️ 세션 비용 초기화 실패: {e}")

    steps = [
        "COLLECTOR",
        "ROTATION",
        "DETECTOR",
        "WRITER",
        "PUBLISHER",
    ]
    
    pipeline_results = {}
    for name in steps:
        print(f"\n{'='*50}")
        print(f"🚀 STEP: {name}")
        print(f"{'='*50}")
        
        try:
            if name == "COLLECTOR":
                from src.agents.collector import CollectorAgent
                pipeline_results["collector"] = CollectorAgent().run()
            elif name == "ROTATION":
                from scripts.rotation_radar import run as rotation_run
                rotation_run()
                pipeline_results["rotation"] = {"status": "ok"}
            elif name == "DETECTOR":
                from src.agents.detector import DetectorAgent
                pipeline_results["detector"] = DetectorAgent().run()
            elif name == "WRITER":
                from src.agents.writer import WriterAgent
                # Detector 결과가 있으면 전달
                det_res = pipeline_results.get("detector", {})
                pipeline_results["writer"] = WriterAgent().run(analyst_results=det_res.get("fact_pack"))
            elif name == "PUBLISHER":
                from src.agents.publisher import PublisherAgent
                # 모든 결과를 Publisher에게 전달하여 대시보드/텔레그램 최종 처리
                pipeline_results["publisher"] = PublisherAgent().run(pipeline_results=pipeline_results)
            
            print(f"\n✅ {name} 완료")
        except Exception as e:
            print(f"\n❌ {name} 실패: {e}")
            import traceback
            traceback.print_exc()
            break
    else:
        print(f"\n{'='*50}")
        print("🏆 모든 파이프라인 공정이 성공적으로 종료되었습니다!")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
