# TIMING_INVALIDATION_ENGINE.md
# (Economic Hunter – Step 6)

## 0. Purpose

This engine governs the "Lifecycle" of a Locked Topic.

It answers:
- When does a Locked Topic expire?
- What kills a Topic instantly?
- How do we know if the regime has shifted?

A Topic is not forever. It is valid only as long as
the Structural Necessity remains "Unavoidable."

---

## 1. Validity Duration Rule (Time-to-Live)

Every Locked Topic is assigned a strict TTL based on its Trigger Type.

### TYPE A — EVENT Trigger
- TTL: **3 Months**
- Logic: Event impact usually fades or normalizes within a quarter.

### TYPE B — SCHEDULE Trigger
- TTL: **Until Next Schedule Instance**
- Logic: Valid only until the next FOMC, Earnings, or Policy meeting overrides it.

### TYPE C — SPEECH Trigger
- TTL: **14 Days**
- Logic: Market attention span for words is short unless followed by Action (Event).

### TYPE D — SHOCK Trigger
- TTL: **72 Hours (Review required)**
- Logic: Shocks evolve rapidly. Must be re-verified every 3 days.

*Expiration = Automatic Drop (unless re-triggered)*

---

## 2. Invalidation Kill-Switch (Immediate Death)

If ANY of the following occurs, the Topic is **INSTANTLY KILLED** regardless of TTL.

1.  **Thesis Reversal Event**: The "Forced Spender" cancels the budget or project. (e.g., "Government scraps green ship funding")
2.  **Bottleneck Rupture**: A new alternative emerges that bypasses the identified bottleneck. (e.g., "New tech eliminates need for HBM")
3.  **Regulatory Veto**: The "Must-Have" status is legally revoked. (e.g., "Import ban lifted")
4.  **Consensus Saturation**: The narrative becomes front-page news on general media (Signal -> Noise transition).

*Action: Move to "DEAD_TOPIC_LOG" immediately.*

---

## 3. Monitoring Signals (Regime Shift)

Watch for these "Early Warning Signs" of breakdown.

- **Divergence**: Price moves generally up, but our Ticker moves down (-5% vs Sector).
- **Volume Fade**: Discussion volume drops >50% while price stagnates.
- **Narrative Drift**: Market starts discussing "Valuation" instead of "Necessity." (Transition from Structural to Speculative).

---

## 4. Re-Validation Protocol

Expired Topics can be "Resurrected" ONLY if:

1.  A **NEW** Trigger (Step 1) occurs.
2.  The Structural Necessity (Step 3) is confirmed to be **STRONGER** than before.

*Simple extension of timeline is FORBIDDEN.*

---

## 5. Output Format

[LIFECYCLE_STATUS]
- Topic ID:
- Current State: ACTIVE / EXPIRED / KILLED
- Time Remaining (TTL): X Days
- Kill-Switch Status: SAFE / TRIPPED
- Warning Level: LOW / MEDIUM / HIGH

---

## 6. Absolute Prohibitions

- "Buy and Hold Forever" ❌
- "Long-term Investment" ❌
- Ignoring bad news ❌
- Moving goalposts ❌

This engine ensures
we hunt only "Live" targets.
