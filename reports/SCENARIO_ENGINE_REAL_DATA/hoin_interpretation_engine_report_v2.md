# [REPORT] EVENT INTERPRETATION & SCENARIO ENGINE (REAL DATA VERIFIED)

## 🎯 검증 목적
- 테스트 데이터(Mock)가 아닌 **2026년 4월 22일 실제 시장 데이터** 기반 엔진 작동 확인
- '신호 포착' -> '정상 흐름 매핑' -> '시나리오 생성' -> '이상 여부 판정'의 Full-Chain 검증

---

## 📊 실데이터 분석 결과 (2026-04-22)

### 1. 포착된 핵심 신호 (CORRELATION)
- **토픽**: 안전자산 동반 이탈과 유동성 재배치
- **상황**: 달러(Z:-0.84)와 금리(Z:-0.54)가 동반 하락하며 증시(Z:1.31)로 자금 쏠림
- **분류**: **NORMAL** (현재 매크로 환경에서 합리적으로 설명 가능한 흐름)

### 2. 시장 시나리오 (Scenario Engine)
실제 데이터를 바탕으로 생성된 3가지 합리적 설명입니다.
- **Scenario A (시장 선반영)**: 뉴스가 나오기 전 이미 가격이 반영되어 반대 방향으로 되돌림 가능성 체크
- **Scenario B (매크로 노이즈)**: 지정학 이슈보다 금리/환율 지표가 시장을 압도하는 국면
- **Scenario C (수급 불균형)**: 특정 주체의 포지션 청산으로 인한 흐름

---

## 📂 실데이터 검증 파일 (Clickable Links)

분석에 사용된 실제 데이터와 결과 파일들입니다. 클릭하여 상세 구조를 확인하세요.

- **[종합 팩트 팩]**: [candidates_fact_pack.json](file:///Users/jihopa/Antigravity/hoininsight/data/fact_pack/candidates_fact_pack.json) (해석/시나리오 통합본)
- **[이벤트 해석]**: [event_normal_flow.json](file:///Users/jihopa/Antigravity/hoininsight/data/event_interpretation/event_normal_flow.json)
- **[시나리오 팩]**: [scenarios_today.json](file:///Users/jihopa/Antigravity/hoininsight/data/scenario_pack/scenarios_today.json)
- **[이상징후 결과]**: [anomaly_results.json](file:///Users/jihopa/Antigravity/hoininsight/data/anomaly_overlay/anomaly_results.json)
- **[원본 시장 데이터]**: [market.json](file:///Users/jihopa/Antigravity/hoininsight/data/raw/20260422/market.json)

---

## 🚀 결론: 엔진 고도화 완료
엔진은 이제 숫자의 나열이 아닌, **시장의 맥락(Scenario)**을 이해할 수 있는 핵심 지능을 갖추었습니다. 
특히 **#083-2 하드닝**이 적용되어, 수치적 근거가 없는 토픽은 실데이터 기반으로 자동 보강되거나 탈락되는 품질 게이트가 정상 작동함을 확인했습니다.

---
*Next Stage: #090 (NORMAL/ANOMALY 분리 콘텐츠 생성 로직 설계)*
