# IS-98-2 Content Pack Layer

This document defines the **Content Pack Layer**, which aggregates all decision assets into a standardized, upload-ready bundle.

## 1. Assembly Goals

The Content Pack Layer ensures that all relevant context for a topic is stored in one place (`content_pack.json`), facilitating publishing and auditing.

---

## 2. Component Assembly Rules

### 2-1. Shorts Script
- **Priority**: `script_with_citation_guard.json` content.
- **Evidence Selection**: Only **VERIFIED** or **PARTIAL** status evidence is allowed. **UNVERIFIED** evidence must be excluded from the 60s shorts format.
- **Checklist**: Combination of skeleton checklist items and observation targets.

### 2-2. Long Script Sections
- Structurally fixed headers: HOOK, WHAT_CHANGED, EVIDENCE, RISKS, WHAT_TO_WATCH, MENTIONABLES, CLOSE.
- EVIDENCE section allows up to 7 items.
- UNVERIFIED items must use "Observation/Inference" tone (from citation guard).

### 2-3. Decision Card (Key Numbers)
- Automatically extracts numerical patterns (e.g., "$10B", "60% increase") from interpretation units using regex.

---

## 3. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates `data/decision/content_pack.json` without modifying any upstream sensing or interpretive logic.
