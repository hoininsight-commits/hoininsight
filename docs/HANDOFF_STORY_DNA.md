# HOIN Insight v17.3 [The Intelligent Hunter] Handover

## 1. 핵심 진화 사항 (The Great Evolution)
- **Learner Loop (v16.0)**: 사냥꾼의 최신 영상을 매일 학습하여 우리 로직과의 갭을 메우는 '자기 진화 루프'가 가동되었습니다. (`LearnerAgent`)
- **Sentry-Triggered Hunting (v17.0)**: 저비용 Flash 모델(Sentry)이 시장 변동성을 먼저 체크하여, 사냥 가치가 충분할 때만 Hunter 엔진을 깨웁니다. (90% 비용 절감)
- **Model Tiering (v17.1)**: 모든 작업에 Tier를 부여하여 추론은 Pro(Tier 1), 파싱은 Flash(Tier 3)가 담당하는 지능형 모델 배치가 완료되었습니다.
- **Session Cost Tracking (v17.2)**: 매 사냥마다 소요되는 USD 비용을 실시간으로 계산하여 텔레그램 브리핑에 포함합니다.

## 2. 엔진 가동 가이드
- **실전 사냥**: `python3 src/core/scheduler.py` (Sentry → Hunter 풀루프 가동)
- **강제 사냥**: `python3 src/core/scheduler.py --force` (Sentry 무시하고 즉시 사냥)
- **DNA 학습**: `python3 src/agents/learner_agent.py` (최신 영상 수집 및 갭 분석)
- **배포**: GitHub Actions 통합 완료 (`daily_pipeline.yml`이 스케줄러 기반으로 개편됨)

## 3. 사냥꾼의 지능 (Hunter Intelligence)
- **Flash (Tier 3)**: Detector, Sentry, Learner (대량 파싱 및 고속 판단)
- **Pro (Tier 1)**: WhyGenerator, StockAnalyst, Writer (고차원 인과관계 분석 및 대본 작성)
- **비용 정책**: Pro(In $3.5/Out $10.5), Flash(In $0.075/Out $0.3) 정책이 `GeminiClient`에 내장되어 실시간 정산됩니다.

## 4. 제거 및 변경된 항목
- `daily_pipeline.yml`의 개별 에이전트 다단 실행 구조 제거 -> `scheduler.py` 단일 통합.
- `LearnerAgent`와 메인 파이프라인의 의존성 분리 (학습은 학습대로, 실전은 실전대로).

---
*본 문서는 2026-04-26 지능형 스케줄링 및 비용 최적화 완료 후 갱신된 최종 지침서입니다.*
