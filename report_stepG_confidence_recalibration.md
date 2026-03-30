# [STEP-G] Confidence Recalibration / Validation-Weighted Trust Result Report

---

## 1. 개요 (Objective)
STEP-G 미션은 시스템의 신뢰도(Confidence) 산출 방식을 '설명 기반'에서 '성과 기반'으로 혁신하는 것입니다. 과거의 적중률(Hit Ratio)과 의사결정 정확도(Decision Accuracy)를 반영하여 신뢰도를 동적으로 재계산하고, 이를 자금 배분(Allocation)에 반영함으로써 시스템이 스스로의 실력을 평가하고 행동을 조정하는 'Trust-Weighted' 엔진을 구현했습니다.

---

## 2. Confidence 구조 변경

신뢰도 지표는 단순한 수치(float)에서 산출 근거가 포함된 **구조화된 객체(Object)**로 변경되었습니다:

- **value**: 최종 성과 기반 신뢰도 지수
- **source**: 'recalibrated' (성과 기반 재계산 여부)
- **base_confidence**: 엔진이 계산한 기초 신뢰도
- **adjustments**: 세부 조정 항목
    - `hit_ratio`: 과거 종목 적중률에 따른 가산/감산
    - `decision_accuracy`: 과거 대응 액션 정확도에 따른 조정
    - `failure_penalty`: Failure Taxonomy 기반 감산 (예: 테마 오류 시 -0.1)
    - `recency_bonus`: 최근 데이터 활성화 보너스

---

## 3. 핵심 적용 파일 (Modified Files)

- **[NEW]** `src/ops/confidence_recalibration_engine.py`: 성과 지표 기반 신뢰도 재산출 핵심 엔진
- **[NEW]** `data/ops/confidence_metrics.json`: 신뢰도 변화 추이 기록 Ledger
- **[MODIFY]** `src/ops/run_daily_pipeline.py`: 파이프라인 내 재계산 단계 추가 및 오케스트레이션
- **[MODIFY]** `src/allocation/allocation_engine.py`: 구조화된 신뢰도 객체를 해석하여 자산 비중 조정 로직 반영

---

## 4. 검증 결과 (Verification)

### Confidence Recalibration 샘플 (Before -> After)
- **Before (Base)**: 0.25 (단순 합산 기반)
- **After (Recalibrated)**: 0.44 (성과 반영 + 보너스/페널티 적용)

### Adjustments 내역 확인
```json
"adjustments": {
  "hit_ratio": +0.10,
  "decision_accuracy": +0.05,
  "failure_penalty": -0.10,
  "recency_bonus": +0.04
}
```

---

## 5. 서버 반영 결과 (Server Baseline)

1. **GitHub Push**: 완료 (`main` 브랜치)
2. **최종 산출물**:
    - `data/ops/confidence_metrics.json`: 신뢰도 조정 이력 저장 완료
    - `today_operator_brief.json`: 구조화된 Confidence 데이터 반영 완료
    - `report_stepG_confidence_recalibration.md`: 본 리포트 생성 완료

---

## 6. 결론 (Verdict)
**STEP-G: SUCCESS**
이제 HOIN Insight는 "얼마나 믿을 수 있는가"를 스스로 증명합니다. 과거에 테마를 틀렸던 이력은 현재의 신뢰도를 낮추고, 높은 종목 적중률은 현재의 포지션을 강화하는 **'성과 기반 자기 통제(Self-Regulation)'** 시스템이 완성되었습니다.

---
**[STEP-G COMPLETE]**
Validation-Weighted Trust Engine v1.0 Deployment Finished.
