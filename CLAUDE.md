# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **세션 시작 전 반드시 `HANDOFF.md`를 먼저 읽으세요** — 현재 작업 상태, 이슈, 다음 할 일이 기록되어 있습니다.

## 실행 명령어

모든 명령어는 `hoininsight/` 디렉토리에서 실행한다.

```bash
# 의존성 설치
pip install -r requirements.txt

# 전체 파이프라인 (로컬 실행)
python run_full_pipeline.py

# 에이전트 개별 독립 실행 (GitHub Actions 각 Job과 동일)
python -m src.agents.collector
python -m src.agents.detector
python -m src.agents.writer
python -m src.agents.publisher

# Rotation Radar (collector 직후 실행)
python scripts/rotation_radar.py

# CI / 검증
bash scripts/run_audit.sh
python scripts/run_ci_minimal_tests.py
python scripts/run_tests_and_summarize.py
```

### 런타임 모드

```bash
# 오프라인 모드 (네트워크 수집 생략, 로컬 캐시 사용)
export HOIN_RUNTIME_MODE=offline && python -m src.agents.collector

# 특정 날짜 백테스트
export HOIN_TARGET_DATE=2026-03-05 && python run_full_pipeline.py
```

### 환경 설정

```bash
cp env.example .env
# 필수: GEMINI_API_KEY, FRED_API_KEY, ECOS_API_KEY
# 선택: OPENDART_API_KEY, DATA_GO_KR_API_KEY, FINNHUB_API_KEY
# 알림: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

## 아키텍처

HOIN Insight는 시장 데이터를 수집하고 이상징후를 탐지하여 Gemini AI로 "경제사냥꾼" 스타일 유튜브 스크립트를 자동 생성하는 파이프라인이다. GitHub Actions로 하루 4회(00/06/12/18 KST) 자동 실행된다.

### 파이프라인 흐름

```
GitHub Actions
├── Job 1: python -m src.agents.collector   → data/raw/YYYY/MM/DD/*.json
├── Job 2: python -m src.agents.detector   → data/fact_pack/ + data/signals/
├── Job 3: python -m src.agents.writer     → data/scripts/YYYY/MM/DD/Topic_N/
└── Job 4: python -m src.agents.publisher  → docs/data/ (GitHub Pages) + Telegram
```

각 Job은 독립 실행 가능하다. `workflow_dispatch` 트리거로 특정 단계부터 재실행할 수 있다(`start_from: detect|write|publish`).

### 에이전트 패키지 구조

각 에이전트는 `src/agents/{name}/` 패키지이며 `__main__.py`가 CLI 진입점이다.

```
src/agents/
├── collector/                  # Job 1: 데이터 수집
│   ├── __init__.py             (CollectorAgent)
│   ├── __main__.py             (진입점)
│   ├── collector_runner.py     (2단계 병렬 오케스트레이터)
│   ├── market_agent.py         Yahoo Finance / pykrx
│   ├── macro_agent.py          FRED / ECOS
│   ├── dart_agent.py           DART 공시
│   ├── sentiment_agent.py      RSS 뉴스
│   ├── social_agent.py         소셜 리서치
│   ├── flow_collector.py       수급 흐름
│   ├── financial_collectors.py Consensus / COT
│   ├── putcall_collector.py
│   └── deep_research_agent.py  (Arbiter에서 호출)
├── detector/                   # Job 2: 이상징후 탐지 + 토픽 선정
│   ├── __init__.py             (DetectorAgent → TopicArbiter 위임)
│   └── __main__.py
├── writer/                     # Job 3: 스크립트 생성
│   ├── __init__.py             (WriterAgent → ContentEngine 위임)
│   └── __main__.py
└── publisher/                  # Job 4: 배포
    ├── __init__.py             (PublisherAgent)
    └── __main__.py
```

### 내부 호출 구조

```
CollectorAgent.run()
  └── CollectorRunner.run_all()
        Phase 1 (병렬): MarketAgent, MacroAgent, DartAgent,
                        SentimentAgent, ConsensusCollector, COTCollector, PutCallCollector
        Phase 2 (병렬): FlowCollector, SocialAgent

DetectorAgent.run()
  └── TopicArbiter.select_topic_from_raw(raw_dir)
        ├── DataCondenser (raw JSON → 고농축 텍스트)
        ├── DeepResearchAgent (구조적 연결고리 탐색)
        └── Gemini (최강 토픽 1개 선정)

WriterAgent.run()
  ├── ContentEngine.generate_contents()   ← Gemini 스크립트 생성
  ├── ScriptQualityGate.evaluate()        ← PASS / HOLD / DROP 판정
  └── DeterministicTopicEngine.analyze()  ← AI 실패 시 폴백
```

### SSOT 데이터 경로 (`src/utils/paths.py`)

경로 상수는 반드시 `src/utils/paths.py`에서 임포트한다. 경로 문자열을 코드에 직접 작성하지 않는다.

| 경로 | 용도 |
|---|---|
| `data/raw/YYYY/MM/DD/` | 원천 수집 데이터 (artifact로 Job 간 전달) |
| `data/signals/YYYY/MM/DD/` | 탐지 결과 |
| `data/fact_pack/` | 토픽 패키지 (WriterAgent 입력) |
| `data/scripts/YYYY/MM/DD/Topic_N/` | 생성된 스크립트 |
| `data/history/` | 콘텐츠 이력 (Git 커밋됨) |
| `docs/data/` | GitHub Pages 라이브 데이터 (Git 커밋됨) |
| `data_outputs/` | **DEPRECATED** — 신규 코드에서 사용 금지 |

### 주요 유틸리티

- **`src/utils/target_date.py`**: 모든 날짜는 KST(UTC+9) 기준. `get_target_ymd()`는 `HOIN_TARGET_DATE` 환경변수를 우선 적용(백테스트용). `get_current_round()`는 KST 시각을 라운드 1~4로 매핑한다.
- **`src/core/gemini_client.py`**: Gemini 클라이언트 싱글턴 (모델: `gemini-flash-latest`). `GEMINI_API_KEY` 없을 시 `None`으로 graceful degrade.
- **`src/utils/dna_manager.py`**: YouTube 학습에서 추출한 DNA 패치를 Writer/Arbiter 프롬프트에 주입.
- **`src/utils/data_condenser.py`**: raw JSON을 Gemini에 전달하기 전 고농축 텍스트로 압축.

### Soft-fail 원칙

API 수집 실패 시 해당 필드는 반드시 `null`로 저장한다 — `0.0` 가짜 정상값 절대 금지. 수집기 하나의 실패가 파이프라인 전체를 중단시키지 않는다. 텔레그램 브리핑에는 수집 실패 시 `⚠️ [수집 경고]` 블록이 자동 주입된다.

### 토픽 선정 5기준 (모두 충족 필요)

1. 데이터 간 모순이 존재할 것
2. WHY NOW를 데이터로 설명 가능할 것 (뉴스 키워드만으로 불가)
3. 구조적 확장이 가능할 것 (A → B → C → 한국 투자자 임팩트)
4. 시청자가 즉시 납득 가능할 것
5. 특정 종목/섹터와 액션으로 연결 가능할 것

### GitHub Actions Secrets 설정

| Secret | 필수 | 용도 |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | LLM 분석 전반 |
| `FRED_API_KEY` | ✅ | 미국 거시 데이터 |
| `ECOS_API_KEY` | ✅ | 한국은행 데이터 |
| `OPENDART_API_KEY` | 권장 | DART 공시 수집 |
| `DATA_GO_KR_API_KEY` | 선택 | 공공데이터포털 |
| `FINNHUB_API_KEY` | 선택 | 금융 데이터 보완 |
| `TELEGRAM_BOT_TOKEN` | 권장 | 브리핑 발송 |
| `TELEGRAM_CHAT_ID` | 권장 | 브리핑 발송 |
