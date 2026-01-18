# 🧠 HOIN ENGINE: Session Checkpoint (2026-01-18)

유저의 다른 환경(회사 컴퓨터 등)에서도 AI가 즉시 문맥을 파악할 수 있도록 저장된 정보입니다.

## 🚀 최신 상태 (Project Status)
- **대시보드 버전**: `v1.1.1` (Cache-bust 완료)
- **핵심 주소**: `https://hoininsight-commits.github.io/hoininsight/`
- **핵심 연동**: 
    - **Google Gemini 2.0 Flash**: `src/llm/gemini_client.py` (심층 분석 자동화 완료)
    - **Logic Sync**: `src/anomaly_detectors/z_score_detector.py` (L1-L4 통계적 감지 완료)
    - **Data Sources**: FRED(US), ECOS(KOR), CoinGecko(Crypto/Metals) 동기화 완료.

## ⚖️ 엔진 철학 (Engine Philosophy)
- **Engine-First**: `DATA_COLLECTION_MASTER`는 핵심 지표 위주로 가볍게 유지함.
- **Narrative-Report**: 유튜브 분석 등 풍부한 컨텍스트는 리포트(`daily_brief.md`)에 저장하여 '공부하지 않아도 되는 엔진' 지향.

## 📝 다음 할 일 (Next Steps)
- 상시 데이터 수집 및 이상징후 모니터링.
- 추천 종목(리노공업 등)의 후속 데이터 추적 및 리포트 고도화.
- 429 Error(Gemini Quota) 발생 시 헤메지 않고 Heuristic Fallback이 정상 작동하는지 상시 확인.

---
**[AI 동기화용 프롬프트]**
"SESSION_CHECKPOINT.md 파일을 읽고, 현재 대시보드 버전 v1.1.1과 Gemini 연동 상태, 그리고 엔진 우선 철학을 학습해서 이어서 작업해줘."
