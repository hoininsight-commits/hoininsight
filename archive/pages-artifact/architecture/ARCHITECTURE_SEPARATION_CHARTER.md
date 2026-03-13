# Architecture Separation Charter

**Status**: ACTIVE
**Version**: 1.0
**Goal**: Enforce strict separation between Engine, Interpreter, Contract, and UI layers.

## 1. Layer Definitions

### A) Engine Layer (판단/수집)
- **Responsibility**: Raw data collection, anomaly detection, scoring, and structural logic.
- **Location**: `src/engine/`, `src/collectors/`, `src/anomaly/`, etc.
- **Strict Rule**: No access to `docs/` or `data/ui/`. Must not generate UI-specific strings or HTML.

### B) Interpreter Layer (해석/내러티브)
- **Responsibility**: Transforming raw Engine scores into "Economic Hunter" style narratives.
- **Location**: `src/interpreters/` (NEW)
- **Strict Rule**: Read-only input from Engine outputs. Must use deterministic templates. No direct data collection.

### C) Contract/Builder Layer (JSON 계약)
- **Responsibility**: Pinning Interpreter outputs into stable UI JSON schemas (`manifest.json`, `operator_*.json`).
- **Location**: `src/ui_contracts/`
- **Strict Rule**: No rendering logic. Only data-to-JSON mapping and schema enforcement.

### D) UI Layer (시각화)
- **Responsibility**: Rendering JSON assets in the browser.
- **Location**: `docs/ui/`
- **Strict Rule**: Reads only from `data/ui/` via `manifest.json`. No Python logic, no direct Engine calls.

## 2. Import & Dependency Rules

| Source Layer | Allowed Targets | Forbidden Targets |
| :--- | :--- | :--- |
| **Engine** | Internal Engine, Utils | Interpreter, Contracts, UI, `docs/` |
| **Interpreter** | Engine (read-only), Utils | UI, `docs/` |
| **Contracts** | Interpreter, Engine, Utils | UI Rendering logic |
| **UI** | `data/ui/` via Manifest | `src/` (Python logic) |

## 3. Enforcement
- All violations must lead to immediate `pytest` failure in the `verify_ref013_architecture_boundaries` suite.
