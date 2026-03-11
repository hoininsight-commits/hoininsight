# Legacy Isolation Plan

## Identified Legacy Components
1. **Mirror Path**: `data_outputs/ops/` (Redirects to `data/ops/`)
2. **UI Logic V1/V2**: `src/ui/ui_logic/contracts/manifest_builder_v1.py` etc.
3. **Guards**: `src/ui/ui_logic/guards/legacy_*`
4. **Old Decision Data**: `data/ui_decision/`

## Isolation Strategy
- **Stage 1 (Current)**: Explicitly document these as "Legacy" in `src/utils/paths.py`.
- **Stage 2 (Planned)**: Remove mirror creation from `run_publish_ui_decision_assets.py` once all legacy scripts are updated.
- **Stage 3 (Cleanup)**: Move legacy source files to a dedicated `legacy/` directory or delete after confirmation.

## Legacy Compatibility Rules
- **Read-Only**: Legacy components are prohibited from receiving new feature updates.
- **No Propagation**: New modules must not import from legacy paths.
- **Silent Mode**: Legacy guards should be set to `warning_mode.py` instead of breaking the main pipeline.
