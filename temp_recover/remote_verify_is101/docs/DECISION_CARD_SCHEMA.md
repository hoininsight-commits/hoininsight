# DECISION_CARD_SCHEMA (IS-15)

## 1. 목적 (Purpose)
사람이 10초 이내에 핵심 내용과 리스크를 파악하고 행동 결정을 내릴 수 있도록 정보를 극도로 압축하고 정제한다. 결정 카드(Decision Card)는 "단순 정보 전달"이 아닌 "실행 가능한 결론"을 제공한다.

## 2. 카드 구조 (5-Step Fixed Structure)

1.  **WHAT (Trigger)**: 어떤 사건이 발생했는가? (트리거 명시)
2.  **WHY (Forced Capital movement)**: 왜 지금 자본이 움직여야 하는가? (강제적 이동 논리)
3.  **WHERE (Bottleneck)**: 자본이 어디에 갇혀(Trapped) 있는가? (병목 구간 식별)
4.  **WHO (1–3 Tickers)**: 누가 이 구조의 주인인가? (1~3개 핵심 종목)
5.  **WHEN (Kill-switch)**: 언제 이 논리가 파기되는가? (무효화 조건 및 시그널)

## 3. 출력 원칙 (Rules)
- **가독성**: Markdown 형식을 사용하여 사람이 즉시 읽을 수 있게 한다.
- **추측 배제**: "전망", "목표가", "매칭 점수"와 같은 추측성 데이터를 배제한다.
- **결함 처리**: 가독성 향상을 위해 위 5가지 항목 중 하나라도 누락되거나 신뢰도가 낮을 경우, 카드를 생성하지 않는다.

## 4. 데이터 형식 (Format)
- **File**: `data/issuesignal/decisions/DECISION_YYYYMMDD_ID.md`
- **Content**: 5단계 헤더와 짧은 불렛 포인트 형식.
