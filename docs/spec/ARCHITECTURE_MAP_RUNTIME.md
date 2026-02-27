# Runtime Architecture Map (Phase 20 Audit)

이 문서는 `full_pipeline.yml`의 실제 실행 경로와 코드 간의 `import` 관계를 분석하여 작성된 **실제 작동 구조도**입니다.

## 1. Runtime Flow Diagram (Mermaid)

```mermaid
graph TD
    subgraph "External Sources"
        CG[CoinGecko]
        EC[ECOS]
        FR[FRED]
        MC[Market Sources]
        PC[Policy Sources]
    end

    subgraph "Layer 1: Engine (Collection & Sensing)"
        E1["src.collectors.*"]
        E2["src.engine"]
    end

    subgraph "Layer 2: Ops & Insight (Intelligence)"
        O1["src.ops.narrative_intelligence_layer"]
        O2["src.ops.video_intelligence_layer"]
        O3["src.issuesignal.run_issuesignal"]
    end

    subgraph "Layer 3: Reporting & Governance"
        R1["src.dashboard.dashboard_generator"]
        R2["src.reporting.telegram_daily_summary"]
        R3["src.pipeline.run_topic_gate"]
    end

    subgraph "Layer 4: Publisher (SSOT)"
        P1["src.ui.run_publish_ui_decision_assets"]
    end

    subgraph "Layer 5: UI (Presentation)"
        U1["docs/index.html"]
        U2["docs/ui/*.js"]
    end

    %% Connections
    CG & EC & FR & MC & PC --> E1
    E1 --> E2
    E2 --> O1 & O2 & O3
    O1 & O2 & O3 --> R1 & R2 & R3
    R1 & R3 --> P1
    P1 --> U1 & U2
```

## 2. Key Data Contracts (SSOT)

| Layer | Responsibility | Input Path (Primary) | Output Path (Primary) |
| :--- | :--- | :--- | :--- |
| **Engine** | Sensing & Raw Analysis | API Keys / RSS | `data/raw/`, `data/processed/` |
| **Ops** | Narrative & Video Selection | `data/processed/` | `data/narratives/`, `data/ops/` |
| **Publisher** | UI Sync & Manifesting | `data/narratives/`, `data/ops/` | `docs/data/` |
| **UI** | Visualization | `docs/data/` | Browser Render |

## 3. Data Flow Artifacts (Production)
이 경로는 런타임에서 실제로 데이터가 생성되고 소비되는 SSOT 저장소입니다.
- `docs/data/decision/`: 최종 결정 및 편집자 카드
- `docs/data/ui/`: UI 렌더링용 집계 데이터
- `docs/data/ops/`: 비디오 후보군 및 시스템 상태
- `docs/data/reports/`: 데일리 브리핑 및 차트
