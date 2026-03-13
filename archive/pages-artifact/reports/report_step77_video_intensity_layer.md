# Step 77 완료 보고서: ECONOMIC_HUNTER_VIDEO_INTENSITY_LAYER

## 1. Step 77 설계 요약 (Implementation Summary)

**EconomicHunterVideoIntensityLayer**는 Step 76에서 '경제사냥꾼 영상형'으로 고정된 토픽에 대해 최적화된 제작 강도(Intensity Level)를 결정하는 결정론적(Deterministic) 로직 레이어입니다. 이 레이어는 시간 압박, 트리거 유형, 수혜 및 피해 범위, 그리고 과거 신호 누적 상태를 종합적으로 분석하여 FLASH, STRIKE, DEEP_HUNT 중 단 하나의 레벨을 확정합니다.

### 주요 기능:
- **결정론적 분기**: IF/ELSE 조건만을 사용하여 인간의 개입이나 확률적 요소 없이 강도를 결정합니다.
- **내러티브 변조**: 결정된 레벨에 따라 Narrator가 Hook의 강도를 높이거나(FLASH), 심층 분석 섹션을 추가(DEEP_HUNT)하도록 동작을 변경합니다.
- **파이프라인 통합**: Step 74 → 72 → 75 → 76 → 77로 이어지는 엄격한 순서를 엔진 파이프라인에서 보장합니다.

## 2. Level 분기 규칙 정리 (Branching Rules)

| 레벨 (Level) | 핵심 조건 (Conditions) | 특징 (Characteristics) |
| :--- | :--- | :--- |
| **LEVEL 1: FLASH** | `days_to_event` ≤ 7 AND (Catalyst OR Mechanism) 트리거 | 긴급 알림, 공포/속도 중심, 숏폼 적합 |
| **LEVEL 2: STRIKE** | 구조적 변화 확정 AND 관련 주체 2개 이상 | 표준 경사 포맷, 구조/자금 흐름 분석 |
| **LEVEL 3: DEEP_HUNT** | WHY_NOW 트리거 존재 AND 초기 신호 3회 이상 누적 | 심층 추적, 신뢰 구축, 롱폼 해설 |

## 3. Reject 발생 사례 (Rejection Case)

- **사례**: WHY_NOW 트리거가 명확하지 않거나 (`trigger_id = 0`), 위의 세 가지 레벨 중 어디에도 해당하지 않는 모호한 중요도의 토픽.
- **처리**: "Could not determine Video Intensity Level" 사유와 함께 해당 토픽을 Top-1 제작 후보에서 즉시 배제(Reject)합니다.

## 4. 실제 통과 토픽 예시 (Example: FLASH)

- **토픽**: "미국 연준 긴급 금리 동결 예고 (2026-02-01)"
- **분석 데이터**:
    - `days_to_event`: 5일 (FLASH 조건 충입)
    - `trigger_type`: Scheduled Catalyst (ID:1)
- **결정 결과**:
    - **Level**: `FLASH`
    - **Reason**: Highly urgent trigger (ID:1) with tight deadline (5d)
    - **Narrator 반응**: 🚨 [긴급 FLASH] 접두어 추가 및 Hook 강도 최대화.

## 5. 파이프라인 정상 적용 확인 (Pipeline Status)

`engine.py` 내 파이프라인 순서가 다음과 같이 고정되었음을 확인했습니다:
1.  **Step 74 (Pre-Structural Analysis)**: 초기 시그널 탐지.
2.  **Step 72 (WhyNow Trigger Detection)**: 시드 데이터를 통한 트리거 포착.
3.  **Step 75 (WhyNow Escalation)**: 신규 신호 수동/자동 승격 처리.
4.  **Step 76 (Topic Lock)**: 경제사냥꾼 포맷 고정 여부 판별.
5.  **Step 77 (Video Intensity)**: **[본 단계]** 최종 제작 강도 확정.
6.  **Narrator**: 확정된 레벨을 바탕으로 최종 스크립트 생성.

---
**보고서 종료**
