# ECONOMIC_HUNTER_TOPIC_LOCK.md
# (Economic Hunter – Step 24)

## 0. Purpose
This engine is the **Vault**.
It takes the filtered, humanized, and conflict-checked topics (Step 23)
and applies the **Final Seal**.

Once a topic is LOCKED here, it becomes:
1.  **Immutable**: History cannot change it.
2.  **Trackable**: Engine must update its status daily.
3.  **Accountable**: We are now intellectually committed.

---

## 1. Lock Eligibility Rules (The 4 Checks)

A Topic can ONLY enter the Vault if it passes all 4 checks.

1.  **Trigger Validity Check**: Does it have a verified `WHY_NOW_CANDIDATE` (Step 13)?
2.  **Structural Flow Check**: Is the "Forced Spender" clearly identified (Step 3)?
3.  **Bottleneck Check**: Is the "Target" a specific bottleneck, not a general theme?
4.  **Pressure Score Check**: Is the Final Pressure Score (Step 21) **≥ 15**?

*Failure*: If ANY check fails, the topic is **REJECTED** or **DOWNGRADED** to Watchlist.

---

## 2. Kill-Switch Insertion Rule

**No Trade is Forever.**
Every Locked Topic MUST carry a "Self-Destruct Code".

**Rule**:
- The Kill-Switch must be a **Specific Event** or **Data Point**.
- It simply CANNOT be "If price goes down".

*Valid Examples*:
- "If Regulation X is repealed."
- "If Copper Inventory rises above 200k tons."
- "If Competitor Y launches a better chip."

---

## 3. Output Schema: LOCKED_TOPIC_STATE

The final object stored in the database.

```json
{
  "lock_id": "UUID",
  "topic_headline": "US Grid Emergency forces Transformer Supercycle.",
  "lock_timestamp": "YYYY-MM-DDTHH:MM:SS",
  "trigger_origin": {
    "source": "US DOE",
    "event": "Ban on Chinese Imports",
    "date": "2026-01-29"
  },
  "structural_logic": {
    "forced_spender": "US Utilities",
    "bottleneck_entity": "HD Hyundai Electric / Hyosung",
    "capital_magnitude": "High (Existential)"
  },
  "risk_management": {
    "kill_switch_condition": "Repeal of DOE Ban or normalization of lead times.",
    "monitoring_frequency": "Daily"
  },
  "engine_verdict": {
    "pressure_score": 19,
    "confidence_score": 95,
    "status": "ACTIVE_LOCK"
  }
}
```

---

## 4. Mock Examples

### Mock A: LOCKED (Passed)
- **Topic**: "LFP Battery Mandate".
- **Checks**:
  1. Trigger: EU Law Passed (Pass).
  2. Spender: VW/Renault (Pass).
  3. Bottleneck: Cathode Material (Pass).
  4. Score: 18 (Pass).
- **Kill-Switch**: "If EU delays 2027 deadline."
- **Result**: **LOCKED**.

### Mock B: REJECTED (Downgrade)
- **Topic**: "Consumer discretionary rebound".
- **Checks**:
  1. Trigger: Analyst Upgrade (Weak - Fail step 13).
  2. Spender: Consumers (Diffuse - Fail step 3).
  3. Bottleneck: None (Pass).
  4. Score: 12 (Fail < 15).
- **Result**: **DOWNGRADED TO WATCHLIST**. (Not Structural, Cyclic).

---

## 5. Absolute Prohibition
**Never** Lock a topic because it "looks nice".
Lock it only because the **Constitution** says you have no choice.
We are **Slaves to the Logic**.
