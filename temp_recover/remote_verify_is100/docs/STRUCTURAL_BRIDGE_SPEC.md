# STRUCTURAL_BRIDGE_SPEC.md

본 문서는 `EDITORIAL_LIGHT` 등급의 구조 해설 콘텐츠와 이후 발생하는 실데이터(HARD_FACT/Ticker) 이벤트를 논리적으로 연결하는 `IS-71 Structural Continuity Bridge`의 규격을 정의합니다.

## 1. 구조 식별 및 기억 (Identification & Memory)

### 1-1. Structure ID 생성 규칙
- **정의**: 매크로 테마, 주체(Actor), 섹터의 조합을 통해 고유한 구조적 ID를 부여합니다.
- **포맷**: `hash([MacroTheme]_[Actor]_[Sector])`
- **시점**: `EDITORIAL_LIGHT` 콘텐츠 생성 시 즉시 발행 및 저장.

### 1-2. 저장소 (`structural_memory.json`)
- 경로: `data/memory/structural_memory.json`
- 상태 관리:
  - `ACTIVE`: 구조 해설 발행 후 현실화 신호 대기 중.
  - `RESOLVED`: 실데이터 이벤트와 연결되어 내러티브 브릿지가 성립됨.

## 2. 브릿지 로직 (Continuity Logic)

- **트리거**: 신규 `HARD_FACT`, `WHY-NOW`, `Ticker Path` 감지 시.
- **매칭 조건**: 
  - 신규 이벤트의 `Actor` 가 `structural_memory.json` 내 `ACTIVE` 상태인 구조의 `Actor` 와 일치할 것.
  - 또는 관련 매크로 키워드가 1개 이상 일치할 것.
- **결과**: `RESOLVED` 상태로 전환 및 브릿지 문장 생성.

## 3. 자동 생성 문장 (Narrative Rules)

- **템플릿**: “이 변화는 {N}일 전에 구조 해설로 언급했던 ‘{구조 요약 문장}’이 현실로 전환된 첫 신호입니다.”
- **제약**: 평서문, 확정적 날짜 계산, 추측 배제.

## 4. 대시보드 시각화

- **패널**: `🧠 구조 연속성 추적 (STRUCTURAL CONTINUITY)`
- **요소**: 연결된 ID, 최초 언급일, 매칭된 팩트 요약, 상태 배지(🔵 -> 🟣).
