# OUTPUT_FORMAT_GATE_v1.0

## 0. PURPOSE
Standardize Content Topic Gate output for consistent reporting and automation.

---

## 1. REQUIRED OUTPUT FIELDS (ORDER LOCKED)
1) Title
2) Question
3) Why people are confused
4) Key reasons (2~3 bullets)
5) Numbers (0~3 items; optional)
6) Risk (1 line)
7) Confidence (LOW/MEDIUM/HIGH; content-worthiness)
8) Handoff flag to Structural (boolean)
9) Handoff reason (string)
10) Source candidates (ids)

---

## 2. EXAMPLE (STRUCTURE ONLY)
Title: ...
Question: ...
Why people confused: ...
Key reasons:
- ...
- ...
Numbers:
- label: ..., value: ..., unit: ...
Risk: ...
Confidence: ...
Handoff to Structural: true/false
Handoff reason: ...
Source candidates: [..]

---

## 3. FORBIDDEN CONTENT
- L-levels
- Z-scores
- Anomaly logic citations
- Theme leader lists
- Structural "Insight Script" blocks
