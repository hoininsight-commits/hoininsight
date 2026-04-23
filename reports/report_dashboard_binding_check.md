# Report: Dashboard Binding Check (v2.2)

**상태**: [완료]
**작성일**: 2026-04-23
**목표**: 엔진에서 생성된 새로운 필드(Axis, Why Hypothesis 등)가 대시보드 UI에 정상적으로 노출되는지 확인

---

## 1. 최종 JSON 데이터 구조 확인
`docs/today_data.json` 파일을 점검한 결과, 새로운 엔진 레이어의 산출물이 규격에 맞게 포함되어 있음을 확인했습니다.

### JSON 예시 (Contract v2.2)
```json
{
  "top_decision": {
    "topic": "VIX 5일 누적 약세 추세 (-10.00%)",
    "final_action": "STRONG_BUY",
    "content_tier": "TIER_1",
    "why_hypothesis": "Insufficient evidence to determine the cause",
    "mechanism": "No clear event-driven mechanism identified from provided data",
    "confidence": "Low"
  },
  "market_axis": {
    "primary_axis": "liquidity",
    "secondary_axis": "geopolitics"
  },
  "content_pack": {
    "TIER_1": [
      {
        "topic": "VIX 5일 누적 약세 추세 (-10.00%)",
        "why_hypothesis": "Insufficient evidence to determine the cause",
        "mechanism": "No clear event-driven mechanism identified from provided data",
        "confidence": "Low",
        "market_axis": { "primary_axis": "liquidity", "secondary_axis": "geopolitics" }
      }
    ]
  }
}
```

---

## 2. UI 바인딩 점검 결과

### 2.1 신규 노출 항목
- **Market Axis**: 대시보드 Hero 영역 상단에 `AXIS: LIQUIDITY | GEOPOLITICS` 형태로 노출됨.
- **Why Hypothesis Section**: 원고 프리뷰 하단에 별도 섹션으로 추가됨.
- **Causal Mechanism**: 가설 하단에 연한 텍스트로 메커니즘 상세 설명 노출.
- **Confidence Level**: 가설 섹션 우측 상단에 `CONF: Low/Medium/High` 배지 노출.

### 2.2 바인딩 로직 확인 (`docs/index.html`)
- `loadPack()`: `today_data.json` 로드 후 `market_axis`를 상단 바에 바인딩.
- `showContent(c)`: 선택된 카드의 `why_hypothesis`, `mechanism`, `confidence` 필드를 DOM 요소(`h-why`, `h-mech`, `h-conf`)에 매핑.
- **안전 장치**: 데이터가 없을 경우 "No specific hypothesis generated." 등의 기본 문구가 출력되도록 예외 처리 완료.

---

## 3. 검증 요약

| 항목 | 상태 | 확인 결과 |
| :--- | :---: | :--- |
| 오늘의 MAIN 토픽 | **정상** | TIER_1 카드로 자동 선정 및 렌더링 확인 |
| Primary Axis | **정상** | Hero 섹션 상단에 올바른 축 이름 노출 확인 |
| Why Hypothesis | **정상** | LLM이 생성한(혹은 가드가 생성한) 문구 노출 확인 |
| Mechanism | **정상** | 인과 관계 상세 메커니즘 노출 확인 |
| Confidence | **정상** | 분석 신뢰도 배지 노출 확인 |
| No Evidence Guard | **정상** | 뉴스 없는 날 "Insufficient evidence..." 문구 노출 확인 |
| Tier 구분 | **정상** | MAIN/SECONDARY/EARLY 색상 및 라벨 구분 정상 |

---

## 4. 최종 결론

엔진의 최신 안정화 버전(v2.2)이 생성하는 모든 핵심 판단과 근거가 대시보드에 **사람이 읽을 수 있는 형태**로 바인딩되었습니다. 
데이터 소스(`today_data.json`)와 뷰어(`index.html`) 간의 계약(Contract)이 일치하며, 특히 "No Evidence Guard" 상황에서도 UI가 깨지지 않고 의도된 방어 문구를 정상적으로 출력합니다.

---
**작성자**: Antigravity (AI Coding Assistant)
