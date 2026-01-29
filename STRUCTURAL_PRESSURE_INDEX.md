# STRUCTURAL_PRESSURE_INDEX.md
# (Economic Hunter – Step 36)

## 0. Purpose
This engine is the **Barometer**.
It measures the "Pounds per Square Inch" (PSI) of the capital force identified in Step 35.

It answers:
> "Is this a gentle breeze or a hurricane?"
> "Will the pipe burst?"

It quantifies **Force**, not sentiment.

---

## 1. The 5 Pressure Axes (0–2 Points Each)

Total Score: 0 to 10.

### Axis A: Targeting Rigidity (Who?)
- **2**: The Spender is a specialized entity with no choice (e.g., Grid Operator).
- **1**: The Spender is a broad sector (e.g., "Tech Companies").
- **0**: The Spender is the general public (Consumer).

### Axis B: Coercion Multiplier (Why?)
- **2**: **Existential/Legal**. (Action required to survive or avoid jail/fine).
- **1**: **Competitive**. (Action required to keep market share).
- **0**: **Aspirational**. (Action desired for growth).

### Axis C: Vector Magnitude (How Much?)
- **2**: **Structure-Breaking**. (Capital exceeds available supply).
- **1**: **Material**. (Significant capex increase).
- **0**: **Incremental**. (Normal course of business).

### Axis D: Temporal Urgency (When?)
- **2**: **Immediate**. (Now / Yesterday).
- **1**: **Pending**. (Next Quarter).
- **0**: **Distant**. (Next Year).

### Axis E: Alternative Scarcity (Options?)
- **2**: **Zero Alternatives**. (Must buy THIS specific thing).
- **1**: **Few Alternatives**. (Oligopoly).
- **0**: **Many Alternatives**. (Commodity).

---

## 2. Pressure State Thresholds

| Total SPI | State | Action |
| :--- | :--- | :--- |
| **8 – 10** | **CRITICAL** | **PASS**. Pipe is about to burst. |
| **6 – 7** | **IMMINENT** | **PASS**. Pressure is high enough to hunt. |
| **0 – 5** | **BUILDING** | **FAIL**. Pressure is insufficient. Return to Watchlist. |

---

## 3. Output Schema: STRUCTURAL_PRESSURE_INDEX

```json
{
  "spi_id": "UUID",
  "snapshot_id": "UUID",
  "scores": {
    "calc_a_targeting": 2,
    "calc_b_coercion": 2,
    "calc_c_vector": 2,
    "calc_d_urgency": 2,
    "calc_e_scarcity": 1
  },
  "total_spi": 9,
  "state": "CRITICAL",
  "verdict": "PASS"
}
```

---

## 4. Mock Examples

### Mock 1: PASS (State: CRITICAL)
- **Topic**: Transformer Shortage.
- **A (Targeting)**: 2 (Regulated Utilities).
- **B (Coercion)**: 2 (Blackout Risk + Law).
- **C (Vector)**: 2 (Capex >>> Supply).
- **D (Urgency)**: 2 (Lead times > 4 years).
- **E (Scarcity)**: 1 (Duopoly: HD Hyundai, Hyosung).
- **Total**: **9**.
- **Verdict**: **PASS**.

### Mock 2: FAIL (State: BUILDING)
- **Topic**: Enterprise AI Software.
- **A (Targeting)**: 1 (Corporations).
- **B (Coercion)**: 1 (FOMO/Competition).
- **C (Vector)**: 1 (Budget reallocation).
- **D (Urgency)**: 1 (Next budget cycle).
- **E (Scarcity)**: 0 (Many vendors).
- **Total**: **4**.
- **Verdict**: **FAIL**. (Pressure is just "Building").

---

## 5. Absolute Prohibition
**Never** inflate the score because you like the stock.
If the Pressure is Low, the Trade is Slow.
We hunt **Fast** trades. Fast trades require **High Pressure**.
