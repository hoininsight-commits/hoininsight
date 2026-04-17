# report_step74_pre_structural_signal.md
Date: 2026-04-17

## 1. Definition Recap
Pre-Structural Signal: Market-moving event where narrative/expectation begins reallocating capital BEFORE legal/policy/earnings confirmation.

## 2. Detected Signals
### Topic: data/features/anomalies/2026/04/17/crypto_btc_usd_spot_coingecko.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Liquidity Providers / Market Makers
- **Temporal Anchor:** 2026-04-17 (Anomaly Detection Date)
- **Unresolved Question:** 해당 가격 급등이 특정 거시경제 지표 발표 전의 선취매(Front-running)인지, 혹은 대규모 현물 ETF 유입에 따른 유동성 병목 현상인지는 아직 확인되지 않음.
- **Rationale:** Z-Score 2.49는 단순한 가격 상승(Trend)을 넘어 표준 편차 범위를 크게 벗어난 구조적 이상 징후(L2 Signal)를 의미함. 이는 시장에 아직 공개되지 않은 뉴스나 정책적 변화가 가시화되기 전, 대규모 자본의 선제적 이동(Capital Flow Anticipation)이 발생하고 있음을 시사하는 전형적인 Pre-Structural 신호임.
- **Upgrade Condition:** Z-Score가 3.0을 초과하거나, 특정 기관의 대규모 포지션 공시 혹은 정책적 발언이 동반될 경우
- **Invalidation Condition:** 가격이 48시간 이내에 20일 이동평균선(71,967.2) 이하로 회귀하며 단순 변동성 확대로 판명될 경우

### Topic: data/features/anomalies/2026/04/17/credit_hy_spread_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional High-Yield Credit Desks
- **Temporal Anchor:** 2026-04-17 (Signal Date) + 14-day Mean Reversion Window
- **Unresolved Question:** Does this spread compression reflect a fundamental low-default environment or a terminal 'reach-for-yield' bubble before a liquidity dry-up?
- **Rationale:** High Yield(HY) 스프레드가 Z-Score -1.55 수준으로 급격히 압착(Compression)된 것은 시장의 과도한 낙관론 또는 자본의 위험 자산 쏠림 현상을 나타냄. 이는 역사적 평균으로의 회귀(Mean Reversion)를 앞둔 전조 증상이며, 제도권 자금이 리스크 관리를 위해 자산을 재배분(Rotation)하기 직전의 'Capital Flow Anticipation' 신호로 해석됨. 단순히 저평가된 상태가 아니라, 통계적 임계치를 넘어서는 이상 징후가 발생한 시점이므로 Pre-structural Signal의 요건을 충족함.
- **Upgrade Condition:** A sudden >15bps widening within 48 hours or a hawkish pivot from central banks acting as a catalyst.
- **Invalidation Condition:** Spreads remain at these levels for >30 days with no volatility increase, indicating a structural regime shift rather than an anomaly.

### Topic: data/features/anomalies/2026/04/17/inflation_pce_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (Fed)
- **Temporal Anchor:** 2026-04-17 (PCE Data Release Window)
- **Unresolved Question:** 연준이 이 극단적인 PCE 수치를 일시적 현상으로 치부할 것인가, 아니면 즉각적인 금리 경로 수정(Pivot/Hike)에 나설 것인가?
- **Rationale:** PCE 인플레이션 지표가 100 백분위수(Extreme)에 도달한 것은 단순한 추세가 아닌 정책 변화를 강제하는 구조적 이상 신호임. 이는 연준의 공식 금리 결정 전 시장 자본이 위험 자산에서 안전 자산으로 선제적 재배치(Anticipatory Reallocation)를 일으키는 명확한 트리거가 되며, 데이터 발표 시점으로부터 차기 정책 결정까지의 시간적 제약(Temporal Anchor)이 뚜렷함.
- **Upgrade Condition:** 연준 위원들의 긴급 발언(Verbal Warning)이나 차기 FOMC 금리 인상 확률이 70%를 상회할 경우
- **Invalidation Condition:** 다음 달 PCE 데이터가 급격히 하향 조정되거나, 고용 지표가 예상치를 크게 하회하여 인플레이션 압력을 상쇄할 경우

### Topic: data/features/anomalies/2026/04/17/struct_dart_disposal.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** DART 공시 상장법인 및 금융감독원
- **Temporal Anchor:** 2026-04-17 (Anomaly Detection Date)
- **Unresolved Question:** 대규모 자산/지분 처분 이후 확보된 현금이 주주환원으로 이어질 것인가, 아니면 유동성 위기 대응을 위한 부채 상환에 투입될 것인가?
- **Rationale:** DART(전자공시)상에서 특정 시점에 자산 및 지분 처분(Disposal) 관련 공시가 5건 이상 집중적으로 탐지된 것은 시장 내 자본 재배치를 시사하는 선행 구조적 시그널임. 이는 실제 현금 유입이나 사업 구조 개편이 완료되기 전, 시장 참여자들이 자금 흐름의 방향성을 선반영하게 만드는 트리거로 작용함.
- **Upgrade Condition:** 처분 자산의 매각 대금 사용처가 '자기주식 소각' 또는 '특별배당'으로 확정 발표될 경우
- **Invalidation Condition:** 공시 철회 혹은 30일 이내에 추가적인 자산 매각 관련 후속 데이터가 발생하지 않을 경우

### Topic: data/features/anomalies/2026/04/17/liquidity_m2_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (Central Bank)
- **Temporal Anchor:** 2026-04-17 (M2 Data Release Window)
- **Unresolved Question:** 이러한 M2의 급격한 팽창이 연준의 의도적인 유동성 주입인지, 혹은 은행 시스템 내의 기술적 결함이나 긴급 구제 금융의 결과인지 여부
- **Rationale:** M2 통화 공급량이 100번째 백분위수(Extreme)에 도달했다는 것은 역사적 임계치에 도달했음을 의미함. 이는 공식적인 금리 결정이나 정책 발표가 있기 전, 시장이 유동성 과잉을 선반영하여 자산 가격을 재평가하고 자본을 위험 자산으로 재배분하게 만드는 전구조적(Pre-structural) 신호임. 특히 z-score 1.83은 단순한 변동성을 넘어선 이상 현상으로, 자본 흐름의 즉각적인 변화를 야기함.
- **Upgrade Condition:** 연준 관계자의 통화 정책 스탠스 변화 발언(Dovish pivot)이나 인플레이션 지표의 동반 상승 확인 시
- **Invalidation Condition:** 다음 주 보고 데이터에서 M2 수치가 통계적 오류로 판명되어 대폭 수정(Revision)되거나 평균으로 급격히 회귀할 경우

### Topic: data/features/anomalies/2026/04/17/inflation_kor_cpi_ecos.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Bank of Korea (BOK)
- **Temporal Anchor:** 2026-05-14 (Expected May MPC Meeting)
- **Unresolved Question:** 통계적 이상치(Z-Score 1.86)를 보인 CPI 상승이 한은의 금리 인하 사이클 중단 혹은 금리 인상을 강제할 수준인가?
- **Rationale:** 한국 소비자물가지수(CPI)의 Z-Score가 1.86(임계치 1.5 초과)을 기록하며 통계적 이상 신호를 보냄. 이는 차기 금리 결정 회의(5월) 이전에 시장 참여자들이 긴축적 통화 정책으로의 회귀를 예상하고 채권 매도 및 원화 포지션 재조정을 시작하게 만드는 선제적 자본 흐름(Capital Flow Anticipation) 신호임.
- **Upgrade Condition:** 한은 총재의 긴급 구두 개입 혹은 인플레이션 경고 메시지 발표 시
- **Invalidation Condition:** 30일 이내 발표되는 기대인플레이션 지표가 안정세로 회귀하거나 유가 등 외부 요인의 급락 확인 시

### Topic: data/features/anomalies/2026/04/17/index_nasdaq_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Portfolio Managers & HFT Algorithms
- **Temporal Anchor:** 2026-04-17 (Peak Technical Threshold)
- **Unresolved Question:** Does this 100th percentile breach signal a structural regime shift in valuation or an immediate liquidity-driven blow-off top?
- **Rationale:** 나스닥 지수가 역사적/통계적 극단값인 100% 백분위수(26,333)에 도달한 것은 기술적 한계점에 도달했음을 의미함. 이는 실제 정책 변화나 실적 발표 이전에 알고리즘 및 기관 투자자들의 선제적 자산 재배치(Rotation)를 유발하는 강력한 전구 신호임. 일반적인 상승 추세와 달리 '극단적 이상치(Extreme Anomaly)'로 분류되므로 단기적 변동성 확대 및 자본 흐름의 구조적 변화가 임박했음을 시사함.
- **Upgrade Condition:** If volatility (VIX) spikes within 48 hours or if a major tech constituent announces a 5% deviation in guidance.
- **Invalidation Condition:** If the Nasdaq index maintains the current level (26,333) with low volatility for more than 30 consecutive days.

### Topic: data/features/anomalies/2026/04/17/derived_gold_silver_ratio.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Quantitative Hedge Funds & Precious Metal Institutional Desks
- **Temporal Anchor:** 2026-04-17 (Signal discovery) + 5-trading day mean reversion window
- **Unresolved Question:** 금/은 비율의 급격한 하락이 은의 산업적 수요 폭증에 의한 구조적 변화인지, 아니면 투기적 자본의 일시적 유입에 따른 기술적 오버슈팅인지 여부
- **Rationale:** 금/은 비율(GSR)이 20일 이동평균 대비 Z-Score -1.61을 기록하며 통계적 유의미성 임계점(1.5)을 돌파함. 이는 은이 금 대비 단기적으로 과하게 고평가되었거나 금이 저평가된 상태를 나타내며, 퀀트 알고리즘 및 기관의 페어 트레이딩(Pair Trading)에 의한 자본 재배치(Capital Rotation)를 강제하는 기술적 전조 현상임. 30일 이상 지속되기 어려운 단기적 변동성 데이터로서 시간적 앵커를 보유하므로 Pre-Structural Signal로 판단됨.
- **Upgrade Condition:** Z-Score가 -2.0을 초과 돌파하며 거래대금이 전주 평균 대비 40% 이상 급증할 경우
- **Invalidation Condition:** GSR(Gold-Silver Ratio)이 20일 이동평균선(63.28) 내로 48시간 이내에 복귀할 경우

### Topic: data/features/anomalies/2026/04/17/comm_wti_fred.json L2 Signal
- **Signal Type:** Dependency
- **Trigger Actor:** WTI (West Texas Intermediate) Energy Market
- **Temporal Anchor:** 2026-04-17 (Threshold Breach)
- **Unresolved Question:** 유가 100달러 돌파가 글로벌 공급망의 한계 비용(Marginal Cost) 임계치를 넘어 실물 경제의 가동 중단을 유발할 것인가?
- **Rationale:** WTI 유가가 $100를 돌파하며 97.2%라는 극단적 퍼센타일에 도달한 것은 단순한 가격 상승을 넘어 산업 전반의 비용 구조와 자본 배치를 강제로 재조정하게 만드는 '구조적 의존성 노출(Dependency)' 시그널임. 이는 에너지 비용 급증에 따른 기업 이익 훼손 및 인플레이션 압박이라는 확실한 시간적/가격적 닻(Anchor)을 제공함.
- **Upgrade Condition:** WTI 종가가 3거래일 연속 $100 이상을 유지하며 운송 및 제조 섹터의 가이던스 하향 조정이 시작될 때
- **Invalidation Condition:** WTI 가격이 20일 이동평균선($99.89) 아래로 즉각 회귀하며 90 percentile 이하로 안정화될 때

### Topic: data/features/anomalies/2026/04/17/fx_usdkrw_ecos.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Bank of Korea (BOK) & Institutional FX Desks
- **Temporal Anchor:** 2026-04-17 (Immediate T+5 window)
- **Unresolved Question:** 환율이 1,470원대 초반까지 급락함에 따라 외환 당국의 실질적인 시장 개입(Smoothing Operation)이 즉각적으로 발생할 것인가?
- **Rationale:** USD/KRW 환율이 20일 이동평균선(1497.9) 대비 현저히 낮은 1472.6으로 급락하며 Z-Score -1.55의 이상치가 감지됨. 이는 단순 추세가 아닌 단기 자본의 급격한 이동(Capital Flow)을 시사하며, 수출 기업의 환헤지 전략 수정 및 당국의 개입 압력을 발생시키는 전구조적 신호임. 30일 이내에 정책적 반응이나 실적 전망 수정이 동반될 가능성이 높음.
- **Upgrade Condition:** 한국은행의 공식적인 구두 개입(Verbal Intervention) 발언이나 1,470원선 강력 지지 확인 시
- **Invalidation Condition:** 특별한 재료 없이 5거래일 이내에 20일 이동평균선(1497.9)으로 회귀할 경우

### Topic: data/features/anomalies/2026/04/17/metal_silver_kag_coingecko.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Market Liquidity Providers / Commodity Token Investors
- **Temporal Anchor:** 2026-04-17
- **Unresolved Question:** 실물 은(Silver) 시장의 공급망 병목 현상에 의한 현물 프리미엄 상승인가, 아니면 암호화폐 시장 내 안전 자산으로의 순환매인가?
- **Rationale:** 2026년 4월 17일 기준 KAG(Kinesis Silver)에서 Z-Score 1.67의 통계적 이상 수치가 감지되었습니다. 이는 단순한 가격 상승 트렌드가 아니라, 특정 시점에 집중된 자본의 선제적 재배치(Capital Flow Anticipation)를 나타냅니다. 실물 자산과 연동된 토큰화 상품에서의 이러한 변동성은 향후 원자재 시장의 구조적 변화나 가격 변동성이 확정되기 전 시장 참여자들이 선제적으로 움직이고 있음을 시사하는 전조적 신호로 해석됩니다.
- **Upgrade Condition:** Z-Score가 2.0을 초과하거나 실물 은 인도 지연 보고서가 공식적으로 발표될 경우
- **Invalidation Condition:** 48시간 이내에 Z-Score가 1.0 미만으로 회귀하며 평균치로 수렴할 경우

### Topic: data/features/anomalies/2026/04/17/index_spx_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Market Participants
- **Temporal Anchor:** 2026-04-17
- **Unresolved Question:** S&P 500 지수가 20일 이동평균선 대비 2.07 시그마를 이탈하며 7000선을 돌파한 것이 펀더멘털의 변화인지, 아니면 과매수 구간에서의 기술적 오버슈팅인지 여부
- **Rationale:** S&P 500 지수가 20일 이동평균 대비 Z-Score 2.07이라는 통계적 이상치(Anomaly)를 기록한 것은 시장 내 자본 재배치가 급격하게 일어나고 있음을 시사함. 이는 단순한 추세적 상승이 아니라 특정 심리적/구조적 임계점을 넘어서는 '자본 흐름의 선행적 반응(Capital Flow Anticipation)'으로 판단되며, 30일 이내에 가격 조정 혹은 새로운 가격대 형성이라는 결론이 도출되어야 하는 시점 임계적 신호임.
- **Upgrade Condition:** Z-Score가 2.5를 초과하거나, 3거래일 연속 L2 이상의 시그널이 유지되며 거래량이 동반될 경우
- **Invalidation Condition:** 지수가 20일 이동평균선(6643.64) 이하로 급격히 회귀하며 평균 회귀(Mean Reversion)가 발생할 경우

### Topic: data/features/anomalies/2026/04/17/rates_us10y_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** US Treasury Market Participants
- **Temporal Anchor:** 2026-04-30 (End of Month / Pre-May FOMC Window)
- **Unresolved Question:** 실질 금리의 급격한 변동이 단순한 기술적 반등인지, 아니면 5월 정책 결정을 앞둔 근본적인 인플레이션 기대치 재조정인지 여부
- **Rationale:** US 10년물 국채 수익률이 90.7% 퍼센타일에 도달한 것은 시장이 공식적인 정책 발표나 경제 지표 확인 전, 자본을 선제적으로 재배치하고 있음을 나타내는 신호임. 이는 단순한 추세적 상승이 아니라 특정 임계치(L1 Signal)에 도달하여 구조적 변화를 앞둔 '자본 흐름의 선행적 반응'으로 판단됨.
- **Upgrade Condition:** US10Y 수익률이 95% 퍼센타일을 돌파하거나 연준 위원의 매파적/비둘기파적 발언이 데이터와 결합될 경우
- **Invalidation Condition:** 수익률이 5거래일 이내에 20일 이동평균선(4.33)으로 회귀하며 변동성이 급감할 경우

### Topic: data/features/anomalies/2026/04/17/inflation_cpi_fred.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Federal Reserve (Policy Response Actor)
- **Temporal Anchor:** 2026-04-17 (Data Release & Immediate Repricing Window)
- **Unresolved Question:** 차기 FOMC 이전 시장의 기대 금리(Terminal Rate)가 100th percentile 데이터에 부합하도록 즉각 상향 조정될 것인가?
- **Rationale:** CPI 지수가 100번째 백분위수(Extreme)라는 통계적 임계점에 도달함에 따라, 공식적인 정책 변경이나 연준의 성명이 발표되기 전 시장 참여자들이 금리 인상 가속화를 예상하며 자산 포트폴리오를 선제적으로 재조정(Capital reallocation)하게 만드는 강력한 전구적(Pre-structural) 신호임.
- **Upgrade Condition:** 연준 관계자의 긴급 매파적 발언 또는 시장 금리(10Y)의 즉각적인 20bp 이상 급등 발생 시
- **Invalidation Condition:** 해당 수치가 데이터 집계 오류로 판명되거나 기저효과에 의한 일시적 왜곡으로 확인될 경우

### Topic: data/features/anomalies/2026/04/17/risk_vix_fred.json L1 Signal
- **Signal Type:** Capital
- **Trigger Actor:** Institutional Risk Managers
- **Temporal Anchor:** 2026-04-17 (Window: 5-10 Trading Days)
- **Unresolved Question:** VIX의 급격한 하락(18.17)이 실제 리스크 해소에 따른 안착인지, 아니면 기술적 반등을 앞둔 '변동성 압축' 구간인가?
- **Rationale:** VIX 지수가 20일 이동평균(24.12) 대비 Z-Score -1.56 수준인 18.17까지 급락한 것은 시장의 위험 인식이 단기적으로 과도하게 낙관 편향되어 있음을 나타냄. 이는 구조적 리스크가 완전히 해소되지 않은 상태에서 자본이 위험 자산으로 선제적 이동(Capital Flow Anticipation)하고 있다는 전구조적 신호이며, 통계적 평균 회귀 원리에 따라 단기 내 변동성 폭발이나 포트폴리오 재조정이 발생할 가능성이 높음.
- **Upgrade Condition:** VIX가 20일 이동평균선(24.12) 방향으로 급격히 회귀하며 하락분의 50% 이상을 하루 만에 만회할 때
- **Invalidation Condition:** VIX가 18.0 수준에서 14거래일 이상 박스권을 유지하며 변동성 체제(Regime) 자체가 하향 안정화될 때

### Topic: data/features/anomalies/2026/04/17/struct_dart_cb_bw.json L2 Signal
- **Signal Type:** Capital
- **Trigger Actor:** DART Listed Issuers (CB/BW)
- **Temporal Anchor:** 2026-04-17 (Signal Detection Date)
- **Unresolved Question:** 전환사채(CB) 및 신주인수권부사채(BW)의 전환가액 조정(Refixing) 혹은 권리 행사 기간 진입에 따른 실제 물량 출회 규모와 가격 하방 압력의 실현 여부
- **Rationale:** 본 신호는 한국 기업 공시 시스템(DART) 내 메자닌 금융(CB, BW)과 관련된 구조적 이상 현상(L2)을 탐지한 것임. 이는 단순한 기업 홍보나 업황 기대감이 아닌, 자본 구조의 변화(지분 희석 또는 채무 상환)를 유발하는 실제 공시 이벤트를 앵커로 함. 특히 CB/BW의 리픽싱이나 전환권 행사는 법적 절차 완료 전부터 시장 참여자들의 선제적 포지션 조정(Short-selling 또는 물량 회피)을 유도하므로 Pre-Structural Signal의 정의에 부합함.
- **Upgrade Condition:** 전환권 행사 시작일이 5영업일 이내로 접근하거나, 리픽싱 하한선 도달에 따른 대규모 잠재 물량 확정 공시 발생 시
- **Invalidation Condition:** 발행사의 CB/BW 전량 조기상환(Call Option 행사) 공시 또는 전환사채권자의 전환권 행사 포기 선언 시
