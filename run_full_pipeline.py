
import os
import sys
from pathlib import Path

# PYTHONPATH 설정 (src 모듈을 찾기 위함)
sys.path.append(str(Path(__file__).resolve().parent))
os.environ["PYTHONPATH"] = str(Path(__file__).resolve().parent)

def main():
    steps = [
        ("COLLECTOR", "src/agents/collector.py"),
        ("DETECTOR", "src/agents/detector.py"),
        ("WRITER", "src/agents/writer.py"),
        ("PUBLISHER", "src/agents/publisher.py")
    ]
    
    pipeline_results = {}
    for name, path in steps:
        print(f"\n{'='*50}")
        print(f"🚀 STEP: {name}")
        print(f"{'='*50}")
        
        try:
            if name == "COLLECTOR":
                from src.agents.collector import CollectorAgent
                pipeline_results["collector"] = CollectorAgent().run()
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
