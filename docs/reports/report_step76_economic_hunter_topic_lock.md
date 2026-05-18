# Step 76 완료 보고서: ECONOMIC_HUNTER_TOPIC_LOCK_LAYER

## 1. 설계 요약 (Implementation Summary)

**EconomicHunterTopicLockLayer**는 정성적인 WHY_NOW 분석 결과를 바탕으로, 해당 토픽이 '영상형 내러티브(경사 스타일)'로 제작되어야 하는지 아니면 '표준 리포트'로 유지되어야 하는지를 구조적으로 결정(Lock)하는 레이어입니다. 이 레이어는 단순히 중요도를 넘어서, 시장의 긴급성과 구조적 행위자의 명확성을 기준으로 제작 포맷을 강제합니다.

### 주요 역할:
- **자동 포맷 고정**: Lock 조건 충족 시 `ECONOMIC_HUNTER_VIDEO` 포맷으로 고정하여 Narrator 분기 강제.
- **파이프라인 질서 확립**: Step 72(Trigger)와 Step 75(Escalation)의 결과를 취합하여 최종 의사결정을 내림.
- **Reject 규칙 강화**: 모호한 시점이나 상태형 언어만 존재하는 토픽을 Top-1 후보에서 배제.

## 2. Lock 조건 판단 예시 (Decision Examples)

### 예시 1: 미국 연준(FED)의 긴급 금리 결정 (LOCK)
- **충족 조건**: A(데드라인 명시), B(중앙은행 행위자), C(행동 강제성)
- **판단 결과**: `topic_lock: true`, `topic_format: "ECONOMIC_HUNTER_VIDEO"`
- **사유**: 특정 행위자(FED)가 피할 수 없는 기한 내에 결정을 내려야 하므로, 리포트보다는 긴급한 내러티브 구조가 적합함.

### 예시 2: 단순 반도체 시장 장기 전망 (NO LOCK)
- **충족 조건**: B(빅테크 관련) - 단일 조건 충족
- **판단 결과**: `topic_lock: false`, `topic_format: "STANDARD_REPORT"`
- **사유**: 시간적 압박(A)이나 즉각적인 행동 강제성(C)이 부족하여 표준 리포트 포맷이 더 적절함.

## 3. Reject된 토픽 예시 (Rejected Topics)

- **상태형 언어 중심 토픽**: "반도체 업황 개선 가능성 전망" (Title), "시장의 우려가 깊어지고 있습니다" (Hook)
  - `Reject 사유`: "전망", "가능성", "우려" 등 상태형 언어만 존재하며 구체적인 구조적 변화 시점이 결여됨.
- **저긴급성 토픽**: 30일 후에도 동일한 내용으로 배포 가능한 거시 담론.
  - `Reject 사유`: 시간적 압박(Condition A)이 없어 경제 사냥꾼 스타일의 '지금 당장(Why Now)' 속성에 부합하지 않음.

## 4. WHY_NOW → Lock → Narrator 연결 흐름

시스템은 아래의 고정된 순서에 따라 최종 리포트를 생성합니다.

1.  **Signal Detection**: 시장 이상 징후 및 시그널 포착.
2.  **Step 74/75 (Pre-Structural & Escalation)**: 초기 신호의 압력 점수 산출 및 자동 승격 여부 판별.
3.  **Step 72 (WHY_NOW Trigger)**: 구체적인 시간적 앵커(Temporal Anchor)를 기반으로 WHY_NOW 트리거 바인딩.
4.  **Step 76 (Topic Lock Layer) [CORE]**:
    - 앞선 단계의 결과물을 취합하여 4대 조건(Time, Actor, Action, Pressure) 검사.
    - 2개 이상 조건 충족 시 `topic_lock` 활성화.
5.  **Narrator Selection**:
    - `topic_lock == true`: **EconomicHunterNarrator** 강제 호출 (Hook-Tension-Hunt-Action 구조).
    - `topic_lock == false`: **Standard Report Narrator** 호출.

---
**보고서 종료**
