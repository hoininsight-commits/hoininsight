# TRIGGER_FUSION_ENGINE.md
# (Economic Hunter – Step 20)

## 0. Purpose

This engine acts as the **Pressure Cooker**.
It takes individual triggers (Speech, Schedule, Data) and fuses them into a single **Compelling Force**.

A single trigger is an incident.
Two triggers from different vectors are a **Trend**.
The Engine ONLY hunts Trends.

> "We do not bet on one man's words.
> We bet when his words collide with reality."

---

## 1. Fusion Logic (Orthogonality Rule)

True fusion requires inputs from **Different Reality Layers**.
Same-layer addition is just "News Stacking", not Fusion.

### Allowed Comparisons
| Trigger A | Trigger B | Validity | Logic |
| :--- | :--- | :--- | :--- |
| **SPEECH** (Intent) | **DATA** (Reality) | **VALID** | "He said X, but Data proves Y is broken." |
| **SCHEDULE** (Time) | **POLICY** (Law) | **VALID** | "Deadline is tomorrow, and Law mandates compliance." |
| **DATA** (Supply) | **SHOCK** (Demand) | **VALID** | "Inventory is 0, and Demand just spiked." |
| **SPEECH** (CEO) | **SPEECH** (Analyst) | **INVALID** | "Two people talking is still just talk." |

---

## 2. Strict Rejection Rules

The Fusion Engine REJECTS if:

1.  **Same-Type Fusion**: Fusing two speeches, or two data points from the same source.
2.  **Narrative without Force**: "AI is growing" + "CEO likes AI". (Where is the *Force*? Who *must* spend?)
3.  **Diffuse Destination**: "Money will flow to Technology". (Too broad. Must target a bottleneck).
4.  **Lagged Fusion**: Trigger A and Trigger B are > 14 days apart.

---

## 3. Output Schema: FUSED_TRIGGER_CARD

```json
{
  "fusion_id": "UUID",
  "vector_1": {
    "type": "CENTRAL_BANK_SPEECH",
    "content": "Fed Pivot Confirmed",
    "timestamp": "..."
  },
  "vector_2": {
    "type": "MACRO_DATA",
    "content": "Unemployment Spike above 4.5%",
    "timestamp": "..."
  },
  "collision_logic": "Speech confirms Pivot, Data confirms Recession risk. Expectation Gap maximizes.",
  "target_bottleneck_hint": "Treasury Bonds / Gold",
  "verdict": "PASS_TO_STEP_3"
}
```

---

## 4. Mock Examples

### Mock A: The Pivot (Speech + Data)
- **Trigger 1**: Fed Chair says "Labor market cooling is concerning." (Speech/Break)
- **Trigger 2**: NFP Payrolls print -100k jobs. (Data/Shock)
- **Fusion**: **PASSED**. Intent meets Reality.
- **Output**: Forces liquidity injection. Target: Bond Bottleneck.

### Mock B: The Fiscal Cliff (Policy + Schedule)
- **Trigger 1**: US Debt Ceiling Suspension Expires. (Schedule/Timed Force)
- **Trigger 2**: Congress passes "No New Dept" resolution. (Policy/Lock)
- **Fusion**: **PASSED**. Time meets Law.
- **Output**: Forces immediate spending freeze. Target: Defense Contractors (Negative).

### Mock C: The Shortage (Supply + Demand)
- **Trigger 1**: Taiwan Earthquake halts TSMC plant. (Shock/Event)
- **Trigger 2**: OpenAI releases GPT-6 demanding 10x compute. (Product/Data)
- **Fusion**: **PASSED**. Supply Crash meets Demand Spike.
- **Output**: Forces prices to infinity. Target: Inventory Holders.

---

## 5. Next Step Connectivity

Only **PASSED** Fusion Cards can enter **STEP 3 (Structural Necessity)**.
Loose triggers are retained in the `Memory Pool` for 7 days, then discarded.

**Absolute Rule**:
NO FUSION = NO HUNT.
