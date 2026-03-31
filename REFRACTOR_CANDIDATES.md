# Refactor Candidates - Module Responsibility Audit

이 문서는 책임 분리(SRP) 원칙을 위배하거나 중복된 로직을 포함하고 있는 모듈을 정의합니다.

## 1. Logic Leak (계산 로직 유출)

### [D] Publisher Layer
- **Candidate**: `src/ui/run_publish_ui_decision_assets.py`
- **Issue**:
  - `_publish_editorial` 내부에서 `narrative_score`가 없을 경우 Salt를 이용해 더미 점수를 생성 (Scoring Leak).
  - `intensity` 필드가 없을 경우 `score`를 복사하여 강제 할당 (Data Normalization Leak).
  - `today.json` 생성 시 여러 `data/ops/*.json`을 복합적으로 병합.
- **Action**: 계산 로직은 `src/engine` 또는 `src/ops`로 이전하고, 퍼블리셔는 순수 "Merge & Copy"만 수행하도록 간소화.

### [D] Reporters Layer
- **Candidate**: `src/reporters/daily_report.py`
- **Issue**:
  - `persistence_multiplier` 및 `final_score_m` (Momentum adjusted) 계산을 리포터 레벨에서 수행.
- **Action**: 점수 보정 로직을 `src/topics/scoring.py` 또는 신규 Scoring 모듈로 이전.

### [D] Dashboard Reporter
- **Candidate**: `src/reporters/decision_dashboard.py`
- **Issue**:
  - `READY`, `HOLD`, `DROP` 등의 운영 상태 결정 로직이 리포터 내부에 복잡하게 얽혀 있음.
  - `urgency_score`, `narration_level` 등 핵심 비즈니스 로직 연산 포함.
- **Action**: "Decision Surface" 레이어를 엔진 내부로 격리하여 리포터는 가공된 상태값만 출력하도록 리팩토링.

## 2. Redundancy (중복 및 혼란 유발)

### UI Logic Duplication
- **Candidate**: `src/ui/` vs `src/ui_logic/`
- **Issue**:
  - `manifest_builder.py`, `publish_ui_assets.py`, `operator_main_contract.py` 등 거의 동일한 파일이 두 폴더에 공존.
- **Action**: `src/ui_logic`으로 단일화하고 `src/ui`는 삭제 또는 런타임 진입점만 유지.

### Data Collection Duplication
- **Candidate**: `src/collectors/` vs `src/engine/collectors/` vs `src/events/collectors/`
- **Issue**: 수집기 로직이 3개 이상의 핵심 폴더에 파편화되어 있음.
- **Action**: `src/engine/collectors/`로 통합.
