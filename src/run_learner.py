# src/run_learner.py
# LEARNER (AGENT-02) 단독 실행 스크립트
# 사용법: python3 src/run_learner.py

import sys
import os
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agents.learner import LearnerAgent

def main():
    print("🚀 HOIN Insight LEARNER (유튜브 수집기) 단독 실행 시작")
    try:
        agent = LearnerAgent()
        # 06:00 KST 이전에 어제/오늘 영상을 여유 있게 가져오기 위해 max_videos=10 설정
        result = agent.run(max_videos=10)
        print(f"✅ 수집 완료: 신규 {result.get('new_collected', 0)}개, 스킵 {result.get('skipped', 0)}개")
    except Exception as e:
        print(f"❌ 수집 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
