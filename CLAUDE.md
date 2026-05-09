# HOIN Insight — 안티(Antigravity) 부팅 지침서
# 최종 수정: 2026-05-09 | v23.0 [The Predator's Instinct]

---

## 🚨 "작업 준비하자" 또는 "집에가서 작업 준비 하자" 를 들었다면

사용자가 위 문구 중 하나를 말하면, 안티는 즉시 아래 절차를 수행한다.
다른 말 없이 바로 시작한다.

### Step 1 — 최신 코드 PULL
```bash
git pull origin main
```

### Step 2 — HANDOFF 최신 엔진 DNA 읽기
```
파일: docs/HANDOFF_STORY_DNA.md (v23.0 지능형 사냥꾼 지침서)
```
이 문서는 **지능형 사냥 엔진(Arbiter v2.5)**, **저장 표준(YYYY/MM/DD)**, **페르소나 하드닝**의 핵심 로직을 담고 있으므로 반드시 숙지한다.

### Step 3 — 작업 준비 완료 보고
아래 형식으로 사용자에게 현황을 보고한다:

```
✅ 보급 및 엔진 점검 완료 (git pull 완료, v23.0 HANDOFF 숙지)

📌 현재 상태:
- 엔진 버전: v23.0 [The Predator's Instinct]
- 완료된 것: Arbiter 1.5 Pro 업그레이드, 경로 표준화(YYYY/MM/DD), 로봇 말투 완전 박멸
- 세션 비용 현황: Last run $0.7778 (USD)
- 다음 우선순위: [1순위: 실시간 데이터 소스 확장 / 2순위: Few-shot 데이터셋 고도화]

🔔 사냥을 시작할까요? (python3 src/core/scheduler.py)
```

---

## 📁 프로젝트 개요

**HOIN Insight** — 경제사냥꾼 스타일 시장 인텔리전스 엔진

- 매일 시장 이상징후를 자율 탐지하고 비용 효율적으로 분석함
- Sentry 보초가 시장 가치를 판단하여 유료 모델(Pro) 가동 여부 결정
- 사냥꾼의 최신 대본을 매일 학습하여 엔진 DNA를 스스로 개선(Learner)

---

## 🗂️ 핵심 경로

| 항목 | 경로 |
|---|---|
| **최신 HANDOFF** | `docs/HANDOFF_STORY_DNA.md` |
| **사냥 실록 (Chronicle)** | `docs/CHRONICLE.md` |
| **지능형 스케줄러** | `src/core/scheduler.py` |
| **비용 추적 로그** | `data/monitoring/session_cost.json` |
| **저장 표준** | `data/scripts/YYYY/MM/DD/Round_X` |
| 파이프라인 진입점 | `scheduler.py` (Main) / `local_pipeline.py` (Test) |

---

## 🚫 절대 규칙

1. **Cost Awareness**: 모든 Gemini 호출은 Tier(1 or 3)를 명시해야 함.
2. **Decoupled Learning**: 학습(Learner)과 실전(Hunt)은 독립적으로 작동해야 함.
3. **No Cliché**: "이상한 점..." 등 사냥꾼답지 않은 표현은 Quality Gate에서 자동 차단됨.
4. **API Safety**: 모든 API 호출 실패 시 즉시 비용 로깅 및 텔레그램 경고 발송.

---

## 🏃 빠른 시작 명령어

```bash
# 최신 코드 받기
git pull origin main

# 지능형 자율 사냥 시작
python3 src/core/scheduler.py

# 강제 사냥 (Sentry 건너뛰기)
python3 src/core/scheduler.py --force

# 사냥꾼 영상 학습 루프
python3 src/agents/learner_agent.py
```

---

## GitHub

- Repo: `hoininsight-commits/hoininsight`
- Actions: `Intelligent Hunter Pipeline (v17.3)` 가동 중
