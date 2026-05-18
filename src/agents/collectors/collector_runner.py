# src/agents/collectors/collector_runner.py

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from src.utils.target_date import get_target_ymd, get_current_round

from src.agents.collectors.market_agent import MarketAgent
from src.agents.collectors.macro_agent import MacroAgent
from src.agents.collectors.sentiment_agent import SentimentAgent
from src.agents.collectors.dart_agent import DartAgent
from src.agents.collectors.financial_collectors import ConsensusCollector, COTCollector
from src.agents.collectors.putcall_collector import PutCallCollector
from src.agents.collectors.social_agent import SocialAgent
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
        print("🚀 CollectorRunner 시작 — 2단계 종속성 기반 수집 (Social-Priority Mode)")
        start_time = datetime.now()

        # 1단계: 독립적 에이전트 (기초 데이터)
        phase1_categories = {
            "거시경제": [MacroAgent(self.output_dir), ConsensusCollector(self.output_dir)],
            "시장": [MarketAgent(self.output_dir), PutCallCollector(self.output_dir)],
            "스마트머니": [COTCollector(self.output_dir)],
            "감정/뉴스": [SentimentAgent(self.output_dir)],
            "공시": [DartAgent(self.output_dir)]
        }

        # 2단계: 종속적 에이전트 (가공/분석 데이터)
        # SocialAgent는 Sentiment(뉴스) 필요, FlowCollector는 Market/Consensus 필요
        phase2_categories = {
            "수급/흐름": [FlowCollector(self.output_dir)],
            "예측/소셜": [SocialAgent(self.output_dir)]
        }

        results = {}
        failed = []
        all_categories = {**phase1_categories, **phase2_categories}
        category_stats = {cat: {"success": 0, "fail": 0} for cat in all_categories.keys()}
        total_agents = sum(len(agents) for agents in all_categories.values())

        def execute_phase(categories_subset):
            with ThreadPoolExecutor(max_workers=min(len(categories_subset) * 2, 8)) as executor:
                future_to_agent = {}
                for cat, agents in categories_subset.items():
                    for agent in agents:
                        agent_name = agent.name if hasattr(agent, "name") else type(agent).__name__
                        method = getattr(agent, "run", None) or getattr(agent, "collect")
                        future = executor.submit(method)
                        future_to_agent[future] = {"name": agent_name, "category": cat}

                for future in as_completed(future_to_agent):
                    agent_info = future_to_agent[future]
                    agent_name = agent_info["name"]
                    cat = agent_info["category"]
                    
                    try:
                        result = future.result()
                        if isinstance(result, dict) and not result.get("process_success", True):
                            failed.append(agent_name)
                            category_stats[cat]["fail"] += 1
                        else:
                            results[agent_name] = "success"
                            category_stats[cat]["success"] += 1
                    except Exception as e:
                        print(f"  ❌ [{cat}] {agent_name} 중대 오류: {e}")
                        failed.append(agent_name)
                        category_stats[cat]["fail"] += 1

        # Phase 1 실행
        print("  [Phase 1] 기초 데이터 수집 중...")
        execute_phase(phase1_categories)

        # Phase 2 실행
        print("  [Phase 2] 종속 데이터 및 소셜 분석 중...")
        execute_phase(phase2_categories)

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

        # 상태 저장
        status_path = self.output_dir / "collection_status.json"
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✅ CollectorRunner 완료 — {elapsed:.1f}초 (성공: {summary['success_count']}, 실패: {summary['failed_count']})")
        return summary

if __name__ == "__main__":
    today = get_target_ymd().replace("-", "")
    current_round = get_current_round()
    out_dir = Path(f"data/raw/{today}/{current_round}")
    runner = CollectorRunner(output_dir=out_dir)
    runner.run_all()
