# WHY_NOW_GATE_S47.md
# (Economic Hunter – Step 47)

## 0. Mission
This engine is the **Judge**.
It takes the `PRESSURE_CLUSTER` (status: IGNITE) from Step 46 and decides if it is actionable **Today**.

It answers:
> "We have pressure. But do we have a **Trigger**?"
> "If we wait 24 hours, does the opportunity vanish or get expensive?"

It enforces **Immediacy**.
Pressure without a Trigger is just anxiety.
Pressure + Trigger = **Action**.

---

## 1. The 3 Gates (Strict)

A Cluster must pass ALL THREE gates to generate a `WHY_NOW_CARD`.

### Gate 1: Time Finality (The Clock)
*Is there a fixed point in time acting as a fulcrum?*
- **PASS**: "Effective Date: Jan 1", "Meeting Date: Tomorrow", "Expiration: Tonight".
- **FAIL**: "Soon", "In the coming months", "Eventually".

### Gate 2: Irreversibility (The Law)
*Can the actor change their mind?*
- **PASS**: Signed Law, Physical Disaster, Sold-out Inventory.
- **FAIL**: Proposal, Draft, Rumor, Forecast.

### Gate 3: Forced Action (The Mechanism)
*Does the event chemically force a reaction?*
- **PASS**: "If X happens, Y *must* happen (Physics/Law)."
- **FAIL**: "If X happens, Y *might* happen (Sentiment)."

---

## 2. The Critical Sentence Test

The Engine must attempt to write the **Critical Sentence**:
> **"As of [Time], [Event] has mandated [Action] by removing [Alternative]."**

- If this sentence cannot be written clearly -> **REJECT**.
- If it relies on "Likely" or "Probably" -> **REJECT**.

---

## 3. Output Schema: WHY_NOW_CARD (YAML)

```yaml
why_now_card:
  card_id: "UUID"
  cluster_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Gates
  gates:
    time_finality: "PASS (Jan 1 Deadline)"
    irreversibility: "PASS (Signed CFR 49)"
    forced_action: "PASS (Non-compliance = Fines)"
    
  # The Logic
  critical_sentence: "As of Jan 1st, the DOE Ban has mandated domestic procurement by removing the Chinese supply option."
  
  # The Verdict
  status: "PASS" # PASS / HOLD / REJECT
  risk_factors: []
```

---

## 4. Mock Examples

### Mock 1: PASS (The Perfect Storm)
- **Cluster**: Transformers (Ban + Shortage).
- **Gate 1**: Jan 1 Deadline (Pass).
- **Gate 2**: Law Signed (Pass).
- **Gate 3**: Utilities must buy or go dark (Pass).
- **Sentence**: "As of Jan 1, the Ban mandates domestic buying by removing imports."
- **Result**: **PASS**.

### Mock 2: REJECT (The Soft Catalyst)
- **Cluster**: Rate Cut Speculation.
- **Gate 1**: Next Meeting? (Pass).
- **Gate 2**: Decision made? No (Fail).
- **Gate 3**: Forced? No (Fed can pause).
- **Result**: **REJECT**. (Wait for the Decision).

---

## 5. Final Report
Step 47 is the filter that separates "News" from "Triggers".
News is information.
Triggers are **Commands**.
