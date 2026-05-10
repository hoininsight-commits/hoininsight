# HOIN Insight v23.0 [The Predator's Instinct] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Intelligence Hardening (v23.0)**: `TopicArbiter`를 **Gemini 2.5 Pro**로 격상하여 단순 뉴스 나열이 아닌 '돈의 이동 경로'를 추적하는 고차원 통찰력을 확보했습니다.
- **Data Fidelity (v23.0)**: `DataCondenser`가 뉴스 스니펫(150자)을 보존하게 하여, AI가 제목 너머의 '시장의 뉘앙스'를 읽고 사냥감을 선정하도록 개선되었습니다.
- **Narrative Revolution (v21.0~23.0)**: 로봇 말투(Step 1, [HOOK] 등)를 완전히 제거하고, 시청자를 '너/형'으로 부르는 친근하고 강력한 '경제사냥꾼' 페르소나를 정립했습니다.

## 2. 엔진 가동 및 저장 규칙
- **저장 표준 (Storage Standard)**: 모든 출력물은 `YYYY/MM/DD/Round_X/` 경로에 저장됩니다. (예: `data/scripts/2026/05/09/Round_3/today_script_long.md`)
- **실전 사냥**: `python3 src/core/scheduler.py` (Sentry → Hunter 풀루프 가동)
- **유튜브 수집**: `python3 scripts/auto_learner.py` (KST 기준 회차 판별)

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **Model Tiering**: 
    - **Tier 1 (Pro)**: 토픽 선정(Arbiter), 최종 원고 작성(Writer). 고도의 통찰이 필요한 구간.
    - **Tier 3 (Flash)**: 데이터 수집 및 정제, 기술적 파싱. 비용 효율성이 중요한 구간.
- **Quality Gate**: 로봇 특유의 정형화된 말투나 태그가 발견되면 즉시 DROP 처리하며, 폴백(Fallback) 엔진도 동일한 사냥꾼 페르소나를 유지합니다.

## 4. 제거 및 변경된 항목
- 레거시 경로 구조(`YYYYMMDD/N`) 폐기 및 마이그레이션 완료.
- `WriterAgent` 및 `Arbiter` 프롬프트에서 로봇 말투(Step 1 등) 유발 가이드라인 전면 삭제.

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항

모든 AI 에이전트는 작업 시작 시 `git pull` 후 `docs/CHRONICLE.md`를 정독해야 하며, 종료 시 `CHRONICLE.md`에 오늘자 기록을 APPEND하고 `git push` 해야 함.

---
*본 문서는 2026-05-09 v23.0 [The Predator's Instinct] 업데이트 후 갱신된 최종 지침서입니다.*
