# [REPORT] EVENT SCORING TUNING + WHY NOW HARDENING

## 🎯 Task Overview
- **Objective**: Transition from "Event-Capable" to "Event-Dominant" content selection.
- **Key Constraints**: Strict numeric justification for every topic. No abstract "narrative" topics.

---

## 🧩 1. Event Scoring Tuning (#085-2)

### [Updated Bonus Structure]
- **Presence Bonus**: +2.0 (Matched with any event)
- **Type Bonus**:
  - `GEOPOLITICAL` / `SUPPLY_SHOCK`: **+2.0**
  - `POLICY` / `EARNINGS`: **+1.5**
- **Impact Bonus**:
  - `impact_score >= 0.85`: **+2.0**
  - `impact_score >= 0.70`: **+1.5**
- **Multi-Signal Bonus**: **+2.0** (Numeric Anomaly + Event Match)

### [Verification Scoring Audit]
| Target Event | Type | Impact | Bonus Sum | Final Score | Result |
|:---|:---|:---|:---|:---|:---|
| 삼성전자 노조 파업 | SUPPLY_SHOCK | 0.78 | +7.5 | **14.50** | **MAIN** |
| DeepSeek AI 쇼크 | LIQUIDITY | 0.95 | +4.0 | **12.00** | **SECONDARY** |
| 중동 긴장 완화 | GEOPOLITICAL | 0.82 | +5.5 | **12.00** | **SECONDARY** |
| 금리 정책 (Fed) | POLICY | 0.88 | +7.5 | **15.00** | **MAIN** |

---

## 🧩 2. WHY NOW Hardening (#083-2)

### [Validation Rules]
1. **Numeric Presence**: Must contain fixed numbers (`\d+`)
2. **Magnitude/Change**: Must contain keywords (`%`, `bp`, `상승`, `하락`, etc.)
3. **Threshold/Constraint**: Must contain threshold keywords (`이상`, `이하`, `Z-score`, `기준`, etc.)

### [Numeric Injection Logic]
If the LLM provides a narrative reason, the Python engine automatically appends the latest market stats:
> *Ex: "고금리 유지... (us10y(4.292 / Z-score:-0.54) / sp500(7064.01 / Z-score:1.31))"*

---

## 📂 Verification Data (Workspace)

Verification data has been consolidated in the following directory:
`./reports/EVENT_SCORING_TUNING_HARDENING/verification_data/`

- **Fact Pack**: [candidates_fact_pack.json](./verification_data/candidates_fact_pack.json)
- **Event Pack**: [events_today.json](./verification_data/events_today.json)
- **Sentiment Raw**: [sentiment.json](./verification_data/sentiment.json)

---

## 🚀 Next Stage: #087 (Script Quality Gate)
Ready to implement 3-tier script validation to prevent low-score script generation.
