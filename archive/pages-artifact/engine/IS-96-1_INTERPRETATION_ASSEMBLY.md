# IS-96-1 Interpretation Assembly Layer

This document defines the logic for the **Interpretation Assembly Layer**, which translates multi-axis data signals and derived metrics into structural "Why Now" interpretations.

## 1. WHY_NOW_INTERPRETATION Logic (Add-only)

The engine determines the temporal urgency (Why Now) by examining the alignment between **Strategic Intent** and **Capital Execution**.

| Interpretation Level | Condition | Interpretation Key |
|---|---|---|
| **L4: Structural Origin** | `POLICY` + `PRETEXT` + `FLOW` (Strong alignment) | `STRUCTURAL_ROUTE_FIXATION` |
| **L3: Market Validation** | `EARNINGS` + `FLOW` + `PRETEXT` (Post-event confirmation) | `FUNDAMENTAL_RE-RATING` |
| **L2: Expectation Build** | `GLOBAL_INDEX` + `POLICY` (Anticipatory flow) | `PASSIVE_FRONT_RUNNING` |

---

## 2. Signal Mapping Rules

### 2-1. PRETEXT_SCORE → INTERPRETATION Mapping
Maps the quality of the "Pretext" (justification for capital inflow) to internal interpretation states.

| Pretext Score Range | Evidence Tags | Interpretation Result |
|---|---|---|
| 0.85 - 1.00 | `PRETEXT_VALIDATION`, `KR_POLICY` | **"Authentic Structural Reform"**: Capital flow is justified by long-term roadmap changes. |
| 0.70 - 0.84 | `PRETEXT_VALIDATION`, `EARNINGS_VERIFY` | **"Performance-Backed Re-rating"**: Pretext is confirmed by bottom-line reality. |
| < 0.70 | `PRETEXT_VALIDATION` | **"Narrative Testing"**: Pretext is present but lacks structural/fundamental depth. |

### 2-2. FLOW_ROTATION → CAUSE Mapping
Explains *why* capital is moving between sectors using IS-95-1 data points.

| Flow Pattern | Supporting Signal | Root Cause Interpretation |
|---|---|---|
| Value to Growth | `US_POLICY` (Tech/Chips) | **"Growth Resumption"**: Policy-driven demand cycles. |
| Large to Mid | `KR_POLICY` (Ecosystem) | **"Ecological Deepening"**: Capital spreading to sub-suppliers/infrastructure. |
| Defensive to Cyclical | `GLOBAL_INDEX` (Rebalancing) | **"Global Beta Exposure"**: Passive-led risk-on regime. |

---

## 3. INTERPRETATION_UNIT Schema

The engine outputs the interpretation in the following standardized format (JSON representation).

```json
{
  "schema_version": "is-96-1-interpretation-v1",
  "interpretation_id": "string (UUID)",
  "as_of_date": "string (YYYY-MM-DD)",
  "target_sector": "string (Sector ID)",
  "interpretation_key": "enum [STRUCTURAL_ROUTE_FIXATION, FUNDAMENTAL_RE-RATING, ...]",
  "why_now_type": "enum [Schedule-driven, State-driven, Hybrid]",
  "confidence_score": "float (0.0 - 1.0)",
  "evidence_tags": [
    "KR_POLICY",
    "GLOBAL_INDEX",
    "FLOW_ROTATION",
    "PRETEXT_VALIDATION",
    "EARNINGS_VERIFY"
  ],
  "structural_narrative": "string (Human-readable summary of the 'Why Now' interpretation)",
  "derived_metrics_snapshot": {
    "pretext_score": "float",
    "policy_commitment_score": "float",
    "rotation_signal_score": "float"
  }
}
```

---

## 4. Governance Rules (Strict)

- **Sector Focus**: This layer MUST NOT identify individual stocks. It operates only on sectors, role-flows, and global indices.
- **Add-only Integration**: This document serves as a reference for the Interpretive Engine. It does not modify the sensing logic (IS-95) or the constitutional trigger logic.
- **Tag Integrity**: Every interpretation unit MUST reference at least two unique tags from the IS-95-1 sensing layer to maintain accountability.
