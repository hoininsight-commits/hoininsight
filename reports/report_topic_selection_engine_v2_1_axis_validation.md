# 완료 보고서: Axis Validation Layer (v2.1) 통합

## 1. 개요
토픽 셀렉션 엔진 v2.0의 축 감지(Axis Detection) 기능을 보완하여, 단순히 데이터 수치만으로 축을 결정하는 것이 아니라 **"실제 시장에서 유효하게 작동하는 축인지"**를 다각도로 검증하는 **Axis Validation Layer (v2.1)**를 통합 완료했습니다.

## 2. 검증 레이어 상세 구현 ([axis_detector.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/axis_detector.py))

### A. 3단계 검증 필터 (v2.1)
1. **Reaction Check (반응성)**: 해당 축과 연결된 자산(Assets) 중 하나 이상에서 임계치 이상의 변동성(z-score > 1.2)이나 최근 변화(chg_5d > 0.8%)가 포착되는지 확인합니다.
2. **Direction Check (방향성)**: 축 내 자산 간의 움직임이 경제 논리에 맞는지 검증합니다.
   - 예: `rates` 축에서 `us10y`가 상승할 때 `us2y`가 하락하는 등의 모순이 발생하면 검증 탈락.
   - [v2.1] `CONSISTENCY_RULES`를 도입하여 축별 자산 상관관계 정의.
3. **Timing Check (시급성)**: 최근 1~2일 내의 변화인지를 z-score 기반으로 판단하여 과거 데이터의 잔상이 축으로 오인되지 않게 합니다.

### B. 선정 규칙 고도화
- **검증 기반 가중치**: 검증을 통과하지 못한 축은 강도(Intensity)가 아무리 높더라도 최종 점수 산정 시 **80% 감점(x0.2)** 처리되어 Primary Axis 선정에서 배제됩니다.
- **Confidence 지표**: 선정된 `primary_axis`가 검증을 통과하지 못한 Fallback 케이스인 경우 `confidence: LOW`로 표시하여 운영자에게 경고를 보냅니다.

## 3. 검증 결과 (Evidence)

### 테스트 1: 방향성 모순(Direction Inconsistent) 감지
- **상황**: `us10y`는 급등하나 `us2y`는 급락하는 비논리적 상황 시뮬레이션.
- **결과**: `rates` 축의 `direction_consistent`가 `False`로 판명되며 검증 탈락 확인.

### 테스트 2: 낮은 반응성(No Reaction) 필터링
- **상황**: 미미한 자산 변화만 있는 경우.
- **결과**: `reaction` 체크에서 탈락하며 해당 축이 선정되지 않음.

### 테스트 3: 검증 성공 및 신뢰도
- **상황**: 금리 상승, 달러 강세 등 논리적으로 일치하는 자산 반응 포착.
- **결과**: `passed: True`, `confidence: HIGH`로 `rates` 축이 Primary로 선정됨.

## 4. 출력 데이터 구조 (topic_selection.json)
```json
{
  "market_axis": {
    "primary": "rates",
    "secondary": "geopolitics",
    "confidence": "HIGH",
    "axis_validation": {
      "rates": {
        "passed": true,
        "reaction": true,
        "direction_consistent": true,
        "recent": true
      },
      ...
    }
  },
  ...
}
```

## 5. 결론
이제 엔진은 **"데이터가 튀는 곳"**을 찾는 수준을 넘어, **"시장 논리가 작동하는 지점"**을 검증하여 축을 선정합니다. 이를 통해 노이즈에 의한 잘못된 테마 선정을 방지하고, 경제사냥꾼의 분석 신뢰도를 획기적으로 높였습니다.
