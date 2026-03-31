# [STEP-C] Decision Authority & Provenance Lock Result Report

---

## 1. 개요 (Objective)
STEP-C 미션은 모든 의사결정(Decision) 데이터에 대해 "출처(Source)", "근거(Reason)", "증거(Evidence)"를 강제하는 구조적 잠금을 구현하는 것입니다. 이를 통해 시스템의 투명성을 확보하고 "가짜 정상 상태(Fake Normal)"를 방지합니다.

---

## 2. 변경된 구조 (Provenance Structure)

모든 주요 의사결정 필드가 단일 값에서 아래와 같은 구조화된 객체로 변경되었습니다:

```json
{
  "action": {
    "value": "WATCH",
    "source": "fallback",
    "reason": "Missing or zero action → fallback applied",
    "evidence": []
  },
  "confidence": {
    "value": 0.25,
    "source": "fallback",
    "reason": "fallback base confidence applied",
    "evidence": ["momentum_score=0.51", "early_score=0.8", "pressure=0.47"]
  }
}
```

---

## 3. 핵심 적용 파일 (Modified Files)

- **[NEW]** `src/ops/decision_provenance_engine.py`: 출처 관리 및 무결성 계산 핵심 엔진
- **[MODIFY]** `src/ops/investment_decision_engine.py`: 투자 결정 근거 및 증거 데이터 추가
- **[MODIFY]** `src/ops/risk_engine.py`: 리스트 점수 및 레벨 산출 근거 명시
- **[MODIFY]** `src/allocation/allocation_engine.py`: 자산 배분 로직의 출처 추적 기능 추가
- **[MODIFY]** `src/ops/run_daily_pipeline.py`: 파이프라인 최종 단계에서 Provenance 적용 및 무결성 체크 통합

---

## 4. 무결성 검증 결과 (Decision Integrity)

현재 서버 데이터 기준 무결성 상태는 다음과 같습니다:

- **상태**: `DEGRADED`
- **Fallback 비율**: `0.33` (33%)
- **엔진 필드 수**: 4
- **Fallback 필드 수**: 2

> [!NOTE]
> 일부 필드에서 Fallback이 발생했으나, 이는 시스템이 "N/A"를 숨기지 않고 명확히 "출처(Fallback)"를 밝히고 있음을 의미합니다.

---

## 5. 서버 반영 및 최종 산출물 (Server Baseline)

1. **GitHub Push**: 완료 (`main` 브랜치)
2. **최종 산출물**:
    - `data/ops/today_operator_brief.json`: 구조화된 Provenance 데이터 반영 완료
    - `data/ops/decision_evidence_chain.json`: 전체 근거 체인 저장 완료
    - `report_stepC_decision_provenance.md`: 본 리포트 생성 완료

---

## 6. 결론 (Verdict)
**STEP-C: SUCCESS**
시스템은 이제 단순한 "표시" 기능을 넘어 "왜 그렇게 판단했는가"를 설명할 수 있는 구조적 기틀을 갖추었습니다.

---
**[STEP-C COMPLETE]**
Decision Provenance Engine v1.1 Deployment Finished.
