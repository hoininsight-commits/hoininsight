# MARKET_MEMORY_ENGINE (IS-23)

## 1. 목적 (Purpose)
동일하거나 매우 유사한 구조적 트리거가 반복적으로 발화되는 것을 방지한다. 서로 다른 뉴스나 표면적 사건이라 하더라도, 그 배후의 자본 논리와 구조적 모순이 동일하다면 IssueSignal은 침묵해야 한다.

## 2. 구조적 메모리 해시 (Structural Memory Hash)
모든 발화된 `TRIGGER`는 다음 요소로 구성된 구조적 해시를 생성하여 저장한다.

- **Root Cause (원인)**: 사건의 근본 동인 (예: Subsidy Cut, Supply Collapse)
- **Forced Actor (강제 주체)**: 행동을 강제받는 주체 (예: Gov, BigTech, Central Bank)
- **Capital Destination (자본 목적지)**: 자본이 이동하는 최종 목적지 (예: AI Sector, HBM, Debt Market)
- **Irreversibility (불가역성)**: 구조적 경로가 되돌릴 수 없는 상태인지 여부 (Yes/No)

### 해시 예시
`SUBSIDY_CUT + GOVERNMENT + CHIP_CAPEX + IRREVERSIBLE`

## 3. 메모리 저장 및 잠금 규칙 (Storage & Lock)
- 발화 시점의 구조적 해시와 타임스탬프를 `market_memory.json`에 저장한다.
- **최소 잠금 기간**: 21일 (3주).

## 4. 발화 차단 규칙 (Re-speech Block Rules)
새로운 트리거 후보가 발생했을 때 기존 메모리와의 유사도(Overlap)를 측정한다.

1.  **High Overlap (≥ 70%)**:
    - 21일 이내일 경우: **즉시 REJECT**.
    - 사유: **STRUCTURAL DUPLICATION**.
2.  **Partial Overlap (40% ~ 70%)**:
    - **Actor** 또는 **Destination** 중 하나라도 변경되었을 때만 허용.
    - 변경되지 않았다면 **REJECT**.

## 5. 메모리 감쇠 및 만료 (Decay & Expiry)
- **21일 이후 (Soft Lock)**:
    - 새로운 Capital Destination 또는 새로운 Irreversibility 조건이 추가되었을 때만 발화 허용.
- **45일 이후 (Expiry)**:
    - 메모리가 만료되며, 동일 구조도 '새로운 사이클'로 간주하여 발화 가능.

## 6. 파이프라인 통합
트리거 승격(IS-22) 직후, 발화 전 최종 단계에서 메모리 체크를 수행한다.
`PROMOTION (IS-22) → MEMORY CHECK (IS-23) → SILENCE / TRIGGER`
