
import json
from typing import List, Dict
from src.core.gemini_client import GeminiClient

class StockAnalyst:
    """[v15.0] Agent-04: Stock & Sector Analyst - Strategist Mode"""

    def __init__(self):
        self.client = GeminiClient()

    def analyze_stocks(self, main_topic: Dict, evidence_bundle: Dict) -> Dict:
        """
        선정된 토픽과 증거를 바탕으로 관련 섹터 및 종목의 '수익 구조적 연결성'을 분석함.
        """
        topic_event = main_topic.get("event", "")
        logic = main_topic.get("why_hypothesis", "")
        mechanism = main_topic.get("mechanism", "")
        
        prompt = f"""
너는 100만 구독자를 보유한 경제 전문 유튜버 '경제사냥꾼'의 전담 종목 분석가(Agent-04)다.
오늘 선정된 메인 토픽을 바탕으로, 대중이 보지 못하는 '이면의 수혜주'와 그 '필연적 실적 연결 고리'를 분석하라.

[MAIN TOPIC]
{topic_event}

[LOGIC & MECHANISM]
- Logic: {logic}
- Mechanism: {mechanism}

[STRATEGIST TASK]
1. **Second-order Effect (2차 파급 효과)**: 뉴스에 직접 언급된 종목이 아니라, 그 사건으로 인해 '결국 돈을 벌 수밖에 없는' 배후의 섹터 2개를 선정하라. (예: 파업 -> 로봇/자동화, 전쟁 -> 위성/통신)
2. **Revenue Linkage (수익적 필연성)**: 단순히 "호재다"가 아니라, 해당 이슈가 기업의 **매출(Top-line)**이나 **이익률(Margin)**에 어떻게 꽂히는지 산업적/재무적 근거를 제시하라.
3. **Hunter's Verdict (사냥꾼의 판결)**: 대중의 공포나 환희 뒤에 숨겨진 자본의 냉혹한 이동 경로를 단호한 어조로 분석하라. (~할 수 있다가 아니라 ~할 수밖에 없다)

[OUTPUT JSON FORMAT]
{{
  "sectors": [
    {{
      "name": "섹터명",
      "reason": "현상 뒤에 숨겨진 산업적 병목(Bottleneck) 또는 기회 분석",
      "stocks": [
        {{
          "name": "종목명",
          "linkage": "이슈와 실적 사이의 끊을 수 없는 연결 고리 (예: 정부 예산 집행 시 독점 수혜 구조 등)"
        }}
      ]
    }}
  ],
  "overall_strategy": "대중과 반대로 움직여야 할 지점과 자본의 최종 집결지 요약"
}}

주의: 반드시 한국어로 작성하고, 뻔한 이야기는 버려라. 사냥꾼의 눈으로 '급소'를 찾아라.
"""

        print(f"  🕵️‍♂️ [Agent-04] Analyzing stock linkage for: {topic_event[:30]}...")
        try:
            # TIER 1 호출하여 깊이 있는 분석 수행
            response = self.client.call_json_controlled(prompt, agent="STOCK_ANALYST", tier=1)
            return response if response else {}
        except Exception as e:
            print(f"  ❌ [Agent-04] Analysis Error: {e}")
            return {}
