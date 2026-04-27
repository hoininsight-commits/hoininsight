# HOIN Insight v17.5 [The Delivery Hunter] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
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
*본 문서는 2026-04-27 유튜브 자동 배달 및 회차별 관리 시스템 구축 후 갱신된 최종 지침서입니다.*
