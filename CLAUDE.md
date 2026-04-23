# HOIN Insight — 안티(Antigravity) 부팅 지침서
# 최종 수정: 2026-04-23 | v2.0 (Zero-Keyword Purge 이후)

---

## 🚨 "작업 준비하자" 를 들었다면

사용자가 **"작업 준비하자"** 라고 말하면, 안티는 즉시 아래 절차를 수행한다.
다른 말 없이 바로 시작한다.

### Step 1 — 최신 코드 PULL
```bash
cd /Users/taehunlim/dev/HoinInsight && git pull origin main
```
(회사 Mac이라면 경로가 ~/Antigravity/hoininsight일 수 있음. 존재하는 경로로 실행)

### Step 2 — HANDOFF 최신 세션 블록 읽기
```
파일: docs/HANDOFF_FINAL.md (파일 끝부분 — 가장 최근 세션 블록)
```
파일 전체가 길므로 **마지막 500줄**을 우선 읽어 최신 상태를 파악한다.

### Step 3 — 작업 준비 완료 보고
아래 형식으로 사용자에게 현황을 보고한다:

```
✅ 작업 준비 완료 (git pull 완료, HANDOFF 읽음)

📌 현재 상태:
- 마지막 작업일: [날짜]
- 완료된 것: [핵심 항목]
- 다음 우선순위: [1순위 / 2순위 / 3순위]
- 대시보드 실행: python3 hoin_dashboard/server.py

🔔 바로 시작할까요?
```

---

## 📁 프로젝트 개요

**HOIN Insight** — 경제사냥꾼 스타일 시장 인텔리전스 엔진

- 매일 시장 이상징후(Anomaly)를 탐지하고
- WHY NOW를 설명하는 7단계 서사를 생성하며
- 운영자 대시보드로 실시간 시각화하는 시스템

---

## 🗂️ 핵심 경로

| 환경 | 로컬 경로 |
|---|---|
| 집 Mac | `~/dev/HoinInsight` |
| 회사 Mac | `~/Antigravity/hoininsight` (추정, 확인 필요) |

| 항목 | 경로 |
|---|---|
| **최신 HANDOFF** | `docs/HANDOFF_FINAL.md` |
| 시스템 헌장 | `docs/ECONOMIC_HUNTER_SYSTEM_CHARTER.md` |
| 대시보드 서버 | `hoin_dashboard/server.py` (포트 8888) |
| 신호 데이터 | `data/signals/YYYYMMDD/today_signal.json` |
| 파이프라인 진입점 | `src/agents/collector.py` → `detector.py` → `writer.py` |

---

## ⚙️ 현재 시스템 상태 (2026-04-23 기준)

### 완료된 핵심 항목
- **Zero-Keyword Policy**: 시스템 내부 하드코딩 종목/키워드 전면 제거
- **Gemini 모델**: `gemini-1.5-flash-002` (안정 버전 고정)
- **재시도 정책**: TIER 1 기준 6회, 최대 60초 대기
- **E2E 검증 완료**: 백지상태 → 수집 → 분석 → 화면 출력까지 100점(9/9)

### 다음 우선순위
1. ECOS API 복구 (kr_base_rate, kr_cpi)
2. DART 공시 수집 복구
3. TIER 1/2/3 콘텐츠 패키지 UI 반영

---

## 🚫 절대 규칙

1. `git push` 만으로 파이프라인 검증 금지 → Actions UI에서 `workflow_dispatch` 사용
2. API 키 값 출력/로그 기록 금지
3. 파일 삭제 시 목록 확인 후 별도 승인
4. 로컬 테스트만으로 PASS 판정 금지 — 실 데이터 기준 검증 필수
5. **Zero-Keyword Policy**: 코드 내부에 특정 종목명(삼성전자 등) 하드코딩 절대 금지
6. 기존 문서 덮어쓰기 금지 — ADD-ONLY 원칙

---

## 🏃 빠른 시작 명령어

```bash
# 최신 코드 받기
git pull origin main

# 파이프라인 전체 실행 (수동)
PYTHONPATH=. python3 src/agents/collector.py
PYTHONPATH=. python3 src/agents/detector.py
PYTHONPATH=. python3 src/agents/writer.py

# 대시보드 실행
python3 hoin_dashboard/server.py
# → http://localhost:8888

# 세션 자동 준비 스크립트
bash scripts/start_session.sh
```

---

## GitHub

- Repo: `hoininsight-commits/hoininsight`
- Dashboard: `hoininsight-commits.github.io/hoininsight/`
