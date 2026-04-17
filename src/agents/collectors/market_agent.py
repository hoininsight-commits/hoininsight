# src/agents/collectors/market_agent.py

import json
from datetime import datetime
from pathlib import Path

class MarketAgent:
    """
    시장 데이터 수집 에이전트
    yfinance 기반 — kospi, vix, wti, gold, dxy, sp500 등
    """
    name = "MARKET"

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def run(self) -> dict:
        print(f"[{self.name}] 수집 시작...")
        try:
            # 기존 collector.py의 collect_market() 로직 그대로 이식
            from src.agents.collector import CollectorAgent 
            # Note: the user specified DataCollector, but the class name in collector.py is CollectorAgent.
            # I will use CollectorAgent because DataCollector doesn't exist. Let me just check this actually.
            # wait, I should verify what the class name is. In the previous task I saw: 
            # if __name__ == "__main__": CollectorAgent().run_all()
            # so the class is CollectorAgent. I'll use CollectorAgent.
            collector = CollectorAgent()
            collector.output_dir = self.output_dir
            # collector = DataCollector(output_dir=self.output_dir)
            result = collector.collect_market()
            print(f"[{self.name}] ✅ 완료")
            return {"agent": self.name, "status": "success", "result": result}
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {"agent": self.name, "status": "failed", "error": str(e)}
