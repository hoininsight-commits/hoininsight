# HOIN Insight v17.6 [The Synchronized Hunter] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **KST Timezone Enforcement (v17.6)**: 시스템 시각(UTC)에 의존하던 날짜 로직을 KST(UTC+9)로 강제 고정하여, 새벽 시간대 날짜 뒤처짐 현상을 완벽히 해결했습니다.
- **YouTube Delivery System (v17.5)**: 유튜브 수집기가 단순 학습용을 넘어, 수집된 자막 전문을 즉시 텔레그램으로 배달하는 '정보 배달부' 역할을 겸하게 되었습니다.
- **Round-Based Management**: 유튜브 수집은 메인 파이프라인 1시간 전(23, 05, 11, 17시)에 수행되며, 파일명은 `날짜_회차_제목.txt` 규칙을 따릅니다.
- **Analysis Pause (Learner)**: 제미나이 서버 불안정 및 효율성을 고려하여, LearnerAgent의 LLM 분석(Gap Analysis)은 잠시 비활성화하고 데이터 수집 및 전송에 집중합니다.
- **Session Cost Tracking (v17.2)**: 매 사냥마다 소요되는 USD 비용을 실시간으로 계산하여 텔레그램 브리핑에 포함합니다.

## 2. 엔진 가동 가이드
- **실전 사냥**: `python3 src/core/scheduler.py` (Sentry → Hunter 풀루프 가동)
- **유튜브 수집**: `python3 scripts/auto_learner.py` (현재 시각 기준 회차 판별 및 자막 배달)
- **배포**: 
    - `daily_pipeline.yml`: 메인 사냥 스케줄 (0, 6, 12, 18시)
    - `youtube_learner.yml`: 유튜브 자막 수집 스케줄 (23, 5, 11, 17시)

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **YouTube Collector**: `youtube_cookies.txt` 또는 RSS 피드를 통해 자막을 확보하며, `TelegramNotifier`를 통해 전체 텍스트를 분할 전송합니다.
- **Model Tiering**: 추론은 Pro(Tier 1), 파싱은 Flash(Tier 3)가 담당하는 지능형 모델 배치가 유지됩니다.

## 4. 제거 및 변경된 항목
- `LearnerAgent`에서 제미나이 분석 로직 주석 처리 (수집 전용 모드).
- 유튜브 자막 저장 경로 규칙 변경: `data/transcripts/youtube/YYYY/MM/DD/YYYYMMDD_N회차_제목.txt`

---
## 🚨 [MANDATORY AI PROTOCOL] - 필수 준수 사항

모든 AI 에이전트(Antigravity 등)는 이 프로젝트에서 작업 시 다음 루틴을 지시 없이도 **자동으로 수행**해야 함.

### 1. "작업 준비하자" 또는 시작 시 (Post-Pull Routine)
- **Action 1**: `git pull`을 수행하여 최신 소스와 기록을 확보함.
- **Action 2**: `docs/CHRONICLE.md`의 가장 최근 기록을 정독함.
- **Action 3**: "지난 세션에서 [A]까지 완료되었고, 현재 [B] 문제가 남아있으니, 바로 [C] 작업을 시작하겠습니다"라고 브리핑하며 업무를 시작함.

### 2. "푸시해줘", "푸시하자", "서버 푸시" 등 종료 시 (Pre-Push Routine)
- **Trigger**: "푸시", "업데이트", "올려줘" 등 서버 동기화와 관련된 모든 명령 포함.
- **Action 1**: 현재까지의 성과, 발생한 에러(삽질), 해결 방법, 남은 과제를 `docs/CHRONICLE.md` 하단에 누적하여 기록함. (절대 기존 내용을 지우지 말 것)
- **Action 2**: `docs/HANDOFF_STORY_DNA.md`의 버전 및 핵심 설정을 업데이트함.
- **Action 3**: 모든 문서와 소스 코드를 `git push` 함.

---
*본 문서는 2026-04-27 AI 자동 동기화 프로토콜 수립 후 갱신된 최종 지침서입니다.*
