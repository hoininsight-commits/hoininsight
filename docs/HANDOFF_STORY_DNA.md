# HOIN Insight v25.0 [Adaptive Hunter: Autonomous DNA Patching] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Autonomous DNA Patching (v25.0)**: `youtube_data/history/dna_evolution.json`에 축적된 학습 데이터가 이제 `DNAManager`를 통해 **Arbiter**와 **Writer**의 프롬프트에 실시간으로 자동 주입됩니다. 엔진이 매일 밤 사냥꾼의 최신 통찰을 스스로 학습하고 진화합니다.
- **DART Stabilization (v25.0)**: 공시 데이터 추출 로직에 2회 재시도(Retry) 및 백오프(Backoff)를 도입하고, BeautifulSoup 파서를 `xml`로 전환하여 `014` 에러 및 파서 경고를 완벽히 해결했습니다.
- **Unified Logic Flow**: `WriterAgent`가 앞단인 `Detector/Arbiter`의 사냥 결과를 최우선으로 따르도록 하드닝되어, 주제와 내용이 어긋나는 '키메라 현상'을 근본적으로 차단했습니다.

## 2. 엔진 가동 및 저장 규칙
- **저장 표준 (Storage Standard)**: 
    - 메인 사냥 데이터: `data/scripts/YYYY/MM/DD/Topic_N/`
    - 유튜브 학습 데이터: `youtube_data/transcripts/YYYY/MM/DD/`
    - **DNA 패치 로그**: `data/history/dna_patch_log.json`
- **자동화 스케줄 (Automated Schedule)**: 
    - **YouTube Learner**: 01, 07, 13, 19 KST (사냥 1시간 전 학습)
    - **Main Pipeline**: 02, 08, 14, 20 KST (DNA가 적용된 자동 사냥)

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **DNAManager**: 최신 3개의 DNA 패치를 선별하여 프롬프트의 `HUNTER DNA` 섹션에 주입합니다. 이는 데이터 갭 보완, 논리 패턴 강화, 서사 톤 교정의 3단계로 작동합니다.
- **Single Source of Truth**: 모든 에이전트는 `data/signals/YYYY/MM/DD/today_signal.json`을 중심으로 동기화되어 일관된 리포트를 생성합니다.

## 4. 필수 체크포인트 (Next session focus)
- **DNA 패치 실효성 검증**: 자동 적용된 패치가 실제 생성된 스크립트의 품질(Arbiter 통찰력 등)을 얼마나 개선했는지 리포트 분석.
- **카드뉴스 레이아웃 가변화**: 토픽의 성격(ANOMALY/NORMAL)에 따라 카드뉴스 디자인을 동적으로 변경하는 기능 구현.
- **서버 환경 동기화**: 로컬의 `v25.0` 엔진을 서버에 안전하게 배포하고 02시 스케줄링 작동 여부 최종 확인.

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항
1. 모든 유튜브 관련 데이터는 반드시 `youtube_data/` 경로를 사용하십시오.
2. DNA 패치는 `DNAManager` 클래스를 통해 통합 관리되며, 프롬프트 파일 직접 수정보다 매니저를 통한 주입을 우선하십시오.

---
*본 문서는 2026-05-12 v25.0 업데이트 후 갱신된 최종 지침서입니다.*
