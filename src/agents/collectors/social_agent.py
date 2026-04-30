# src/agents/collectors/social_agent.py

import json
import os
from pathlib import Path
from datetime import datetime
from src.utils.target_date import get_target_ymd, get_current_round
from src.agents.collectors.social_prediction_collector import SocialPredictionCollector
from src.agents.collectors.last30days_collector import Last30DaysCollector

class SocialAgent:
    """[TASK #104] Social & Prediction Market Intelligence Agent"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.name = "SocialAgent"
        self.ttl_minutes = 240  # 4시간
        self.sensitivity = "MID"
        self.collector = SocialPredictionCollector()
        self.deep_collector = Last30DaysCollector()

    def run(self) -> dict:
        print(f"🚀 SocialAgent 가동: Deep Research & 소셜 트렌드 분석 시작")
        
        # 1. 실제 데이터 기반 검색 키워드 동적 로드
        search_keywords = ["Market", "Economy", "AI", "Nvidia"]
        try:
            sentiment_path = self.output_dir / "sentiment.json"
            # (생략: 기존 sentiment.json 로직과 동일하게 작동하도록 구성)
            # 실제 파일 시스템에서 sentiment.json을 찾는 로직 유지
            if not sentiment_path.exists():
                raw_root = self.output_dir.parent.parent # data/raw/YYYYMMDD
                latest_rounds = sorted(raw_root.glob("*"), reverse=True)
                for d in latest_rounds:
                    if d.is_dir():
                        p = d / "sentiment.json"
                        if p.exists():
                            sentiment_path = p
                            break
            
            if sentiment_path.exists():
                sentiment_data = json.loads(sentiment_path.read_text())
                headlines = sentiment_data.get("data", {}).get("news_headlines", [])
                titles = " ".join([h.get("title", "") for h in headlines[:20]]).lower()
                
                dynamic_keywords = []
                if "hormuz" in titles or "oil" in titles: dynamic_keywords.append("Oil Supply")
                if "fed" in titles or "interest" in titles: dynamic_keywords.append("Interest Rates")
                if "nvidia" in titles or "semiconductor" in titles or "삼성" in titles: dynamic_keywords.append("Semiconductor")
                if "trump" in titles: dynamic_keywords.append("Trump")
                if "openai" in titles or "ai" in titles: dynamic_keywords.append("AI")
                
                if dynamic_keywords:
                    search_keywords = list(set(dynamic_keywords))
                    print(f"  🔍 실시간 추출 키워드: {search_keywords}")
        except Exception as e:
            print(f"  ⚠️ 키워드 추출 중 오류: {e}")

        try:
            # 2. 기존 Collector (Polymarket, HN) 실행 - Baseline
            base_data = self.collector.collect_all(search_keywords)
            
            # 3. Last30Days Collector (Deep Research) 실행
            # 속도를 위해 가장 중요한 상위 2개 키워드만 Deep Research 수행
            deep_reports = []
            for kw in search_keywords[:2]:
                report = self.deep_collector.collect(kw, depth="quick")
                if report:
                    deep_reports.append(report)
            
            deep_data = self.deep_collector.transform_to_social_format(deep_reports)
            
            # 4. 데이터 병합
            merged_data = {
                "polymarket": self._merge_lists(base_data["polymarket"], deep_data["polymarket"], "url"),
                "hacker_news": self._merge_lists(base_data["hacker_news"], deep_data["hacker_news"], "url"),
                "reddit": deep_data["reddit"],
                "x": deep_data["x"],
                "youtube": deep_data["youtube"],
                "github": deep_data["github"]
            }
            
            result_data = {
                "date": datetime.now().strftime("%Y%m%d"),
                "data": merged_data
            }

            result = self._wrap_data(result_data, ttl_minutes=self.ttl_minutes)

            output_path = self.output_dir / "social.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ social.json 통합 저장 완료")
            print(f"  📊 수집 요약: Reddit({len(merged_data['reddit'])}), X({len(merged_data['x'])}), YT({len(merged_data['youtube'])}), PM({len(merged_data['polymarket'])}), HN({len(merged_data['hacker_news'])})")
            
            return {
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH"
            }
        except Exception as e:
            print(f"❌ SocialAgent 실행 실패: {e}")
            import traceback
            traceback.print_exc()
            return {
                "process_success": False,
                "error": str(e)
            }

    def _merge_lists(self, list1: list, list2: list, key: str) -> list:
        combined = {item[key]: item for item in list1}
        for item in list2:
            combined[item[key]] = item
        return list(combined.values())

    def _wrap_data(self, data: dict, ttl_minutes: int) -> dict:
        return {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "ttl_minutes": ttl_minutes,
                "source": "Last30Days-Integrated-Collector"
            },
            "data": data
        }

if __name__ == "__main__":
    today = get_target_ymd().replace("-", "")
    current_round = get_current_round()
    out_dir = Path(f"data/raw/{today}/{current_round}")
    agent = SocialAgent(output_dir=out_dir)
    agent.run()

