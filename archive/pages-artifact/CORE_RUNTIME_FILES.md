# Core Runtime Files

The following files are essential for the 2026-03 operational runtime.

## Orchestration
- `src/ops/run_daily_pipeline.py`: Main entry point.
- `src/ui/run_publish_ui_decision_assets.py`: Data SSOT synchronization.

## Logic Layers
- `src/ops/agents/narrative_agent.py`: (A3) Regime and Timing analysis.
- `src/ops/agents/decision_agent.py`: (A4) Approval and Card generation.
- `src/ops/agents/publish_agent.py`: (A6) Final verification and sync trigger.

## Utilities & Paths
- `src/utils/paths.py`: Central path authority.
- `src/utils/date_utils.py`: Timezone (KST) handling.

## Frontend
- `docs/ui/operator_today.js`: Real-time dashboard data loader.
- `docs/ui/operator_history.js`: Decision history viewer.
