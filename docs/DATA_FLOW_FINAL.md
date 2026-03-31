# Data Flow Final Authority

## 1. Input Flow
- **Collectors** (`src/engine/collectors/`) -> `data/raw/`
- **Fact-First Loader** (`src/ops/fact_first_input_loader.py`) -> `data/ops/`

## 2. Processing Flow
- **Narrative Engine** -> `data/narratives/`
- **Core Engine** -> `data/topics/`, `data/ops/`
- **Agents (A3, A4)** -> `data/ops/`, `data/decision/`

## 3. Decision Flow
- **Decision Agent** -> `data/decision/YYYY/MM/DD/final_decision_card.json`
- **Approval Logic** -> `data/ops/auto_approved_today.json`

## 4. UI Publishing (LIVE)
- **Authority SSOT** (`data/ops/`, `data/decision/`)
- **Publisher** (`src/ui/run_publish_ui_decision_assets.py`)
- **Target (Live)** -> `docs/data/`
- **Legacy Mirror** -> `data_outputs/ops/`
