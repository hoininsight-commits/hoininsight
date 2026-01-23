# TEMPORAL INTERPRETATION RULES v1.0

## 1. Event vs State vs Structural
Narrative Layer와 Structural Layer의 충돌을 막기 위한 시간 규칙.

### 1-Day Event (감지)
*   **범위**: 오늘 하루(D-day)의 급등락, 뉴스, 공시.
*   **역할**: `candidates.json` 생성.
*   **권한**: 사실(Fact) 전달만 가능. "추세"라고 단정 금지.

### Short-term Narrative (3~7일)
*   **범위**: 최근 1주일 내의 데이터 흐름.
*   **역할**: `narrative_topics.json` 생성 (영상용).
*   **권한**: "최근 흐름", "단기적 관심" 표현 가능.
*   **금지**: "구조적 변화", "L3/L4 레벨", "장기 투자 권고".

### Structural State (1개월 이상)
*   **범위**: 20일 이동평균 이상, 거시적 변화.
*   **역할**: 기존 `topics.json` (Structural) 생성.
*   **권한**: "구조적 변화", " WHY NOW 확정", "L3/L4 판정".

## 2. Gate Rule
*   Narrative Topic이 Structural Topic으로 승격되려면 반드시 **최소 20일 간의 데이터 일관성**이 입증되어야 한다.
*   단순 뉴스나 이벤트로는 절대 Structural로 승격되지 않는다.
