# Removal Plan V2 (Phase 20: Structural Sanitation)

이 문서는 `audit_deadcode_candidates.py` 결과를 바탕으로 한 자산 격리 계획입니다. **Phase 20의 원칙에 따라 실제 삭제는 하지 않으며, 전량 `archive/` 폴더로 이동**하여 런타임의 복잡도만 낮춥니다.

## 1. Archival Rules
- **CATEGORY A**: 런타임/수입그래프/UI FETCH 어디에도 해당하지 않는 파일. (즉시 격리)
- **CATEGORY B**: 과거에는 사용되었으나 현재는 더 나은 대체제(SSOT)가 있는 파일. (격리)
- **CATEGORY C**: 현재는 사용되지 않으나 엔진 구조상 복구 가능성이 있거나 Shim 역할을 하는 파일. (유지 또는 주석 처리 후 격리)

## 2. Category A: Immediate Isolation (Archive)
아래 파일들은 `archive/sanitized_src/`로 이동됩니다.

### UI & UX Logic 파편
- `src/ui/capital_perspective_narrator.py`
- `src/ui/expectation_gap_detector.py`
- `src/ui/multi_topic_selector.py`
- `src/ui/narrative_fusion_engine.py`
- ... (외 src/ui/ 내 SSOT 제외 전량)

### UI Logic & Contracts (Redundant)
- `src/ui_logic/` 전체
- `src/ui_contracts/` 전체
- *이유: Phase 19B에서 SSOT가 `src/ui/run_publish_ui_decision_assets.py`로 확정됨에 따라 하위 폴더의 파편화된 계약 로직은 불필요.*

### Legacy Utils
- `src/utils/knowledge_base.py`
- `src/utils/human_language_rewriter.py`
- `src/utils/i18n_ko.py` (UI에서 직접 처리 또는 불필요)

## 3. Category B: Substitution (Shim Points)
- `src/ui/publish_ui_assets.py`: 이미 Shim으로 전환됨. (유지)
- `src/ui_logic/contracts/run_publish_ui_decision_assets.py`: Shim. (유지)

## 4. Execution Logic
1. `archive/sanitized_src/` 디렉토리 생성.
2. `git mv`를 사용하여 위 파일들을 이동.
3. 이동 후 `run_publish_ui_decision_assets.py`를 실행하여 의존성 깨짐이 없는지 최종 확인.

---
*정리된 구조는 Phase 21의 에이전트 모듈화를 위한 클린 베이스가 됩니다.*
