# HANDOFF.md

현재 작업 상태와 다음 할 일을 기록한다. 세션 시작 시 CLAUDE.md와 함께 읽는다.

---

## 마지막 업데이트: 2026-05-19 (5차 세션)

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

### 5차 세션 (2026-05-19) — 순환매 레이더 동적 스테이지 재설계

**1. rotation_radar.json NaN 버그 수정 (`scripts/rotation_radar.py`)**
- `_sanitize()` 함수 추가: NaN/Infinity → null 재귀 치환
- `docs/data/monitoring/rotation_radar.json` 동기화 추가 (대시보드가 읽는 경로)

**2. `StageContextBuilder` v2.0 전면 재작성 (`src/rotation/stage_context_builder.py`)**
- 기존: 오늘 등락률 상위 업종 TOP5 → 스테이지 배정 (소형주 노이즈 심각)
- 신규: 2단계 동적 알고리즘
  - STAGE 1: 네이버 KOSPI 시총 랭킹 스크래핑 → 상위 5종목 자동 탐지 (대장주)
    - 현재: 삼성전자, SK하이닉스, 삼성전자우, SK스퀘어, 현대차 (집중도 66.4%)
    - 대장주가 바뀌면 자동 교체 — 하드코딩 없음
  - STAGE 2~5: 네이버 79개 업종 → 상위 25개 프리필터 → 대장주 수익률 상관계수(20일) 계산 → 내림차순 배정
  - 대장주 포함 업종 자동 제외 (STAGE 1 중복 방지)

**3. Signal 2 동적화 (`src/rotation/signals.py`)**
- `LEAD_TICKERS` 하드코딩 제거
- `market_context.json`의 `leaders` 필드에서 동적 로드
- `compute_signal_2(context_path)` 시그니처 변경

**4. 실행 결과 (2026-05-19)**
- 대장주 5종목 자동 탐지 성공
- STAGE 2: 생명보험(상관계수 0.69) / STAGE 3: 전기유틸리티(0.57) / STAGE 4: 복합기업(0.46) / STAGE 5: 은행(0.46)

### 4차 세션 (2026-05-19) — 순환매 레이더 전면 구현

**1. `src/rotation/` 패키지 신설 (Gemini 미사용, 순수 규칙 기반)**

| 파일 | 역할 |
|------|------|
| `src/rotation/signals.py` | 신호 5개 계산 (시장폭/호재무반응/외인이동/모멘텀/생태계) |
| `src/rotation/confirmation_engine.py` | 5신호 종합 → 스코어(0~19)/전략/스테이지 판정 |
| `src/rotation/context_manager.py` | `market_context.json` basis/is_current/mood 자동 갱신 |
| `src/rotation/stage_context_builder.py` | **핵심** — 79개 KOSPI 업종 자동 랭킹 → 5 스테이지 전체 필드 자동 생성 |

**2. `scripts/rotation_radar.py` 전면 재작성 (v5.0)**
- `StageContextBuilder.build()` → 신호 5개 계산 → 종합 판정 → `market_context.json` 갱신 순서
- `--force` 옵션: 6시간 인터벌 무시하고 즉시 재빌드
- 실행: `python scripts/rotation_radar.py [--force]`

**3. `StageContextBuilder` 동작 방식**
- 네이버 `sise_group.naver?type=upjong` → 79개 업종 + 당일 등락률 수집
- 업종별 상세 페이지 → 대표 종목 5개 (ticker + name) 수집
- pykrx 5일 모멘텀 보정 (dropna 처리 — 상한가 종목 NaN 방지)
- 복합 스코어 = 등락률×0.4 + 5일모멘텀×0.6 → 상위 5개 → STAGE_1~5 배정
- **모든 필드 자동 생성**: name, desc, keywords, tickers, basis, color, is_current
- 6시간마다 자동 재빌드 (시장 국면 변화 반영)

**4. 대시보드 신설**
- `docs/rotation_radar.html` — 순환매 전용 대시보드 (순수 HTML/JS, 프레임워크 없음)
- 스테이지 순서/색상/이름 전부 `rotation_radar.json` 동적 로드 (하드코딩 없음)
- 로컬 서버: `cd docs && python3 -m http.server 8765`
- 접속: http://localhost:8765/rotation_radar.html

**5. `MarketBreadthCollector` 임계값 수정**
- 기존: `advancing > declining` (단순 비교)
- 수정: `advancing > declining × 2` + ratio 필드 추가

**6. 알게 된 이슈**
- 네이버 `sise_trans_stat.naver` URL → 404 (폐기됨). `sise_group.naver?type=upjong`으로 대체
- pykrx `get_index_ohlcv_by_date` → `지수명` KeyError. KODEX 200(069500)으로 대체

---

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
| Signal 3 외국인 수급 데이터 없음 | ⚠️ 중간 | `sector_flow_*.json` 수집 미연동 — FlowCollector 확인 필요 |
| 스테이지 방산/전력기기 미포함 | ℹ️ 낮음 | 프리필터 top25에 해당 섹터 오늘 등락률이 낮아 제외됨. 5일 누적 데이터 쌓이면 개선 예상 |
| Python 3.9 사용 중 | ℹ️ 낮음 | google-auth 등에서 deprecation warning. 3.11+ 권장 |

---

## 다음 할 일

### 즉시
- [ ] Gemini spend cap 조정 (AI Studio) → AI 기반 스크립트 생성 정상화 확인
- [x] GitHub 레포 설정 완료 (Secrets 12개 등록)
- [ ] Schedule 루틴 활성화: `enabled: true` + repo URL 추가 → GitHub Actions 첫 실행 테스트
- [x] `rotation_radar.html` 데이터 로드 실패 수정 (NaN→null 처리 + docs/ 동기화)
- [ ] Signal 3 (외국인 수급 이동) — `sector_flow_*.json` 수집 경로 확인 후 연동 검증
- [ ] `collector` 실행 후 rotation_radar 재실행해서 Signal 3~5 실제 데이터로 검증

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
| 2026-05-19 | 순환매 엔진 Gemini 미사용 결정 | 비용 절감 + 항상 실행 가능. name/desc/tickers 전부 pykrx + naver 스크래핑으로 대체 |
| 2026-05-19 | `market_context.json` 수동 관리 → `StageContextBuilder` 자동 생성으로 전환 | 시장 국면 변화 시 자동 반영. 6시간 인터벌로 재빌드 |
| 2026-05-19 | naver `sise_trans_stat` 대신 `sise_group?type=upjong` 사용 | 구 URL 404 폐기. 신 URL에서 79개 업종 등락률 수집 가능 |

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

# 순환매 레이더 (collector 직후 실행)
python scripts/rotation_radar.py           # 6시간 인터벌 준수
python scripts/rotation_radar.py --force   # 강제 전체 재빌드

# 순환매 대시보드 로컬 서버
cd docs && python3 -m http.server 8765
# → http://localhost:8765/rotation_radar.html
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
