# Agent Module Entrypoints

이 문서는 HOIN Insight 프로젝트의 각 하위 모듈(Agent)을 독립적으로 실행하기 위한 표준 엔트리포인트와 입출력 사양을 정의합니다.

## 1. Engine Agent (Sensing & Discovery)
- **Command**: `python -m src.engine`
- **Output**:
  - `data/topics/today/*.json` (Raw topics)
  - `data/processed/*.json` (Cleaned signals)

## 2. Ops Agent (Intelligence & Selection)
- **Command**: `python -m src.ops.narrative_intelligence_layer`
- **Input**: `data/processed/*.json`
- **Output**: `data/narratives/*.json`

- **Command**: `python -m src.ops.video_intelligence_layer`
- **Input**: `data/processed/*.json`
- **Output**: `data/ops/video_candidate_pool.json`

## 3. Publisher Agent (SSOT Asset Delivery)
- **Command**: `python -m src.ui.run_publish_ui_decision_assets`
- **SSOT Status**: **Authoritative**
- **Input**:
  - `data/narratives/*.json`
  - `docs/data/today.json`
- **Output**:
  - `docs/data/decision/manifest.json`
  - `docs/data/decision/today.json`

## 4. Reporter Agent (Dashboard & Notify)
- **Command**: `python -m src.dashboard.dashboard_generator`
- **Input**: `docs/data/decision/manifest.json`
- **Output**: `docs/index.html` (Legacy update point)

---
*모든 모듈은 위 엔트리포인트를 통해 개별적으로 테스트 및 실행이 가능해야 하며, 입출력 경로는 반드시 명시된 SSOT 경로를 준수해야 합니다.*
