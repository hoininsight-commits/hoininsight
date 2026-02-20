# TRAP_DETECTION_ENGINE (IS-24)

## 1. 목적 (Purpose)
IssueSignal이 "말하면 위험한 가짜 트리거 또는 함정(Trap)"을 자동으로 식별하고 거절(REJECT)하기 위함이다. 뉴스나 발언만 있고 실질적인 자본 집행이 없거나, 구조적으로 빠져나갈 틈이 없는 서사를 사전에 차단하여 정보의 신뢰도를 극대화한다.

## 2. 3축 검증 시스템 (The 3-Axis Validation)
모든 트리거 후보는 다음 세 가지 축을 모두 통과해야 한다.

### A) CAPITAL_CONFIRMATION_SCORE (자본 실재 확인)
- **목적**: 뉴스나 발언만 떠도는 "공기 트리거" 차단.
- **점수 산정**:
    - **Strong (+50)**: 공시, 계약, 증설 집행, 납품 기록 등 확정적 물적 근거.
    - **Medium (+30)**: 공식 문서, 공신력 있는 기관의 데이터, 다중 출처 보고서.
    - **Weak (+0)**: 단일 기사, 루머, 기업 PR 문구.
- **PASS 조건**: 점수 합계 **50점 이상**.
- **FAIL 코드**: `NO_CAPITAL_EVIDENCE`

### B) EXIT_VISIBILITY_CHECK (출구/수요 주체 존재)
- **목적**: 병목은 존재하나 실제 돈을 써야 할 주체나 시점이 불명확한 "막힌 서사" 차단.
- **PASS 조건**:
    - **Actor**: {GOV, BIGTECH, OEM, UTILITY, BANK, DEFENSE, CONSUMER, EXPORTER} 중 하나가 명시됨.
    - **Must Item**: 병목 현상을 일으키는 핵심 아이템이 명시됨.
    - **Time Window**: 72h / 2w / 1q 등 구체적인 시간 구간이 명시됨.
- **FAIL 코드**: `NO_FORCED_BUYER`, `NO_MUST_ITEM`, `NO_TIME_WINDOW`

### C) TIME_ASYMMETRY_TRAP (시간 비대칭 함정)
- **목적**: 진입은 쉽지만 퇴출이 너무 빠른 리스크 노출 구조 차단.
- **논리**:
    - **EntryLatency**: 실물 반영까지 걸리는 지연 시간.
    - **ExitShock**: 무효화(Kill-switch) 시 시장 반응 속도.
- **PASS 조건**:
    - `EntryLatency <= ExitShock` (진입이 퇴출보다 빠름)
    - 또는, `EntryLatency`가 길더라도 자본이 이미 집행된(`Strong evidence`) 경우.
- **FAIL 코드**: `TIME_ASYMMETRY_TRAP`

## 3. 사유 코드 테이블 (Reason Codes)
| 코드 | 설명 |
| :--- | :--- |
| `NO_CAPITAL_EVIDENCE` | 자본 집행이나 물적 근거가 기준(50점) 미달 |
| `NO_FORCED_BUYER` | 강제적 수요 주체(Actor)가 불명확함 |
| `NO_MUST_ITEM` | 병목의 핵심인 'Must Item'이 정의되지 않음 |
| `NO_TIME_WINDOW` | 사건의 시간적 범위가 모호함 |
| `TIME_ASYMMETRY_TRAP` | 정책/발언의 휘발성이 실물 반영 속도보다 지나치게 빠름 |

## 4. 예시 (Examples)

### PASS 예시
- **상황**: 보조금 삭감안 법안 통과 + 기업들의 공장 증설 주문 취소 공시.
- **판정**: PASS (`CAPITAL_SCORE: 100`, `ACTOR: GOV`, `ASYMMETRY: SAFE`)

### REJECT 예시
- **상황**: "정부 관계자가 보조금을 삭감할 수도 있다고 언급했다"는 단일 기사.
- **판정**: REJECT (`NO_CAPITAL_EVIDENCE`)

## 5. 역할 분리 (Separation of Concerns)
IS-24는 **신뢰도와 구조적 안전성**을 검증하며, IS-23(메모리)의 **중복성 체크**와는 독립적으로 작동한다.
