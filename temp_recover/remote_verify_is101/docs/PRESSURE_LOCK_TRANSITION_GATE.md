# PRESSURE_LOCK_TRANSITION_GATE.md
# (Economic Hunter – Step 13)

## 0. Purpose

This engine acts as the **Up-link**.
It connects the passive `Periscope` (Step 12)
to the active `Why Now Gate` (Step 1).

It decides:
> "Has the pressure accumulated enough
> to justify a formal inquiry today?"

It does **NOT** decide validity.
It only authorizes **Escalation**.

---

## 1. Transition Triggers (The 3 Keys)

A signal can only cross this gate if it triggers one of these keys.

### Key A: Time-Bound Collision
Two previously separate timelines intersect.
- *Example:* "Budget Approval Deadline" coincides with "Critical Supply Shortage Report."
- *Logic:* `Timeline(A) + Timeline(B) < 7 Days`

### Key B: Language Hardening
Ambiguous language shifts to Absolutes.
- *Shift:* "Monitoring" → "Acting"
- *Shift:* "Concerned" → "Unacceptable"
- *Shift:* "Plan" → "Mandate"
- *Logic:* `detect_modality_shift(passive -> active)`

### Key C: Behavioral Confirmation
Words are validated by Money/Action.
- *Observation:* CEO says "Capital discipline" → Capex cut reported in filings.
- *Observation:* Govt says "Energy Security" → Strategic Reserve purchase announced.
- *Logic:* `Speech(A) == Action(A)`

---

## 2. Escalation Thresholds

How a signal climbs the ladder.

### [STATE: NOISE] → [STATE: NOISE] (Permanent)
- If input remains "Opinion", "Rumor", or "Future Hope".
- *Action:* Archive.

### [STATE: PRE-TRIGGER] → [STATE: WHY_NOW_CANDIDATE]
- **Condition**: `D-Day <= 24 Hours` OR `Key B (Hardening)` occurs.
- *Action:* Send to Step 1 immediately.

### [STATE: PRESSURE_BUILDING] → [STATE: WHY_NOW_CANDIDATE]
- **Condition**: Accumulation of `3+ independent data points` OR `Key C (Confirmation)`.
- *Action:* Bundle all points into one Packet and send to Step 1.

---

## 3. Rejection Rules (The Filter)

Signals must be rejected/held if:

1.  **Reversion detected**: Hard language softens back to passive.
2.  **Timeline extension**: Deadline pushed back > 3 months.
3.  **Conflict**: Confirmation data contradicts the speech.

---

## 4. Output Schema: WHY_NOW_CANDIDATE_PACKET

When escalated, the Scanned Signal becomes a Candidate Packet.

```json
{
  "packet_id": "UUID",
  "source_ids": ["Signal_A", "Signal_B"],
  "transition_type": "COLLISION / HARDENING / CONFIRMATION",
  "escalation_reason": "Language shifted from 'Monitoring' to 'Mandating'",
  "urgency_score": "HIGH",
  "timestamp": "ISO-8601",
  "associated_actor": "US Department of Energy"
}
```

---

## 5. Mock Examples

### Transition 1: Time Collision (Type A)
- **Input 1**: US Debt Ceiling Deadline (Schedule).
- **Input 2**: Treasury Cash Balance drops near zero (Data).
- **Event**: Timelines overlap within 48h.
- **Output**: `ESCALATED to Step 1`

### Transition 2: Language Hardening (Type B)
- **Input**: Fed Chair Speech.
- **Shift**: Last month: "Data dependent". This month: "We will not hesitate."
- **Event**: Modality shift to Absolute.
- **Output**: `ESCALATED to Step 1`

### Transition 3: Behavioral Confirmation (Type C)
- **Input 1**: Tech CEO says "AI Sovereignty is key" (Speech).
- **Input 2**: Company files permit for 1GW Power Plant (Action).
- **Event**: Action confirms Speech.
- **Output**: `ESCALATED to Step 1`

---

## 6. Strict Definition
This Gate **does not know** if the topic is good or bad.
It only knows that **something changed state**.
