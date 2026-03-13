# TICKER_SKELETON_INSERTION_POINT.md
# (Economic Hunter – Step 41)

## 0. Purpose
This engine is the **Surgeon**.
It takes the clean `SCRIPT_SKELETON` (Step 40) and performs the delicate operation of inserting the **Ticker**.

It answers:
> "Where is the *exact* moment the listener is ready to hear the name?"

It enforces **Patience**.
You cannot name the solution until the listener feels the pain of the problem.

---

## 1. The Insertion Zone (Block 3 Only)

Tickers are **STRICTLY LIMITED** to **Block 3 (The Bottleneck)**.

- **Block 1 (Situation)**: **FORBIDDEN**. (Too early).
- **Block 2 (Force)**: **FORBIDDEN**. (Focus on the Event, not the Company).
- **Block 3 (Bottleneck)**: **MANDATORY**. (This is where the "Clog" lives).
- **Block 4 (State)**: **FORBIDDEN**. (Focus on the Outcome/Price, not the Name).

---

## 2. Insertion Conditions (Strict)

1.  **Direct Occupancy**: The Ticker must *physically own* the bottleneck.
    - *Right*: "Capacity is controlled by **HD Hyundai**."
    - *Wrong*: "**HD Hyundai** is a good stock."
2.  **Scarcity Count**: Max **1 to 3** names.
    - If > 3 names fit the bottleneck, the bottleneck is too wide. **ABORT**.
3.  **No Adjectives**: The name must stand naked.
    - *Right*: "**Hyosung Heavy Industries**."
    - *Wrong*: "The undervalued **Hyosung Heavy Industries**."

---

## 3. Forbidden Cases (Hard Kill)

The Insertion is **REJECTED** if:

1.  **Block 1 Leak**: "While investors watch **Nvidia**..." (Name-dropping early).
2.  **Block 4 Pitch**: "...meaning **Samsung** is a strong buy." (Sales pitch).
3.  **Valuation Context**: "...trading at 8x P/E." (Forbidden universally).

---

## 4. Output Schema: TICKER_INSERTION_MARKER

```json
{
  "insertion_id": "UUID",
  "skeleton_id": "UUID",
  "block_3_content": {
    "bottleneck_logic": "Global supply of 345kV transformers is sold out until 2029.",
    "ticker_insert": "This capacity is legally monpolized by [TICKER_A] and [TICKER_B].",
    "tickers": ["HD Hyundai Electric", "Hyosung Heavy Ind"]
  },
  "safety_check": {
    "is_block_3": true,
    "no_valuation": true,
    "max_ticker_count_valid": true
  },
  "verdict": "PASS"
}
```

---

## 5. Mock Examples

### Mock 1: PASS (Structural Fit)
- **Skeleton Block 3**: "The sudden demand hits a supply chain that has not expanded in 10 years."
- **Insertion**: "The sudden demand hits a supply chain that has not expanded in 10 years, forcing all orders to flow through the only certified vendors: **HD Hyundai Electric** and **Hyosung**."
- **Verdict**: **PASS**. (Seamless Logic -> Name).

### Mock 2: FAIL (Block 1 Leak)
- **Skeleton Block 1**: "While everyone is talking about **Tesla**, the grid is breaking."
- **Verdict**: **FAIL**. (Ticker "Tesla" used in Block 1).

### Mock 3: FAIL (Sales Pitch)
- **Insertion**: "...making **Doosan** a great opportunity for investors."
- **Verdict**: **FAIL**. ("Great opportunity").

---

## 6. Absolute Prohibition
**Never** use the Ticker as the *Subject* of the sentence.
The **Force** is the Subject. The **Ticker** is the Object.
"The Ban (Subject) forces capital into **HD Hyundai** (Object)."
Not: "**HD Hyundai** (Subject) benefits from the Ban."
