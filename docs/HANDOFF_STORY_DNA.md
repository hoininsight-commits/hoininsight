# HOIN Insight v24.0 [The Visual Predator] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Visual Revolution (v24.0)**: **Gemini Imagen 4.0**을 엔진에 직접 통합했습니다. 이제 모든 리포트는 주제의 정수를 담은 고유한 시각적 에셋(`cover.png`)을 자동으로 생성합니다.
- **Infrastructure Purge (v24.0)**: 50여 개의 레거시 파일과 복잡한 `Round_N` 경로 의존성을 완전히 제거했습니다. 시스템은 이제 더욱 가볍고 강력합니다.
- **Unified Pipeline (v24.0)**: 모든 사냥 공정을 `run_full_pipeline.py` 하나로 통합하여 실행의 복잡성을 획기적으로 줄였습니다.
- **Data Integrity (v24.0)**: 대시보드 중복 방지 로직과 카드뉴스 JSON 규격 교정을 통해 데이터와 UI 간의 완벽한 정합성을 확보했습니다.

## 2. 엔진 가동 및 저장 규칙
- **저장 표준 (Storage Standard)**: `data/scripts/YYYY/MM/DD/Topic_N/` 경로를 표준으로 삼습니다. (레거시 `Round_X`는 폐기됨)
- **실전 사냥 (Main)**: `python3 run_full_pipeline.py` (수집부터 발행까지 원스톱 실행)
- **에셋 저장**: 모든 시각적 결과물은 `Topic_N/assets/` 폴더 내에 저장됩니다.

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **Model Tiering**: 
    - **Tier 1 (Pro)**: 토픽 선정(Arbiter), 최종 원고 작성(Writer), 이미지 생성(Imagen 4.0).
    - **Tier 3 (Flash)**: 데이터 수집 및 정제, 기술적 파싱, 품질 검증(Quality Gate).
- **Anti-Duplication Shield**: 리포트 발행 시 날짜와 제목을 대조하여 대시보드 내 중복 카드를 원천 차단합니다.

## 4. 제거 및 변경된 항목
- 레거시 `scheduler.py`, `Sentry`, `Round_N` 관련 모든 스크립트 및 경로 폐기.
- `WriterAgent` 내에 Imagen 4.0 호출 및 `assets` 생성 로직 영구 반영.

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항

모든 AI 에이전트는 작업 시작 시 `git pull` 후 `docs/CHRONICLE.md`를 정독해야 하며, 종료 시 `CHRONICLE.md`에 오늘자 기록을 APPEND하고 `git push` 해야 함. **특히 이미지 생성 실패 시 로그를 남기고 즉시 보고할 것.**

---
*본 문서는 2026-05-10 v24.0 [The Visual Predator] 업데이트 후 갱신된 최종 지침서입니다.*
