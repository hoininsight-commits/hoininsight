# [PHASE-14A] NARRATIVE COMPONENT DISTRIBUTION REPORT
**분석 기간**: 최근 14일 (총 1051건 토픽 데이터 추출)
**목적**: Narrative Score 0점 수렴의 구성요소별 정밀 해부분석.

---

## 1. 구성요소별 통계 분포

| 구성요소 | 평균 | 중앙값 | 0값 비율(%) | Non-zero 비율(%) | 상위 10개 샘플 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Actor Tier Score** | 0.00 | 0.00 | 100.0% | 0.0% | [0.0, 0.0, 0.0, 0.0, 0.0]... |
| **Capital Flow Score** | 0.00 | 0.00 | 100.0% | 0.0% | [0.0, 0.0, 0.0, 0.0, 0.0]... |
| **Policy Score** | 0.00 | 0.00 | 100.0% | 0.0% | [0.0, 0.0, 0.0, 0.0, 0.0]... |
| **Persistence Score**| 0.00 | 0.00 | 100.0% | 0.0% | [0.0, 0.0, 0.0, 0.0, 0.0]... |
| **Narrative Score** | 0.14 | 0.00 | 99.6% | 0.4% | [35.65, 35.65, 35.65, 35.65, 0.0]... |

*   **Cross Axis Multiplier 발동 횟수 (> 1.0)**: 4 회 발동
*   **Escalation Detected True 횟수**: 0 회 발동
*   **Conflict Flag True 횟수**: 0 회 발동

---

## 2. 점수 계산 0점 원인 (Root Cause Classification)
총 1047건의 Narrative Score === 0 토픽을 분해한 결과입니다.

*   `CASE A (Actor Score == 0)`: 0건
*   `CASE B (All Structural Scores == 0)`: 0건
*   `CASE C (Intensity < 50)`: 0건
*   `CASE E (Missing Fields / None)`: 1047건
    -> 전체 1051건 중 `narrative_score` 호출/세팅 누락 빈도: 99.6%

---

## 3. 최종 진단 결론
① **계산 로직은 정상이나 입력 조건이 충족되지 않는 상태인가?**: 계산 로직 자체가 누락됨 (CASE E 지배적)
② **계산 로직이 사실상 발동하지 않는 상태인가?**: 호출 누락 빈도 높음
③ **구조적 신호 감지 알고리즘이 현실을 반영하지 못하는가?**: 현실 반영 미흡 (모든 구조축 점수가 0에 수렴하는 극단적 보수성 표출)

> **[조치 권고사항]**
> Actor Score 와 Flow/Policy Score 의 산출 방식이 비정상적으로 억제되어 있습니다. Component 의 가중치가 아니라, 엔진이 **구조적 액터를 인지하는 기준(Dictionary 또는 Regex 매칭률)** 자체가 완전히 망가져 있을 확률이 유력합니다.
