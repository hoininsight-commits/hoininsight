# src/agents/collectors/social_agent.py

import json
import os
from pathlib import Path
from datetime import datetime
from src.collectors.social_prediction import SocialPredictionCollector

class SocialAgent:
    """[TASK #104] Social & Prediction Market Intelligence Agent"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.name = "SocialAgent"
        self.ttl_minutes = 240  # 4시간 (소셜 반응은 조금 느려도 됨)
        self.sensitivity = "MID"
        self.collector = SocialPredictionCollector()

    def run(self) -> dict:
        print(f"🚀 SocialAgent 가동: 실제 뉴스 테마 기반 Deep Research 시작 (Real-Data Mode)")
        
        # 1. 실제 데이터 기반 검색 키워드 동적 로드
        search_keywords = ["Market", "Interest Rates", "Nvidia", "AI", "Oil", "Gold"] # Default fallbacks
        try:
            today_str = datetime.now().strftime("%Y%m%d")
            sentiment_path = self.output_dir / "sentiment.json"
            if not sentiment_path.exists():
                # 어제 폴더 뒤지기
                raw_root = self.output_dir.parent
                latest_dirs = sorted(raw_root.glob("202*"), reverse=True)
                for d in latest_dirs:
                    p = d / "sentiment.json"
                    if p.exists():
                        sentiment_path = p
                        break
            
            if sentiment_path.exists():
                sentiment_data = json.loads(sentiment_path.read_text())
                headlines = sentiment_data.get("data", {}).get("news_headlines", [])
                titles = " ".join([h.get("title", "") for h in headlines[:20]]).lower()
                
                # 유의미한 키워드 추출
                dynamic_keywords = []
                if "hormuz" in titles or "oil" in titles: dynamic_keywords.append("Oil Supply")
                if "fed" in titles or "interest" in titles: dynamic_keywords.append("Interest Rates")
                if "nvidia" in titles or "semiconductor" in titles or "삼성" in titles: dynamic_keywords.append("Semiconductor")
                if "trump" in titles: dynamic_keywords.append("Trump")
                if "openai" in titles or "ai" in titles: dynamic_keywords.append("AI Prediction")
                
                if dynamic_keywords:
                    search_keywords = list(set(dynamic_keywords + ["Market Analysis"]))
                    print(f"  🔍 실시간 추출 키워드: {search_keywords}")
        except Exception as e:
            print(f"  ⚠️ 키워드 추출 중 오류 (기본값 사용): {e}")

        try:
            # 동적 키워드로 수집 수행
            data = self.collector.collect_all(search_keywords)
            
            result_data = {
                "date": datetime.now().strftime("%Y%m%d"),
                "data": data
            }

            # 메타데이터 래핑
            result = self._wrap_data(result_data, ttl_minutes=self.ttl_minutes)

            output_path = self.output_dir / "social.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ social.json 저장 완료 (Polymarket: {len(data['polymarket'])}건, HN: {len(data['hacker_news'])}건)")
            
            return {
                "process_success": True,
                "data_valid": True,
                "freshness_status": "FRESH"
            }
        except Exception as e:
            print(f"❌ SocialAgent 실행 실패: {e}")
            return {
                "process_success": False,
                "error": str(e)
            }

    def _wrap_data(self, data: dict, ttl_minutes: int) -> dict:
        """기존 에이전트들의 표준 데이터 규격 적용"""
        return {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "ttl_minutes": ttl_minutes,
                "source": "SocialPredictionCollector"
            },
            "data": data
        }

if __name__ == "__main__":
    today = datetime.now().strftime("%Y%m%d")
    out_dir = Path(f"data/raw/{today}")
    agent = SocialAgent(output_dir=out_dir)
    agent.run()
