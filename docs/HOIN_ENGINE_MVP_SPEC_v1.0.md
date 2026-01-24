# ✅ HOIN ENGINE vNext (US+KR) — Economic Hunter MVP Spec

## 0) 최상위 목표 (고정)

**HOIN ENGINE의 MVP 목표:**

1. 매일 데이터 기반으로 **토픽 후보 5~10개 자동 생성**
2. 후보 중 **TOP 1~3개 영상 토픽 자동 선정**
3. 각 토픽에 대해 **60~120초 영상 스크립트 자동 생성**
4. (확장) TTS/영상 합성까지 자동화 가능하도록 출력 포맷 고정

**중요 원칙:**

* 정확한 예측이 아니라 **“말이 되는 토픽을 매일 꾸준히 생산”**이 1차 목표
* 하루 데이터는 **판단이 아니라 감지(Event)**에만 사용
* 기존 HOIN ENGINE의 “확정(Structural)” 엔진은 유지하되, **영상용 레이어를 별도 추가**
* **무분별한 데이터 수집/무분별한 로직 변경 금지**

---

## 1) 최종 엔진 구조 (3-Layer)

### Layer A — Event Detection (Daily, 1일)

* 목적: 오늘 “이상하게 튄 것”을 빠르게 포착
* 출력: `candidates.json` (토픽 후보 5~10개)
* 금지: 확정/레벨/WHY_NOW/투자추천

### Layer B — Narrative Topic (Short-term, 3~7일)

* 목적: 후보를 “영상으로 말할 수 있는 주제”로 승격/정리
* 출력: `narrative_topics.json` (상위 1~3개)
* 금지: Level 부여, Structural 확정

### Layer C — Structural Topic (기존 HOIN ENGINE)

* 기존 STEP 1~6를 통과한 것만 확정
* 출력: 기존 `topics.json` 유지
* Narrative가 Structural을 오염시키면 실패

---

## 2) 토픽 생성의 핵심 개념 (반드시 반영)

### 2.1 Topic Anchor vs Narrative Driver

경제사냥꾼 영상은 항상 “겉(Anchor) + 속(Driver)” 구조다.

* **Topic Anchor:** 사람들이 체감하는 관측 지점
  (섹터 하락, 지수 레벨 돌파, 큰 계약, 강한 발언 등)
* **Narrative Driver:** 그 현상을 만든 구조적 힘
  (자본의 평가 기준 변화, 자금 경로 이동, 생산성 증명 단계 진입 등)

> 고정 문장(엔진 헌법급):
> **“토픽은 사람들이 느끼는 곳에서 잡고, 설명은 자본이 움직이는 이유에서 한다.”**

---

## 3) “무슨 데이터를 얼마나?” 최소 데이터 기준 (US+KR 혼합)

**MVP 데이터는 5종만 사용 (늘리지 말 것):**

1. **Benchmark Index (US+KR)**

   * US: S&P500(또는 NASDAQ), VIX, US10Y(가능하면)
   * KR: KOSPI, KOSDAQ
2. **Sector/Theme Proxy (가능한 범위에서 최소)**

   * 대표 섹터 ETF/지수(US: XLK/XLF/XLV 등, KR: 가능한 섹터 ETF/업종지수)
3. **Leader 1~3 (선택)**

   * 섹터 대장/대표 종목 1~3개 가격/거래량 (없으면 생략 가능)
4. **Flow Proxy 1개 (가능한 것만)**

   * ETF AUM/순유입/거래대금 중 하나 (미수집이면 “NULL” 허용)
5. **Event Text (텍스트 기반 이벤트 최소)**

   * 계약/발언/정책/실적/가이던스 “발생 여부” 정도
   * (뉴스 크롤링/공시/핵심 헤드라인만)

> 원칙: 데이터 부족하면 “모른다/미확인”을 출력하고 Confidence 낮추면 된다.
> “데이터 확장”은 재현 실패가 반복될 때만 추가 제안.

---

## 4) Candidate Detector (후보 탐지) — 알고리즘 (최소 로직)

### 4.1 후보 카테고리 풀 (고정 6개, 다양성 확보)

매일 후보는 아래 6풀에서 생성한다.
최종 TOP 1~3개는 가능하면 서로 다른 풀에서 1개씩 선정.

1. **Sector Divergence** (특정 섹터만 반대로 움직임)
2. **Index Regime** (지수 레벨/레짐 변화)
3. **Big Contract / Alliance** (대형 계약/동맹)
4. **Policy / Politics** (정책/정치 발언)
5. **Earnings / Guidance** (실적/가이던스)
6. **Flow / Liquidity** (ETF/유동성/자금 경로)

---

### 4.2 SDF: Sector Divergence Finder (핵심)

사용자가 “바이오” 같은 섹터를 주지 않아도 엔진이 먼저 잡는다.

**최소 신호 5개(고정, 추가 금지):**

1. 시장 대비 섹터 상대수익 괴리 Top-K
2. 섹터 내부 Breadth 붕괴(상승/하락 비율)
3. Leader Shock(대장 1~3개 급락/거래량)
4. Expectation Reset(호재에도 하락)
5. Style Rotation Proxy(실적 섹터 vs 성장 섹터 상대강도)

---

### 4.3 MRDF: Market Regime Finder (Index Regime) — 최소 3신호

(코스피5000 같은 영상 자동 포착용)

1. **Round-number Level Break / Approach**

   * 5000/4000/20000 등 상징 레벨 돌파/접근
2. **Earnings Step-Change Proxy**

   * 컨센서스/영업이익 추정 레벨업(가능한 범위 내)
3. **ETF/Flow Step-Change Proxy**

   * AUM/유입/거래대금 레벨업(가능하면)

> 데이터 부족 시: 1)만으로도 후보는 만들되 Confidence 낮게.

---

### 4.4 Event Text Candidate

(팔란티어×HD현대, 트럼프 발언 같은)

* “큰 발언/계약/정책 발표”는 **후보 생성 가능**
* 단, 반드시 **Claim Type 태그**로 보호(아래 6장 참조)

---

## 5) TOPIC SELECTOR (후보 중 1~3개 선택) — 3점수만 사용

MVP는 복잡하면 망한다. **점수 3개만** 사용.

1. **Hook Score (체감성)**

   * 섹터/지수/대형 계약/대형 발언이면 높음
2. **Number Score (숫자 가능성)**

   * %, 조원, 계약 규모, 수익률, 레벨 등 “숫자 1개 이상” 붙일 수 있으면 높음
3. **Why-now Score (오늘 말할 이유)**

   * 급등락, 레벨 돌파, 이벤트 발생, 동시 신호(2개 이상)면 높음

**Selection Rule:**

* TOP 1~3개 선정
* 가능하면 서로 다른 카테고리 풀에서 1개씩

---

## 6) Script Generator (60~120초) — 경제사냥꾼 템플릿 고정

### 6.1 고정 스크립트 구조

1. **Hook (0~10s)**
2. **Observation (10~30s)** — 숫자 2~3개
3. **Driver (30~70s)** — “진짜 이유는 ~다” 1~2개
4. **Implication (70~95s)** — 시장이 왜 그렇게 움직이는지
5. **Risk (95~110s)** — 반대 시나리오 1개
6. **Close (110~120s)** — 다음 체크 포인트

### 6.2 Claim Type Safety (필수 안전장치 2개)

#### (A) Claim Type 태그

* **Observed(관측 수치)**: 이미 발생한 수치(수익률, AUM, 지수 레벨 등)
* **Interpretation(해석)**: 돈의 성격 변화 등
* **Projection(전망)**: “유지되면” 수준의 조건부 전망

**규칙:**

* Observed 최소 1개 필수
* Projection은 1개만 허용 + Risk 문장 필수

#### (B) Evidence Type 분리

* Observed Metrics: 검증 가능한 과거 수치
* Interpretive Claims: 해석/서사

> “Observed metrics increase credibility, but do not confirm causality.”

---

## 7) 출력 JSON 스키마 (개발 필수)

### 7.1 candidates.json

```json
{
  "date": "YYYY-MM-DD",
  "market": "US|KR|MIXED",
  "candidates": [
    {
      "candidate_id": "string",
      "category_pool": "SectorDivergence|IndexRegime|BigContract|Policy|Earnings|Flow",
      "topic_anchor": "string",
      "trigger_event": "string",
      "observed_metrics": ["string"],
      "driver_candidates": ["string"],
      "hook_score": 0,
      "number_score": 0,
      "why_now_score": 0,
      "confidence": "LOW|MEDIUM|HIGH",
      "risk_note": "string",
      "claim_tags": ["Observed","Interpretation","Projection"]
    }
  ]
}
```

### 7.2 narrative_topics.json (최종 TOP 1~3)

```json
{
  "date": "YYYY-MM-DD",
  "topics": [
    {
      "topic_id": "string",
      "topic_anchor": "string",
      "narrative_driver": "string",
      "trigger_event": "string",
      "core_narrative": "string",
      "observed_metrics": ["string"],
      "intent_signals": ["string"],
      "structural_hint": "string",
      "era_fit": "string",
      "confidence_level": "LOW|MEDIUM|HIGH",
      "risk_note": "string",
      "disclaimer": "This is NOT a confirmed structural topic.",
      "script_kr": "string"
    }
  ]
}
```

---

## 8) 기존 HOIN ENGINE(Structural)과의 충돌 방지 (게이트)

* Narrative Topic에는 **Level(L2~L4) 부여 금지**
* Narrative Topic에는 **WHY_NOW 확정 금지**
* Structural Topic은 기존 STEP 1~6 통과한 것만 생성
* Narrative → Structural 자동 승격 금지

---

## 9) ZIP 문서 기준 “수정/추가” 정리 (필수)

### 9.1 수정(EDIT) — 최소 1개 문서

ZIP 내부의 “최상위 헌법/부트로더 성격 문서”에 섹션 추가:

* `## ENGINE LAYERS (Event → Narrative → Structural)`
* `## TEMPORAL RULES (Event vs State vs Structural)`
* Narrative는 영상용 후보이며 확정/레벨 금지 명시

### 9.2 추가(ADD) — 신규 디렉토리/문서

```text
SIGNAL_DETECTION_LAYER/
  ├─ SECTOR_DIVERGENCE_FINDER_v1.0.md
  ├─ MARKET_REGIME_FINDER_v1.0.md
  ├─ TEMPORAL_INTERPRETATION_RULES_v1.0.md
  └─ SCHEMAS/
      ├─ sector_anchor_candidate_v1.0.yml
      └─ market_regime_candidate_v1.0.yml

NARRATIVE_LAYER/
  ├─ NARRATIVE_TOPIC_DEFINITION_v1.1.md
  ├─ TOPIC_ANCHOR_AND_DRIVER_v1.0.md
  ├─ NARRATIVE_TOPIC_SCHEMA_v1.0.yml
  ├─ SCRIPT_TEMPLATE_60_120S_v1.0.md
  └─ CASE_STUDIES/
      ├─ case_palantir_hdhyundai_v1.0.md
      ├─ case_bio_sector_drawdown_v1.0.md
      └─ case_kospi5000_pres_portfolio_v1.0.md

INTEGRATION_RULES/
  └─ NARRATIVE_TO_STRUCTURAL_GATE_v1.0.md
```

---

## 10) MVP 검증 테스트 (반드시 통과)

1. **섹터를 사용자 입력 없이** SDF가 “이상 섹터” 후보로 뽑아야 함
2. 후보 중 TOP 1~3 토픽이 매일 생성되어야 함 (“주제 없음” 최소화)
3. 각 토픽은 60~120초 스크립트가 생성되어야 함
4. Narrative Topic에 Level/WHY_NOW가 붙으면 실패
5. Structural Topic은 기존 엔진 결과만 유지(오염 금지)

---

## 11) 운영 성공 기준(1차)

* “정확도”가 아니라 **“매일 토픽이 나온다”**
* 토픽 다양성이 유지된다(6풀 분산)
* 스크립트에 Observed 수치가 최소 1개 포함된다
* Risk 문장이 포함된다
