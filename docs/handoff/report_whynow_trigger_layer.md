# [STEP 72 완료 보고서] WHY_NOW Trigger Layer 구현

## 1. 구현 개요
기존 경제 사냥꾼 내러티브(4단계) 구조를 변경하지 않고, 토픽의 시간적 시의성(Why Now?)을 설명하는 **'WHY_NOW Trigger Layer'**를 추가형 모듈로 구현했습니다. 이 레이어는 내러티브 생성 후 실행되며, 결과물(JSON)에 해설을 덧붙이는 방식으로 작동하므로 기존 코어 로직에 영향을 주지 않습니다.

## 2. 모듈 위치
*   **신규 모듈**: `src/ops/whynow_trigger_layer.py`
    *   트리거 감지, 거절(Rejection) 판단, 내러티브 바인딩 로직을 전담합니다.
*   **실행 포인트**: `src/engine.py` (Step 72)
    *   `EconomicHunterNarrator` 실행 직후에 배치하여, 생성된 내러티브에 트리거 해설을 주입합니다.

## 3. 트리거 감지 로직 (Trigger Detection)
`whynow_trigger_layer.py` 내부의 `_detect_trigger` 함수에서 키워드 및 패턴 매칭을 통해 3가지 유형을 판별합니다.

*   **Trigger 1: Scheduled Catalyst Arrival (예정된 이벤트)**
    *   **감지 신호**: '발표', '출시', '만기', 'earnings', 'launch' 등 + 날짜/분기 패턴.
    *   **바인딩 위치**: **Action** (행동 지침) 섹션에 추가.
*   **Trigger 2: Mechanism Activation (메커니즘 발동)**
    *   **감지 신호**: '시행', '발효', '판결', 'policy', 'ruling' 등.
    *   **바인딩 위치**: **Tension** (구조적 역학) 섹션에 추가.
*   **Trigger 3: Smart Money Divergence (수급 괴리)**
    *   **감지 신호**: '매집', '순매수', 'divergence', 'spike' 등.
    *   **바인딩 위치**: **Hunt** (결정적 증거) 섹션에 추가.

## 4. 거절 로직 (Rejection Logic)
*   **거절 조건**: 위 3가지 트리거 중 어느 하나에도 해당하지 않는 경우 (Trigger 0).
*   **처리 방식**:
    *   내러티브 JSON에 `is_rejected: true` 플래그 설정.
    *   Hook(도입부) 섹션 최상단에 `[🚫 REJECTED: ...]` 경고 문구 강제 삽입.
    *   이를 통해 대시보드에서 운영자가 즉시 인지할 수 있도록 처리.

## 5. 무결성 확인 (Integrity Check)
*   **기존 로직 보존**: `EconomicHunterNarrator`, `StructuralTop1Compressor` 등 기존 클래스의 코드는 단 한 줄도 수정되지 않았습니다.
*   **Additive Only**: 오직 새로운 파일(`whynow_trigger_layer.py`)을 추가하고, 엔진 파이프라인의 뒷단에 실행 단계만 추가했습니다.
*   **검증**: 테스트 실행 결과, Trigger 2(Mechanism Activation)가 정상 감지되어 Tension 섹션에 해설이 자동 주입됨을 확인했습니다.

---
**작성자**: HOIN Engine System Engineer
**일자**: 2026-01-27
