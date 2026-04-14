# report_step74_pre_structural_signal.md
Date: 2026-04-15

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/15/crypto_btc_usd_spot_coingecko.json L2 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** Institutional and Retail Market Participants (US Tax Liquidity)
- **Temporal Anchor:** 2026-04-15 (US Tax Deadline)
- **Unresolved Question:** 실제 세금 납부를 위한 대규모 유동성 유출(Liquidity Outflow)이 가격 하락을 유도할 것인가, 아니면 마감 직후 재진입을 노린 선제적 매수세인가?
- **Rationale:** 본 신호는 4월 15일이라는 미국 세금 신고 마감일(Temporal Anchor)과 결합된 통계적 이상 현상(Z-Score 2.2)을 나타냄. 이는 일반적인 가격 상승 추세가 아니라, 특정 기한을 앞두고 자산 포트폴리오를 조정하거나 세금 납부를 위한 유동성 확보 과정에서 발생하는 '선제적 자본 재배치(Capital Flow Anticipation)'의 성격이 강함. L2 수준의 임계점 돌파는 단순 노이즈를 넘어선 구조적 변곡점의 전조로 판단됨.
- **Upgrade Condition:** Z-Score가 3.0을 초과하거나 거래소 내 스테이블코인 유입량이 급증하며 변동성이 폭발할 경우
- **Invalidation Condition:** 48시간 이내에 Z-Score가 1.0 미만으로 회귀하며 평균 가격대로 수렴할 경우

### Topic: data/features/anomalies/2026/04/15/inflation_pce_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (FRED)
- **Temporal Anchor:** 2026-04-15 (PCE Data Release / April FOMC Cycle)
- **Unresolved Question:** PCE 데이터의 100% 백분위 도달이 연준의 금리 인하 경로를 완전히 폐기하고 'Higher for Longer' 또는 추가 인상 기조로 전환시킬 것인가?
- **Rationale:** 2026년 4월 15일 발표된 PCE 데이터가 100.0%라는 극단적 백분위(Extreme Anomaly)를 기록하며 통계적 임계치를 초과함. 이는 정책 결정(FOMC) 전 시장이 인플레이션 고착화를 선반영하여 자본을 성장주에서 가치주 또는 현금성 자산으로 재배분하게 만드는 전형적인 Pre-Structural Signal임.
- **Upgrade Condition:** 연준 의장 또는 주요 이사의 긴급 매파적 발언(Verbal Threat)이 48시간 이내에 발생할 경우
- **Invalidation Condition:** 익월 데이터의 급격한 기저효과 반영 또는 공급망 해소에 따른 에너지 가격의 비정상적 폭락 확인 시

### Topic: data/features/anomalies/2026/04/15/struct_dart_disposal.json L2 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** 대주주 및 내부 공시 의무자 (DART Filers)
- **Temporal Anchor:** 2026-04-15 (이상 신호 감지 시점)
- **Unresolved Question:** 이번 지분 매각(Disposal)이 단순 자산 유동화인지, 혹은 특정 규제 변화나 기업 지배구조 개편을 앞둔 집단적 이탈인가?
- **Rationale:** 2026년 4월 15일 DART 시스템에서 포착된 5건의 대량 지분 처분(Disposal) 이상 신호는 시장 내 대규모 자본 이탈의 전조 현상으로 판단됨. 이는 단순한 장기적 하락 추세가 아니라, 특정 일자에 집중된 '이상 수치(Anomaly Count=5)'를 통해 시장이 공식적인 실적 발표나 정책 변화 이전에 내부자 정보를 바탕으로 자본 재배치를 시작했음을 시사하는 전구조적(Pre-structural) 신호임.
- **Upgrade Condition:** 매각 주체가 시가총액 상위 종목으로 확산되거나, 매각 사유가 '장내 매도'로 확인될 경우
- **Invalidation Condition:** 해당 공시들이 단순 계열사 간 지분 교환(Block deal) 또는 상속세 납부를 위한 공탁으로 판명될 경우
