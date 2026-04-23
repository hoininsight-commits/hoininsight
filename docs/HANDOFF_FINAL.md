좋다.
기존 인수인계서는 **초기 엔진 고도화 단계 기준**이라서, 지금 상태를 이어받기엔 많이 부족하다.
특히 이후에 실제로 진행된 것들:

* Gemini 의존성 전수 감사
* Control Layer
* Fallback / Retry / Loop 차단
* Observability
* Metric Calibration
* Quality Score v2
* Quality Validation
* Validation Hardening
* Market Reality Validation
* Market Intelligence Upgrade
* Content Tier System
* UI/대시보드 방향 재정의

이 전부가 빠져 있다.
그래서 아래는 **기존 handoff를 완전히 확장한 “이사용 최종 인수인계서”**다.
기존 첨부 문서의 골격과 핵심 문장을 기반으로, 이후 실제 작업된 내용까지 모두 반영해서 다시 썼다. 

아래 그대로 다음 채팅으로 옮기면 된다.

```markdown
===========================================
# HOIN INSIGHT 최종 인수인계서
# 경제사냥꾼형 콘텐츠 엔진 / 판단 엔진 / 검증 엔진 / 운영 UI 프로젝트
# 작성일: 2026-04-21
# 목적: 새 채팅/새 모델/새 작업자가 현재 프로젝트의 정의, 목적, 구조, 운영 원칙, 개발 이력, 현재 상태를 오해 없이 그대로 이어받도록 하기 위한 최종 handoff
===========================================

## 0. 이 문서의 성격

이 문서는 단순 요약문이 아니다.
이 문서는 다음 목적을 가진다.

1. HOIN Insight 프로젝트의 **정의와 철학**을 왜곡 없이 전달한다.
2. 지금까지 확정된 **시스템 구조와 고정 원칙**을 전달한다.
3. 어떤 기능이 왜 만들어졌는지, 어떤 순서로 진화했는지를 전달한다.
4. 현재 무엇까지 완료되었고, 무엇이 아직 남았는지를 전달한다.
5. 다음 채팅/다음 모델이 **맥락 손실 없이 즉시 작업을 이어갈 수 있도록** 한다.

중요:
- 이 프로젝트는 단순 뉴스 요약기나 단순 스크립트 생성기가 아니다.
- 이 프로젝트는 단순 투자 추천기도 아니다.
- 이 프로젝트는 **경제사냥꾼 스타일의 구조적 주제 선점형 콘텐츠 엔진**이다.
- 단, “그럴듯한 콘텐츠”를 많이 뽑는 게 목적이 아니라,
  **시장 구조의 이상징후/모순/WHY NOW를 포착하고, 그것을 실제 콘텐츠로 전환하는 엔진**이 목적이다.
- 모든 확장은 기본적으로 **ADD-ONLY** 원칙을 따른다.
- 기존 정의 문서, 기존 파이프라인, 기존 문서 체계는 함부로 덮어쓰지 않는다.

---

# 1. 프로젝트의 최종 정의

## 1.1 HOIN Insight는 무엇인가

HOIN Insight는 본질적으로 다음과 같은 시스템이다.

> “시장 구조의 이상징후를 탐지하고,
> WHY NOW를 설명하고,
> 경제사냥꾼형 주제로 구조화하고,
> 그것을 실제 운영 가능한 콘텐츠 후보로 변환하며,
> 그 판단과 콘텐츠를 현실 시장 및 후속 데이터로 다시 검증하는 엔진”

즉, 이 프로젝트는 아래 네 가지를 동시에 가진다.

1. **탐지 엔진**
   - 시장 이상징후 / 뉴스-가격 모순 / 흐름 구조 감지

2. **해석 엔진**
   - 왜 지금 이 주제가 의미 있는지 구조적으로 설명

3. **콘텐츠 엔진**
   - 경제사냥꾼형 영상/스크립트로 변환

4. **검증 엔진**
   - 품질/신뢰도/현실 적합성/미래 적중도를 추적

---

## 1.2 이 프로젝트가 아닌 것

아래로 오해하면 안 된다.

- 단순 뉴스 요약기 아님
- 단순 데이터 대시보드 아님
- 단순 유튜브 스크립트 생성기 아님
- 단순 매매 신호기 아님
- 단순 “정답 찾기” 시스템 아님

이 프로젝트는 본질적으로:

> “무슨 일이 벌어졌는가”보다
> “왜 하필 지금 이 주제를 먼저 말해야 하는가”를 찾는 시스템

이다.

---

# 2. 최종 목적

## 2.1 표면 목적

표면 목적은 다음과 같다.

- 매일 3~4개의 경제사냥꾼형 콘텐츠 후보를 안정적으로 생산
- 각 콘텐츠는 WHY NOW, 구조적 원인, 시장 현실, 리스크를 포함
- 대시보드를 통해 운영자가 빠르게 판단 가능

---

## 2.2 진짜 목적

진짜 목적은 이것이다.

> “경제사냥꾼처럼 남들보다 먼저 말할 수 있는 주제 선점 엔진”

즉:
- 이미 다 알려진 사건을 요약하는 것이 아니라
- 아직 시장이 완전히 가격화하지 않았거나,
- 사람들이 표면적으로만 보고 있는 구조를
- **먼저 포착해서 먼저 말하는 것**

---

## 2.3 왜 이게 중요한가

경제사냥꾼은 단순 해설자가 아니다.
그는 구조를 먼저 보고, 자본 이동을 먼저 읽고, 주제를 먼저 선택한다.

따라서 HOIN Insight의 목적은:

> “정확한 분석을 만드는 것”을 넘어서
> “콘텐츠로 말할 가치가 있는 구조를 먼저 포착하는 것”

이다.

---

# 3. 프로젝트 철학 / 경제사냥꾼 DNA

## 3.1 경제사냥꾼의 본질

경제사냥꾼은:

- 이벤트를 설명하지 않는다
- 구조를 먼저 선택한다
- 왜 지금 이 구조가 말해질 수밖에 없는지 만든다
- 자본 이동 경로를 설계한다
- 마지막에 행동/포지션/시나리오로 연결한다

즉 경제사냥꾼은:

> “무슨 일이 벌어졌는지”를 말하는 사람이 아니라
> “왜 돈이 움직일 수밖에 없는지”를 말하는 사람

이다.

---

## 3.2 경제사냥꾼 DNA 핵심 철학

1. 데이터 자체보다 **데이터의 모순**을 본다
2. 뉴스보다 **뉴스와 시장의 불일치**를 본다
3. 결과보다 **자본 이동 경로**를 본다
4. 단순 예측보다 **조건부 시나리오**를 준다
5. 테마보다 **실제 수혜 구조**를 찾는다
6. 현재 사건보다 **WHY NOW**를 설명한다
7. 확신형 / 조건형 / 초기신호형 콘텐츠를 구분한다

---

## 3.3 경제사냥꾼 콘텐츠 패턴

경제사냥꾼 콘텐츠는 대체로 아래 유형들로 나타난다.

1. 거시 자금 흐름형
2. 정책 자금형
3. 청산/붕괴형
4. 기대 vs 현실 이벤트형
5. 구조 분해형
6. 크로스애셋 연결형
7. 이익 귀속 추적형
8. 연쇄 반응형
9. 시간 기반 패턴형
10. 겉 vs 본질 분리형
11. 진짜 타겟 탐지형
12. 멀티 엔진 합성형
13. 테마주 vs 구조 수혜주 분리형
14. 섹터 로테이션형

---

# 4. 문서 체계 및 고정 원칙

## 4.1 핵심 문서

- `CLAUDE.md`
  - 새 작업자가 가장 먼저 보는 기본 지침
- `docs/HANDOFF.md`
  - 현재 상태 / 최근 완료 / 다음 우선순위
- `docs/dna/ECONOMIC_HUNTER.md`
  - 경제사냥꾼 DNA 정의
- `docs/dna/PIPELINE_RULES.md`
  - 파이프라인 규칙
- `docs/agents/*.md`
  - 에이전트별 설계 문서

---

## 4.2 절대 원칙

1. **ADD-ONLY**
   - 기존 구조를 교체/삭제하지 않고 덧붙이는 방식 우선
2. **SSOT**
   - JSON/문서/대시보드 데이터의 단일 진실 원천 유지
3. **기존 문서 덮어쓰기 금지**
   - ECONOMIC_HUNTER.md 원문 철학 유지
4. **기존 파이프라인 순서 임의 변경 금지**
5. **문체 흉내만 내는 작업 금지**
   - 구조 없는 스타일 카피 금지
6. **로그 없는 완료 보고 금지**
7. **로컬 PASS만으로 완료 판정 금지**
8. **Git push만으로 파이프라인 검증 금지**
   - 반드시 workflow_dispatch 기반 확인

---

# 5. 시스템 구조 (최신 이해 기준)

## 5.1 전체 파이프라인

전체 파이프라인은 4단계다.

1. **Collect**
2. **Intelligence**
3. **Write**
4. **Publish**

핵심 진입점:

- `CollectorRunner.run_all()`
- `DetectorAgent.run()`
- `AnalystAgent.run()`
- `WriterAgent.run()`
- `PublisherAgent.run()`

---

## 5.2 산출물 흐름

기본 흐름은 다음과 같다.

- raw data
→ `today_signal`
→ `today_analysis`
→ `today_stocks`
→ `today_script_long`
→ `docs/today_data.json`

대시보드 SSOT는 최종적으로 `docs/today_data.json`이다.

과거 이력/아카이브는 `docs/topics/index.json` 계열을 통해 관리된다.

---

## 5.3 데이터 레이어

주요 raw 데이터 레이어는 다음과 같다.

- Market
- Macro (US / KR)
- Consensus
- Smart Money (COT)
- Sentiment
- Corporate (DART)
- Put/Call
- 이후 확장된 레이어:
  - Flow
  - Reality validation inputs
  - Quality validation inputs
  - Forward validation logs

---

## 5.4 구조적 장점

- JSON 중심 SSOT
- 에이전트 분리 구조
- 3계층 문장 관리 ([F], [I], [S]) 기반 사고
- Writer 7단 구조
- 후속 확장이 가능하도록 모듈화

---

# 6. 실제로 진행된 개발 진화 과정 (최신까지 포함)

이 부분이 중요하다.
초기 handoff는 v8.x 이전까지만 설명하고 있으나, 실제로는 그 이후 단계가 훨씬 많다.
아래가 최신까지의 핵심 진화 순서다.

---

## 6.1 초기 엔진 고도화 단계

### Detector 지능화 확장 (v7.5)
추가:
- Second-order Deviation
- Signal Persistence
- Signal Death
- Event Trigger Binding

의미:
- 단순 이상치 탐지 → 구조적 이상징후 감지 강화

---

### Flow Layer 도입 (v8.0)
추가:
- 외국인 수급
- ETF Flow
- 이벤트 캘린더

의미:
- anomaly + flow 결합
- 단순 이상징후에서 자금 흐름 관점으로 확장

---

### Flow State 구조화 (v8.1)
상태:
- CONFIRMED_UPTREND
- DISTRIBUTION
- ACCUMULATION
- CONFIRMED_DOWNTREND

의미:
- 상승/하락 자체가 아니라
  “상승 중 털기 / 하락 중 매집” 같은 해석 가능

---

### Flow 입력 정교화 (v8.2)
추가:
- price_strength
- flow_consistency
- state_detail

의미:
- 가격과 수급의 속내를 동시에 읽는 레이어

---

## 6.2 Analyst 고도화 단계

### Analyst Layer 확장 (v1.0)
추가:
- Surface vs Structure
- Chain of Consequence
- Flow Interpreter
- Beneficiary Mapper
- Why Now Hunter

의미:
- 단순 설명 → 경제사냥꾼형 구조 해석

---

### Analyst Decision Engine (v2.0)
추가:
- Action
- Confidence
- Best Scenario
- Multi-Scenario
- Probability
- Kill-Switch
- Trigger Time Condition

의미:
- “설명”에서 “판단”으로 이동

---

### Probability Engine (v2.1)
구조:
- Flow Score
- Price Score
- Event Score
- Consistency Score
→ 가중합 + Sigmoid

의미:
- 느낌 기반이 아니라 수치 기반 확률화

---

## 6.3 Gemini 의존성 감사 및 통제 구조 단계

### Gemini 연동 전수 감사
실제로 확인된 것:
- Detector: 일부 Gemini 의존
- Analyst: 구조 해석에서 Gemini 의존
- Writer: 강한 Gemini 의존
- 일부 추가 보조 영역 존재

핵심 결론:
> HOIN Insight는 Rule Engine + Gemini 추론 레이어의 혼합 구조다.

즉:
- Rule layer: 수집/정규화/점수화/검증
- Gemini layer: 비정형 해석/서사/스크립트 생성

---

### Gemini Control Layer v1.0
추가:
- Gemini Responsibility Map
- Output Contract
- Gemini Wrapper
- Writer Fallback
- Failure Attribution

목적:
- Gemini를 “블랙박스”로 쓰지 않고
  “통제 가능한 모듈”로 전환

---

## 6.4 안정화 / Fail-safe 단계

### 루프 분석 및 차단
문제:
- Gemini contract fail
- retry loop
- pipeline 재진입 의심

조치:
- retry hard limit
- contract fail 시 무한 재시도 차단
- execution guard
- timeout
- 재진입 방지

핵심 결론:
> 파이프라인은 “멈출 수 없는 시스템”이 아니라 “반드시 종료되는 시스템”이어야 한다.

---

### Analyst Fallback / 안정화 레이어
추가:
- fallback analyst
- exception 대신 fallback trigger
- writer input 보호
- minimal quality gate

의미:
- 실패해도 죽지 않고 최소 품질 유지

---

## 6.5 성능 최적화 단계

### Collector 병렬화
추가:
- ThreadPoolExecutor 기반 병렬 수집
- FRED / ECOS / 뉴스 피드 동시 수집

효과:
- Collector 단계 시간 대폭 단축

---

### Smart Cache Guard
기능:
- 동일 날짜 성공 데이터 존재 시 재수집 건너뜀

효과:
- API 낭비 방지
- 속도 개선

주의:
- 이후 검증 단계에서는 캐시가 “가짜 안정성”을 만들 수 있으므로
  cache on/off 검증 분리 필요성 확인

---

## 6.6 Observability / 상태 가시화 단계

### Observability + Quality Control Layer
추가:
- `gemini_health.json`
- `fallback_stats.json`
- `quality_score`
- degraded / critical 상태 판정
- dashboard status 반영

의미:
- 시스템 상태를 감으로 보지 않고 수치로 본다

---

### Metric Calibration
문제:
- fallback_ratio 높아도 NORMAL
- failure 많아도 HEALTHY
- fallback인데 quality 100

조치:
- 임계치 강화
- fallback penalty cap
- 상태 일관성 강화

핵심:
> “가짜 정상 상태” 제거

---

## 6.7 품질 평가 / 품질 검증 단계

### Quality Score v2
추가:
- field completeness
- logical coherence
- numerical evidence
- specificity
- why now strength
- structure quality

효과:
- 점수 분포 복구
- fallback 고득점 차단
- HIGH / MEDIUM / LOW grade 구분

---

### Truth Engine ↔ Quality Feedback Loop
추가:
- failure_reasons
- feedback log
- prompt feedback
- regenerate 정책

의미:
- 점수를 계산만 하는 것이 아니라
  다음 실행에서 더 좋아지게 함

---

### Quality Validation Layer
추가:
- validation_score
- score_trust
- quality_score vs validation_score 교차 검증
- high score low trust 탐지
- action: USE / REVIEW / REGENERATE

의미:
- “몇 점인가”가 아니라
  “그 점수를 믿어도 되는가”를 검증

---

### Validation Hardening
추가:
- stronger trust rules
- claim-evidence alignment
- anti-hallucination checks
- validation_reasons

효과:
- high score여도 claim mismatch면 REVIEW/차단
- “그럴듯한 결과”보다 “근거 있는 결과” 우선

---

## 6.8 현실 시장 검증 단계

### Market Reality Validation
추가:
- 시장 데이터 매핑
- 방향성 검증
- 강도 검증
- reality_score
- final decision = quality + reality

의미:
- 논리적으로 맞아도 시장이 안 움직이면 그냥 통과시키지 않음

---

### Market Intelligence Upgrade
추가:
- 자산별 threshold
- trend 기반 검증
- reality score 0~5
- forward validation logging
- final conservative decision

효과:
- 단일 시점이 아니라 흐름 기반 판단
- 현재 맞음 + 미래 적중도 추적 기반

주의:
- 아직 자산별 threshold는 정적이며 향후 더 정교화 가능

---

## 6.9 콘텐츠 엔진 방향 재정의 단계

이 부분이 매우 중요하다.

초기에는 USE / REVIEW / DROP를
“통과 / 애매 / 폐기”로 해석했으나, 이후 방향이 바뀌었다.

핵심 재정의:

> 우리는 “하루 1개 완벽한 정답”을 찾는 엔진이 아니라  
> “매일 3~4개의 경제사냥꾼형 콘텐츠를 생산하는 엔진”이다.

따라서:
- USE = 확신형 콘텐츠
- REVIEW = 조건형 콘텐츠
- DROP = 초기 신호형 콘텐츠

즉,
> DROP은 폐기가 아니라 “초기 신호 콘텐츠 티어”로 재해석되었다.

---

### Content Tier System
추가:
- TIER_1 = HIGH_CONFIDENCE
- TIER_2 = CONDITIONAL
- TIER_3 = EARLY_SIGNAL

의미:
- 모든 결과를 콘텐츠로 활용
- 단, 톤과 확신 레벨이 다름

톤 가이드:
- TIER_1: 확정형
- TIER_2: 조건형
- TIER_3: 탐지형/조기 신호형

최종 목표:
- 하루 3~4개 콘텐츠 자동 패키징
- MAIN / SECONDARY / EARLY 구성

---

# 7. 현재 프로젝트의 진짜 방향 (매우 중요)

이 프로젝트를 새 채팅에서 이해할 때 가장 중요한 것은
“이 시스템이 지금 무엇을 하려는지”다.

## 7.1 잘못된 이해
- 정답을 하나 찾는 엔진
- DROP이면 버리는 엔진
- 판단만 하고 끝나는 엔진

## 7.2 올바른 이해
이 시스템은:

> “경제사냥꾼처럼 매일 말할 수 있는 주제를 구조적으로 생산하고,
> 그 주제를 확신형 / 조건형 / 초기 신호형으로 나눠서,
> 콘텐츠로 변환하고,
> 동시에 품질/현실/후속 결과로 계속 검증하는 시스템”

즉:
- 판단 자체가 목적이 아니다
- **콘텐츠 선택과 콘텐츠 등급화**가 목적이다

---

# 8. 안티(Antigravity)와 작업하는 방식

## 8.1 작업 방식의 기본 구조

사용자는 직접 코딩하지 않고,
안티(Claude Code / Antigravity)를 외부 구현 에이전트로 사용한다.

즉 작업 흐름은:

1. ChatGPT가 방향/구조/검증 기준을 제안
2. ChatGPT가 **안티 지시서**를 작성
3. 사용자가 그 지시서를 안티에게 전달
4. 안티가 코드 수정/검증/배포/보고 수행
5. 완료보고서를 다시 ChatGPT가 검토
6. 문제 있으면 보완 지시서 다시 작성

---

## 8.2 안티에게 지시할 때의 원칙

- 항상 **지시서 형식**으로 작성
- 한 줄 목표 정의가 있어야 함
- Task 분리가 있어야 함
- 완료 조건 체크리스트가 있어야 함
- 보고서 파일명까지 지정
- “다운로드 폴더에 보고서 저장” 요구 포함
- 실제 로그/증거 첨부 요구
- 추정/미화/정상 동작이라는 말만 쓰는 보고 금지

---

## 8.3 안티 완료보고서를 볼 때의 원칙

반드시 확인할 것:
- 코드 구현과 보고 내용이 일치하는가
- 실제 로그가 있는가
- “정상 동작”이라고만 하고 증거가 없는가
- 테스트 코드만 돌리고 끝낸 건 아닌가
- 실제 파이프라인/실데이터 기준 검증이 있었는가
- 비용/토큰/실행 회수 보고가 과장/축소되지 않았는가

---

## 8.4 안티와 주고받을 때 자주 발생한 문제

1. 테스트 스크립트만 돌리고 “완료”라고 보고
2. 증거 없이 정상 동작 보고
3. 비용을 happy path 기준으로 축소 보고
4. 단일 실행을 과장해서 “완벽”이라고 표현
5. validation/quality 로직을 너무 느슨하게 작성
6. 캐시 때문에 가짜 안정성을 보고하는 경우

따라서 다음 채팅에서도 반드시 유지할 원칙:

> “설명보다 증거,
> 결과보다 로그,
> 느낌보다 수치”

---

# 9. 현재 대시보드/UI에 대한 최신 판단

이 부분도 중요하다.

현재 배포 화면은 실제로 존재하며,
사용자와 같이 점검한 결과 다음 판단이 나왔다:

## 9.1 현재 화면의 본질
현재 화면은:

> “엔진 내부 결과 뷰어”

이지,

> “운영자가 즉시 판단하는 운영 대시보드”

는 아니다.

---

## 9.2 현재 UI의 핵심 문제

- SIGNAL / 강도 / WHY NOW / 수치 나열 위주
- “그래서 오늘 무엇을 콘텐츠로 만들지”가 안 보임
- USE / REVIEW / DROP이 최상단 결론으로 안 보임
- Risk / Kill Switch가 전면에 없음
- Reality vs Claim 비교가 부족
- 로그/내부 상태가 운영자 언어보다 먼저 보임

---

## 9.3 UI 방향 재정의
우리가 만들려는 UI는:

> “엔진 상태판”이 아니라
> “콘텐츠 선택 대시보드”

여야 한다.

즉 앞으로 UI는 아래 구조가 맞다.

1. 오늘의 컨텐츠 패키지
   - MAIN (TIER_1)
   - SECONDARY (TIER_2)
   - EARLY SIGNAL (TIER_3)

2. 왜 지금 말하는가 (WHY NOW)

3. 왜 이 티어인가
   - Quality
   - Validation
   - Reality

4. 실제 시장 상태

5. 리스크 / Kill Switch

6. 최근 적중/검증 이력

즉,
> UI는 “분석 결과 화면”이 아니라
> “오늘 말할 콘텐츠를 고르는 화면”이어야 한다.

---

# 10. 현재 프로젝트 상태 요약 (최신)

## 10.1 완료된 큰 축
- Detector / Flow / Analyst / Probability 고도화
- Gemini 의존성 전수 감사
- Gemini Control Layer
- Fallback / Loop 차단 / Retry 정책
- Performance optimization / 병렬 수집
- Observability / Health / Fallback / Quality
- Metric Calibration
- Quality Score v2
- Truth Engine ↔ Feedback Loop
- Quality Validation
- Validation Hardening
- Market Reality Validation
- Market Intelligence Upgrade
- Content Tier System 방향 확정
- Dashboard는 리팩토링 필요성 확정

---

## 10.2 현재 엔진 수준
현재 엔진은 다음 수준까지 와 있다.

- 생성한다
- 평가한다
- 검증한다
- 현실 검증한다
- 필터링한다
- 미래 검증 로그를 남긴다
- 콘텐츠 티어링 방향을 갖고 있다

즉 현재는:

> “단순 엔진”이 아니라
> “판단 + 콘텐츠 + 검증 시스템”

이다.

---

## 10.3 아직 남은 큰 과제
현재 가장 중요한 남은 과제는 크게 2개다.

### 1) Content Tier System 실제 적용 완료
현재 방향과 규칙은 정리됐지만,
실제 엔진 산출물과 UI에 TIER_1 / TIER_2 / TIER_3가 완전히 반영되어
“하루 3~4개 콘텐츠 패키지”로 동작하는지까지는 추가 확인이 필요하다.

### 2) Dashboard 구조 리팩토링
현재 UI는 운영자용 콘텐츠 선택 대시보드가 아니라
엔진 뷰어에 가까움.
따라서 다음 대화/작업에서 가장 중요한 축은:

> “분석 결과를 보여주는 UI”가 아니라
> “오늘 만들 콘텐츠를 고르는 UI”로 바꾸는 것

이다.

---

===========================================
# [추가] TOPIC SELECTION ENGINE
# 목적: "좋은 이벤트"가 아니라 "말해야 할 주제"를 선택하는 상위 엔진 규칙

## 1. 핵심 정의

토픽 선택 기준은 다음이다.

> “이 이벤트가 아니라
> 이 이벤트로 시장을 설명할 수 있는가”

---

## 2. 선택 순서 (절대 고정)

### Step 1 — 구조 축 생성
먼저 오늘 시장을 설명할 구조 축을 만든다.

예:
- 금리
- 유동성
- 지정학
- 공급망
- 정책
- 자금 흐름

핵심:
> 이벤트를 먼저 고르는 것이 아니라
> 시장을 설명할 축을 먼저 잡는다

---

### Step 2 — 축별 candidate 매핑
각 이벤트를 아래 기준으로 구조 축에 매핑한다.

- 어떤 구조 축에 속하는가
- 설명력이 있는가

---

### Step 3 — WHY NOW 필터
다음 조건을 통과해야 한다.

- 최근 변화인가
- 시장 반응이 시작됐는가
- 아직 완전히 가격 반영이 끝나지 않았는가

셋 중 핵심이 부족하면 MAIN 후보에서 제외한다.

---

### Step 4 — 설명력 평가
다음 질문을 통과해야 한다.

> “이 하나로 오늘 시장을 설명할 수 있는가”

설명력이 약하면 보조 후보 또는 EARLY로 내린다.

---

### Step 5 — 경쟁 토픽 제거
- 같은 구조 축에서 중복 토픽 제거
- 유사 이벤트 중 가장 설명력 높은 것만 남김

---

### Step 6 — 티어 분류
- MAIN / TIER_1: 설명력 강함 + WHY NOW 강함
- SECONDARY / TIER_2: 조건형, 보조 설명 가능
- EARLY / TIER_3: 초기 신호, 아직 본격 가격화 전

---

## 3. 금지 규칙

- 점수만 높다고 MAIN 선정 금지
- 데이터가 많다고 MAIN 선정 금지
- 뉴스 규모가 크다고 MAIN 선정 금지
- entity가 빈약한데 MAIN 선정 금지
- 관련 시장 반응 연결 없이 MAIN 선정 금지

---

## 4. 핵심 한 줄

> “토픽은 점수로 고르는 것이 아니라
> 시장 설명력으로 고른다”


# 11. 지금 이후 올바른 우선순위

새 채팅에서 이어갈 때 우선순위는 아래가 맞다.

## 우선순위 1 — Content Tier System 실제 반영 검증
- USE / REVIEW / DROP를 실제 콘텐츠 티어로 전환
- TIER_1 / TIER_2 / TIER_3 생성 확인
- 하루 3~4개 콘텐츠 패키지 생성 검증

## 우선순위 2 — Dashboard 구조 리팩토링
- Hero = 오늘의 MAIN 콘텐츠
- Secondary / Early Signal 분리
- Quality / Validation / Reality를 “판단 이유”로 재배치
- Risk / Kill Switch 전면화
- 과거 검증 이력 표시

## 우선순위 3 — UI Contract 분리
- 엔진 내부 JSON을 UI가 직접 읽지 않도록
- 운영용 contract layer 별도 구성

## 우선순위 4 — 이후에야 추가 고도화
- Hook 최적화
- 조회수형 제목 시스템
- Topic Selection Intelligence
- 전략 엔진

---

# 12. 새 채팅에서 반드시 유지해야 할 핵심 인식

다음 채팅/다음 모델은 아래를 반드시 이해해야 한다.

1. 우리는 **정답 하나 찾는 프로젝트**를 하는 게 아니다.
2. 우리는 **경제사냥꾼처럼 매일 3~4개 말할 수 있는 구조적 콘텐츠 엔진**을 만드는 중이다.
3. USE / REVIEW / DROP는 더 이상 단순 “통과/폐기”가 아니다.
4. DROP는 버리는 게 아니라 **EARLY SIGNAL 콘텐츠**다.
5. 엔진의 목표는 판단 그 자체가 아니라 **콘텐츠 선택과 콘텐츠 등급화**다.
6. UI는 엔진 상태판이 아니라 **콘텐츠 운영 대시보드**가 되어야 한다.
7. 안티에게는 항상 **지시서 + 증거 중심 완료보고** 체계로 작업시킨다.
8. 모든 작업은 ADD-ONLY, SSOT, 문서 보호 원칙 위에서 진행한다.

---

# 13. 다음 채팅에서 바로 해야 할 질문/작업

새 채팅에서 이어서 바로 하려면 아래 중 하나로 시작하면 된다.

### 방법 A — UI/운영 대시보드 기준으로 시작
“현재 엔진 결과를 TIER_1 / TIER_2 / TIER_3 콘텐츠 패키지로 변환하는 UI contract를 설계해줘”

### 방법 B — 안티 지시서 기준으로 시작
“#087 Content Tier System이 실제 엔진/대시보드에 반영되도록 후속 지시서를 작성해줘”

### 방법 C — 대시보드 구조 리팩토링부터 시작
“현재 대시보드를 운영용 콘텐츠 선택 대시보드로 바꾸는 UI 구조안을 작성해줘”

---

# 14. 최종 한 줄 요약

현재 HOIN Insight는

> “이상징후를 탐지하고,
> 구조를 해석하고,
> 품질과 현실을 검증하고,
> 그 결과를 경제사냥꾼형 콘텐츠 티어로 변환할 준비가 된 시스템”

까지 왔다.

이제 남은 핵심은

> “이 엔진이 만든 결과를
> 운영자가 매일 3~4개의 콘텐츠로 즉시 선택할 수 있게 만드는 것”

이다.


좋다. 네가 올린 인수인계서에 **지금 만든 TASK #102까지 자연스럽게 이어붙인 최종 버전** 만들어준다.
(그대로 복붙해서 덮어쓰면 된다)

---

## 📌 추가 반영 내용

* Event Filter
* Entity Builder 수정
* Context Enricher 재설계
  → **토픽 엔진이 실제로 동작하게 만드는 핵심 보완**

---

# ✅ 최종 추가 블록 (맨 마지막에 붙여라)

````markdown
===========================================
# [추가] TOPIC ENGINE FIX (TASK #102)
# 목적: "뉴스 나열 시스템 → 실제 토픽 선정 엔진" 전환
===========================================

## 1. 현재 문제 정의 (핵심)

현재 엔진 상태:

- 이벤트는 생성됨
- candidate는 생성됨
- LLM 평가도 수행됨

하지만:

1. 중요하지 않은 이벤트가 MAIN으로 선정됨
2. entity가 "Market"으로 뭉개짐
3. 모든 이벤트에 동일 데이터 붙음
4. 이벤트와 시장 반응 연결이 없음

즉:

> 현재 시스템은 "토픽 엔진"이 아니라  
> "뉴스 + 데이터 나열 시스템" 상태

---

## 2. 해결 방향

핵심 수정 3가지:

1. EVENT FILTER 추가
2. ENTITY BUILDER 재설계
3. CONTEXT ENRICHER 재구성

---

## 3. EVENT FILTER

### 목적
의미 없는 뉴스 제거

---

### 필터 조건

다음 중 하나라도 만족해야 candidate 생성:

- 글로벌 영향 가능
- 자산 반응 가능 (금리 / 유가 / 지수 등)
- 섹터 영향 명확
- 대형 기업 이벤트
- 정책 / 지정학 이벤트

---

### 제거 대상

- 단순 사고
- 개인 인터뷰
- 지역 뉴스
- 시장 영향 없는 기사

---

### 핵심 기준

> “이 이벤트 하나로 시장 설명이 가능한가?”

---

## 4. ENTITY BUILDER

### 현재 문제

```json
"entity": "Market"
````

→ 완전 실패

---

### 수정 규칙

* 반드시 실제 entity 사용
* 다중 entity 허용
* fallback 금지

---

### 예

```json
"entity": ["Samsung Electronics", "SK Hynix"]
"entity": ["Iran", "Oil Market"]
```

---

### 핵심 기준

> entity 없으면 LLM 판단은 전부 추측이 된다

---

## 5. CONTEXT ENRICHER (가장 중요)

### 현재 문제

모든 이벤트 동일 데이터 사용

→ 의미 없음

---

### 수정 방향

이벤트 → 관련 자산만 연결

---

### 매핑 규칙

#### GEOPOLITICAL

* Oil
* Gold
* VIX
* Dollar

---

#### SUPPLY_SHOCK

* 해당 기업
* 경쟁사
* 섹터

---

#### POLICY

* Bond
* Dollar
* Growth stocks

---

#### EARNINGS

* 해당 기업
* 동일 섹터

---

---

### 출력 구조

```json
{
  "event": "...",
  "entity": "...",
  "related_market_data": {
    "assets": [
      {"name": "oil", "change": ...},
      {"name": "vix", "change": ...}
    ]
  }
}
```

---

### 핵심 기준

> “이 사건 때문에 이 숫자가 움직였는가?”

---

## 6. VALIDATION RULE

candidate 생성 조건:

1. entity 존재
2. 관련 데이터 존재
3. 이벤트 필터 통과

---

조건 미충족 시:

→ candidate 생성 금지

---

## 7. 기대 결과

수정 후 변화:

* 의미 없는 토픽 제거
* entity 기반 해석 가능
* 이벤트별 시장 반응 연결
* MAIN 토픽 품질 상승

---

## 8. 최종 한 줄

> “이제부터는 뉴스가 아니라
> 시장을 설명하는 이벤트만 살아남는다”

===========================================
END OF TASK #102
================


===========================================
END OF FINAL HANDOFF
===========================================
```

원하면 이걸 내가 바로 **더 압축한 버전**이 아니라,
**안티에게 바로 넘기는 “이식용 절대 앵커 프롬프트” 버전**으로도 다시 정리해줄 수 있다.


===========================================
# [세션 업데이트] 2026-04-23
# 제목: Zero-Keyword Purge + E2E 검증 완료
===========================================

## 1. 이 세션의 핵심 문제 인식

사용자 발언:
> "시스템에서 그 키워드를 하나라도 가지고 있으면 안 될 것 같아"

이 발언이 이번 세션 전체의 방향을 결정했다.

---

## 2. 발견된 하드코딩 오염원

| 파일 | 문제 |
|---|---|
| `src/engine/content_engine.py` | 삼성/유가/금리 등 규칙 딕셔너리 |
| `src/engine/rule_generator.py` | 동일 매핑 규칙 |
| `src/agents/detector.py` | deepseek/호르무즈 가중치, 고정 문구 |
| `src/topic_engine/event_builder.py` | ENTITY_MAP (22개 종목 하드코딩) |
| `src/core/sector_map.py` | SECTOR_STOCK_MAP (수백 개 종목) |
| `src/collectors/contract.py` | 가짜 "삼성전자 5000억" 공시 주입 |
| `src/collectors/auto_generated/collect_value_up_participants.py` | 예시 기업 하드코딩 |

---

## 3. Zero-Keyword Policy 수립 및 조치

> **시스템 코드 내부에 특정 종목·키워드를 단 하나도 허용하지 않는다.**
> 모든 테마·종목 연결은 실시간 데이터와 LLM 추론에서만 나와야 한다.

- 7개 파일 전면 정화 완료
- ENTITY_MAP 삭제 → 정규식 기반 동적 추출로 교체
- sector_map.py → Zero-Keyword 선언 파일로 교체
- 가짜 공시 데이터 삭제

---

## 4. Gemini 안정화

- 모델: `gemini-flash-latest` → **`gemini-1.5-flash-002`**
- TIER 1 재시도: 4회→6회, 대기 최대 12초→60초
- gemini_wrapper.py + gemini_client.py 양쪽 동기화

---

## 5. E2E 검증 결과 (백지→화면 출력)

### 선정된 메인 토픽 변화
- 변경 전: `이재용 발언` (하드코딩 편향)
- 변경 후: **`KOSPI 상방 이상징후 (Z-score: 1.58)`** (순수 데이터 기반) ✅

### 대시보드 화면 확인
- Signal 탭: KOSPI Z-score 1.58, 강도 7.35/10, 7단계 서사 완전 렌더링 ✅
- Market 탭: 환율 1,477.51원, KOSPI 6,475.81, VIX 19.16, WTI $93.36 ✅
- 시스템 점수: 100점 (9/9) ✅

---

## 6. 현재 상태 (2026-04-23)

### ✅ 완료
- Zero-Keyword Policy 전면 시행
- Gemini 안정화
- E2E 검증 통과

### ⚠️ 다음 우선순위
1. ECOS API 복구 (kr_base_rate, kr_cpi)
2. DART 공시 수집 복구
3. TIER 1/2/3 콘텐츠 패키지 UI 반영

---

## 7. 다음 세션 시작 방법

```
안티, HANDOFF 문서 읽어줘. 지금 상태에서 이어서 할게.
파일: /Users/taehunlim/dev/HoinInsight/docs/HANDOFF_FINAL.md
```

===========================================
END OF SESSION 2026-04-23
===========================================
