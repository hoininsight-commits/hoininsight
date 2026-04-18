# HOIN Insight — Project Architecture & Status

이 파일은 HOIN Insight v3.0 파이프라인의 실제 구조와 개발 진행 상황을 기록하는 SSOT(Single Source of Truth) 문서입니다.

---

## 1. 파이프라인 구조 (v3.0)

### CollectorRunner (병렬 서브에이전트, 7개)
에이전트들이 병렬로 가동되어 `data/raw/` 폴더에 원천 데이터를 저장합니다.
- **MarketAgent**      → `market.json` (Yahoo Finance)
- **MacroAgent**       → `fred.json` / `ecos.json` (미국/한국 금리 및 지표)
- **ConsensusAgent**   → `consensus.json` (Finnhub 업계 전망)
- **COTAgent**         → `cot.json` (헤지펀드 포지션)
- **SentimentAgent**   → `sentiment.json` (글로벌 뉴스 및 공포지수)
- **DartAgent**        → `dart.json` (DART 공시 정밀 타격)
- **PutCallCollector** → `putcall.json` (CBOE 풋/콜 비율)

### 메인 분석 및 생성 워크플로
독립된 에이전트들이 순차적으로 데이터를 가공하여 최종 결과물을 만듭니다.
1. **DETECTOR**   → 이상징후 탐지 및 오늘 최고의 토픽 선정
2. **ANALYST**    → Gemini 기반 레벨2 인과관계 분석
3. **WRITER**     → 경제사냥꾼 DNA 기반 스크립트(Long/Short) 생성
4. **FACT_CHECKER** → 생성된 스크립트의 수치 데이터 검증 및 차단
5. **PUBLISHER**  → 대시보드 업데이트 및 텔레그램 알림

**최종 흐름:**
`WRITER` → `FACT_CHECKER` → `PUBLISHER` → `TELEGRAM(Docs)`

---

## 2. 과제 진행 상황 (Roadmap)

### 즉시 필요 과제 (Main Pipeline)
- [x] FACT_CHECKER 파이프라인 내장 (#033)
- [x] 파이프라인 실행 단일화 (`python -m src.pipeline`) (#038)
- [x] 레거시 코드 일괄 정리 및 최적화 (#038)

### 중기 과제 (Signals & Data)
- [x] Put/Call Ratio 수집 및 신호화 (#034)
- [ ] RRG 섹터 로테이션 분석 고도화
- [ ] 백테스팅 엔진 연동

---

## 3. 자동화 및 실행 구조

### GitHub Actions (Server)
- **daily_pipeline.yml** (매일 KST 06:00)
  - 데이터 수집 + 신호 탐지 + 분석 + 스크립트 생성 + 대시보드 배포
- **learner_pipeline.yml** (수동 트리거 / 비정기)
  - 유튜브 자막 대량 수집 및 학습용 데이터 아카이빙

### 독립 실행 도구
- **run_learner.py** → `LearnerAgent` (유튜브 자막 수집, 파이프라인과 독립 실행)
- **utils/sanity_check.py** → 운영 환경 데이터 무결성 검증

---

## 4. 데이터 경로 (Authority Path)

- **Raw Data**: `data/raw/YYYYMMDD/`
- **Signals**: `data/signals/YYYYMMDD/`
- **Output Scripts**: `data/scripts/YYYYMMDD/`
- **Dashboard**: `docs/` (GitHub Pages)
