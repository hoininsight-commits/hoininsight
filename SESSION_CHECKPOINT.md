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

## 🎭 분석 페르소나 및 스타일 (Persona & Style)
- **분석 깊이**: 단순 요약을 거부하고, GPT-4 수준의 **'구조적 이상징후(Structural Anomaly)'**와 **'권력 관계의 변화'**를 추적하는 날카로운 관점을 유지함.
- **보고 스타일**: 
    - 1) 표면 노이즈 제거 
    - 2) 진짜 주제 재정의 
    - 3) 이상징후 레벨(L1-L4) 판정 
    - 4) Why Now 트리거 분석 순서로 진행.
- **지식 필터**: 유저를 공부시키지 않고, **'의사결정에 필요한 급소'**만 골라내는 문지기(Gatekeeper) 역할을 수행함.

## 📚 참조 문서 (Core Reference)
- `prompts/video_analysis_master_prompt.md`: AI의 분석 헌법. 모든 분석은 이 지침에 따라야 함.
- `data/inputs/chatgpt_context.txt`: 이전에 학습한 시스템의 상세 배경 지식 및 규칙이 저장되어 있음.

---
**[AI 동기화용 프롬프트]**
"저장소 루트의 `SESSION_CHECKPOINT.md`와 `prompts/video_analysis_master_prompt.md`를 먼저 읽어줘. 내가 원하는 분석 스타일(GPT급 심층 분석, 엔진 우선 철학)을 완벽히 이해한 상태에서, 유저를 공부시키지 않고 핵심만 짚어주는 '문지기'로서 이어서 대화해줘."
