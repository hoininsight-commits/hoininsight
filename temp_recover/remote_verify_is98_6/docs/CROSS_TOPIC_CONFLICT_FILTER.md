# CROSS_TOPIC_CONFLICT_FILTER.md
# (Economic Hunter – Step 23)

## 0. Purpose
This engine is the **Air Traffic Controller**.
It prevents the Human Operator from being overwhelmed by multiple valid but conflicting stories.

It answers:
> "Are these two different stories?
> Or two angles on the same story?"

It enforces the **Cognitive Limit**:
The market can only digest **1–2 Structural Shifts** per day.

---

## 1. Root Cause Collision Check

If Topic A and Topic B share the same **Primary Trigger** (Step 1/2), they represent the *Same Event*.

**Rule**:
- If `Trigger_ID(A) == Trigger_ID(B)`:
  - **MERGE** them into the stronger narrative.
  - Do NOT publish two briefs.

*Example*:
- Brief A: "Fed Pivot drives Bond Buying."
- Brief B: "Fed Pivot drives Dollar Selling."
- **Action**: Merge into "Fed Pivot Liquidity Shock".

---

## 2. Capital Flow Overlap Check

If Topic A and Topic B target the same **Bottleneck** (Step 4/5), they represent the *Same Trade*.

**Rule**:
- If `Bottleneck_Ticker(A)` is in `Bottleneck_Ticker(B)`:
  - **KEEP** the one with the higher Pressure Score (Step 21).
  - **DROP** the weaker narratve.

*Example*:
- Brief A: "AI forces utility capex (Target: HD Hyundai)."
- Brief B: "EV Grid upgrade forces utility capex (Target: HD Hyundai)."
- **Action**: Keep Brief A (AI is the stronger/faster force). Drop Brief B.

---

## 3. Daily Attention Limit (Hard Cap)

The maximum number of **FINAL TOPICS** is **2**.
(Step 21 allowed up to 3, but Step 23 tightens this to 2 for maximum focus).

**Priority Logic**:
1.  **Diamond Lock**: Always Priority 1.
2.  **Highest Total Pressure Score**: Priority 2.
3.  **Highest "Blindness" Score**: Tie-breaker.

*Action*:
- Slot 1: Winner.
- Slot 2: Runner-up (if distinct).
- Slot 3+: **DROP** or **WATCH**.

---

## 4. Story Differentiation Test

Even if triggers and tickers are different, the **Mental Model** must be distinct.

**Rule**:
- If both topics rely on the same "Macro Theme" (e.g., "Inflation is back"),
  they are cognitively identical.
- **Select the sharpest one.** Drop the diffuse one.

---

## 5. Output Schema: DAILY_TOPIC_SET

```json
{
  "date": "YYYY-MM-DD",
  "final_topic_count": 1,
  "topics": [
    {
      "topic_id": "UUID_Topic_A",
      "brief_id": "UUID_Brief_A",
      "status": "PUBLISH"
    }
  ],
  "rejected_log": [
    {
      "topic_id": "UUID_Topic_B",
      "reason": "CAPITAL_OVERLAP with Topic A"
    },
    {
      "topic_id": "UUID_Topic_C",
      "reason": "ATTENTION_LIMIT_EXCEEDED (Rank 3)"
    }
  ]
}
```

---

## 6. Mock Examples (Rejection in Action)

### Mock A: The Double-Dip Rejection
- **Input**:
  1. "War Shock forces Defense Spending" (Score 19).
  2. "War Shock forces Oil Spike" (Score 17).
- **Check**: Same Trigger (War Shock).
- **Result**: **MERGE** or **DROP Weaker**.
- **Output**: Publish "War Shock" (Defense) only. Oil is a side-effect.

### Mock B: The Congestion Rejection
- **Input**:
  1. "AI Data Center Power Crisis" (Score 18).
  2. "Bio-Pharma Patent Cliff" (Score 16).
  3. "Semiconductor Supply Chain" (Score 15).
- **Check**: No collision. All distinct.
- **Limit**: Max 2.
- **Result**:
  1. Publish AI Power (Rank 1).
  2. Publish Bio-Pharma (Rank 2).
  3. **DROP** Semiconductor (Rank 3). *Too much noise for one day.*

---

## 7. Absolute Prohibition
**Never** publish 3 topics just because "they are all good".
The Operator does not have enough time.
**Focus is Force.**
