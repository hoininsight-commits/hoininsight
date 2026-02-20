# TRIGGER_CONFLUENCE_ENGINE.md
# (Economic Hunter – Step 2)

## 0. Purpose

This engine detects whether
multiple independent signals are converging
toward the same economic direction.

Single triggers are insufficient.
Only converged pressure creates Topics.

---

## 1. Input Definition

Inputs are ONLY:
- PASS or HOLD results from WHY_NOW_GATE_v2

REJECT inputs are forbidden.

Each input must include:
- Trigger Type (EVENT / SCHEDULE / SPEECH)
- Core Sentence
- Timestamp
- Affected Actor (implicit or explicit)

---

## 2. Confluence Definition

A valid Confluence requires:

### Condition A — Multi-Source
At least 2 different Trigger Types
(e.g., SPEECH + SCHEDULE, EVENT + DATA)

Same-type repetition is invalid.

---

### Condition B — Directional Alignment

All Triggers must answer the same hidden question:

> “What decision is becoming unavoidable?”

If decisions differ → NO CONFLUENCE

---

### Condition C — Time Compression

Triggers must occur within:
- 14 days (macro)
- 7 days (policy / earnings)
- 72 hours (shock)

Outside window → INVALID

---

## 3. Conflict Resolution Rule

If Triggers point to opposing actions
(e.g., tighten vs loosen, invest vs delay):

→ FORCE HOLD
→ No Topic allowed

Ambiguity is NOT alpha.

---

## 4. Pressure Scoring (Non-Numeric)

Each Trigger adds one of:

- PRESSURE_ADD
- PRESSURE_CONFIRM
- PRESSURE_ACCELERATE

If total pressure < 2 → HOLD

---

## 5. Output State

[CONFLUENCE_RESULT]

- Status:
  - CONFLUENCE_CONFIRMED
  - WEAK_CONFLUENCE
  - NO_CONFLUENCE

- Unified Question:
  - “Because of X, Y, Z,
     who must now decide what?”

- Trigger List (IDs only)

Only CONFLUENCE_CONFIRMED
may proceed to Step 3 (Structural Engine).

---

## 6. Absolute Prohibitions

- Topic naming ❌
- Sector labeling ❌
- Company inference ❌
- Price / forecast ❌

This engine does NOT explain.
It only detects convergence.
