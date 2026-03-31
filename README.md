# Project HOIN: The Insight Oracle

**Project HOIN** is an automated economic intelligence engine designed to uncover hidden market signals and generate "Economic Hunter" style content.

## System Overview (Hoin Insight)

파일 기반 데이터 수집 → 이상징후 탐지 → 주제 선정까지를 GitHub Actions + Git로 자동화하는 프로젝트.

## Repository Structure

- `HOIN_System_Config.md`: The core system prompt and configuration for the HOIN Engine.
- `scripts/`: Generated video scripts based on real-time market anomalies.
  - `HOIN_Script_001.md`: Pilot episode script (The Silent Crash).

## Setup & Execution

### 1. Dependency Installation
Install required packages using `pip`:
```bash
pip install -r requirements.txt
```
For development tools:
```bash
pip install -r requirements-dev.txt
```

### 2. Environment Configuration
Copy `env.example` to `.env` and fill in your API keys:
```bash
cp env.example .env
```
Key required variables:
- `GEMINI_API_KEY`: For LLM analysis
- `FRED_API_KEY`: Macro data collection
- `ECOS_API_KEY`: Bank of Korea data

### 3. Execution Routes
The engine can be executed via two main routes:

#### Route A: Main Engine
The primary automated logic starting from data normalization.
```bash
python -m src.engine
```

#### Route B: Daily Pipeline Runner
Orchestrates collection, engine, and publishing.
```bash
python src/ops/run_daily_pipeline.py
```

### 4. Runtime Modes
Control the engine behavior via `HOIN_RUNTIME_MODE`:

- **Offline Mode**: Skip network/API collection, use local data if exists.
  ```bash
  export HOIN_RUNTIME_MODE=offline
  python -m src.engine
  ```
- **Live Mode** (Default): Perform full data collection and analysis.
  ```bash
  export HOIN_RUNTIME_MODE=live
  python -m src.engine
  ```

## Authority Map (SSOT)

HoinInsight follows a strict Single Source of Truth (SSOT) for data and UI.

| Category | Authority Path | Role |
| :--- | :--- | :--- |
| **Engine Data** | `data/` | **Primary SSOT** (Decisions, Ops, Reports) |
| **UI Code** | `docs/ui/` | Primary UI (Ground truth for renderer) |
| **UI Data** | `docs/data/` | Live data for GitHub Pages |
| **Legacy** | `data_outputs/` | Backward compatibility layer |

Detailed path mapping and rules can be found in [SSOT_PATH_MAP.md](docs/SSOT_PATH_MAP.md).

## Principles (Phase 28 Baseline)
- **Soft-fail**: External API failures skip the collector but do not crash the engine.
- **SSOT**: Primary data lives in `data/`.
- **Additive**: Preservation of existing logic and historical data.

## 문서 체계 (Documentation)
- docs/HOIN_ATLAS.md
- docs/DATA_COLLECTION_MASTER.md
- docs/ANOMALY_DETECTION_LOGIC.md

## Usage
This project uses an AI Agent to:
1. Gather real-time data from FRED, WhaleWisdom, etc.
2. Analyze discrepancies (Surprise Index).
3. Draft scripts for YouTube content.

## Disclaimer

This content is for informational purposes only and does not constitute financial advice.

---
*Maintained by: hoin.insight*
Deployment check
Permission test at Sun Jan 25 03:19:22 KST 2026
System verified on correct repository - Sun Jan 25 07:01:24 KST 2026
