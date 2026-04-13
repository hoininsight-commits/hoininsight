# report_step74_pre_structural_signal.md
Date: 2026-04-13

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/13/liquidity_m2_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (FRED)
- **Temporal Anchor:** 2026-04-13
- **Unresolved Question:** 통화량의 극단적 급증이 단순 기술적 오류인가, 아니면 연준의 긴급 유동성 주입에 따른 인플레이션 헤지 수요의 즉각적 폭발을 야기할 것인가?
- **Rationale:** M2 통화량이 100.0% 백분위수라는 극단적 수치(Extreme)에 도달한 것은 단순한 경제 지표의 상승이 아닌 시스템적 유동성 충격을 의미합니다. 이는 시장 참여자들이 연준의 정책 변화(긴축 또는 인플레이션 용인)를 공식 발표 이전에 선제적으로 가격에 반영하게 만드는 강력한 자본 흐름 재배치(Capital Flow Anticipation) 신호입니다. 지표 발표 직후 30일 이내에 시장의 포지션 변화가 불가피하므로 시계열적 앵커가 뚜렷한 프리-스트럭처럴 신호로 판단됩니다.
- **Upgrade Condition:** 연준 관계자가 해당 통화량 팽창에 대해 언급하거나 차기 FOMC에서의 긴급 금리 인상 가능성이 대두될 때
- **Invalidation Condition:** 데이터 오류로 판명되거나, 다음 보고 주기에서 M2 수치가 급격히 평균으로 회귀(Mean Reversion)할 경우
