# Removal & Archival Plan

본 계획은 프로젝트의 복잡도를 낮추고 유지보수 효율을 높이기 위해 불필요한 파일을 정리하는 실행 계획입니다.

## 1. CATEGORY A: 완전 제거 (Immediate Deletion)
*승인 후 삭제 수행*

### [Legacy UI]
- `docs/legacy/` 전축 (index.html, render.js, styles.css)
- `src/legacy_shims/` 내부의 불필요한 어댑터
- `src/ui_logic/guards/` 내부의 `legacy_*` 파일들

### [Redundant Scripts]
- `src/ui/` 폴더 내 `src/ui_logic`과 중복되는 모든 `.py` 파일
- `src/decision/run_is96_4.py` 등의 특정 Phase용 임시 실행 스크립트

---

## 2. CATEGORY B: 격리 필요 (Move to Archive)
*프로젝트 루트의 `archive/` 폴더로 이동*

### [Forensics & Reports]
- `data_outputs/ops/` 폴더 내 지난 Phase의 분석 리포트 (`phase15_*`, `phase16_*`, `phase17_*`)
- `src/refactor/` 내부의 deprecation 스캐너 등 분석 전용 툴

### [Experimental Logic]
- `src/ops/` 내 현재 런타임 파이프라인에서 호출되지 않는 실험용 파일들
- `src/hoin/` 하위의 구형 하이브리드 엔진 잔재

---

## 3. CATEGORY C: 통합 및 재배치 (Consolidation)

### [Collectors & Normalizers]
- `src/collectors/` → `src/engine/collectors/`
- `src/normalizers/` → `src/engine/normalize/`

### [Publisher & Contracts]
- `src/ui/run_publish_ui_decision_assets.py` → `src/publisher/` (신규)
- `src/ui_contracts/` → `src/publisher/contracts/`

---

## 4. 안전 수칙 (Safety Protocol)
1. **의존성 확인**: `grep`을 통해 호출부(import)가 없는지 최종 확인.
2. **비파괴적 격리**: Category B는 즉시 삭제하지 않고 `archive/` 폴더에 최소 2주간 보관.
3. **데이터 정합성**: JSON Schema를 생성/검증하는 로직은 절대 건드리지 않음.
