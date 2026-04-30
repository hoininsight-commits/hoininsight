import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 경로 설정
sys.path.append(os.getcwd())

from src.topic_engine.sentry import SentryAgent

class HunterScheduler:
    """
    [v17.0] The Intelligent Hunter Scheduler
    6시간 주기 구동을 관리하며, 비용 최적화와 지능적 실행을 담당함.
    """

    def __init__(self):
        self.sentry = SentryAgent()
        self.base_dir = Path(os.getcwd())
        self._reset_session_cost()

    def _reset_session_cost(self):
        session_path = Path("data/monitoring/session_cost.json")
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps({"session_cost": 0.0, "start_time": datetime.now().isoformat()}))

    def run_cycle(self, force=False):
        print(f"\n🔔 [SCHEDULER] 6시간 주기 사냥 감지 시작 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")

        # 1. Sentry 가동 (사냥 가치 판단) - 더 이상 Learner를 기다리지 않음
        print("🔍 [SCHEDULER] 1단계: 시장 보초(Sentry) 가동")
        
        # 최신 데이터 로드
        news, market_change = self._get_latest_market_pulse()
        
        if force:
            print("  [SCHEDULER] 강제 실행 모드 (Force Run)")
            decision = {"trigger_hunter": True, "impact_score": 10.0, "reason": "Manual Override"}
        else:
            decision = self.sentry.check_market_volatility(news, market_change)
            if not decision:
                print("  ⚠️ [SENTRY] AI 호출 실패. 폴백(HUNT) 모드로 진행합니다.")
                decision = {"trigger_hunter": True, "impact_score": 50, "reason": "AI Sentry Offline - Forced Hunt"}
            print(f"  [SENTRY 결과] 점수: {decision.get('impact_score')}, 사유: {decision.get('reason')}")

        # 3. Hunter 엔진 (Full Pipeline) 트리거 결정
        if self.sentry.should_trigger(decision):
            print("🚀 [SCHEDULER] 3단계: 사냥 가치 충분! Hunter 엔진 가동...")
            self._trigger_full_pipeline()
        else:
            print("💤 [SCHEDULER] 3단계: 사냥 가치 미달. Hunter 엔진 수면 모드 유지 (비용 절감)")

    def _get_latest_market_pulse(self) -> tuple:
        """최신 뉴스 헤드라인과 시장 변동폭 추출"""
        today = datetime.now().strftime("%Y%m%d")
        news_path = self.base_dir / f"data/raw/{today}/sentiment.json"
        market_path = self.base_dir / f"data/raw/{today}/market.json"
        
        headlines = []
        change = 0.0
        
        try:
            if news_path.exists():
                news_data = json.loads(news_path.read_text(encoding="utf-8"))
                headlines = [h["title"] for h in news_data.get("data", {}).get("news_headlines", [])]
            
            if market_path.exists():
                market_data = json.loads(market_path.read_text(encoding="utf-8"))
                change = market_data.get("data", {}).get("kospi_1d_change", 0.0)
        except:
            pass
            
        return headlines, change

    def _trigger_full_pipeline(self):
        """기존의 run_engine.py 로직 또는 개별 에이전트 순차 실행"""
        # 여기서는 기존 에이전트들을 순차적으로 호출하거나, subprocess로 run_engine.py 실행
        import subprocess
        try:
            # PYTHONPATH 설정 유지하며 실행
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}"
            
            # 1. Detector 가동
            print("  [Hunter] DetectorAgent 가동...")
            subprocess.run(["python3", "src/agents/detector.py"], env=env, check=True)
            
            # 2. Writer 가동 (스크립트 생성)
            print("  [Hunter] WriterAgent 가동...")
            subprocess.run(["python3", "src/agents/writer.py"], env=env, check=True)
            
            # 3. Publisher 가동 (브리핑 생성)
            print("  [Hunter] PublisherAgent 가동...")
            subprocess.run(["python3", "src/agents/publisher.py"], env=env, check=True)
            
            print("✅ [Hunter] 전체 사냥 파이프라인 완료.")
        except Exception as e:
            print(f"  ❌ [Hunter] 파이프라인 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    # 인자 처리: --force 있으면 강제 실행
    force_run = "--force" in sys.argv
    scheduler = HunterScheduler()
    scheduler.run_cycle(force=force_run)
