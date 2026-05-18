# HOIN Insight Zero-Trust Audit Log

## 1. 운영 서버 정보
- **Base URL**: `https://hoininsight-commits.github.io/hoininsight/`
- **검사 시점**: 2026-03-24 15:20 KST
- **배포 버전 (Build Meta)**:
    - **Commit Hash**: `6baa728c2873ba012b692783b7191b00e223bce9`
    - **Build Time**: 2026-03-17 11:12:38 KST

## 2. 수집된 증거 파일 목록

### UI 캡처 (`hoin_server_ui_screenshots.zip`)
1. `01_main_dashboard.png`: 메인 대시보드 (Radar 초기화면)
2. `02_market_radar.png`: 마켓 레이더 상세
3. `03_narrative_brief.png`: 내러티브 브리핑 상세
4. `04_impact_map.png`: 임팩트 맵 (종목 리스트)
5. `05_content_studio.png`: 콘텐츠 스튜디오 (스크립트/토픽)
6. `06_sidebar_full.png`: 사이드바 전체 구조
7. `07_operator_today.png`: '오늘의 선정' 결정 대시보드
8. `08_system_dashboard.png`: 시스템/디벨로퍼 상황판

### 서버 데이터 (`hoin_server_data_snapshot.zip`)
- `data_ops_today_operator_brief.json` (SSOT)
- `data_ops_core_theme_state.json` (404 - 로컬 경로 `data/ops/core_theme_state.json` 서버 미존재)
- `data_ops_early_topic_candidates.json`
- `data_ops_top_early_theme.json`
- `data_ops_theme_narrative.json`
- `data_ops_theme_evolution_state.json`
- `data_ops_theme_momentum_state.json`
- `data_ops_today_story.json`
- `data_ops_mentionables.json`
- `data_ops_top_topic.json`
- `data_ops_today_video_script.json`
- `data_ops_risk_state.json`
- `data_ops_capital_allocation_state.json`
- (누락 3종): `execution_log.json`, `performance_report.json`, `core_theme_state.json`

## 3. 작업 로그
- **15:15**: 브라우저 자동화를 통한 8종 화면 캡처 완료.
- **15:18**: `curl`을 통한 서버 JSON 데이터(13종 성공, 3종 실패) 추출 완료.
- **15:20**: 로컬 소스 코드(`src/`, `docs/ui/`, `docs/data/`) 패키징 완료.
- **15:21**: 모든 산출물 압축 및 `/Users/jihopa/Downloads/` 복사 완료.
