import json
from typing import List, Dict
from src.core.gemini_client import GeminiClient

class TopicEvaluator:
    """[TASK #100.5] Gemini를 사용하여 토픽 후보를 평가"""

    def __init__(self):
        self.gemini = GeminiClient()

    def evaluate_all(self, candidates: List[Dict]) -> List[Dict]:
        evaluations = []
        for cand in candidates:
            res = self.evaluate_single(cand)
            if res:
                evaluations.append(res)
        return evaluations

    def evaluate_single(self, candidate: Dict) -> Dict:
        prompt = f"""
너는 '경제사냥꾼(Economic Hunter)' 스타일의 시장 분석 전문가다.
다음 토픽 후보를 평가하여 HOIN Insight의 메인 콘텐츠로 적합한지 판단하라.

[토픽 후보 데이터]
{json.dumps(candidate, ensure_ascii=False, indent=2)}

[평가 지침]
1. topic_fit_score: 지금 이 시점에 말할 가치가 있는가 (0~10)
2. market_impact_score: 시장 전체나 특정 섹터에 실질적 충격이 있는가 (0~10)
3. novelty_score: 뻔한 이야기가 아닌 새로운 시각이 있는가 (0~10)
4. theme_expandability_score: 다른 테마나 종목으로 확장이 쉬운가 (0~10)
5. contentability_score: '경제사냥꾼' 캐릭터로 흥미롭게 풀기 좋은가 (0~10)
6. flow_type: 시장이 예상대로 가고 있는가(NORMAL), 아니면 모순적인가(ANOMALY), 섞여있는가(MIXED)
7. topic_decision: 발행 추천(PROMOTE), 보류(HOLD), 탈락(DROP)

[응답 형식]
반드시 아래 JSON 구조로만 응답하라.
{{
  "candidate_id": "{candidate['candidate_id']}",
  "topic_fit_score": 0,
  "market_impact_score": 0,
  "novelty_score": 0,
  "theme_expandability_score": 0,
  "contentability_score": 0,
  "flow_type": "NORMAL | ANOMALY | MIXED",
  "why_now_summary": "이 토픽이 지금 왜 중요한지 1문장 요약",
  "topic_decision": "PROMOTE | HOLD | DROP"
}}
"""
        try:
            # TIER 3: 품질 평가용 (재시도 없음)
            res = self.gemini.call_json_controlled(prompt, agent="TOPIC_EVALUATOR", tier=3)
            return res
        except Exception as e:
            print(f"  ⚠️ 토픽 평가 실패 ({candidate['candidate_id']}): {e}")
            return None
