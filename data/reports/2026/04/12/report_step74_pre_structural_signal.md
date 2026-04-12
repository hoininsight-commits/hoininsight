# report_step74_pre_structural_signal.md
Date: 2026-04-12

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/12/credit_hy_spread_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Fixed Income Investors / High-Yield Desks
- **Temporal Anchor:** 2026-04-26 (14-day mean reversion window)
- **Unresolved Question:** Does the current spread compression reflect a fundamental improvement in credit quality, or is it a liquidity-driven bubble prone to a sudden widening?
- **Rationale:** High Yield Spread의 Z-Score가 -2.21에 도달했다는 것은 통계적으로 매우 드문 수준의 신용 스프레드 압축을 의미함. 이는 시장 참여자들이 리스크를 극도로 과소평가하고 고수익 자산으로 자본을 선제적으로 집중시켰음을 나타내는 신호임. 이러한 극단적 수치는 일반적으로 구조적 조정이나 자산 재배분(Rotation)이 발생하기 직전의 'Pre-Structural' 상태로 간주됨.
- **Upgrade Condition:** If a major HY issuer misses an earnings target or a sovereign rate spike causes a sudden widening (>20bps in 24h).
- **Invalidation Condition:** Spread remains compressed at current levels for more than 30 days without an increase in VIX or corporate defaults.

### Topic: data/features/anomalies/2026/04/12/inflation_pce_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (FOMC)
- **Temporal Anchor:** 2026-04-30 (PCE Official Release Window)
- **Unresolved Question:** 이번 PCE 이상치가 공급망 충격에 의한 일시적 현상인가, 아니면 금리 인상을 강제하는 구조적 인플레이션의 재점화인가?
- **Rationale:** PCE 데이터가 100.0% 백분위수라는 극단적 이상치(L2 Signal)를 기록한 것은 공식적인 통화 정책 변화 이전에 시장 자본이 인플레이션 헤지 자산으로 선제적 이동을 시작하게 만드는 강력한 신호임. 이는 단순한 경제 지표의 변동을 넘어, 차기 금리 결정 및 공식 발표라는 확정적 데드라인을 앞두고 시장의 포지션 재구축을 강제하는 전조적(Pre-Structural) 사건임.
- **Upgrade Condition:** 연준 위원들의 긴급 매파적 발언(Verbal Commitment)이 뒤따르거나 국채 금리(US10Y)가 심리적 저항선을 돌파할 경우
- **Invalidation Condition:** 익월 데이터에서 강력한 평균 회귀(Mean Reversion)가 발생하거나 데이터 산출 오류로 판명될 경우

### Topic: data/features/anomalies/2026/04/12/struct_dart_disposal.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** DART(전자공시시스템) 상장사 주요주주 및 법인
- **Temporal Anchor:** 2026-04-12 (Anomaly Detection Date)
- **Unresolved Question:** 5건의 대규모 지분 처분(Disposal)이 특정 섹터에 집중되어 있는지, 아니면 시장 전반의 유동성 확보를 위한 강제적 매각인지 여부
- **Rationale:** 본 신호는 한국 DART 시스템에서 단기간(Count=5) 내에 발생한 지분 처분(Disposal) 이상 현상을 포착한 것입니다. 이는 단순한 '미래 성장성' 담론이 아니라, 실제 자본의 이탈과 재배치가 시작되었음을 나타내는 구조적 전조입니다. 대량 매도 공시는 즉각적인 수급 불균형과 가격 조정을 유발하며, 30일 이상 지속되는 일반 트렌드와 달리 공시 시점으로부터 특정 기간 내에 자본 이동이 완료되어야 하는 시점 구속성(Temporal Anchor)을 가집니다.
- **Upgrade Condition:** 처분 주체가 동일 계열사이거나, 특정 규제(대주주 적격성/공정거래법) 시한 임박과 맞물릴 경우
- **Invalidation Condition:** 단순 오기입 정정 공시이거나, 기획된 블록딜이 시장가에 영향을 주지 않고 종료될 경우

### Topic: data/features/anomalies/2026/04/12/liquidity_m2_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (FRED)
- **Temporal Anchor:** 2026-04-12 (Anomaly Detection Date)
- **Unresolved Question:** 이 급격한 M2 증가가 연준의 의도적 공급(QE 재개)인지, 아니면 상업은행의 급격한 신용 팽창에 의한 일시적 노이즈인가?
- **Rationale:** M2 통화량이 100.0% 백분위수라는 극단적 수치에 도달한 것은 시장의 유동성 과잉 상태를 나타냄. 이는 연준의 정책 공식 발표 이전에 인플레이션 헤지 자산으로의 자본 재배치(Capital Flow Anticipation)를 유도하는 강력한 전조 신호임. 일반적인 추세가 아닌 'Extreme' 상태의 아노말리이므로 구조적 변화(금리 인상 압박 또는 자산 버블 시작)의 임계점에 도달함.
- **Upgrade Condition:** 다음 FOMC 의사록에서 과잉 유동성 흡수(QT 강화) 언급이 나오거나 CPI 데이터가 예상치를 상회할 경우
- **Invalidation Condition:** 데이터 오류 수정 또는 다음 달 M2 데이터가 80번째 백분위수 이하로 급격히 회귀할 경우

### Topic: data/features/anomalies/2026/04/12/inflation_kor_cpi_ecos.json L1 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** Bank of Korea (BoK)
- **Temporal Anchor:** 2026-04-12 (Data Release) / Next MPC Meeting Window
- **Unresolved Question:** 한국은행이 수출 둔화 우려에도 불구하고 1.86 Z-Score에 달하는 인플레이션 압력을 억제하기 위해 즉각적인 금리 인상 카드를 꺼낼 것인가?
- **Rationale:** 한국 CPI가 Z-Score 1.86(임계치 1.5 상회)을 기록하며 통계적 유의미한 변동성을 보임. 이는 시장이 한국은행의 정책 금리 결정을 기다리기 전에 채권 금리 및 외환 시장에서 선제적인 자본 재배치를 유도하는 전형적인 Pre-Structural Signal임. 단순 추세가 아닌 특정 시점(4월 12일)의 데이터 충격에 기반한 신호로 판단됨.
- **Upgrade Condition:** 한국은행 총재의 매파적(Hawkish) 발언이나 추가적인 생산자물가지수(PPI)의 동반 상승 확인 시
- **Invalidation Condition:** 다음 지표에서 기저효과가 확인되거나 원화 가치의 급격한 절상으로 수입 물가 압력이 자연 해소될 경우

### Topic: data/features/anomalies/2026/04/12/comm_wti_fred.json L2 Signal
- **Signal Type:** Dependency
- **Trigger Actor:** Global Energy Market Participants / Supply Chain Nodes
- **Temporal Anchor:** 2026-04-12 to 2026-04-19 (Immediate response window)
- **Unresolved Question:** 실물 공급 차질에 의한 물리적 숏스퀴즈인가, 아니면 특정 지정학적 이벤트에 대한 선제적 헷징 수요인가?
- **Rationale:** WTI 유가가 20일 평균($97.38)을 크게 상회하여 $114에 도달하며 Z-Score 2.19를 기록한 것은 단순한 변동성이 아닌 에너지 공급망의 구조적 취약성(Dependency)이 노출된 신호임. 이는 에너지 비용 급증에 따른 타 산업군의 자본 재배치와 리스크 오프 심리를 즉각적으로 유도하는 전형적인 Pre-Structural Signal에 해당함.
- **Upgrade Condition:** OPEC+의 긴급 감산 발표 또는 주요 산유국의 수출 통제 공식화 시
- **Invalidation Condition:** WTI 가격이 48시간 이내에 $100 이하로 회귀하거나 데이터 오류로 판명될 경우

### Topic: data/features/anomalies/2026/04/12/fx_usdkrw_ecos.json L1 Signal
- **Signal Type:** Capital Flow Anticipation
- **Trigger Actor:** Bank of Korea (BoK) / Ministry of Economy and Finance (MOEF)
- **Temporal Anchor:** 2026-04-12 (T+48h Window)
- **Unresolved Question:** 환율 1,480원선 붕괴 시 외환당국의 실개입(Smoothing Operation)이 즉각적으로 단행될 것인가, 아니면 추가 하락을 용인할 것인가?
- **Rationale:** USD/KRW 환율이 20일 이동평균 대비 -1.55 Z-Score 수준인 1481.1원까지 급락한 것은 단순 변동성을 넘어선 통계적 이상치임. 이는 외환 당국의 개입 가능성을 높이고 시장 참여자들의 선제적 포지션 청산 또는 자금 재배치를 유도하는 전구조적 신호(Pre-Structural Signal)로 판단됨.
- **Upgrade Condition:** 당국의 '구두 개입(Verbal Warning)' 공식 발표 또는 외환보유고 변동 수반 시
- **Invalidation Condition:** Z-Score가 -1.0 이내로 회복되며 20일 이동평균선(1501원)으로 회귀할 경우

### Topic: data/features/anomalies/2026/04/12/index_spx_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Market Participants
- **Temporal Anchor:** 2026-04-15 (Q1 Earnings Season Kick-off / US Tax Deadline)
- **Unresolved Question:** 이 Z-Score 1.69의 이탈이 실적 발표 전의 선제적 수익 실현인가, 아니면 새로운 펀더멘탈 반영을 위한 포지션 구축인가?
- **Rationale:** S&P 500 지수가 FRED 데이터 기준 Z-Score 1.69의 유의미한 이탈을 보임. 이는 4월 중순 실적 시즌 및 매크로 지표 발표를 앞두고 자본이 선제적으로 이동하고 있음을 시사하는 L1 신호임. 단순한 추세 지속이 아닌 통계적 이상점(Anomaly)으로서 자본 재배치(Capital Flow Anticipation)의 전조 현상으로 판단됨.
- **Upgrade Condition:** VIX 또는 US10Y ROC가 임계값을 돌파하여 Regime Multiplier가 1.2 이상으로 상승할 경우
- **Invalidation Condition:** Z-Score가 3거래일 이내에 1.0 미만으로 회귀하며 평균 회귀(Mean Reversion)가 발생할 경우

### Topic: data/features/anomalies/2026/04/12/rates_us10y_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Liquidity Providers / FOMC
- **Temporal Anchor:** 2026-04-12 (T+5 Day Rebalancing Window)
- **Unresolved Question:** 금리가 90.5% 백분위수 임계점에서 저항을 형성할 것인가, 아니면 기술적 돌파를 통해 주식 시장의 투매를 유도할 것인가?
- **Rationale:** US 10년물 국채 금리가 90.5%라는 극단적인 통계적 임계점(Percentile)에 도달한 것은 단순한 가격 변동이 아닌, 기관 투자자들의 포트폴리오 재조정 및 자본 유출입 압박이 즉각적으로 발생하는 지점임. 이는 법적/정책적 확정 이전에 시장 데이터 자체가 자본의 대이동(Rotation)을 강제하는 '자본 흐름 기대' 신호의 전형적인 모습임.
- **Upgrade Condition:** US10Y 금리가 4.35%를 돌파하거나 백분위수가 95%를 상회하여 'Risk-Off' 정서가 확산될 경우
- **Invalidation Condition:** 금리가 20일 이동평균선(4.321%) 아래로 급격히 하회하며 4.20% 수준으로 회귀할 경우
