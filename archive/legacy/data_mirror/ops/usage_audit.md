# Repository Usage Audit Report (Sanitized)

> **Note**: Self-references (`data_outputs/ops/`) are excluded.

## UI Entrypoints
- ui/index.html
- docs/index.html
- docs/ui/index.html
- dashboard/index.html

## Deprecated Path Quantification

### `docs/data/ui`
- **Total References**: 22
  - **Runtime**: 9
  - **Tests**: 13
  - **Verify Copies**: 0
- **Top Runtime Referrers**:
  - `docs/engine/REF-001_REMOTE_VERIFICATION_REPORT.md`: 2 refs
  - `docs/ui/sidebar_registry_loader.js`: 1 refs
  - `docs/architecture/WIRING_RULES.md`: 1 refs
  - `docs/engine/REF-013_REMOTE_VERIFICATION_REPORT.md`: 1 refs
  - `scripts/audit_usage.py`: 1 refs
  - `registry/refactor/legacy_map_v1.yml`: 1 refs
  - `data/ui/DEPRECATED.md`: 1 refs
  - `src/ui_logic/contracts/publish_ui_assets.py`: 1 refs

### `data/ui`
- **Total References**: 155
  - **Runtime**: 93
  - **Tests**: 18
  - **Verify Copies**: 44
- **Top Runtime Referrers**:
  - `src/ui_logic/contracts/manifest_builder_v1.py`: 7 refs
  - `registry/ui_cards/ui_card_registry_v1.yml`: 6 refs
  - `data/ui/manifest.json`: 6 refs
  - `data_outputs/ui/manifest.json`: 6 refs
  - `docs/engine/REF-001_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/engine/REF-003_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/ui/sidebar_registry_loader.js`: 3 refs
  - `docs/architecture/ARCHITECTURE_SEPARATION_CHARTER.md`: 3 refs
  - `data/ui/_deprecated.json`: 3 refs
  - `data_outputs/ui/_deprecated.json`: 3 refs

### `data_outputs/ui`
- **Total References**: 3
  - **Runtime**: 1
  - **Tests**: 2
  - **Verify Copies**: 0
- **Top Runtime Referrers**:
  - `scripts/audit_usage.py`: 1 refs

### `exports`
- **Total References**: 387
  - **Runtime**: 74
  - **Tests**: 20
  - **Verify Copies**: 293
- **Top Runtime Referrers**:
  - `src/ui_logic/narrators/risk_timeline_narrator.py`: 6 refs
  - `docs/engine/IS-109-A_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/engine/IS-108_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/engine/IS-110_REMOTE_VERIFICATION_REPORT.md`: 3 refs
  - `docs/engine/IS-99-1_REMOTE_VERIFICATION_REPORT.md`: 3 refs
  - `docs/engine/IS-99-2_DAILY_SCHEDULER.md`: 3 refs
  - `walkthrough.md`: 2 refs
  - `docs/engine/IS-106_REMOTE_VERIFICATION_REPORT.md`: 2 refs
  - `docs/engine/IS-111_REMOTE_VERIFICATION_REPORT.md`: 2 refs
  - `docs/engine/IS-98-6_REMOTE_VERIFICATION_REPORT.md`: 2 refs

### `docs/data/decision`
- **Total References**: 133
  - **Runtime**: 8
  - **Tests**: 13
  - **Verify Copies**: 112
- **Top Runtime Referrers**:
  - `src/ui_logic/contracts/run_publish_ui_decision_assets.py`: 3 refs
  - `docs/engine/IS-100_UI_REMOTE_VERIFICATION_REPORT.md`: 2 refs
  - `docs/engine/IS-100_REMOTE_VERIFICATION_REPORT.md`: 1 refs
  - `scripts/audit_usage.py`: 1 refs
  - `src/ui_logic/contracts/publish_ui_assets.py`: 1 refs
