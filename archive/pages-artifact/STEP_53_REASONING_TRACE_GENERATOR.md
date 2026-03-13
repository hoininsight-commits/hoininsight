# STEP 53 — REASONING TRACE GENERATOR (Constitution)

## 1. 목적 (Goal)
분석 결과가 도출된 과정을 단계별로 투명하게 기록하여, 운영자가 "왜 이 Ticker가 선정되었는지"를 한눈에 파약하고 신뢰할 수 있게 한다.

## 2. Trace 구조 (Chain of Thought)
추론 추적은 다음 5단계를 반드시 포함한다.

1.  **Anomaly (시발점)**: 어떤 수치적/데이터적 이상 징후가 이 분석을 시작했는가?
2.  **Intake (구조적 포착)**: 이상 징후가 어떤 "구조적 변화(Structural Shift)"로 해석되었는가?
3.  **Why Now (시점의 필연성)**: 왜 지금 이 이야기가 중요한가? (데드라인, 임계점 등)
4.  **Reality Validation (병목 검증)**: 실제 현장에서 이 변화가 병목(Bottleneck)으로 작동하고 있는가?
5.  **Ticker Occupancy (대상 확정)**: 해당 병목의 주인은 누구인가?

## 3. 출력 규격 (Trace Schema)
```yaml
reasoning_trace:
  steps:
    - id: 1
      label: "ANOMALY"
      content: "TSMC 2nm 수율 부진 루머 확산 및 장비 반입 지연 포착."
    - id: 2
      label: "STRUCTURAL_SHIFT"
      content: "파운드리 시장의 기술적 우위 독점이 하이엔드 칩 공급망 전체의 병목으로 전이."
    - id: 3
      label: "WHY_NOW"
      content: "차기 아이폰 AP 생산 스케줄 확정 임박 (D-90)."
    - id: 4
      label: "BOTTLENECK"
      content: "High-NA EUV 노광 장비 가동률 및 하이브리드 본딩 수율이 실질적 병목임 확인."
    - id: 5
      label: "TICKER"
      content: "ASML(장비), TSM(제조)을 유일한 병목 해결자로 식별."
```

## 4. 로직 규칙 (Trace Rules)
- **Compactness**: 각 단계는 1문장으로 요약한다.
- **Causality**: 이전 단계의 결과가 다음 단계의 입력이 되는 인과관계를 유지한다.
- **Fact-Based**: 형용사보다는 명사(데이터, 사건) 중심으로 서술한다.
