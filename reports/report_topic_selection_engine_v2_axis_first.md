# 완료 보고서: Topic Selection Engine v2.0 (Axis-First Selection) 통합

## 1. 개요
기존의 "이벤트 중심(Event-first)" 토픽 선정 방식에서 벗어나, 시장의 지배적 흐름인 **"구조적 축(Market Axis)"을 먼저 정의**하고 이에 부합하는 토픽을 우선 선정하는 **Axis-First Selection (v2.0)** 엔진 통합을 완료했습니다.

## 2. 주요 변경 사항

### A. 신규 컴포넌트: Axis Detector ([axis_detector.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/axis_detector.py))
- **역할**: 후보군 평가 전, 시장 데이터(`market_data`)와 후보군 밀도를 분석하여 오늘의 `primary_axis`와 `secondary_axis`를 결정합니다.
- **감지 로직**: 
  - **Intensity (70%)**: 금리, 유가, VIX 등 핵심 자산의 변동성(z-score)과 최근 변화율을 축별로 계산.
  - **Density (30%)**: 현재 수집된 후보군(Candidates)이 어떤 축에 많이 분포되어 있는지 분석.
- **주요 축**: `rates`, `liquidity`, `geopolitics`, `supply_chain`, `policy`, `flow`.

### B. 파이프라인 고도화 ([engine.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/engine.py))
- **Axis Filtering 단계 추가**: 감지된 축(`primary`, `secondary`)에 속하지 않는 후보를 1차적으로 제거합니다.
- **예외 조항**: 축 밖의 후보라도 증거 점수(`evidence_score`)가 0.9 이상인 매우 강력한 신호는 `EARLY` 후보로 유지합니다.
- **출력 데이터 확장**: 최종 결과에 `market_axis`, `filtered_candidates_count`, `remaining_candidates_count`를 포함하여 의사결정 과정을 투명하게 공개합니다.

### C. 티어 결정 규칙 강화 ([topic_ranker.py](file:///Users/taehunlim/dev/HoinInsight/src/topic_engine/topic_ranker.py))
- **MAIN (TIER_1)**: 반드시 `primary_axis` 소속이어야 하며, WHY NOW 게이트 통과, 높은 설명력, 구체적 엔티티/데이터 존재 시에만 선정됩니다.
- **SECONDARY (TIER_2)**: `secondary_axis` 소속이거나, `primary_axis`지만 설명력이 상대적으로 약한 토픽이 배치됩니다.
- **EARLY (TIER_3)**: 축 범위를 벗어나지만 강력한 초기 신호를 가진 토픽이 선정됩니다.
- **축 내부 경쟁**: 동일한 `structure_axis` 내에서 MAIN 후보는 단 1개만 허용하여 정보 중복을 원천 차단합니다.

## 3. 검증 결과 (Evidence)

### 테스트 1: Axis Filtering 확인
- **상황**: 서로 다른 4개 축의 후보 생성. 시장 데이터로 `geopolitics`와 `rates` 축이 감지됨.
- **결과**: `geopolitics`, `rates` 소속 후보는 생존. 무관한 `flow` 축 후보는 탈락. 단, 매우 강한 `flow` 후보는 생존 확인.
- **로그**: `✅ Axis Filtering: 4 -> 3` (의도된 결과)

### 테스트 2: 티어링 규칙 확인
- **상황**: `primary_axis`인 `geopolitics` 후보와 `secondary_axis`인 `rates` 후보가 모두 높은 점수를 기록.
- **결과**: 
  - `geopolitics` 후보 -> **MAIN/TIER_1**
  - `rates` 후보 -> **SECONDARY/TIER_2**
- **근거**: 점수가 높더라도 시장 축의 우선순위에 따라 티어가 결정됨을 확인.

### 테스트 3: 동일 축 중복 제거 확인
- **상황**: `rates` 축에 2개의 강력한 후보가 존재.
- **결과**: 점수가 더 높은 1개만 MAIN으로 선정되고 나머지는 SECONDARY 이하로 강등됨.

## 4. 최종 JSON 구조 (topic_selection.json)
```json
{
  "market_axis": {
    "primary": "geopolitics",
    "secondary": "rates"
  },
  "filtered_candidates_count": 12,
  "remaining_candidates_count": 4,
  "MAIN": { ... "tier": "MAIN/TIER_1", "structure_axis": "geopolitics" ... },
  ...
}
```

## 5. 결론
이제 엔진은 단순한 데이터 매칭을 넘어, **"오늘 시장은 금리로 설명되는가, 아니면 지정학으로 설명되는가?"**를 먼저 스스로 질문하고 그 대답에 맞는 콘텐츠를 선별합니다. 이는 "경제사냥꾼" 페르소나의 일관된 시장 해석력을 보장하는 핵심 기반이 될 것입니다.
