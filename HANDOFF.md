# HANDOFF.md

현재 작업 상태와 다음 할 일을 기록한다. 세션 시작 시 CLAUDE.md와 함께 읽는다.

---

## 마지막 업데이트: 2026-05-19

---

## 현재 상태 (완료)

### 1차 세션 (2026-05-18) — 구조 정비

**1. 데드 코드 제거 (~1,750줄)**
- `collector.py`: `collect_market/fred/ecos/dart()` 등 서브에이전트가 대체한 메서드 전부 제거
- `detector.py`: `select_best()`, `generate_fact_pack()`, `detect_*()` 메서드 전부 제거
- `writer.py`: `generate_long/shorts()`, `load_data()` 제거
- `engine/interpretation_layer.py`, `scenario_engine.py`, `anomaly_overlay.py` 삭제

**2. 하드코딩 제거 / 에이전트 패키지화 / GitHub Actions 워크플로우 생성**
- 에이전트 4개 → 패키지 구조 전환, `python -m src.agents.{name}` 독립 실행 가능
- `.github/workflows/pipeline.yml` 생성 (collect→detect→write→publish, 4회/일)

### 2차 세션 (2026-05-18) — 하네스 엔지니어링

**1. 로컬 실행 검증**
- 전체 파이프라인 순차 실행 성공 (Gemini 할당량 초과 → DeterministicEngine 폴백 동작 확인)
- `duckduckgo_search` → `ddgs` 교체 (`deep_research_agent.py` line 3)

**2. Hook 기반 자동화 (`.claude/settings.json`)**
- `SessionStart`: HANDOFF.md 자동 로드
- `Stop`: 세션 종료 시 HANDOFF.md 업데이트 리마인더
- `PostToolUse(Bash)`: `src.agents` 포함 명령 실행 시 `data/history/pipeline_run_log.txt`에 타임스탬프 기록

**3. Schedule 루틴 등록**
- ID: `trig_01PW7ugfiQF8efgFzUpD5rMQ`
- Cron: `0 3,9,15,21 * * *` (00/06/12/18 KST)
- 현재 `enabled: false` — GitHub 레포 연결 후 활성화 필요
- URL: https://claude.ai/code/routines/trig_01PW7ugfiQF8efgFzUpD5rMQ

**4. 멀티 에이전트 병렬 실행**
- 서브수집기 5개에 `__main__` 독립 진입점 추가
  - `market_agent.py`, `macro_agent.py`, `sentiment_agent.py`, `dart_agent.py`, `financial_collectors.py`
- `scripts/parallel_collect.py` 신규 생성 — subprocess 기반 프로세스 격리 병렬 오케스트레이터
  - Phase 1: 7개 독립 에이전트 동시 실행
  - Phase 2: 2개 종속 에이전트 동시 실행
  - 실행 검증 완료: 9/9 성공, 21.4초

### 3차 세션 (2026-05-19) — GitHub 확인 및 코드 개선 커밋

**1. GitHub 레포 상태 확인**
- `hoininsight-commits/hoininsight` (public) 정상 연결 확인
- Secrets 12개 등록 완료 (필수 8개 + KRX_ID/PW, YOUTUBE_COOKIES, TELEGRAM_CHAT_ID_TRANSCRIPT)

**2. 코드 개선 사항 커밋 (staged 15개 파일)**
- `src/prompts/writer_prompt.py`: 프롬프트 대폭 개선 (+143줄)
- `src/topic_engine/arbiter.py`: 토픽 선정 로직 강화 (+58줄)
- `src/engine/content_engine.py`: 콘텐츠 엔진 수정
- `src/agents/collector/`: 수집기 안정성 개선
- `dashboard/`: 대시보드 데이터 업데이트
- `data/history/`: 콘텐츠 이력 업데이트

---

## 현재 이슈 / 주의사항

| 이슈 | 심각도 | 내용 |
|---|---|---|
| Gemini API 할당량 초과 | ⚠️ 높음 | `429 RESOURCE_EXHAUSTED` — AI Studio에서 monthly spend cap 확인/조정 필요 |
| Schedule 루틴 미활성화 | ⚠️ 높음 | GitHub 레포 연결은 완료. Schedule 루틴만 `enabled: true`로 업데이트 필요 |
| Python 3.9 사용 중 | ℹ️ 낮음 | google-auth 등에서 deprecation warning. 3.11+ 권장 |
| Gemini API 모델명 불일치 | ℹ️ 낮음 | `arbiter.py`에서 `gemini-1.5-pro` 참조하나 실제는 `gemini-flash-latest` 사용 |

---

## 다음 할 일

### 즉시
- [ ] Gemini spend cap 조정 (AI Studio) → AI 기반 스크립트 생성 정상화 확인
- [x] GitHub 레포 설정 완료 (Secrets 12개 등록)
- [ ] Schedule 루틴 활성화: `enabled: true` + repo URL 추가 → GitHub Actions 첫 실행 테스트

### 단기
- [ ] `src/ui/narratives/` 학습 시스템을 파이프라인에 연동 (현재 고립 상태)
- [ ] Python 3.11 가상환경으로 전환

### 장기
- [ ] 서브 에이전트들이 `CollectorAgent`를 역호출하는 구조 개선
  - 현재: `MacroAgent.run()` → `CollectorAgent().collect_fred()`
  - 목표: 각 서브 에이전트가 자체 수집 로직 보유
- [ ] `src/core/filters.py` 미사용 확인 후 삭제 또는 Arbiter 전 필터로 재도입

---

## 핵심 결정 이력

| 날짜 | 결정 | 이유 |
|---|---|---|
| 2026-05-18 | `collectors/` → `collector/`로 통합 | 에이전트명과 폴더명 일치, 단수화 |
| 2026-05-18 | `detector.py` select_best() 전체 삭제 | v21.0 이후 Arbiter로 완전 대체 |
| 2026-05-18 | 에이전트를 `.py` 단일 파일 → `패키지/` 구조로 변환 | `python -m src.agents.X` 독립 실행 + GitHub Actions Job 분리 |
| 2026-05-18 | `collector/__init__.py`에 `collect_*()` 메서드 복원 | 서브 에이전트들이 역호출하는 구조 — 삭제 시 런타임 오류 발생 |
| 2026-05-18 | subprocess 기반 멀티 에이전트 오케스트레이터 도입 | ThreadPoolExecutor 대비 프로세스 격리, 독립 실행 가능성 확보 |

---

## 현재 파이프라인 실행 방법

```bash
cd /Users/jihopa/claude/hoininsight

# 표준 순차 실행
python -m src.agents.collector
python -m src.agents.detector
python -m src.agents.writer
python -m src.agents.publisher

# 멀티 에이전트 병렬 수집 (수집 단계만)
python scripts/parallel_collect.py
python scripts/parallel_collect.py --phase 1   # Phase 1만
python scripts/parallel_collect.py --phase 2   # Phase 2만

# 전체 파이프라인 한 번에
python run_full_pipeline.py
```

---

## GitHub Actions Secrets 등록 필요 목록

```
GEMINI_API_KEY       ← 필수 (현재 할당량 초과 상태)
FRED_API_KEY         ← 필수
ECOS_API_KEY         ← 필수
OPENDART_API_KEY     ← 권장
DATA_GO_KR_API_KEY   ← 선택
FINNHUB_API_KEY      ← 선택
TELEGRAM_BOT_TOKEN   ← 권장
TELEGRAM_CHAT_ID     ← 권장
```
