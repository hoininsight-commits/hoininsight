# Report: LLM Call Optimization & Structural Enforcement (v2.2)

**상태**: [완료]
**작성일**: 2026-04-23
**목표**: 과도한 LLM 호출(기존 26회+)을 억제하고, "선택 후 설명" 원칙을 코드 수준에서 강제함

---

## 1. 핵심 변경 사항

### 1.1 TopicEvaluator: Heuristic 기반 전환
- **기존**: 모든 후보(10개 이상)를 제미나이로 평가하여 점수화 (호출 횟수 폭증 원인)
- **변경**: **Rule-based Heuristic Evaluator**로 대체.
  - Z-score, Change Intensity를 기반으로 정량적 점수(`explainability_score`) 산출.
  - LLM 호출 횟수: **0회**

### 1.2 호출 위치 및 대상 제한
- **위치**: 모든 필터링, 랭킹, 티어 결정이 끝난 후 **FINAL MAIN** 확정 단계에서만 호출.
- **대상**: `MAIN` 토픽 1개에 대해서만 `Why Hypothesis` 생성을 위해 호출.
- **제한**: `MAX_LLM_CALL = 3` (하루 최대 3회 제한) 적용.

---

## 2. 검증 결과 (10일 리플레이)

### 2.1 호출 횟수 기록 (전/후 비교)

| 날짜 | 시나리오 | 기존 호출 (v2.1) | 최적화 호출 (v2.2) | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| 04-10 | fed_hawkish | 4회 | **1회** | MAIN만 생성 |
| 04-13 | geopolitics | 2회 | **0회** | No Evidence Guard |
| 04-14 | cpi_hot | 4회 | **1회** | MAIN만 생성 |
| 04-15 | tech_rally | 4회 | **1회** | MAIN만 생성 |
| 04-16 | liquidity | 2회 | **0회** | No Evidence Guard |
| 04-17 | supply_chain | 2회 | **1회** | MAIN만 생성 |
| 04-20 | mismatch | 1회 | **0회** | No Evidence Guard |
| 04-21 | stimulus | 3회 | **1회** | MAIN만 생성 |
| 04-22 | rate_cut | 3회 | **1회** | MAIN만 생성 |
| 04-23 | peace_talks | 2회 | **0회** | No Evidence Guard |
| **합계** | - | **27회** | **6회** | **78% 절감** |

### 2.2 호출 로그 예시
```plaintext
--- Replaying Date: 2026-04-14 (cpi_hot) ---
🚀 Topic Selection Engine v2.0 (Axis-First Build) 가동
  🎯 Market Axis Detected: Primary=rates, Secondary=policy
  ✅ Axis Filtering: 3 -> 3
  🧠 Generating Why Hypothesis for FINAL MAIN (Call Count: 1/3)
    ✅ Hypothesis Generated (Total Calls: 1)
  🏆 MAIN Topic: US10Y 상방 변동성 폭발 (Z-score: 3.20) (rates)
```

---

## 3. 핵심 규칙 준수 여부

1.  **candidate 단계 호출 금지**: 준수 (TopicEvaluator 로직 수정 완료)
2.  **MAIN 외 호출 금지**: 준수 (Engine 로직 수정 완료)
3.  **MAX_LLM_CALL 유지**: 준수 (하루 최대 1회 사용됨, 임계치 3회 이내)
4.  **No Evidence Guard 유지**: 준수 (04-13, 04-16 등에서 정상 작동)

---

## 4. 결론

> **"선택은 엔진이 하고, 설명만 LLM이 한다"**

이번 최적화를 통해 시스템의 일관성과 속도가 비약적으로 향상되었습니다. 불필요한 호출을 제거함으로써 API 할당량 소진 위험을 최소화하고, 가장 중요한 `MAIN` 토픽에 대해서만 집중적인 분석을 제공하도록 안정화되었습니다.

---
**작성자**: Antigravity (AI Coding Assistant)
