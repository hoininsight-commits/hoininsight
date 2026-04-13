# report_step74_pre_structural_signal.md
Date: 2026-04-13

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/13/credit_hy_spread_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional High-Yield Credit Investors
- **Temporal Anchor:** 2026-04-13 (L2 Anomaly Detection Date)
- **Unresolved Question:** 하이일드 스프레드가 2.9% 이하로 추가 축소될 수 있는 펀더멘탈적 근거가 있는가, 아니면 단순한 유동성 과잉에 의한 기술적 오버슈팅인가?
- **Rationale:** 본 신호는 하이일드 스프레드가 20일 이동평균 대비 -2.21 시그마 수준으로 급격히 축소되었음을 나타냄. 이는 시장 참여자들이 향후 경기 낙관론에 베팅하며 자본을 고수익 채권으로 공격적으로 재배치(Capital Flow Anticipation)하고 있음을 시사함. 통상적인 변동 범위를 벗어난 이러한 극단적 수치는 구조적 금리 변화나 부도율 발표 이전에 자본이 선제적으로 이동한 'Pre-Structural' 신호로 간주되며, 단기 내 포지션 청산이나 로테이션을 유발할 가능성이 높음.
- **Upgrade Condition:** Z-Score가 -2.5를 초과하거나, VIX 지수와 스프레드 간의 다이버전스가 발생하며 크레딧 시장의 '추세 반전' 징후가 포착될 때
- **Invalidation Condition:** 기업 이익 전망의 비약적 상승 또는 금리 인하 기대감 확산으로 인해 스프레드 2.0-3.0 구간이 새로운 정상(New Normal)으로 고착될 경우
