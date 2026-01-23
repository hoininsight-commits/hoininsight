# SECTOR DIVERGENCE FINDER (SDF) v1.0

## 1. 목적
시장 전체 흐름과 다르게 독자적인 움직임을 보이는 **"괴리(Divergence)" 섹터**를 포착한다.
이는 Narrative Topic의 가장 강력한 후보다.

## 2. 최소 신호 (5 Signals)
이 5가지 신호 외에 무분별한 추가를 금지한다.

1.  **시장 대비 섹터 상대수익 괴리 (Rel. Return Gap)**
    *   `|Sector Return - Market Return| > Threshold`
2.  **섹터 내부 Breadth 붕괴 (Internal Breadth Collapse)**
    *   섹터 지수는 상승하나 상승 종목 비율이 20% 미만인 경우 (Mega Cap 주도)
3.  **Leader Shock**
    *   섹터 대장주(Top 1~3)의 3% 이상 급락 또는 대량 거래량 터짐
4.  **Expectation Reset**
    *   호재(실적 서프라이즈 등) 발표 당일 주가 하락
5.  **Style Rotation Proxy**
    *   성장(Growth) vs 가치(Value) 섹터 간의 급격한 수익률 격차 발생

## 3. 판단 기준
*   위 신호 중 **1개 이상** 발생 시 후보(Candidate)로 등록.
*   **Confidence**:
    *   1 Signal: LOW
    *   2 Signals: MEDIUM
    *   3+ Signals: HIGH
