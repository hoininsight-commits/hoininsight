# HOIN Insight v24.5 [Two-Track Strategy & Isolated Learning] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Two-Track Hunting Logic (v24.5)**: 이제 사냥꾼은 글로벌 거시 흐름(Track A)과 국내 구조적 특수성/희소성(Track B)을 동시에 사냥합니다. IPO 희소성이나 정부 정책 자금 같은 국내 전용 트리거를 포착할 수 있습니다.
- **Isolated Learning Territory (v24.5)**: 유튜브 학습 데이터와 메인 사냥 데이터를 물리적으로 분리했습니다. 모든 유튜브 관련 데이터는 `youtube_data/` 폴더 내에서만 관리되어 메인 파이프라인과의 충돌을 원천 차단합니다.
- **Robust Transcript Ingestion (v24.5)**: `yt-dlp` 기반의 강화된 자막 추출 엔진을 도입하여 경제사냥꾼의 모든 영상 대본을 100% 수집 가능하게 수리했습니다.
- **Dashboard Deep Reading (v24.5)**: 인스타 카드뉴스 뷰어에서 '사냥 보고서 전문'을 즉시 읽을 수 있는 모달 기능을 추가하여 분석의 깊이를 대시보드에 통합했습니다.

## 2. 엔진 가동 및 저장 규칙
- **저장 표준 (Storage Standard)**: 
    - 메인 사냥 데이터: `data/scripts/YYYY/MM/DD/Topic_N/`
    - 유튜브 학습 데이터: `youtube_data/transcripts/YYYY/MM/DD/`
- **자동화 스케줄 (Automated Schedule)**: 
    - **YouTube Learner**: 01, 07, 13, 19 KST (사냥 1시간 전)
    - **Main Pipeline**: 02, 08, 14, 20 KST
- **충돌 방지 전략**: GitHub Actions에서 데이터 충돌 시 `-X theirs` 옵션을 통해 서버가 생성한 최신 데이터를 우선하여 자동 합병합니다.

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **Agnostic Context**: 메인 파이프라인은 유튜브 학습 데이터에 의존하지 않고 오직 로우 데이터(DART, ECOS, News)만으로 독자적인 사냥을 수행합니다.
- **DNA Evolution Log**: `youtube_data/history/dna_evolution.json`에 사냥꾼의 안목 분석 결과가 쌓이며, 향후 프롬프트 자동 패치(DNA Patch)의 재료로 활용됩니다.

## 4. 필수 체크포인트 (Next session focus)
- **02시 자동 사냥 모니터링**: 스케줄러가 첫 주기를 정상적으로 도는지, 대시보드 배포가 잘 되는지 확인.
- **DNA Patch 자동화**: 학습된 사냥꾼의 페르소나를 `analyst_prompt.py`에 자동으로 반영하는 로직 설계.

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항
모든 유튜브 관련 데이터는 반드시 `youtube_data/` 경로를 사용해야 하며, `data/` 경로와 혼용하지 마십시오.

---
*본 문서는 2026-05-11 v24.5 업데이트 후 갱신된 최종 지침서입니다.*
