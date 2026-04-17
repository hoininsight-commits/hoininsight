# src/agents/collectors/collector_runner.py

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from src.agents.collectors.market_agent import MarketAgent
from src.agents.collectors.macro_agent import MacroAgent
from src.agents.collectors.sentiment_agent import SentimentAgent
from src.agents.collectors.dart_agent import DartAgent
from src.agents.consensus_collector import ConsensusCollector
from src.agents.cot_collector import COTCollector

class CollectorRunner:
    """
    수집 에이전트 오케스트레이터
    모든 서브에이전트를 병렬 실행하고 결과 취합
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_all(self) -> dict:
        print("🚀 CollectorRunner 시작 — 병렬 수집")
        start_time = datetime.now()

        # 에이전트 목록
        agents = [
            MarketAgent(self.output_dir),
            MacroAgent(self.output_dir),
            SentimentAgent(self.output_dir),
            DartAgent(self.output_dir),
            ConsensusCollector(self.output_dir),
            COTCollector(self.output_dir),
        ]

        results = {}
        failed = []

        # ThreadPoolExecutor로 병렬 실행
        # ConsensusCollector/COTCollector는 run() 메서드 사용
        # 나머지는 run() 메서드 사용
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_agent = {}
            for agent in agents:
                # run() 메서드가 있으면 run(), 없으면 collect() 사용
                method = getattr(agent, "run", None) or getattr(agent, "collect")
                future = executor.submit(method)
                future_to_agent[future] = agent.name if hasattr(agent, "name") else type(agent).__name__

            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_name] = "success"
                    print(f"  ✅ {agent_name} 완료")
                except Exception as e:
                    results[agent_name] = f"failed: {e}"
                    failed.append(agent_name)
                    print(f"  ❌ {agent_name} 실패: {e}")

        elapsed = (datetime.now() - start_time).total_seconds()

        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "run_at": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "total_agents": len(agents),
            "success_count": len(agents) - len(failed),
            "failed_count": len(failed),
            "failed_agents": failed,
            "agent_results": results,
        }

        # 수집 상태 저장
        status_path = self.output_dir / "collection_status.json"
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✅ CollectorRunner 완료 — {elapsed:.1f}초")
        print(f"   성공: {summary['success_count']}/{summary['total_agents']}")
        if failed:
            print(f"   실패: {failed}")

        return summary

if __name__ == "__main__":
    today = datetime.now().strftime("%Y%m%d")
    out_dir = Path(f"data/raw/{today}")
    runner = CollectorRunner(output_dir=out_dir)
    runner.run_all()

