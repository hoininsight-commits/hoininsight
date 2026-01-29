# HARD_FACT_VERIFIER (IS-25)

## 1. 목적 (Purpose)
IssueSignal이 발화하는 모든 트리거가 "출처 2중 이상 검증된 하드 팩트"에 기반하도록 강제한다. 단일 매체, 단일 기관, 또는 단순 인용 보도에 의한 편향된 확신을 배제하고, 구조적 진실만을 전달하는 '심판자'로서의 권위를 확보하기 위함이다.

## 2. 출처 타입 정의 (Source Types)

### Strong Sources (강력한 출처)
- **GOV_DOC**: 정부 공문, 법안, 예산 집행문, 행정명령.
- **REGULATORY**: 규제/감독기관 승인 및 인가 문서.
- **COMPANY_FILINGS**: 공식 공시(DART/SEC), 실적 발표 자료, IR 공식 문서.
- **CONTRACT_DATA**: 확정된 계약서, 수주/발주 데이터, 납품 기록.

### Medium Sources (중간 수준 출처)
- **FLOW_DATA**: ETF/펀드 자금 유출입, 시장 수급 데이터.
- **PHYSICAL_DATA**: 공급망 리드타임 데이터, 물류 설치 현황, 생산 능력 지표.
- **EARNINGS_CALL**: 실적 발표 컨퍼런스 콜 공식 발언.
- **MAJOR_MEDIA**: Bloomberg, Reuters 등 원천 취재력이 있는 1차 주요 매체.

### Weak/Exclude Sources (제외 또는 보조 출처)
- **ANALYST_REPORT**: 기관 리포트 (단독 사용 불가, 2중 검증 필수).
- **BLOG/SNS**: 개인 의견 및 미확인 정보.
- **RE-QUOTE**: 타 매체 기사를 단순히 재인용한 보도.

## 3. PASS 조건 (Pass Criteria)
다음 중 하나라도 충족해야 통과한다.

1.  **서로 다른 SourceType 2개 이상이 동일 팩트를 지지**:
    - 예: `GOV_DOC` + `COMPANY_FILINGS`
    - 예: `CONTRACT_DATA` + `FLOW_DATA`
2.  **Strong Source 1개 + Medium Source 1개 조합**:
    - 예: `REGULATORY` + `PHYSICAL_DATA`
    - 예: `COMPANY_FILINGS` + `EARNINGS_CALL`

## 4. FAIL 조건 (Fail Criteria)
- 출처가 1개뿐인 경우.
- `ANALYST_REPORT` 또는 `MAJOR_MEDIA` 단독 보도인 경우.
- 동일 기사를 여러 곳에서 베껴 쓴 재인용 구조(Redundancy).
- 구체적 수치나 행위 없이 "전망", "가능성", "기대" 등 발언만 존재하는 경우.

**FAIL 코드**: `SINGLE_SOURCE_RISK`

## 5. 파이프라인 위치 (Pipeline Integration)
`TRAP_ENGINE (IS-24) → FACT_VERIFIER (IS-25) → FINAL_DECISION (IS-15)`

IS-24가 구조적 함정을 제거한다면, IS-25는 그 서사를 지탱하는 **데이터의 객관적 증거력**을 최종 심판한다.
