# HOIN Insight — 안티(Antigravity) 부팅 지침서
# 최종 수정: 2026-04-24 | v10.2 [Autonomous Discovery & Purity]

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
파일: docs/HANDOFF_STORY_DNA.md (v10.2 최종 지침서)
```
이 문서는 현재 **자율 탐지 엔진(Zero-Shot)**의 핵심 로직과 **서사 정제 규칙**을 담고 있으므로 반드시 숙지한다.

### Step 3 — 작업 준비 완료 보고
아래 형식으로 사용자에게 현황을 보고한다:

```
✅ 보급 및 엔진 점검 완료 (git pull 완료, HANDOFF_STORY_DNA 숙지)

📌 현재 상태:
- 엔진 버전: v10.2 [Autonomous Discovery & Narrative Purity]
- 완료된 것: 자율 탐지 로직 안정화, 상투어(이상한 점...) 박멸, 레거시 폴더(dashboard 등) 대청소
- 다음 우선순위: [1순위: 실전 사냥 모니터링 / 2순위: ECOS/DART 복구]

🔔 사냥을 시작할까요?
```

---

## 📁 프로젝트 개요

**HOIN Insight** — 경제사냥꾼 스타일 시장 인텔리전스 엔진

- 매일 시장 이상징후(Anomaly)를 자율 탐지하고
- WHY NOW를 설명하는 7단계 서사를 생성하며
- GitHub Pages(`docs/index.html`) 및 로컬 대시보드로 시각화하는 시스템

---

## 🗂️ 핵심 경로

| 항목 | 경로 |
|---|---|
| **최신 HANDOFF** | `docs/HANDOFF_STORY_DNA.md` |
| 시스템 헌장 | `skills/economy-hunter-dna/SKILL.md` |
| 대시보드 (View) | `docs/index.html` (GitHub Pages 연동) |
| 신호 데이터 | `data/signals/YYYYMMDD/today_signal.json` |
| 파이프라인 진입점 | `src/agents/collector.py` → `detector.py` → `writer.py` |

---

## ⚙️ 현재 시스템 상태 (2026-04-24 기준)

### 완료된 핵심 항목 (v10.2)
- **Autonomous Discovery**: 하드코딩된 섹터 가이드 제거, 실시간 지표 기반 자율 축 탐지
- **Narrative Purity**: 훅-본문 테마 일치성 강제 및 상투적 오프닝 금지 로직 (Quality Gate)
- **Deep Purge**: 레거시 폴더(`dashboard`, `hoin_dashboard`, `reports`, `scratch`) 전면 삭제

### 다음 우선순위
1. 실전 시장 데이터 기반 자율 탐지 정확도 모니터링
2. ECOS API 복구 (기준금리, CPI 등 매크로 지표)
3. DART 실시간 공시 수집 레이어 재연결

---

## 🚫 절대 규칙

1. `git push` 만으로 파이프라인 검증 금지 → Actions UI에서 `workflow_dispatch` 사용
2. API 키 값 출력/로그 기록 금지
3. 파일 삭제 시 목록 확인 후 별도 승인 (오늘 대청소 완료로 더 이상의 삭제는 신중히)
4. 로컬 테스트만으로 PASS 판정 금지 — 실 데이터 기준 검증 필수
5. **Zero-Keyword Policy**: 코드 내부에 특정 종목명(삼성전자 등) 하드코딩 절대 금지
6. **No Cliché Policy**: "이상한 점이 느껴지지 않아?" 등 상투적 오프닝 절대 금지 (검증기에서 걸러짐)

---

## 🏃 빠른 시작 명령어

```bash
# 최신 코드 받기
git pull origin main

# 파이프라인 전체 실행 (수동)
PYTHONPATH=. python3 src/agents/collector.py
PYTHONPATH=. python3 src/agents/detector.py
PYTHONPATH=. python3 src/agents/writer.py

# 대시보드 업데이트 및 배포
python3 src/ui/run_publish_ui_decision_assets.py
```

---

## GitHub

- Repo: `hoininsight-commits/hoininsight`
- Dashboard: `hoininsight-commits.github.io/hoininsight/`
