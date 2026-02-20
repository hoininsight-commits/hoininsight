# IS-99-4 UPLOAD PACK ORCHESTRATOR LAYER

**Version**: v1.0 (2026-02-04)
**Purpose**: Automate the creation of a daily, upload-ready asset package.

## 1. Directory Structure
The orchestrator bundles files into `exports/upload_pack_daily/`:

- `00_README.md`: Summary, upload order, and hypothesis warnings.
- `01_LONG/`:
  - `long_script.txt`: The full video script.
- `02_SHORTS/`:
  - `short_01_macro.txt`: Macro Structural angle.
  - `short_02_pickaxe.txt`: Pickaxe / Bottleneck angle.
  - `short_03_data.txt`: Data Signal angle.
  - `short_04_risk.txt`: Risk / Contrarian angle.
- `03_METADATA/`:
  - `upload_manifest.json`: Machine-readable metadata.
  - `upload_manifest.csv`: Tabular asset list.

## 2. Manifest Schema

### JSON Schema
- `date`: YYYY-MM-DD
- `hero_topic_id`: Unique ID of the locked topic.
- `theme`: Sector name.
- `topic_type`: (STRUCTURAL / REGIME / CAPITAL / HYPOTHESIS_JUMP)
- `hypothesis_flag`: Boolean (True if `HYPOTHESIS_JUMP`).
- `shorts_count`: Exactly 4.

### CSV Columns
- `asset_type`: LONG | SHORT
- `filename`: Relative path.
- `angle`: macro | pickaxe | data | risk | main
- `hypothesis_flag`: Boolean.

## 3. Validation Rules
- The orchestrator **fails hard** if any of the 4 shorts are missing.
- It enforces strict naming conventions to prevent operator confusion.
