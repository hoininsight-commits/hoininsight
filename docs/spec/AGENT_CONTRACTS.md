# Agent Data Contracts (Phase 21)

본 문서는 HOIN Insight 프로젝트의 6개 Agent 간의 데이터 인터페이스와 무결성 요건을 정의합니다.

## A1. DataAgent (Collect + Normalize)
- **Inputs**: External APIs (FRED, ECOS, CoinGecko, etc.)
- **Outputs**:
  - `data/raw/*.json`
  - `data/processed/*.json`
- **Contract**:
  - `date`: YYYY-MM-DD 형식의 필드 포함 (정규화 시점).
  - 수집된 원천 자료의 원본 값 유지.

## A2. SignalAgent (Anomaly -> Base Topics)
- **Inputs**: `data/processed/*.json`
- **Outputs**:
  - `data/topics/candidates/YYYY/MM/DD/topic_candidates.json`
  - `data/decision/YYYY/MM/DD/final_decision_card.json` (Initial draft)
- **Contract**:
  - `dataset_id`: 고유 식별자 필수.
  - `score`: 엔진 기초 점수 (0~100).
  - `intensity`: `score`와 동일 값으로 자동 매핑 필수.

## A3. NarrativeAgent (Narrative Intelligence)
- **Inputs**: `data/topics/candidates/` 및 `data/ops/` 컨텍스트
- **Outputs**:
  - `data/ops/narrative_intelligence_v2.json`
  - `data/ops/freshness/YYYY/MM/DD/freshness_summary.json`
- **Contract**:
  - `narrative_score`: 지능 레이어의 최종 가중치 합산 점수.
  - `conflict_flag`: 다축 충돌 여부 (boolean).
  - **No Scoring Leak**: Publisher/UI 레이어로의 로직 유출 금지.

## A4. DecisionAgent (Final Decision Card)
- **Inputs**: Narrative/Signal 출력물
- **Outputs**:
  - `data/decision/YYYY/MM/DD/final_decision_card.json` (Update with metadata)
- **Contract**:
  - `card_version`: `phase66_editorial_v1` 준수.
  - `status`: `APPROVED` 또는 `REJECTED` 등 게이트 상태 명시.

## A5. VideoAgent (Video Pool)
- **Inputs**: `data/ops/narrative_intelligence_v2.json`
- **Outputs**:
  - `data_outputs/ops/video_candidate_pool.json`
- **Contract**:
  - `video_ready`: 영상 제작 가용 여부.
  - `narrative_score`: 최상위 60점 이상만 후보군 포함 권장.

## A6. PublishAgent (SSOT Publisher)
- **Inputs**: 모든 Agent의 산출물
- **Outputs**:
  - `docs/data/decision/today.json`
  - `docs/data/decision/manifest.json`
- **Contract**:
  - **Authoritative**: `docs/` 하위 배포본의 최종 형태를 결정함.
  - **No Calculation**: 계산 로직이 없어야 하며, 오직 Copy & Field Alignment만 수행.
