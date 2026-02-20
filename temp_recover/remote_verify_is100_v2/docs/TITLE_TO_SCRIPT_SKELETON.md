# TITLE_TO_SCRIPT_SKELETON.md
# (Economic Hunter – Step 40)

## 0. Purpose
This engine is the **Architect**.
It takes the compressed `TOPIC_TITLE` (Step 39) and expands it back into a rigid **4-Block Skeleton**.

It answers:
> "If the Title is the Headline, what is the Outline?"

It does **NOT** write the script.
It draws the **Boxes** that the scriptwriter must fill.

---

## 1. The 4-Block Skeleton (30s Structure)

Every Script must follow this logical progression.

### Block 1: The Situation (Status Quo)
*Intent*: Establish the baseline reality that is about to be broken.
- **Focus**: What does the crowd believe? What is the "Normal"?
- *Time*: 0s - 7s.

### Block 2: The Force (The Trigger)
*Intent*: Introduce the specific Event/Law that breaks the Situation.
- **Focus**: The `WHY_NOW_SENTENCE` (Step 38).
- *Time*: 7s - 15s.

### Block 3: The Bottleneck (The Constriction)
*Intent*: Show where the Force gets stuck.
- **Focus**: Physics, Capacity, or Legal Limits.
- *Time*: 15s - 22s.

### Block 4: The State (The Outcome)
*Intent*: Define the final, irreversible reality.
- **Focus**: The new Price/Supply dynamic.
- *Time*: 22s - 30s.

---

## 2. Rejection Rules (Structure Fail)

The Skeleton is **REJECTED** if:

1.  **Circular Logic**: Block 4 just repeats Block 1. (No change).
2.  **Missing Force**: Block 2 is vague ("Things changed"). Must be specific.
3.  **No Bottleneck**: Block 3 jumps straight to "Profit". (Skip the mechanism).
4.  **Wrong Order**: Placing the Solution before the Problem.

---

## 3. Output Schema: SCRIPT_SKELETON

```json
{
  "skeleton_id": "UUID",
  "title_id": "UUID",
  "blocks": {
    "block_1_situation": "Market assumes Soft Landing and lower power demand.",
    "block_2_force": "Jan 1st DOE Ban forces immediate replacement of 40% of grid hardware.",
    "block_3_bottleneck": "Non-China production capacity is sold out until 2029.",
    "block_4_state": "Structural Supply Deficit is now mathematically locked."
  },
  "structure_check": {
    "has_clear_progression": true,
    "has_specific_force": true
  },
  "verdict": "PASS"
}
```

---

## 4. Mock Examples

### Mock 1: PASS (Linear Progression)
- **Title**: "Jan 1st Ban Triggers Transformer Crisis"
- **B1 (Situation)**: Utilities are relaxed, expecting normal replacement cycles.
- **B2 (Force)**: Jan 1st Ban makes Chinese inventory illegal overnight.
- **B3 (Bottleneck)**: Domestic factories cannot ramp up; 4-year lead times.
- **B4 (State)**: Panic buying begins; Prices unanchored.
- **Verdict**: **PASS**.

### Mock 2: FAIL (No Bottleneck)
- **Title**: "AI Boom Boosts Tech Stocks"
- **B1 (Situation)**: AI is popular.
- **B2 (Force)**: Companies spending money.
- **B3 (Bottleneck)**: Tech stocks will go up. (Error: This is a forecast, not a bottleneck).
- **B4 (State)**: Investors make money.
- **Verdict**: **FAIL**. (Missing the "Constriction" mechanism).

---

## 5. Absolute Prohibition
**Never** let the skeleton drift into "Opinion".
Block 3 (Bottleneck) is the most critical.
If you cannot define the Bottleneck, you do not have a story. You have a **Hope**.
