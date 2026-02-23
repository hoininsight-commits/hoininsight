# [STRUCTURE-FINAL-FREEZE] Baseline Ledger

본 문서는 HoinInsight 구조 및 파이프라인 동결 시점의 기준점(Baseline)을 기록합니다.
이후 아키텍처나 파이프라인의 핵심 구조가 이 기준에서 이탈할 경우 CI 파이프라인은 실패합니다.

## 1. Directory & File Statistics
- **Total Files in `docs/data/decision`**: 49
- **Manifest.json Status**: Exists and verified

## 2. Publish Script SSOT (Single Source of Truth)
- **Authoritative Publisher**: `src/ui/run_publish_ui_decision_assets.py`
- **Wrapper Shim**: `src/ui_logic/contracts/run_publish_ui_decision_assets.py` 
  (Restricted entirely to: `from src.ui.run_publish_ui_decision_assets import main`)

## 3. Remote Verify Frozen Zones
All `remote_verify_*` directories have been purged of runtime scripts and locked via `DEPRECATED.md`. Any new files placed here will fail CI (`V6` rule).

## 4. UI Data Flow Lock
`docs/ui/` fetch targets are restricted solely to `docs/data/decision/` and `docs/data/ops/`. References to legacy `data_outputs` or `remote_verify` emit CI failures (`V7` rule).

## 5. Directory Tree Snapshot (`src`)
```text
src
src/anomalies
src/anomaly_detectors
src/bridge
src/collectors
src/collectors/auto_generated
src/collectors/calendar
src/collectors/financials
src/collectors/market
src/collectors/statements
src/dashboard
src/data
src/decision
src/editorial
src/engine
src/events
src/evolution
src/hoin
src/interpreters
src/issuesignal
src/layers
src/learning
src/legacy_guard
src/legacy_shims
src/llm
src/narratives
src/normalizers
src/ops
src/orchestrators
src/pipeline
src/refactor
src/registry
src/reporters
src/reporting
src/schemas
src/strategies
src/synthesis
src/templates
src/tickers
src/tools
src/topic_selectors
src/topics
src/ui
src/ui_contracts
src/ui_logic
src/utils
src/validation
```
*Note: Inner data partitions omitted for brevity.*
