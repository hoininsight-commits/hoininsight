# SSOT PATH MAP v1.0

This document defines the authoritative paths for HoinInsight data and UI. All code modifications should respect this hierarchy.

## 1. Data Authority (Local)

The `data/` directory is the **Primary SSOT** for all engine-generated data.

| Path | Role | Authority Level |
| :--- | :--- | :--- |
| `data/raw/` | Original fetched data (unmodified) | Primary |
| `data/curated/` | Normalized and cleaned data | Primary |
| `data/decision/` | Final engine outputs (Topic Cards, Packs) | **Supreme Authority** |
| `data/ops/` | Operational state (Regime, Calibration) | Primary |
| `data/reports/` | Human-readable Markdown and Charts | Primary |

## 2. Legacy Compatibility Layer

The `data_outputs/` directory exists solely for **backward compatibility** with older agents and scripts.

| Path | Role | Source |
| :--- | :--- | :--- |
| `data_outputs/ops/` | Mirror of operational decision files | `data/ops/` or `data/decision/` |

> [!CAUTION]
> Do not use `data_outputs/` for new logic. Always read from and write to `data/`.

## 3. UI Authority (Published)

The `docs/` directory is the root for **GitHub Pages** deployment.

| Path | Role | Authority Level |
| :--- | :--- | :--- |
| `docs/ui/` | Ground truth for UI Code (HTML/JS/CSS) | Primary |
| `docs/data/` | Target and Ground truth for UI Data | **Live Authority** |
| `ui/` | Local development or legacy shim | Deprecated / Secondary |

## 4. Path Synchronization Workflow

The system follows a strict "Write-then-Publish" flow:

1. **Engine Execution**: Outputs are written to `data/decision/` and `data/ops/`.
2. **Publishing**: `src/ui_logic/contracts/publish_ui_assets.py` synchronizes these files to `docs/data/`.
3. **Deployment**: GitHub Actions pushes `docs/` to the web.

## 5. Test & Mismatch Inventory

All verification scripts (`scripts/verify_*.py`) and integration tests (`tests/verify_*.py`) expect data in the **Published Path** (`docs/data/`) to ensure the user-facing site is correct.

- **Status**: Mostly Aligned.
- **Identified Mismatches**:
  - `src/ui/run_publish_ui_decision_assets.py` uses `data_outputs/ops/` as source instead of `data/decision/`. (To be addressed in Step 3).
