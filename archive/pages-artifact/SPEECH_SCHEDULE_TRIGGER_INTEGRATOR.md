# SPEECH_SCHEDULE_TRIGGER_INTEGRATOR.md
# (Economic Hunter – Step 19)

## 0. Purpose

This engine is the **Official Record Keeper**.
It processes Speeches and Scheduled Events.

It does NOT care if the news is "Good" or "Bad".
It cares only if the **Expectation Structure** changed.

> "Did the official confirm the plan (LOCK),
> break the plan (BREAK),
> or simple enforce the deadline (FORCE)?"

---

## 1. Trigger Type Definitions (Strict 3-Type)

Inputs must be classified into exactly one of these types.

### TYPE A: EXPECTATION_LOCK (Confirmation)
- **Definition**: Official explicitly confirms the market's current assumption.
- **Effect**: Eliminates "Uncertainty Risk".
- **Key Phrase**: "We remain committed...", "As planned...", "No change to..."

### TYPE B: EXPECTATION_BREAK (Pivot)
- **Definition**: Official explicitly contradicts the market's current assumption.
- **Effect**: Forces "Repricing".
- **Key Phrase**: "However, due to...", "We must adjust...", "No longer viable..."

### TYPE C: TIMED_FORCE (Deadline)
- **Definition**: A fixed date arrives, forcing action regardless of mood.
- **Effect**: Forces "Execution".
- **Key Phrase**: "Effective Today", "Compliance Deadline", "Expiration".

---

## 2. Rejection Rules (The Filter)

Triggers are **REJECTED** if they rely on:

1.  **Sentiment/Tone**: "He sounded confident" -> **REJECT**.
2.  **Ambiguity**: "We are monitoring the situation" -> **REJECT** (This is Noise).
3.  **Media Framing**: "CNN says this is a signal" -> **REJECT** (Must use primary transcript).
4.  **Opinion**: "Analyst X thinks..." -> **REJECT**.

---

## 3. Output Schema: SPEECH_TRIGGER_CARD

```json
{
  "trigger_id": "UUID",
  "source_type": "CENTRAL_BANK / GOVT_LEADER / SCHEDULE",
  "trigger_class": "EXPECTATION_BREAK",
  "primary_text": "We are pausing the rate cuts immediately.",
  "market_assumption": "Market pricing in 3 cuts.",
  "gap_logic": "Reality (Pause) != Assumption (Cuts)",
  "timestamp": "ISO-8601"
}
```

---

## 4. Mock Examples

### Mock A: Central Bank Pivot (BREAK)
- **Source**: Fed Chair Transcript.
- **Text**: "Inflation has re-accelerated; we are discussing hikes."
- **Assumption**: Market expected Cuts.
- **Class**: `EXPECTATION_BREAK`.
- **Verdict**: **PASS** to Step 2 (Why Now).

### Mock B: Global Forum Consensus (LOCK)
- **Source**: G7 Joint Statement.
- **Text**: "We unanimously agree to ban Russian Uranium imports by 2026."
- **Assumption**: Market doubted unity.
- **Class**: `EXPECTATION_LOCK`.
- **Verdict**: **PASS** to Step 2 (Why Now -> Structural).

### Mock C: Policy Deadline (TIMED FORCE)
- **Source**: US Treasury Schedule.
- **Text**: "Debt Ceiling Suspension expires tomorrow."
- **Assumption**: Market ignoring it (Complacency).
- **Class**: `TIMED_FORCE`.
- **Verdict**: **PASS** to Step 2 (Why Now -> Time Pressure).

---

## 5. Absolute Prohibitions

- **No Psychotherapy**: Do not guess what the speaker "felt".
- **No Translation**: Use the exact words. Do not paraphrase into "Dovish/Hawkish".
- **No Price Prediction**: Do not say "This is bullish". Say "This breaks the Bear Thesis".
