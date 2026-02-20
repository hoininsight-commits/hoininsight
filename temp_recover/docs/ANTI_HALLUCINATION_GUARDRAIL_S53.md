# ANTI_HALLUCINATION_GUARDRAIL_S53.md
# (Economic Hunter – Step 53)

## 0. Mission
This engine is the **Polygraph**.
It scans the entire pipeline (Steps 45-52) and verifies every **Factual Claim**.

It answers:
> "Did we just make this up?"
> "Is that '5-Year Backlog' a real number or a creative guess?"

It enforces **Reality**.
In the Hunter Engine, a single hallucination is a **Systemic Failure**.
We deal in hard truths.

---

## 1. Verification Rules (Strict)

A claim is valid ONLY if it satisfies these 3 rules.

### Rule A: The Source Token Rule
*Every number must have a father.*
- **Criteria**: Every date, percentage, or currency figure must be tagged with a `SOURCE_TOKEN`.
- **Allowed Sources**: Primary Docs (SEC, Gov, Court), Direct Transcripts, Raw Inventory Data.
- **Forbidden Sources**: "Analysts expect...", "Market rumors...", "AI Inference".

### Rule B: The Adjective Ban (Re-Verification)
*Kill the fluff.*
- **Criteria**: Find all adjectives (e.g., "Massive", "Incredible", "Huge").
- **Action**: Replace with numbers or **REJECT**.
- *Example*: Change "Massive Backlog" to "Backlog: $500M (source: 10-Q)".

### Rule C: The "Now" Conflict
*Does this fact contradict a more recent one?*
- **Criteria**: Cross-check Step 45 (Intake) for more recent events that might invalidate the claim.
- *Example*: If the original signal said "Ban likely" but Step 45 last night said "Ban Blocked by Court", the claim is **HALTED**.

---

## 2. Thresholds for Failure

| Failure Type | Action |
| :--- | :--- |
| **Missing Source** | **HALT & NOTIFY**. (Manual verification required). |
| **Numeric Discrepancy** | **REJECT**. (Discard signal). |
| **Adjective Saturation** | **STRIP**. (Remove fluff and re-evaluate). |

---

## 3. Output Schema: GUARDRAIL_CARD (YAML)

```yaml
guardrail_card:
  card_id: "UUID"
  verified_id: "UUID" # Referring to Step 52 Card
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Scan
  verified_claims:
    - claim: "US Utilities must replace Transformers."
      token: "2024_EPRI_Grid_Report"
      status: "PASS"
      
    - claim: "HD Hyundai Backlog spans 48 months."
      token: "Q3_Earnings_Transcript"
      status: "PASS"
      
  # The Cleanup
  fluff_removed:
    - "Unprecedented"
    - "Skyrocketing"
    - "No-brainer"
    
  # The Verdict
  status: "FAIL-SAFE" # PASS / FAIL-SAFE
  is_hallucination_free: true
```

---

## 4. Mock Examples

### Mock 1: PASS (The Dry Truth)
- **Claim**: "Lead times are 100 weeks."
- **Source**: Industry Log (verified).
- **Result**: **PASS**.

### Mock 2: FAIL (The AI Guess)
- **Claim**: "The sector will grow 50% because AI needs power."
- **Source**: General Inference.
- **Result**: **REJECT**. (This is a forecast/guess, not a structural fact).

---

## 5. Final Report
Step 53 is the **Anti-Entropy Layer**.
Information decays. Truth is hard to maintain.
The Hunter Engine must be **Viciously Accurate**.
**One error destroys the brand.**
