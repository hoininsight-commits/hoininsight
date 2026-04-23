# Report: Why Hypothesis Layer Evidence & LLM Output

**점검 대상**: 2026-04-23 (Dashboard) & 2026-04-22 (Success Case)

---

## 1. CASE #1: 2026-04-23 (Dashboard 현재 상태)

### 1.1 입력 데이터 (Evidence Bundle)
엔진이 수집한 증거 꾸러미입니다.
- **Axis**: `liquidity`, `geopolitics`
- **Market Reaction**: VIX -10.00% (약세 추세), WTI_OIL -2.50%
- **Related Events**: `[]` (뉴스/이벤트 없음)
- **Supporting Assets**: `[]`

### 1.2 처리 결과
- **Status**: **LLM 호출 스킵 (No Evidence Guard)**
- **이유**: `related_events`가 비어 있어, 근거 없는 가설 생성을 방지하기 위해 LLM을 호출하지 않았습니다.
- **최종 출력**: 
  - `why_hypothesis`: "Insufficient evidence to determine the cause"
  - `mechanism`: "No clear event-driven mechanism identified from provided data"

---

## 2. CASE #2: 2026-04-22 (LLM 호출 성공 사례)

LLM이 실제 시장 데이터를 어떻게 해석했는지 보여주는 원본 로그입니다.

### 2.1 입력 데이터 (Prompt Input)
```json
{
  "axis": "rates",
  "market_reaction": { "us10y": -2.10 },
  "related_events": ["Soft Job Data Boosts Expectations for Fed Rate Cut"],
  "event_market_link": ["policy/rates → bond yields → dollar index → growth stocks"],
  "supporting_assets": ["us2y", "usd_krw"],
  "contradictions": []
}
```

### 2.2 LLM 원본 응답 (`data/debug/last_why_raw.txt`)
Gemini API가 생성한 텍스트입니다.
```markdown
- **Why Hypothesis:** The decline in US 10-year bond yields is likely driven by the release of soft employment data, which has increased market expectations for a Federal Reserve interest rate cut.

- **Mechanism:** Soft job data → Increased expectations for a reduction in policy rates → Downward pressure on bond yields (us10y).

- **Confidence:** High

- **Evidence Links:** 
    - policy/rates → bond yields → dollar index → growth stocks
```

### 2.3 최종 파싱 결과
엔진이 UI로 전달한 JSON 데이터입니다.
```json
{
  "why_hypothesis": "The decline in US 10-year bond yields is likely driven by the release of soft employment data, which has increased market expectations for a Federal Reserve interest rate cut.",
  "mechanism": "Soft job data → Increased expectations for a reduction in policy rates → Downward pressure on bond yields (us10y).",
  "confidence": "High"
}
```

---

## 3. 요약
- **현재 대시보드(4/23)**: 뉴스가 없는 날이므로 **할루시네이션 방지 가드**가 작동하여 "근거 부족"으로 안전하게 출력되었습니다.
- **전일(4/22)**: 고용 지표 약화 뉴스가 존재했으므로, **LLM이 인과 관계(Soft Jobs → Rate Cut Hope → Yield Down)를 정확히 구성**하여 가설을 생성했습니다.

---
**작성자**: Antigravity (AI Coding Assistant)
