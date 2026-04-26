import json
import os
from pathlib import Path
from src.core.gemini_client import GeminiClient

class SentryAgent:
    """
    [v17.0] The Market Sentry (보초 에이전트)
    역할: 6시간마다 시장의 변화를 감지하여, 비싼 전체 파이프라인(Hunter)을 가동할지 결정함.
    비용 최적화의 핵심.
    """

    def __init__(self):
        self.client = GeminiClient()
        self.threshold = 7.0 # 가동 임계치

    def check_market_volatility(self, news_headlines: list, market_change: float) -> dict:
        """
        뉴스 헤드라인과 지수 변동폭을 보고 '사냥 가치'를 판단.
        """
        # 초경량 판단을 위한 프롬프트 (Flash 모델 사용)
        prompt = f"""
당신은 시장의 냄새를 맡는 보초(Sentry)입니다.
최근 6시간 동안의 변화를 보고, 새로운 경제 분석 리포트를 생성할 만큼 중요한 사건이 있는지 판단하세요.

[최근 지수 변동]
코스피/나스닥 변동: {market_change}%

[최근 뉴스 헤드라인]
{chr(10).join(news_headlines[:20])}

[JUDGMENT CRITERIA]
- 지수가 1% 이상 급변했는가?
- 공급망, 전쟁, 정책 변화 등 '병목'과 관련된 새로운 뉴스가 있는가?
- 기존에 다뤘던 주제와 완전히 다른 새로운 국면이 전개되었는가?

아래 JSON 형식으로만 응답하라:
{{
  "impact_score": (1.0~10.0),
  "reason": "간결한 판단 사유",
  "trigger_hunter": (true/false)
}}
"""
        try:
            # Tier 3 (Flash) 사용하여 최소 비용으로 판단
            result = self.client.call_json_controlled(prompt, agent="SENTRY_WATCHER", tier=3)
            return result
        except Exception as e:
            print(f"  [SENTRY] Error: {e}")
            return {"impact_score": 5.0, "reason": "Sentry Error - Fallback", "trigger_hunter": True}

    def should_trigger(self, result: dict) -> bool:
        return result.get("trigger_hunter", False) or result.get("impact_score", 0) >= self.threshold
