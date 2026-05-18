# IS-97-2 Tone & Persona Lock Layer

This document defines the **Tone & Persona Lock Layer**, which standardizes the communicative stance of the HOIN Engine's outputs.

## 1. Purpose

The Tone & Persona Lock Layer ensures that every topic is voiced with a consistent "authority" and "personality" regardless of the underlying data source. It prevents narrative drifting by locking the persona and tone BEFORE script generation.

---

## 2. Deterministic Mapping Rules

### 2-1. Persona Logic (Based on Root Cause)
- **POLICY_ANALYST**: If interpretation tags include `KR_POLICY` or `US_POLICY`.
- **ECONOMIC_HUNTER**: If interpretation tags include `FLOW_ROTATION` or `GLOBAL_INDEX`.
- **MARKET_OBSERVER**: If interpretation tags include `EARNINGS_VERIFY` or `PRETEXT_VALIDATION`.

### 2-2. Tone Logic (Based on Content Mode & Status)
- **ASSERTIVE**: `content_mode` == "SHORT" and `speakability` == "READY".
- **EXPLANATORY**: `content_mode` == "LONG" and `speakability` == "READY".
- **OBSERVATIONAL**: `speakability` == "HOLD".
- **CAUTIONARY**: If `policy_execution_gap` > threshold or `confidence_level` == "LOW".

### 2-3. Confidence & Authority
- **HIGH Authority**: `content_mode` in ["SHORT", "LONG"] and `pretext_score` >= 0.85.
- **MEDIUM Authority**: All others.
- **HIGH Confidence**: `pretext_score` >= 0.8 and `execution_gap` <= 0.2.
- **LOW Confidence**: `speakability` == "HOLD".

---

## 3. Implementation Policy

- **No LLM**: All assignments are based on if-else logic using structured metadata.
- **Lock First**: This metadata must be generated and saved to `data/decision/tone_persona_lock.json` before any natural language generation starts.

---

## 4. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates new decision assets without modifying existing sensing or interpretive logic.
