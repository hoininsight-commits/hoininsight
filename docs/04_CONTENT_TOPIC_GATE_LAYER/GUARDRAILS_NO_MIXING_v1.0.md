# GUARDRAILS_NO_MIXING_v1.0 (STRICT)

## 0. PURPOSE
Prevent the failure mode:
- Topic says "Tesla FSD"
- Evidence says "Monetary Tightening (rates/gold/silver)"
- Leaders map to banks
=> Mixed engines / invalid output.

This document enforces separation between:
- Structural Engine output
- Content Topic Gate output

---

## 1. GUARDRAIL RULES (MUST ENFORCE)

### G1 — No L-Levels in Gate
Gate output must NOT contain:
- "L2", "L3", "L4"
- "level"
- "anomaly_level"

### G2 — No Z-score in Gate
Gate output must NOT contain:
- "z_score"
- "zscore"
- "sigma"
- "stddev"

### G3 — No Legacy Leader Mapping in Gate
Gate output must NOT contain:
- theme leader lists (e.g., KB금융, JPM, etc.)
- "leaders", "theme_leaders", "related_stocks"

### G4 — Topic/Evidence Alignment
If the Gate topic includes a named entity (company/sector/event),
then Gate evidence_refs must include at least one corresponding reference.
If not:
- auto re-pick TOP 1 from ranked candidates
OR
- rewrite topic into a non-entity macro question.

### G5 — No Structural Script Template Reuse
Gate output must not include:
- "Insight Script"
- Structural narrative templates
- Structural "WHY_NOW + Level + Evidence" formats

Gate uses its own minimal output format only.

---

## 2. REQUIRED TESTS (PASS/FAIL)
A build/run is FAIL if:
- Any of G1~G5 is violated
- Gate output missing (Gate must always output TOP 1)
- Candidates < 3

---

## 3. ENFORCEMENT LOCATION
Guardrails should be enforced at:
- Gate output builder (string/field checks)
- Gate output schema (fields absent by design)
- CI test (json scan for forbidden keys/strings)
