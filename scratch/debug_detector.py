import os
import json
from pathlib import Path
from src.agents.detector import DetectorAgent

agent = DetectorAgent()
all_data = agent.load_all_data()
summary = agent.build_data_summary(all_data)
print("=== Summary ===")
print(summary)

prompt = f"""
너는 경제사냥꾼의 탐지 엔진이이다. 아래 데이터를 보고 가장 이상한 징후 3개를 찾아라.
{summary}

[탐지 관점]
1. 속도: Z-score > 2.0 또는 5일 급변 지표
2. 붕괴: 지표 간 상관관계 역전
3. 모순: 뉴스와 숫자의 엇박자
4. 결정적 시점: 왜 하필 오늘인가
5. 컨센서스 충격 (가장 강한 선점 신호): 오늘 발표된 경제지표 중 예상치와 실제치의 괴리가 5% 이상인 것이 있는가? BEAT(예상 상회)든 MISS(예상 하회)든 시장 기대가 깨진 것 자체가 WHY NOW의 핵심이다. 이게 있으면 다른 신호보다 우선 선택해라.

[출력 규칙]
- 유가/환율 절대값 위주 제목 금지 (변화율/Z-score 근거 필수)
- [절대 금지 토픽 패턴] 아래 패턴의 토픽은 생성하지 마라. 이런 토픽은 매일 같은 상황이라 WHY NOW가 없다.
  * 금지 패턴:
    - "환율 XXX원 돌파" 또는 "환율 XXX원 → 위기" (단, 환율이 5일 Z-score 2.0 이상이거나 5일 변화율 1.5% 이상이면 허용)
    - "유가 $XX → 에너지 비용 압박" (단, WTI 5일 변화율이 ±5% 이상이면 허용)
    - "VIX XX → 시장 불안" (단, VIX 5일 변화율이 ±20% 이상이면 허용)
  * 허용 기준:
    - 반드시 Z-score 또는 변화율 근거가 있어야 함
    - "왜 오늘인가"를 데이터로 설명할 수 있어야 함
    - 어제도 같은 수준이었다면 오늘 신호가 아님
- 순수 JSON 배열만 출력.

[구조]
[
  {{
    "topic": "경제사냥꾼 스타일 제목",
    "anomaly_type": "SPEED|CORRELATION|NEWS_MISMATCH|WHY_NOW",
    "why_anomalous": "데이터 근거 (한 문장)",
    "why_now": "결정적 이유 (한 문장)",
    "key_indicators": ["지표1", "지표2"],
    "strength": 0.0~10.0,
    "signal_type": "Type1~Type9"
  }}
]
"""

print("=== AI Response ===")
try:
    # call_json 대신 직접 호출하여 원본 확인
    from src.core.gemini_client import GeminiClient
    client = GeminiClient()
    # model = client.genai.GenerativeModel("gemini-1.5-flash-latest")
    # resp = model.generate_content(prompt)
    # print(resp.text)
    
    # call_json의 결과 확인
    results = client.call_json(prompt)
    print(json.dumps(results, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")

# 필터링 테스트
print("\n=== Filtering Test ===")
test_anomalies = [
    {
        "topic": "환율 1483원 돌파 → 위기 징조",
        "strength": 9.0,
        "why_anomalous": "환율이 1483원 수준에 도달함.",
        "key_indicators": ["usd_krw"]
    },
    {
        "topic": "WTI 유가 0 → 에너지 가격 하락",
        "strength": 8.0,
        "why_anomalous": "유가가 0 수준임.",
        "key_indicators": ["wti_oil"]
    },
    {
        "topic": "금리 스프레드 비정상 폭 확대 (BEAT)",
        "strength": 9.5,
        "why_anomalous": "HY 스프레드가 전월비 117% 이상 서프라이즈 발생",
        "key_indicators": ["consensus"]
    }
]

for a in test_anomalies:
    is_filtered = agent._is_absolute_value_topic(a["topic"], a)
    print(f"Topic: {a['topic']} | Filtered: {is_filtered}")

selected = agent.select_best(test_anomalies)
print(f"\nSelected Topic: {selected['topic'] if selected else 'None'}")
