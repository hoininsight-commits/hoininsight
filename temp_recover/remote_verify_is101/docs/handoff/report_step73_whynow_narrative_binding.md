# [STEP 73 완료 보고서] WHY_NOW × ECONOMIC HUNTER NARRATIVE BINDING

## 1. 구조적 강제성 구현 (Structural Enforcement)
`EconomicHunterNarrator`가 내러티브르 생성하기 이전에 **반드시** `WhyNowTriggerLayer`의 감지 로직을 통과하도록 코드를 재설계했습니다. 이제 "Why Now" 트리거가 없는 토픽은 아예 내러티브 생성 단계로 진입할 수 없으며, 생성된 모든 내러티브는 물리적으로 `[⚡ WHY NOW]` 섹션을 포함하게 됩니다. 이는 선택 사항이 아닌 **필수 조건(Mandatory Condition)**으로 동작합니다.

## 2. WHY_NOW 내러티브 배치 (Binding Logic)
트리거 유형에 따라 내러티브의 다음 3가지 섹션 중 하나에 해설이 자동 주입됩니다.

*   **Trigger 1 (Scheduled Catalyst)** → **Action (행동 지침)** 섹션
    *   *이유*: 날짜가 확정된 이벤트는 구체적인 행동 시점을 지시하는 Action 단계와 직결되기 때문입니다.
*   **Trigger 2 (Mechanism Activation)** → **Tension (구조적 역학)** 섹션
    *   *이유*: 제도의 시행이나 판결은 시장 구조의 변화(Tension)를 설명하는 핵심 기제이기 때문입니다.
*   **Trigger 3 (Smart Money Divergence)** → **Hunt (결정적 증거)** 섹션
    *   *이유*: 수급의 괴리는 경제 사냥꾼이 포착한 강력한 증거(Hunt)에 해당하기 때문입니다.

## 3. 거절 로직 (Rejection Logic)
*   **작동 방식**: `EconomicHunterNarrator.run()` 실행 초기에 `check_rejection()`을 호출합니다.
*   **거절 기준**: 명시적인 시간적 앵커(날짜, 시행일, 통계적 특이점)가 없는 "상태 기술형(Continuous State)" 토픽은 즉시 거절됩니다.
*   **결과**:
    *   내러티브 생성이 중단됩니다.
    *   JSON 결과에 `is_rejected: true`가 기록됩니다.
    *   대시보드 노출용 MD 파일에 `[🚫 REJECTED]` 경고가 굵게 표시됩니다.

## 4. 수정된 파일 목록
1.  `src/ops/whynow_trigger_layer.py`: 감지 및 거절 로직을 외부에서 호출 가능한 정적 메서드(`staticmethod`)로 리팩토링.
2.  `src/ops/economic_hunter_narrator.py`: 내러티브 생성 로직 전체를 재작성하여 트리거 감지 및 바인딩 과정을 필수 절차로 통합.
3.  `data/ops/issue_signal_narrative_today.json`: `whynow_trigger` 객체 및 섹션 내 `[⚡ WHY NOW]` 텍스트 포함 확인.
4.  `data/ops/issue_signal_narrative_today.md`: 마크다운 출력에 트리거 해설 반영 확인.

---
**작성자**: HOIN Engine System Engineer
**일자**: 2026-01-27
