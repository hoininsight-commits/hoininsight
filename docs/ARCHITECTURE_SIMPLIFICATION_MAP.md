# Architecture Simplification Map

## Core Structure
The HOIN Insight project is organized into two primary domains: **Ops (Engine/Automation)** and **UI (Dashboard/Docs)**.

### 1. Operations Layer (`src/ops/`)
- **Agents**: Autonomous processors for data, signals, and narrative.
- **Engines**: Core logic for structural and narrative analysis.
- **Orchestration**: `run_daily_pipeline.py` serves as the master switch.

### 2. UI/Data Layer (`data/`, `docs/data/`)
- **Authority Data (`data/`)**: The Single Source of Truth for engine outputs and decisions.
- **Live Assets (`docs/data/`)**: Published assets consumed by the dashboard.

### 3. Standardized Namespaces (`src/`)
To ensure import consistency, core engine modules are consolidated in the `src/` root:
- `src/topics/`: Narrative and topic scoring logic.
- `src/events/`: Event loading and anchor gate definitions.
- `src/reporters/`: Dashboard and brief generator logic.
- `src/strategies/`: Regime-based strategy frameworks.
- `src/anomalies/`: Drift and anomaly detection.
- `src/normalize/`: Data cleaning and curation.

### 4. Simplification Principles
- **Minimal Cross-Referencing**: Agents should output to `data/ops/` and `data/decision/` only.
- **Explicit Publishing**: Only `run_publish_ui_decision_assets.py` should move data to `docs/data/`.
- **Legacy Containment**: All compatibility code is isolated in `src/ui/ui_logic/guards/` and `data_outputs/`.
