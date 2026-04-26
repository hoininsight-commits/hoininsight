
import json
from datetime import datetime, timedelta
from typing import List, Dict
from src.core.gemini_client import GeminiClient

class WeeklyStrategyMapper:
    """[v15.0] Weekly Strategic Forecast & Logic Chain Generator"""

    def __init__(self):
        self.client = GeminiClient()

    def generate_weekly_map(self, upcoming_events: List[Dict], current_market: Dict) -> Dict:
        """
        한 주간의 주요 일정과 현재 시장 상황을 결합하여 '전략 지도'를 생성함.
        """
        prompt = f"""
너는 100만 구독자를 보유한 경제 전문 유튜버 '경제사냥꾼'의 메인 전략가다.
이번 주(또는 다음 주) 예정된 주요 금융 일정들을 바탕으로, 시장을 관통할 하나의 거대한 '서사(Narrative)'와 각 날짜별 '논리적 연결 고리'를 설계하라.

[UPCOMING EVENTS]
{json.dumps(upcoming_events, ensure_ascii=False, indent=2)}

[CURRENT MARKET STATE]
{json.dumps(current_market, ensure_ascii=False, indent=2)}

[TASK]
1. **The Grand Narrative (거대 서사)**: 이번 주 시장을 지배할 핵심 테마는 무엇인가? (예: "금리 인하 지연과 실적 장세의 충돌")
2. **Logic Chain (인과 관계 사슬)**: 각 일정이 어떻게 다음 일정으로 에너지를 전달하는지 설명하라. (예: "월요일 BOJ의 톤이 엔화 약세를 부추기면, 화요일 국내 수출주의 반응을 거쳐 수요일 하이닉스 실적 발표의 환율 효과로 연결됨")
3. **Hunter's Checkpoint (사냥꾼의 체크포인트)**: 투자자들이 이번 주에 '돈'을 벌기 위해 반드시 확인해야 할 3가지 급소는 무엇인가?
4. **Historical Precedent (역사적 전례)**: 이번 주의 흐름이 과거 어떤 역사적 시점과 닮았는가?

[OUTPUT JSON FORMAT]
{{
  "grand_narrative": "이번 주 시장 요약 헤드라인",
  "narrative_description": "상세 분석 내용",
  "daily_logic": [
    {{
      "date": "YYYY-MM-DD",
      "event": "핵심 일정",
      "influence": "이 일정이 다음 시장/일정에 줄 영향",
      "link_to_next": "다음 일정과의 연결 고리"
    }}
  ],
  "checkpoints": ["급소 1", "급소 2", "급소 3"],
  "historical_parallel": {{
    "period": "역사적 시점/사건",
    "reason": "현재와 닮은 이유"
  }}
}}
"""
        try:
            print(f"  📅 [StrategyMapper] Generating Weekly Strategic Map...")
            return self.client.call_json_controlled(prompt, agent="STRATEGY_MAPPER", tier=1)
        except Exception as e:
            print(f"  ❌ [StrategyMapper] Error: {e}")
            return {}
