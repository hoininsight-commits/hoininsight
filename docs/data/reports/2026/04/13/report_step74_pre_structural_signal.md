# report_step74_pre_structural_signal.md
Date: 2026-04-13

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/13/crypto_btc_usd_spot_coingecko.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** US Tax-exposed Market Participants
- **Temporal Anchor:** 2026-04-15 (US Tax Deadline)
- **Unresolved Question:** 실제 납세 목적의 매도 물량이 이번 하락으로 충분히 소화되었는가, 아니면 15일 당일까지 추가적인 유동성 압박이 지속될 것인가?
- **Rationale:** 2026년 4월 13일 발생한 Z-Score -1.57의 하락 신호는 미국 세금 납부 마감일(4월 15일)을 불과 이틀 앞두고 발생함. 이는 단순한 시장 변동성이 아니라, 세금 납부를 위한 유동성 확보 목적의 자산 매각(Capital Flow Anticipation)이 시작되었음을 나타내는 구조적 전조 신호임. 통상적인 '성장성' 담론이 아닌 특정 마감 기한(Deadline)에 의한 자본 재배치 현상으로 판단됨.
- **Upgrade Condition:** Z-Score가 -2.0을 초과하여 하락하거나, 거래량이 직전 5일 평균 대비 50% 이상 급증할 경우
- **Invalidation Condition:** 4월 15일 이전에 가격이 20일 이동평균선(71,883.2) 위로 회복될 경우

### Topic: data/features/anomalies/2026/04/13/credit_hy_spread_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Credit Investors
- **Temporal Anchor:** 2026-04-13 (Anomaly Detection Date)
- **Unresolved Question:** 하이일드 스프레드의 급격한 축소가 펀더멘털의 개선 때문인가, 아니면 특정 매크로 이벤트(금리 인하 등)를 앞둔 투기적 선취매인가?
- **Rationale:** 본 신호는 하이일드 스프레드가 20일 이동평균 대비 -2.21 표준편차 수준으로 급격히 압착되었음을 나타냅니다. 이는 공식적인 경제 지표나 정책 변화가 확정되기 전, 자본이 고수익 위험 자산으로 선제적으로 재배치(Capital Flow Anticipation)되고 있음을 의미하는 전구조적(Pre-structural) 신호입니다. 단순 추세가 아닌 통계적 이상치(Z-Score > 2.0)를 기반으로 하므로 유효한 신호로 판단됩니다.
- **Upgrade Condition:** 스프레드 Z-Score가 -2.5를 초과하며 VIX 지수의 급격한 하락이 동반될 경우 리스크 온(Risk-on) 정점 신호로 격상
- **Invalidation Condition:** 5거래일 이내에 스프레드가 20일 이동평균선(3.19)으로 회귀하는 평균 반전 발생 시

### Topic: data/features/anomalies/2026/04/13/inflation_pce_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (via FRED PCE Data Release)
- **Temporal Anchor:** 2026-04-13 (Data Anomaly Release Window)
- **Unresolved Question:** 금리 인상 또는 긴축 강도에 대한 연준의 공식적 태도 변화가 즉각적으로 뒤따를 것인가?
- **Rationale:** 2026년 4월 13일 발표된 PCE 데이터가 100.0%라는 극단적 퍼센타일에 도달함에 따라, 실제 정책 금리 결정(법적/정책적 확인)이 내려지기 전 시장이 선제적으로 자본을 재배분(Capital Flow)하기 시작하는 강력한 전조 신호임. 이는 단순한 추세가 아니라 특정 시점의 데이터 충격에 기반한 구조적 변화의 예고탄임.
- **Upgrade Condition:** 연준 위원들이 해당 PCE 데이터를 인용하며 매파적 발언(Verbal Commitment)을 시작할 경우
- **Invalidation Condition:** 익월 데이터의 급격한 하향 수정 또는 인플레이션 기대치의 급격한 둔화 확인 시

### Topic: data/features/anomalies/2026/04/13/struct_dart_disposal.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** DART 공시 주체 (주요 주주 및 법인)
- **Temporal Anchor:** 2026-04-13
- **Unresolved Question:** 단기간 내 5건의 대규모 자산/지분 처분 공시가 집중된 배경이 특정 규제 준수를 위한 것인가, 아니면 거시적 유동성 위기에 따른 선제적 현금 확보인가?
- **Rationale:** DART(기업공시시스템) 상에서 'Disposal(처분)' 관련 이상 징후가 L2 수준(Count=5)으로 포착됨. 이는 개별 기업의 우발적 사건을 넘어, 특정 시점에 다수의 주요 주주들이 자산을 현금화하려는 움직임으로 해석됨. 법적/회계적 확정 결과가 시장에 완전히 반영되기 전, 내부자들의 자본 재배치 신호가 감지된 것이므로 프리-스트럭처럴(Pre-Structural) 신호의 요건을 충족함.
- **Upgrade Condition:** 처분 주체가 특정 섹터에 집중되거나, 처분 목적이 '채무 상환' 또는 '운영자금 확보'로 통일될 경우
- **Invalidation Condition:** 공시 내용이 통상적인 사외이사 교체나 미미한 지분 변동 등 시장 영향력이 낮은 단순 보고로 판명될 경우

### Topic: data/features/anomalies/2026/04/13/liquidity_m2_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (FRED)
- **Temporal Anchor:** 2026-05-01 (Next Fed Liquidity Window)
- **Unresolved Question:** 극단적인 M2 급증이 연준의 의도된 유동성 주입인지, 아니면 상업 은행 시스템의 단기적 병목 현상에 의한 일시적 왜곡인지 여부
- **Rationale:** M2 통화 공급량이 100번째 백분위수(Extreme)에 도달한 것은 통상적인 경제 성장 흐름을 벗어난 구조적 이상 신호임. 이는 시장 참여자들이 연준의 긴급 통화 정책 수정(유동성 회수 또는 금리 조정)을 예상하고 자본을 선제적으로 재배치하게 만드는 강력한 촉매제로 작용함. 단순한 우상향 추세가 아닌 1.83의 Z-Score를 동반한 단기 충격이므로 Pre-Structural Signal 조건에 부합함.
- **Upgrade Condition:** 연준 관계자가 M2 수치에 대해 '일시적' 또는 '긴급 대응' 언급을 할 경우
- **Invalidation Condition:** 다음 주 M2 데이터가 20일 이동평균선(21828.2) 이내로 급격히 회귀할 경우

### Topic: data/features/anomalies/2026/04/13/inflation_kor_cpi_ecos.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Bank of Korea (BOK)
- **Temporal Anchor:** 2026-04-13 (CPI Release) / Next MPC Meeting
- **Unresolved Question:** Does this CPI anomaly represent a persistent inflationary trend that will force the BOK into an unscheduled hawkish pivot?
- **Rationale:** 한국 CPI 데이터의 Z-Score가 1.86으로 임계치(1.5)를 상회하며 통계적 이상징후를 보임. 이는 한국은행의 금리 정책 변화에 대한 시장의 기대를 즉각적으로 재조정하게 만드는 강력한 데이터적 트리거임. 실제 금리 결정(Structural Event)이 내려지기 전, 지표 발표 직후 발생하는 자금 재배치 및 기대 인플레이션의 구조적 변화를 시사하므로 Pre-Structural Signal로 분류됨.
- **Upgrade Condition:** Official BOK commentary acknowledging the anomaly as a 'structural risk' or 'monitored threat' within the next 7 days.
- **Invalidation Condition:** Mean reversion in the next data release or if the BOK attributes the anomaly to one-time seasonal factors/statistical noise.

### Topic: data/features/anomalies/2026/04/13/comm_wti_fred.json L2 Signal
- **Signal Type:** Dependency
- **Trigger Actor:** Global Energy Supply Chain / Commodity Markets
- **Temporal Anchor:** 2026-04-13 (L2 Anomaly Detection Date)
- **Unresolved Question:** WTI 유가의 $114 돌파가 단순 수급 불균형인지, 아니면 지정학적 충격에 의한 장기적 공급망 단절의 시작인가?
- **Rationale:** WTI 유가가 통계적 임계치인 Z-Score 2.19를 돌파하며 $114.01에 도달한 것은 단순한 가격 변동이 아닌 에너지 비용 구조의 급격한 변화를 암시함. 이는 실물 경제의 공급망 구조적 의존성(Structural Dependency)을 자극하며, 공식적인 정책 대응이나 실적 발표 이전에 자본이 위험 자산에서 이탈하여 에너지 및 인플레이션 헤지 수단으로 재배치되기 시작하는 'Pre-Structural' 신호로 판단됨.
- **Upgrade Condition:** WTI 가격이 3거래일 연속 $115 상단에서 유지되거나 주요 산유국의 긴급 성명이 발표될 경우
- **Invalidation Condition:** 48시간 이내에 Z-Score가 1.0 미만으로 회귀하며 기술적 조정이 발생하는 경우

### Topic: data/features/anomalies/2026/04/13/index_spx_fred.json L1 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** Institutional Algorithmic Traders
- **Temporal Anchor:** 2026-04-13
- **Unresolved Question:** 실질적인 거시 경제 지표 발표 없이 발생한 S&P 500의 통계적 이탈이 단순 오버슈팅인가, 아니면 미공개 정보에 기반한 선제적 포지셔닝인가?
- **Rationale:** S&P 500 지수의 Z-Score가 1.69를 기록하며 임계치(1.5)를 상회했습니다. 이는 특정 뉴스나 정책 발표 전, 시장 내 자본이 기술적 임계점을 넘어서며 이동하기 시작했음을 나타내는 '자본 흐름 선취(Capital Flow Anticipation)' 신호입니다. 2026년 4월 13일이라는 특정 시점에 발생한 데이터 이상치는 단순한 추세가 아닌, 단기적인 구조적 변화를 암시하는 Pre-Structural 신호로 판단됩니다.
- **Upgrade Condition:** Z-Score가 2.0을 돌파하거나 거래량이 동반된 섹터 간 자금 이동이 관측될 때
- **Invalidation Condition:** 48시간 이내에 Z-Score가 1.0 미만으로 회귀하며 평균 회귀(Mean Reversion)가 발생할 경우

### Topic: data/features/anomalies/2026/04/13/rates_us10y_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** US Treasury Market / Federal Reserve
- **Temporal Anchor:** 2026-04-13 (Threshold Breach Window)
- **Unresolved Question:** 미국 10년물 국채 금리 4.3% 수준이 실질적인 저항선(Ceiling)으로 작용하여 채권 매수세가 유입될 것인가, 아니면 새로운 고금리 체제(Regime Shift)의 시작인가?
- **Rationale:** 미국 10년물 국채 금리가 90.5% 퍼센타일에 도달한 것은 시장의 무위험 수익률(Risk-free rate) 임계값에 도달했음을 의미함. 이는 단순한 추세가 아니라, 주식 및 채권 간 자산 배분을 재조정해야 하는 기술적/구조적 압박을 발생시킴. 4.29%라는 구체적인 수치는 정책 결정(FOMC) 이전에 시장 참여자들이 선제적으로 자본을 재배치(Rotation)하게 만드는 전조적 신호(Pre-structural signal)로 해석됨.
- **Upgrade Condition:** US10Y_ROC_1d가 0.5%를 초과하거나, 금리 변동성이 VIX 지수 상승과 동기화되어 나타날 경우
- **Invalidation Condition:** 10년물 금리가 20일 이동평균선(4.321) 아래로 급격히 회귀하며 percentile 80% 이하로 하락할 경우

### Topic: data/features/anomalies/2026/04/13/inflation_cpi_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve
- **Temporal Anchor:** 2026-04-13 (CPI Release Date)
- **Unresolved Question:** Does this 100th percentile CPI anomaly force an immediate hawkish pivot in the upcoming FOMC meeting despite previous guidance?
- **Rationale:** 이 신호는 2026년 4월 13일 발표된 CPI 데이터가 100th percentile(극단적 이상치)에 도달했음을 나타냅니다. 이는 단순한 물가 상승 트렌드가 아니라, 정책 당국의 공식적인 금리 결정이나 정책 변화가 내려지기 직전 시장 자금이 인플레이션 헷지 자산으로 즉각 재배치되도록 강제하는 '자본 흐름 선행 신호(Capital Flow Anticipation)'입니다. 구체적인 타임스탬프와 극단적인 Z-score(1.98)는 시장 참여자들에게 즉각적인 대응(Risk-off 또는 Rotation)을 요구하는 구조적 압박으로 작용합니다.
- **Upgrade Condition:** Immediate spike in 10-year Treasury yields above a key resistance level or emergency verbal intervention by a Fed governor.
- **Invalidation Condition:** Official statement clarifying a data reporting error or a simultaneous collapse in energy prices that offsets core inflation.

### Topic: data/features/anomalies/2026/04/13/risk_vix_fred.json L2 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** Institutional Hedgers & Market Makers
- **Temporal Anchor:** 2026-04-15 (US Tax Deadline / Q1 Earnings Season Kick-off)
- **Unresolved Question:** VIX의 급격한 Z-Score 하락이 실제 리스크 감소를 반영하는 것인가, 아니면 실적 발표 및 세금 납부 기한을 앞둔 일시적인 볼러틸리티 매도(Short Vol) 과밀 현상인가?
- **Rationale:** 해당 신호는 4월 중순이라는 특정 시점에 VIX 지수가 통계적 임계치(Z-Score -2.12)를 벗어나 급격히 하락했음을 나타냄. 이는 단순한 추세가 아니라, 주요 매크로 이벤트(세금 납부 기한 및 실적 발표)를 앞두고 자본이 위험 프리미엄을 급격히 축소하며 재배치되고 있다는 선행적 신호임. 통상적인 변동성 범위에서 벗어난 이례적 움직임이므로 구조적 변화 전 단계의 신호로 간주됨.
- **Upgrade Condition:** VIX가 20일 이동평균선(25.39)으로 급격히 회귀하며 실적 발표 직전 헷지 수요가 폭발할 경우
- **Invalidation Condition:** VIX가 현재 수준(19.49)에서 10거래일 이상 횡보하며 저변동성 체제가 고착화될 경우
