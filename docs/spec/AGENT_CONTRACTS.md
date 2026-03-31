# Agent Data Contracts (Phase 21)

본 문서는 HOIN Insight 프로젝트의 6개 Agent 간의 데이터 인터페이스와 무결성 요건을 정의합니다.

## 공통 원칙 (Common Policies)
- **Standard Params**: 모든 에이전트는 `--date`, `--dry-run`, `--emit-runlog`를 필수 구현합니다.
- **Fail-Safe**: 데이터 누락 시 `None` 또는 빈 리스트를 반환하되, 전체 프로세스를 중단시키지 않는 "Soft-Fail"을 지향합니다. (단, Publish단계는 예외)
- **No Scoring Leak**: 모든 스코어링 로직은 A3(Narrative) 또는 A4(Decision)에서 종료되어야 하며, A6(Publish) 또는 UI 레이어에서 재계산되어서는 안 됩니다.

## A1. DataAgent (Collect + Normalize)
- **Inputs**: 외부 API (FRED, ECOS, CoinGecko 등)
- **Outputs**:
  - `data/raw/*.json`: 원천 데이터
  - `data/processed/*.json`: 정규화 데이터
- **Contract**:
  - `date`: YYYY-MM-DD 형식의 필드 포함 (정규화 시점).
  - **Failure Mode**: API 오류 시 이전 캐시 데이터를 사용하거나 로그에 기록 후 종료.
- **Required Fields**: `source`, `raw_value`, `normalized_value`.

## A2. SignalAgent (Anomaly -> Base Topics)
- **Inputs**: `data/processed/*.json`
- **Outputs**:
  - `data/topics/candidates/YYYY/MM/DD/topic_candidates.json`
- **Contract**:
  - `dataset_id`: 고유 식별자 필수.
  - `intensity`: 엔진 기초 점수 (0~100). `score` 필드와 싱크 필수.
  - **Failure Mode**: 이상징후 미발견 시 `alive_count: 0`인 결과물 생성.
- **Required Fields**: `dataset_id`, `intensity`, `title`.

## A3. NarrativeAgent (Narrative Intelligence)
- **Inputs**: A2 출력물 및 `data/ops/` 컨텍스트
- **Outputs**:
  - `data/ops/narrative_intelligence_v2.json`
  - `data/ops/freshness/YYYY/MM/DD/freshness_summary.json`
- **Contract**:
  - `narrative_score`: 지능 레이어의 최종 가중치 합산 점수.
  - `conflict_flag`: 다축 충돌 여부 (boolean).
- **Required Fields**: `narrative_score`, `why_now`.

## A4. DecisionAgent (Final Decision Card)
- **Inputs**: A2, A3 출력물
- **Outputs**:
  - `data/decision/YYYY/MM/DD/final_decision_card.json`
- **Contract**:
  - `card_version`: `phase66_editorial_v1` 준수.
  - `status`: `APPROVED` 또는 `REJECTED` 등 게이트 상태 명시.
- **Required Fields**: `status`, `decision_date`.

## A5. VideoAgent (Video Pool)
- **Inputs**: A3 출력물
- **Outputs**:
  - `data_outputs/ops/video_candidate_pool.json`
- **Contract**:
  - `video_ready`: 영상 제작 가용 여부.
  - `narrative_score`: 최상위 60점 이상만 후보군 포함.
- **Required Fields**: `video_ready`.

## A6. PublishAgent (SSOT Publisher)
- **Inputs**: 모든 Agent의 산출물
- **Outputs**:
  - `docs/data/decision/today.json`
  - `docs/data/decision/manifest.json`
- **Contract**:
  - **SSOT Purest**: **로직 복제 금지**. 반드시 내부적으로 `src.ui.run_publish_ui_decision_assets`만 호출해야 함.
  - **No Calculation**: 어떠한 점수 계산이나 해시 생성 로직도 포함해서는 안 됨.
  - **Failure Mode**: `manifest.json` 생성 실패 시 배포를 중단하고 Exit 1.
- **Required Fields**: `files` (manifest 내), `top_topics` (today 내).
