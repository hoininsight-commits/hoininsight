# HOIN Insight v24.2 [The Omnipresent Hunter] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Intelligent Environment Awareness (v24.2)**: 사냥꾼이 스스로의 위치(GitHub Server, Home, Office)를 식별합니다. 이제 어떤 로컬 환경에서도 경로 설정 없이 즉시 사냥이 가능합니다.
- **Path Standardization (v24.2)**: 대시보드 주소 체계를 `BASE_URL` 기반의 절대 경로 시스템으로 통합했습니다. GitHub Pages 배포 시 발생하는 이미지 엑박 문제를 근본적으로 해결했습니다.
- **Visual Revolution (v24.0)**: **Imagen 4.0**을 통해 주제별 맞춤형 커버 이미지(`cover.png`)를 자동 생성합니다.
- **Unified Pipeline (v24.0)**: 모든 공정을 `run_full_pipeline.py` 하나로 통합하여 안정성을 극대화했습니다.

## 2. 엔진 가동 및 저장 규칙
- **저장 표준 (Storage Standard)**: `data/scripts/YYYY/MM/DD/Topic_N/` 경로를 엄수합니다.
- **환경 식별 로직**: `PublisherAgent`의 `env_type` 속성을 참조하여 현재 실행 환경을 판별할 수 있습니다.
- **대시보드 기준점**: HTML/JS 내의 `const BASE_URL`이 모든 경로의 기준이 됩니다.

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **Actual Title Extraction (v24.2)**: 장부(`content_log.json`)에는 AI가 최종적으로 다듬은 실제 마크다운 파일 내의 제목을 추출하여 기록합니다.
- **Model Tiering**: 
    - **Tier 1 (Pro)**: 토픽 선정(Arbiter), 최종 원고 작성(Writer), 이미지 생성(Imagen 4.0).
    - **Tier 3 (Flash)**: 데이터 수집 및 정제, 기술적 파싱, 품질 검증.

## 4. 필수 체크포인트 (Next session focus)
- **지능형 스케줄러(v24.5) 런칭**: 수동 실행을 대체할 경량화된 배치 스케줄러 구축 필요.
- **이미지 생성 다각화**: 슬라이드별 배경 이미지 생성을 통한 시각적 깊이 확보.

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항

모든 AI 에이전트는 종료 시 `docs/CHRONICLE.md`에 기록을 APPEND하고 `git push` 해야 함. **특히 경로 수정 시 `BASE_URL`과 `env_type` 로직을 해치지 않도록 각별히 유의할 것.**

---
*본 문서는 2026-05-10 v24.2 [The Omnipresent Hunter] 업데이트 후 갱신된 최종 지침서입니다.*
