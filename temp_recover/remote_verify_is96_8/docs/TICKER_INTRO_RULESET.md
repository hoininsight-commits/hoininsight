# TICKER_INTRO_RULESET.md
# (Economic Hunter – Step 31)

## 0. Purpose
This engine is the **Bouncer**.
It controls exactly *when* and *how* a company name enters the script.

It enforces the **Order of Operations**:
**Logic First. Ticker Last.**

> "We do not introduce a company to sell it.
> We introduce it because it is the only bucket that catches the rain."

---

## 1. The 4 Rules (Strict)

### Rule A: The Gate (Prerequisite)
Tickers can ONLY be introduced if **Step 30 (Core Explanation)** is fully **LOCKED**.
- If the "Why" is weak, the "Who" is irrelevant.
- *Status*: If Step 30 != LOCK, Step 31 = ABORT.

### Rule B: The Timing (Bottleneck First)
The Ticker must appear **AFTER** the Bottleneck is defined.
- *Wrong*: "Buy HD Hyundai because transformers are short."
- *Right*: "Transformers are short... leading to a bottleneck... which is controlled by HD Hyundai."
- *Logic*: The User must buy the *Problem* before they hear the *Solution*.

### Rule C: The Quantity (Scarcity)
Maximum **1 to 3** tickers allowed.
- *1 Ticker*: The Monopoly (Best).
- *2 Tickers*: The Duopoly.
- *3 Tickers*: The Oligopoly.
- *4+ Tickers*: The Sector (REJECT. Too diffuse).

### Rule D: The Ban (No Sales)
- **No Valuation**: P/E, P/B, Market Cap discourse is forbidden.
- **No Price Targets**: "$100 target" is forbidden.
- **No Adjectives**: "Great management", "Undervalued" is forbidden.
- *Permitted*: "Capacity sold out", "Only certified vendor", "Market share > 50%".

---

## 2. Ticker Kill-Switch Logic

Every Ticker must carry its own **Invalidation Condition**.
Just because the *Thesis* is valid doesn't mean the *Company* is safe.

*Schema*: `Ticker_X -> Kill_Switch_X`
- "HD Hyundai leads... unless Copper prices explode (Margin crush)."
- "Samsung leads... unless Yield fails to reach 50% (Tech failure)."

---

## 3. Output Schema: TICKER_INTRO_LOCK_SPEC

```json
{
  "intro_id": "UUID",
  "step30_lock_id": "UUID_Required",
  "tickers": [
    {
      "name": "HD Hyundai Electric",
      "role": "The Pure Play",
      "moat_evidence": "Order book filled to 2029.",
      "ticker_kill_switch": "If US lifts ban on Chinese imports."
    },
    {
      "name": "Hyosung Heavy Industries",
      "role": "The Alternative",
      "moat_evidence": "Only other certified non-China vendor.",
      "ticker_kill_switch": "If production ramp fails execution."
    }
  ],
  "compliance_check": {
    "count_valid": true,
    "position_valid": true,
    "language_valid": true
  },
  "verdict": "LOCK"
}
```

---

## 4. Mock Examples

### Mock 1: LOCK (Structural Intro)
- **Script Context**: "...This capital force hits a supply chain with zero spare capacity." (Step 30 End).
- **Intro**: "This mathematical surplus flows exclusively to **HD Hyundai Electric** and **Hyosung**, as they hold the only certified non-Chinese production lines capable of 345kV delivery."
- **Analysis**:
    - *Timing*: After bottleneck.
    - *Count*: 2 (Valid).
    - *Language*: "Certified", "Capable" (Fact-based).
- **Verdict**: **LOCK**.

### Mock 2: REJECT (Sales Pitch)
- **Script Context**: "The market is heating up."
- **Intro**: "We really like **Samsung Electronics** here. It is trading at a low P/E of 10x and has massive upside potential compared to peers."
- **Analysis**:
    - *Timing*: Premature (No bottleneck defined).
    - *Language*: "Like", "Low P/E", "Upside" (Valuation/Opinion).
- **Verdict**: **REJECT**. (Return to Analysis).

---

## 5. Absolute Prohibition
**Never** use the phrase "Stock Pick".
We are identifying **Beneficiaries of Force**.
The moment it sounds like a stock tip, the Engine has failed.
