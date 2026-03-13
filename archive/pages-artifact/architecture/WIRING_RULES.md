# Wiring Rules

## 1. Operational Flow
The project must follow a unidirectional data flow to ensure stability:

1.  **COLLECT**: `src/collectors/` -> `data/raw/`
2.  **ENGINE**: `src/engine/` -> `data/decision/` (Structural signals)
3.  **INTERPRET**: `src/interpreters/` -> `data/narrative/` (Style & Context)
4.  **CONTRACT**: `src/ui_contracts/` -> `data/ui/` (Manifest pinning)
5.  **PUBLISH**: `src/ui_logic/publish/` -> `docs/data/ui/` (Final asset swap)
6.  **RENDER**: `docs/ui/` (Browser view)

## 2. Wiring at Pipeline End
The `run_publish()` orchestrator in `src/ui_logic/publish/publish_all.py` is the only approved entry point for UI asset generation. 

- **DO NOT** trigger UI writes directly from `src/engine/`.
- **DO NOT** bypass the `manifest.json` generation.

## 3. Placeholder Standard
- If a layer fails, it must emit a safe "Missing/Placeholder" payload.
- Undefined or Null values must be caught by the `Contract` layer before reaching `UI`.
