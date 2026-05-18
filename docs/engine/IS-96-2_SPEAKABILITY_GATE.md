# IS-96-2 Speakability Gate

This document defines the **Speakability Gate**, a critical decision layer that determines whether a structural interpretation is ready for narration (content creation).

## 1. Gate Definition

The Speakability Gate evaluates the **INTERPRETATION_UNIT** to decide its propagation status. It ensures that only topics with high-integrity evidence and clear "Why Now" timing are discussed.

### Status Categories

- **READY**: The topic has high-quality pretext and confirmed execution or fundamental backing. It is safe and compelling to speak about.
- **HOLD**: The topic has a valid pretext and flow but lacks the final "confirmation" signal (e.g., earnings pending or policy execution data delayed).
- **DROP**: The topic lacks a sufficient fundamental pretext, or there is a fatal gap between the "narrative" and the "execution" data.

---

## 2. Decision Criteria

### 2-1. READY Criteria
- `pretext_score` >= 0.85
- `confidence_score` >= 0.80
- `evidence_tags` includes (`EARNINGS_VERIFY` OR `KR_POLICY` OR `US_POLICY`)
- `why_now_type` is NOT empty.

### 2-2. HOLD Criteria
- `pretext_score` between 0.70 and 0.85
- `evidence_tags` contains `FLOW_ROTATION` or `GLOBAL_INDEX` but lacks final verification tags.
- Missing `EARNINGS_VERIFY` when the event is scheduled but not yet reported.

### 2-3. DROP Criteria
- `pretext_score` < 0.70
- `policy_execution_gap` > 0.50 (High verbal commitment, zero budget/execution)
- `interpretation_key` is `NARRATIVE_TESTING` without any flow support.

---

## 3. Implementation Specification

### Required Inputs (from INTERPRETATION_UNIT)
- `pretext_score` (from `derived_metrics_snapshot`)
- `policy_execution_gap` (if available)
- `evidence_tags` (list of sensing tags)
- `confidence_score`
- `why_now_type`

### Required Outputs
- `speakability_flag`: `READY` | `HOLD` | `DROP`
- `speakability_reasons`: 3~5 bullet lines explaining the decision.

---

## 4. Governance Rule

This gate is **DETERMINISTIC**. It must not rely on LLM intuition but on the predefined metric thresholds and tag existence checks. This ensures consistency and prevents narrative hallucination.
