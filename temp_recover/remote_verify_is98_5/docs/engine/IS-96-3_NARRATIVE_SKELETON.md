# IS-96-3 Narrative Skeleton Layer

This document defines the **Narrative Skeleton Layer**, which converts interpreted and gated topics into a structured, deterministic script skeleton for content production.

## 1. Purpose

The Narrative Skeleton serves as the "logical blueprint" for a broadcast or report. It ensures that the core reason for the topic (Why Now), the supporting evidence, and the necessary caution points (Checklist) are consistently presented without relying on LLM creativity for the structure.

---

## 2. Input Dependencies

The skeleton generation requires outputs from:
1. **IS-96-1**: `INTERPRETATION_UNIT` (Context, Key, Narrative, Metrics)
2. **IS-96-2**: `Speakability Results` (Flag, Reasons)

---

## 3. Output Schema: NARRATIVE_SKELETON

The output is a standardized dictionary with the following fields:

| Field | Content | Requirement |
|---|---|---|
| **HOOK** | 1-2 lines summarizing the immediate urgency. | Mandatory (READY/HOLD) |
| **CLAIM** | 1 sentence stating the structural shift occurring. | Mandatory (READY/HOLD) |
| **EVIDENCE_3** | 3 bullets of data-backed proof points. | Exactly 3 (READY/HOLD) |
| **CHECKLIST_3** | 3 bullets of follow-up validation items. | Exactly 3 (READY/HOLD) |
| **WHAT_TO_AVOID** | 1-2 bullets of common misinterpretations or risks. | Mandatory (READY/HOLD) |
| **HOLD_TRIGGER** | Conditions to watch for state transition. | Mandatory (HOLD only) |
| **DROP_NOTE** | Reason for rejection. | Mandatory (DROP only) |

---

## 4. Deterministic Transformation Rules

- **READY Status**: Generates a full skeleton focused on "Execution Verification".
- **HOLD Status**: Generates a full skeleton focused on "State Monitoring" with a distinct "Watch Next" tone.
- **DROP Status**: Returns only the failure reason (DROP_NOTE).

---

## 5. Governance Rule (Strict)

- **No Hallucination**: All evidence points MUST be derived from the sensing tags (`KR_POLICY`, `GLOBAL_INDEX`, etc.) present in the `INTERPRETATION_UNIT`.
- **No Stock Names**: The skeleton must speak only of sectors, indices, and flow patterns.
- **Deterministic**: Templates are used for concatenation; no LLM is involved in this layer's primary construction.
