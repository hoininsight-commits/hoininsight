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
    sensitivity = "HIGH"
    ttl_minutes = 30

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def run(self) -> dict:
        print(f"[{self.name}] 수집 시작...")
        try:
            from src.agents.collector import CollectorAgent 
            collector = CollectorAgent()
            collector.output_dir = self.output_dir
            result = collector.collect_market()
            print(f"[{self.name}] ✅ 완료")
            return {
                "agent": self.name,
                "process_success": True,
                "data_valid": result["metadata"]["freshness_status"] != "UNKNOWN",
                "freshness_status": result["metadata"]["freshness_status"],
                "result": result
            }
        except Exception as e:
            print(f"[{self.name}] ❌ 실패: {e}")
            return {
                "agent": self.name,
                "process_success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    from src.utils.target_date import get_standard_path_prefix
    out = Path("data/raw") / get_standard_path_prefix()
    out.mkdir(parents=True, exist_ok=True)
    MarketAgent(out).run()
