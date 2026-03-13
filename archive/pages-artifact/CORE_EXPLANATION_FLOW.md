# CORE_EXPLANATION_FLOW.md
# (Economic Hunter – Step 30)

## 0. Purpose
This engine is the **Logic Core**.
It owns the middle 30 seconds of the script (Seconds 15–45).

It answers the only question that matters:
> "Why does money HAVE to flow here?"

It connects the dots: **Event -> Law/Physics -> Target**.
It does **NOT** ask for agreement. It demonstrates **Force**.

---

## 1. The 3-Block Core Flow (Fixed)

The explanation must proceed in this exact linear order.

### Block 1: The Trigger (Why Now?)
*The specific event that makes the old reality impossible.*
- **Constraint**: Must cite a specific Date, Law, or Physical Event.
- **Syntax**: "As of [Date], [Event] has legally/physically mandated [Result]."

### Block 2: The Structure (Who must spend?)
*The actor who has lost their choice.*
- **Constraint**: Must name the entity (Utility, Govt, Shipper) and the coercion (Fine, Blackout, Loss).
- **Syntax**: "[Actor] is now forced to inject capital to avoid [Penalty/Disaster]."

### Block 3: The Bottleneck (Where does it go?)
*The specific asset that catches the flow.*
- **Constraint**: Must explain the moat (Certification, Capacity, Physics).
- **Syntax**: "This capital has only one destination: [Asset Class], which is strictly limited by [Constraint]."

---

## 2. Rejection Rules (Hard Kill)

The Core Flow is **REJECTED** if it relies on:

1.  **Attractiveness**: "This sector is growing fast." (Growth ≠ Force).
2.  **Valuation**: "The stock is cheap." (Price ≠ Force).
3.  **Possibility**: "If things go well..." (Hope ≠ Force).
4.  **Recommendation**: "We like this setup." (Opinion ≠ Force).

*The logic must work even if the stock price is down.*

---

## 3. Output Schema: CORE_EXPLANATION_LOCK_SPEC

```json
{
  "flow_id": "UUID",
  "topic_id": "UUID",
  "blocks": {
    "block_1_trigger": "US DOE Ban on Chinese Transformers (Effective Jan 2026).",
    "block_2_structure": "US Utilities face blackouts if they cannot secure domestic heavy equipment.",
    "block_3_bottleneck": "Non-China capacity is sold out for 4 years; new factories take 3 years to build."
  },
  "logic_check": {
    "is_predictive": false,
    "is_coercive": true,
    "is_specific": true
  },
  "verdict": "LOCK"
}
```

---

## 4. Mock Examples

### Mock 1: LOCK (Structural Force)
- **Topic**: Maritime Carbon Regulation.
- **Block 1**: "On Jan 1st, the IMO Carbon Intensity Indicator (CII) became law."
- **Block 2**: "This forces shipping lines to slow down or scrap 40% of the global fleet immediately."
- **Block 3**: "This supply shock hits a shipbuilding industry with zero open slots until 2028."
- **Verdict**: **LOCK**. (Law -> Scrap -> Shortage).

### Mock 2: REJECT (Forecasting)
- **Topic**: AI Software Boom.
- **Block 1**: "AI is the future of everything and everyone wants it."
- **Block 2**: "Companies will likely spend billions to upgrade their software."
- **Block 3**: "This should drive up the price of AI stocks significantly."
- **Verdict**: **REJECT**.
    - *Reason 1*: "Is the future" (Vague).
    - *Reason 2*: "Likely spend" (Not forced).
    - *Reason 3*: "Should drive up" (Forecast).

---

## 5. Absolute Prohibition
**Never** use the word "Opportunity".
The Hunter does not see opportunity.
The Hunter sees **Displacement**.
We are tracking the displacement of energy and capital.
