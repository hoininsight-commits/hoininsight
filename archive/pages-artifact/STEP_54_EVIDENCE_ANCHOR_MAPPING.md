# STEP 54 — EVIDENCE ANCHOR MAPPING (Constitution)

## 1. 목적 (Goal)
추론의 각 단계에 사용된 실제 데이터 소스(Evidence)를 연결(Mapping)하여, 결과의 객관성을 보장한다.

## 2. Anchor 유형 (Source Types)
- **Macro**: FRED, ECOS 등 거시 경제 지표.
- **Market**: Stooq, Coingecko 등 가격 및 수급 데이터.
- **Policy**: DART 공시, 정부 보도자료.
- **On-chain**: 블록체인 트랜잭션 및 유입/유출 데이터.
- **News**: 외신 및 주요 언론사의 팩트 기반 보도.

## 3. Mapping 로직 (Mapping Logic)
- **Source Link**: 각 데이터 포인트는 고유한 URI 또는 Reference ID를 가진다.
- **Timestamp**: 데이터가 수집된 정확한 시점을 기록한다.
- **Key Value**: 추론에 결정적 영향을 준 핵심 수치(Critial Number)를 추출한다.

## 4. 출력 규격 (Evidence Schema)
```yaml
evidence_anchors:
  - type: "MACRO"
    source: "FRED"
    ref_id: "FEDFUNDS"
    key_value: "5.5%"
    rationale: "실질 금리 압박이 테크 섹터 밸류에이션의 하방 압력으로 작용."
  - type: "POLICY"
    source: "DART"
    ref_id: "202601290001"
    key_value: "제3자 배정 증자"
    rationale: "대주주 지분 희석 없는 자금 조달로 구조적 신뢰도 하락."
```
