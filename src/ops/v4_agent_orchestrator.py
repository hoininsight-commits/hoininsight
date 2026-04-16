"""
HOIN Insight v4.0 Agent Orchestrator
연결: Collector -> Detector -> Analyst(검증자) -> Writer(스크립트작성자) -> Publisher
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.collector import CollectorAgent
from src.agents.detector import DetectorAgent
from src.agents.analyst import AnalystAgent
from src.agents.writer import WriterAgent
from src.agents.publisher import PublisherAgent

def run_v4_pipeline():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🚀 [{today}] HOIN Insight v4.0 Pipeline 가동\n")
    print("="*50)

    try:
        # 1. 데이터 수집 (Collector)
        print("\n[Step 1] 데이터 수집 시작 (Collector)...")
        collector = CollectorAgent()
        collector.run()

        # 2. 이상징후 탐지 (Detector)
        print("\n[Step 2] 이상징후 탐지 시작 (Detector)...")
        detector = DetectorAgent()
        detector_result = detector.run()

        if not detector_result.get("selected") or not detector_result["selected"].get("selected"):
            print("  ⚠️ 중요 신호 없음 - 파이프라인 중단")
            return

        # 3. 신호 검증 (Analyst / 검증자)
        print("\n[Step 3] 신호 정밀 검증 시작 (Analyst)...")
        analyst = AnalystAgent()
        analyst.run()

        # 4. 스크립트 집필 (Writer / 스크립트작성자)
        print("\n[Step 4] 경제사냥꾼 스크립트 집필 시작 (Writer)...")
        writer = WriterAgent()
        writer.run()

        # 5. 최종 배포 (Publisher)
        print("\n[Step 5] 대시보드 및 결과 배포 시작 (Publisher)...")
        publisher = PublisherAgent()
        publisher.run()

        print(f"\n✨ [{datetime.now().strftime('%H:%M:%S')}] v4.0 Pipeline 완결")

    except Exception as e:
        print(f"\n❌ 파이프라인 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_v4_pipeline()
