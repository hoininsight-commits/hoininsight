# KILL_SWITCH_ENGINE (IS-14)

## 1. 목적 (Purpose)
모든 Ticker와 분석에는 단 하나의 객관적인 "데드풀(Death Condition)"이 존재해야 한다. IssueSignal은 자신의 가설이 언제 즉시 틀렸는지를 알고 있어야 하며, 이를 통해 손실이나 불필요한 관찰 비용을 최소화한다.

## 2. Kill-Switch 유형 (Kill Switch Types)
해석의 여지가 없는 객관적인 지표를 기준으로 한다.

- **정책 반전 (Policy Reversal)**: 추진되던 법안이 폐기되거나, 공식적인 반대 성명이 발표될 경우.
- **공급 과잉/해소 (Capacity Release)**: 병목 현상의 원인이던 공급 부족이 대규모 공장 가동이나 기술 혁신으로 즉각 해소될 경우.
- **대체 기술 검증 (Alternative Tech Validation)**: 기존 병목을 우회하는 완전히 새로운 표준이 검증될 경우.
- **일정 지연 (Timeline Slippage)**: 임계점을 넘어서는 일정 연기로 인해 기회비용이 구조적 한계를 초과할 경우.

## 3. 규칙 (Rules)
- **Ticker당 1개**: 각 Ticker는 명확히 구분되는 **단 하나**의 Kill-switch 조건을 가져야 한다.
- **객관적 관찰**: "심리 위축", "전망 불투명"과 같은 주관적 표현이 아닌, "반대 법안 통과", "재고율 30% 초과" 등 관찰 가능한 지표여야 한다.

## 4. 출력 (Output)
모든 결정 카드(Decision Card)에는 다음 항목이 포함되어야 한다.
- **Kill-switch Condition**: 구체적인 무효화 조건.
- **Monitoring Signal**: 해당 조건을 확인하기 위해 주시해야 할 데이터 포인트.
