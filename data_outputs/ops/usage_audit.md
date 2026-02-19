# Repository Usage Audit Report (Quantified)

## UI Entrypoints
- ui/index.html
- docs/index.html
- docs/ui/index.html
- dashboard/index.html

## Deprecated Path Quantification

### `docs/data/ui`
- **Total References**: 27
- **Breakdown by Type**:
  - tests: 13
  - scripts: 1
  - docs: 5
  - runtime: 8
- **Top Referrers**:
  - `data_outputs/ops/usage_audit.json`: 4 refs
  - `tests/verify_architecture_guards.py`: 3 refs
  - `tests/verify_ref011_single_entry_and_legacy_readonly.py`: 3 refs
  - `tests/verify_ref013_no_undefined_across_ui_assets.py`: 2 refs
  - `docs/engine/REF-001_REMOTE_VERIFICATION_REPORT.md`: 2 refs
  - `tests/verify_ref002_registry_contracts.py`: 1 refs
  - `tests/verify_is99_2_scheduler.py`: 1 refs
  - `tests/verify_ref012_manifest_only_legacy.py`: 1 refs
  - `tests/verify_ref005_structure_integrity.py`: 1 refs
  - `tests/verify_ref001_manifest_and_publish.py`: 1 refs

### `data/ui`
- **Total References**: 165
- **Breakdown by Type**:
  - tests: 18
  - scripts: 2
  - docs: 52
  - runtime: 93
- **Top Referrers**:
  - `data_outputs/ops/usage_audit.json`: 8 refs
  - `src/ui_logic/contracts/manifest_builder_v1.py`: 7 refs
  - `registry/ui_cards/ui_card_registry_v1.yml`: 6 refs
  - `data/ui/manifest.json`: 6 refs
  - `data_outputs/ui/manifest.json`: 6 refs
  - `docs/engine/REF-001_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/engine/REF-003_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `remote_verify_is101_2/src/ui/run_publish_ui_decision_assets.py`: 3 refs
  - `remote_verify_is102/src/ui/run_publish_ui_decision_assets.py`: 3 refs
  - `remote_verify_is98_5/src/ui/run_publish_ui_decision_assets.py`: 3 refs

### `data_outputs/ui`
- **Total References**: 8
- **Breakdown by Type**:
  - tests: 2
  - scripts: 1
  - runtime: 5
- **Top Referrers**:
  - `data_outputs/ops/usage_audit.json`: 4 refs
  - `tests/verify_ref005_structure_integrity.py`: 2 refs
  - `scripts/audit_usage.py`: 1 refs
  - `data_outputs/ops/usage_audit.md`: 1 refs

### `exports`
- **Total References**: 390
- **Breakdown by Type**:
  - tests: 77
  - scripts: 1
  - docs: 170
  - runtime: 142
- **Top Referrers**:
  - `tests/verify_is98_6_risk_timeline_narrator.py`: 7 refs
  - `remote_verify_is98_6/tests/verify_is98_6_risk_timeline_narrator.py`: 7 refs
  - `remote_verify_is98_6/src/ui/risk_timeline_narrator.py`: 6 refs
  - `src/ui_logic/narrators/risk_timeline_narrator.py`: 6 refs
  - `docs/engine/IS-109-A_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `docs/engine/IS-108_REMOTE_VERIFICATION_REPORT.md`: 4 refs
  - `remote_verify_is101_2/tests/verify_is99_2_scheduler.py`: 3 refs
  - `remote_verify_is101_2/docs/engine/IS-99-1_REMOTE_VERIFICATION_REPORT.md`: 3 refs
  - `remote_verify_is101_2/docs/engine/IS-99-2_DAILY_SCHEDULER.md`: 3 refs
  - `remote_verify_is102/tests/verify_is99_2_scheduler.py`: 3 refs

### `docs/data/decision`
- **Total References**: 136
- **Breakdown by Type**:
  - tests: 69
  - scripts: 1
  - docs: 35
  - runtime: 31
- **Top Referrers**:
  - `remote_verify_is101_2/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is102/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is98_5/tests/verify_is100_pages_paths.py`: 7 refs
  - `tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is101_1/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is101/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is96_8/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is98_6/tests/verify_is100_pages_paths.py`: 7 refs
  - `remote_verify_is100_v2/tests/verify_is100_pages_paths.py`: 7 refs
  - `tests/verify_architecture_guards.py`: 6 refs
