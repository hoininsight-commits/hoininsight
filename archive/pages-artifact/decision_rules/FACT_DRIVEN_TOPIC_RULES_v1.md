# FACT-DRIVEN TOPIC RULES v1.0 (Official Decision Anchor)

## 1. Purpose of Fact-Driven Topic Classification
본 문서는 주관적 추측이나 내러티브 중심의 분석 대신, **객관적 수치와 보고서(Report) 기반의 명확한 증거**가 존재하는 토픽을 판별하기 위한 기준을 정의한다. 시장 규모 변화나 대규모 자금 집행 등 '팩트'가 주도하는 토픽을 선별함으로써 HOIN 엔진의 신뢰도를 확보하는 데 목적이 있다.

## 2. Minimum Required Conditions (Mandatory)
모든 FACT-DRIVEN 토픽은 아래 세 가지 조건(F1, F2, F3)을 반드시 **동시에 충족**해야 한다.

- **F1 (Financial/Quantitative Metric)**: 명확한 화폐 단위(KRW, USD 등) 혹은 수량 단위가 포함된 구체적인 수치가 있어야 한다.
- **F2 (Factual Evidence Source)**: 정부 기관, 공시 자료(DART), 공식 보도자료, 혹은 검증된 시장 조사 기관의 리포트 등 신뢰할 수 있는 출처를 기반으로 해야 한다.
- **F3 (Fixed Timeline)**: 해당 사건이나 지표가 발생하는 구체적인 시점(발표일, 집행 기간, 마일스톤 등)이 명시되어야 한다.

## 3. Optional Topic Tags (FACT_*)
필요에 따라 아래의 태그를 추가하여 토픽의 성격을 세분화할 수 있다.
- `FACT_GOV_PLAN`: 정부 공식 계획 및 예산안 기반
- `FACT_CORP_DISCLOSURE`: 기업 공시 및 IR 자료 기반
- `FACT_MACRO_DATA`: FRED, ECOS 등 거시 지표 기반
- `FACT_INVEST_FLOW`: 대규모 투자 유치 및 지분 공시 기반

## 4. HOLD / DROP Criteria
아래 기준에 해당할 경우 토픽 선정을 보류하거나 취소한다.

### DROP (탈락)
- 수치 데이터 없이 "대규모", "획기적", "빠른 성장" 등 형용사만 존재하는 경우.
- 정보 출처가 불분명한 찌라시나 개인 블로그성 정보인 경우.
- 시점 정보가 없어 막연한 미래를 이야기하는 경우.

### HOLD (보류)
- 수치는 있으나 출처의 2차 검증(Cross-check)이 필요한 경우.
- 수치와 시점은 명확하나, 해당 데이터가 역사적 변동성 범위 내에 있어 '사건'으로 규정하기 모호한 경우.

## 5. Concrete Example: Data Center 24T KRW Case

- **토픽**: 대한민국 AI 데이터 센터 24조원 투자 계획
- **분석 (F1/F2/F3)**:
    - **F1 (수치)**: 총 투자 규모 **24조원** 명시.
    - **F2 (출처)**: 산업통상자원부 및 관련 주요 기업 연합 보드자료.
    - **F3 (시점)**: 향후 **5년(2025~2030)** 동안의 단계적 집행 계획.
- **판단**: 모든 조건을 충족하므로 `FACT_GOV_PLAN`, `FACT_INVEST_FLOW` 태그와 함께 `READY` 상태로 분류.
