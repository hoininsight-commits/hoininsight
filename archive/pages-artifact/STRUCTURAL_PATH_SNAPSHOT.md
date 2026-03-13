# STRUCTURAL_PATH_SNAPSHOT.md
# (Economic Hunter – Step 35)

## 0. Purpose
This engine is the **Pathfinder**.
It operates strictly after the Topic is Locked (Step 34).

It answers:
> "We know SOMETHING must happen.
> Show me the exact **Path of Force**."

It verifies the "Pipe" through which money must travel.
It does **NOT** yet identify the "Clog" (Bottleneck) or the "Brand" (Ticker).
It defines the **Physics of the Flow**.

---

## 1. Structural Path Logic (The 4-Point Verification)

The Snapshot is valid only if ALL 4 points are clearly defined.

### Logic 35-A: Spender Identification (Who?)
*Who is the entity holding the bag?*
- **Valid**: "US Utility Companies", "Global Shipping Lines", "The Federal Gov".
- **Invalid**: "Consumers" (Too diffuse), "Investors" (Too fickle), "The Market" (Too vague).

### Logic 35-B: Coercion Verification (Why?)
*What prevents them from doing nothing?*
- **Valid**: "Federal Mandate (Fine)", "Physical Blackout (Existential)", "Competitor Leap (Survival)".
- **Invalid**: "FOMO", "Growth Aspiration", "ESG Goals" (Soft).

### Logic 35-C: Capital Vector (How Much?)
*Is the flow material relative to the recipient?*
- **Valid**: "Entire Annual Capex Budget", "Emergency Reserve Fund".
- **Invalid**: "R&D Budget" (Small), "Pilot Program".

### Logic 35-D: Timeline Rigidity (When?)
*Can they kick the can down the road?*
- **Valid**: "Fixed Deadline (Jan 1)", "Immediate Failure".
- **Invalid**: "By 2030", "Eventually".

---

## 2. Rejection Rules (Broken Path)

If the Path is not "Sealed", the Snapshot **FAILS**.

1.  **Leakage**: "The Spender could choose to pay a small fine instead of spending." -> **FAIL**.
2.  **Bypass**: "The Spender could import from a different country." -> **FAIL**.
3.  **Delay**: "The Spender can wait for rates to drop." -> **FAIL**.

---

## 3. Output Schema: STRUCTURAL_PATH_SNAPSHOT

```json
{
  "snapshot_id": "UUID",
  "lock_id": "UUID",
  "path_definition": {
    "spender_entity": "US Regulated Utilities",
    "coercion_mechanism": "Federal Reliability Mandate (FERC) + DOE Import Ban",
    "capital_vector": "Grid Modernization Capex (approx $50B/yr)",
    "timeline_rigidity": "Immediate (Lead times exceed compliance window)"
  },
  "integrity_check": {
    "is_sealed": true,
    "no_bypass_detected": true
  },
  "verdict": "PASS"
}
```

---

## 4. Mock Examples

### Mock 1: PASS (Sealed Pipe)
- **Topic**: Transformer Shortage.
- **Spender**: Utilities.
- **Coercion**: Law (Ban) + Physics (Blackout).
- **Vector**: Major Capex.
- **Timeline**: Now.
- **Integrity**: Can they bypass? No. Can they wait? No.
- **Verdict**: **PASS**.

### Mock 2: FAIL (Leaky Pipe)
- **Topic**: EV Consumer Adoption.
- **Spender**: US Consumers.
- **Coercion**: Tax Credit ($7500).
- **Vector**: Car Purchase.
- **Timeline**: Flexible.
- **Integrity**: Can they bypass? Yes (Buy Gas Car). Can they wait? Yes (Old car works).
- **Verdict**: **FAIL**. (Path is not forced).

---

## 5. Absolute Prohibition
**Never** assume the Spender *wants* to spend.
Assume the Spender *hates* spending.
We hunt only when they **Have No Choice**.
