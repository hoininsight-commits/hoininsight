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
from src.agents.collectors.putcall_collector import PutCallCollector
from src.agents.collectors.flow_collector import FlowCollector

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

        categories = {
            "거시경제": [MacroAgent(self.output_dir), ConsensusCollector(self.output_dir)],
            "시장": [MarketAgent(self.output_dir), PutCallCollector(self.output_dir)],
            "스마트머니": [COTCollector(self.output_dir)],
            "감정/뉴스": [SentimentAgent(self.output_dir)],
            "공시": [DartAgent(self.output_dir)]
        }

        results = {}
        failed = []
        category_stats = {cat: {"success": 0, "fail": 0} for cat in categories.keys()}
        total_agents = sum(len(agents) for agents in categories.values())

        # ThreadPoolExecutor로 병렬 실행
        with ThreadPoolExecutor(max_workers=7) as executor:
            future_to_agent = {}
            for cat, agents in categories.items():
                for agent in agents:
                    # run() 메서드가 있으면 run(), 없으면 collect() 사용
                    method = getattr(agent, "run", None) or getattr(agent, "collect")
                    future = executor.submit(method)
                    agent_name = agent.name if hasattr(agent, "name") else type(agent).__name__
                    future_to_agent[future] = {"name": agent_name, "category": cat}

            for future in as_completed(future_to_agent):
                agent_info = future_to_agent[future]
                agent_name = agent_info["name"]
                cat = agent_info["category"]
                
                try:
                    result = future.result()
                    if isinstance(result, dict) and result.get("status") == "failed":
                        error_msg = result.get("error", "Unknown error")
                        results[agent_name] = f"failed: {error_msg}"
                        failed.append(agent_name)
                        category_stats[cat]["fail"] += 1
                        print(f"  ❌ [{cat}] {agent_name} 실패: {error_msg}")
                    else:
                        results[agent_name] = "success"
                        category_stats[cat]["success"] += 1
                        print(f"  ✅ [{cat}] {agent_name} 완료")
                except Exception as e:
                    results[agent_name] = f"failed: {e}"
                    failed.append(agent_name)
                    category_stats[cat]["fail"] += 1
                    print(f"  ❌ [{cat}] {agent_name} 실패: {e}")

        elapsed = (datetime.now() - start_time).total_seconds()

        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "run_at": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "total_agents": total_agents,
            "success_count": total_agents - len(failed),
            "failed_count": len(failed),
            "failed_agents": failed,
            "category_stats": category_stats,
            "agent_results": results,
        }

        # 수집 상태 저장
        status_path = self.output_dir / "collection_status.json"
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # [EXTENSION] Flow 데이터 레이어 수집 (지시서 #070) — 후처리 성격
        try:
            FlowCollector().run()
            summary["agent_results"]["FlowCollector"] = "success"
        except Exception as e:
            print(f"  ❌ FlowCollector 실행 실패: {e}")
            summary["agent_results"]["FlowCollector"] = f"failed: {e}"

        print(f"\n✅ CollectorRunner 완료 — {elapsed:.1f}초")
        print(f"   성공: {summary['success_count']}/{summary['total_agents']}")
        for cat, stat in category_stats.items():
            print(f"     - {cat}: {stat['success']} 성공, {stat['fail']} 실패")
        if failed:
            print(f"   실패: {failed}")

        return summary

if __name__ == "__main__":
    today = datetime.now().strftime("%Y%m%d")
    out_dir = Path(f"data/raw/{today}")
    runner = CollectorRunner(output_dir=out_dir)
    runner.run_all()

