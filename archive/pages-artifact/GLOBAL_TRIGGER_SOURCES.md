# GLOBAL_TRIGGER_SOURCES (IS-10)

## 1. 목적 (Purpose)
IssueSignal의 트리거 탐지 범위를 일반 헤드라인 뉴스를 넘어 실질적인 "조기 점화 포인트(Early Ignition Points)"로 확장한다. 주류 언론에 보도되기 전의 구조적 징후를 선제적으로 포착하는 것이 목표다.

## 2. 확장 트리거 소스 분류 (Expanded Sources)

### 2-1. 정책 및 일정 (Policy & Schedule)
- **G7 / G20 캘린더**: 공식 의제 및 실무급 회의 테마 분석.
- **다보스 포럼(Davos) 아젠다**: 글로벌 리더들의 관심사 및 신규 규제 담론 포착.
- **주요 중앙은행(FOMC, BOJ, ECB) 일정**: 이벤트 발생 전 '침묵 기간' 또는 '전조 발언' 페이즈 분석.

### 2-2. 자본 및 시장 구조 (Capital & Market Structure)
- **ETF 유입 급증 (Flow Spikes)**: 특정 섹터 또는 테마 ETF로의 기계적 자금 유입 포착.
- **국채 수익률 레지임 변화**: 채권 시장의 구조적 금리 변동 신호 탐지.
- **FX 캐리 트레이드 스트레스**: 환율 변동에 따른 자본 회수(Unwinding) 징후 포착.

### 2-3. 기업 행동 (Corporate Behavior)
- **자본 지출(Capex) 가이드라인**: 설비 투자 계획의 갑작스러운 변경이나 특정 기술로의 자원 집중.
- **생산 능력 고정(Capacity Lock-in)**: 핵심 부품이나 장비의 장기 공급 계약 또는 선점 공시.
- **비정형 M&A 수사학**: 딜 발표 전, 경영진의 "전략적 옵션" 또는 "도메인 확장"에 관한 특이 표현 탐지.

## 3. 구현 원칙 (Rules)
- **No Scraping Noise**: 일반적인 뉴스 스크랩이 아닌, "강제적 반응(Forced Reaction)"이 예상되는 데이터 소스만을 엄선한다.
- **WHY-NOW 매핑**: 모든 소스는 반드시 WHY-NOW 로직과 연결되어야 한다.
- **Evidence Ready**: 탐지된 신호는 HoinEngine의 증거 데이터와 즉시 대조 가능해야 한다.
