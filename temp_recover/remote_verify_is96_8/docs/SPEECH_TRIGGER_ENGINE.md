# SPEECH_TRIGGER_ENGINE (IS-7)

## 1. 목적 (Purpose)
연설, 어조, 또는 내러티브의 변화를 포착하여 정책(Policy)이나 일정(Schedule) 이벤트가 발생하기 전의 "전조(Pre-event trigger)"를 탐지한다. 이 엔진은 "왜 이 발언이 지금 이 시점에 나왔는가?"에 대한 답을 제공해야 한다.

## 2. Trigger 정의
- **Trigger Type**: `SPEECH_SHIFT`
- **특징**: 정책 결정이나 데이터 발표보다 선행하며, 시장의 유동성 방향과 심리적 임계점에 영향을 미침.

## 3. 감시 대상 (Target Sources)
- **중앙은행**: Powell / FOMC 위원 / ECB / BOJ (공식 연설 및 기자회견)
- **정치 지도자**: 트럼프 및 미국 행정부 핵심 인사 (트윗, 인터뷰, 공식 성명)
- **투자은행(IB)**: Goldman Sachs / Morgan Stanley / JP Morgan (헤드라인 및 내러티브 톤 변화)

## 4. 탐지 로직 (Detection Logic)
수치적 변화가 아닌 **구조적/언어적 변화**를 탐지한다.

- **단어 강도 변화 (Word Intensity)**: "monitor" → "concerned", "patient" → "active" 등 핵심 키워드의 가중치 변화 포착.
- **타이밍 이상 (Timing Abnormality)**: 예상보다 이른 시점의 발언이나, 평소보다 강력한 톤의 발언 포착.
- **초점 이동 (Focus Shift)**: 담론의 중심이 '인플레이션'에서 '고용' 또는 '지정학적 리스크'로 이동하는 현상 탐지.

## 5. 필수 출력 (Required Output)
- **WHY-NOW sentence**: 왜 지금 이 발언이 나왔는지에 대한 1문장 요약.
- **Ignore-Impossibility sentence**: 왜 시장이 이 발언을 무시할 수 없는지에 대한 1문장 요약.
