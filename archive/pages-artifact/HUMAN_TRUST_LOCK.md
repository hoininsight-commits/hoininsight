# HUMAN_TRUST_LOCK_ENGINE (IS-26)

## 1. 목적 (Purpose)
IssueSignal이 생성한 최종 결과물(Final Decision Card)이 "사람이 수정 없이 즉시 사용 가능한 상태"임을 기계적으로 보증한다. 틀릴 수 있는 말은 하지 않고, 확신할 수 없는 단계는 잠그는(Lock) 것이 핵심이다.

## 2. 5대 잠금 조건 (5-Axis Lock Conditions)
모든 결과물은 아래 5가지 조건을 **모두 충족**해야 `TRUST_LOCKED` 상태가 된다.

### A) FACT INTEGRITY (팩트 무결성)
- **기준**: IS-25(2중 출처 검증) 결과가 `PASS`여야 한다.
- **요건**: 검증된 하드 팩트(`verified_facts`)가 최소 1개 이상 존재해야 한다.

### B) STRUCTURAL COMPLETENESS (구조적 완결성)
- **기준**: 리포트에 다음 5대 요소가 반드시 포함되어야 한다.
    - **WHAT**: 발생한 사건의 실체
    - **WHY**: 구조적 필연성 (왜 피할 수 없는가)
    - **WHO**: 강제 행위 주체 (Actor)
    - **WHERE**: 자본의 목적지 (Destination)
    - **KILL SWITCH**: 전제가 틀리는 지점
- **누락 시**: `REJECT (INCOMPLETE_STRUCTURE)`

### C) ACTION CLARITY (행동 명확성)
- **기준**: 추측성 표현을 배제하고 강제 동사를 사용해야 한다.
- **금지어**: "가능성", "전망", "있을 수 있다" 등.
- **강제어**: "해야 한다", "불가피하다", "이동한다".
- **발견 시**: `HOLD (VAGUE_EXPRESSION)`

### D) NOVELTY GUARANTEE (희소성 보장)
- **기준**: IS-23(마켓 메모리) 기준, 최근 30일 이내에 동일한 구조적 해시가 존재하지 않아야 한다.
- **존재 시**: `REJECT (NOT_NOVEL)`

### E) HUMAN READABILITY (인간 가독성)
- **기준**: 문장 수가 과다(5문장 초과)하거나 과도한 기술적 전문용어만 나열된 경우.
- **판정**: `HOLD (LOW_READABILITY)`

## 3. 신뢰 상태 정의 (Trust States)
| 상태 | 설명 | 발화 여부 |
| :--- | :--- | :--- |
| `TRUST_LOCKED` | 즉시 사용 가능 | **발화 (OUTPUT)** |
| `HOLD` | 논리는 맞으나 보완 필요 | 차단 (인간 개입 필요) |
| `REJECT` | 신뢰성 결여 | 차단 (저장만 수행) |

## 4. 파이프라인 위치 (Final Position)
`FACT_VERIFIER (IS-25) → TRUST_LOCK (IS-26) → 배포/출력`

IS-26은 IssueSignal의 마지막 관문이며, 여기서 잠긴 결과물만이 "IssueSignal의 공식 판단"으로 인정된다.
