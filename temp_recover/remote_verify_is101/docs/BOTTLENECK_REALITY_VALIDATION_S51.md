# BOTTLENECK_REALITY_VALIDATION_S51.md
# (Economic Hunter – Step 51)

## 0. Mission
This engine is the **Fact Checker**.
It takes the `BOTTLENECK_CARD` (Step 50) and performs a **Now-Validation** to ensure the bottleneck is a current physical reality, not a future expectation.

It answers:
> "Is the pipe *actually* clogged today, or are people just worried it *might* clog tomorrow?"

It enforces **Current Reality**.
The Hunter does not trade rumors of a shortage. The Hunter trades the **Shortage Itself**.

---

## 1. Reality Gates (Strict)

A bottleneck passes ONLY if it satisfies at least **2 of these 3** proof types.

### Gate A: Physical Proof (The Sight)
*Is there visible evidence of the constriction?*
- **Criteria**: Satellite imagery, port congestion data, inventory-to-sales at multi-year lows.
- **Example**: "60 ships anchored outside the port (source: Lloyd's List)."

### Gate B: Documented Proof (The Script)
*Has an official entity admitted to the failure?*
- **Criteria**: 10-K/Q risk statements, Force Majeure declarations, official trade bans.
- **Example**: "Company X declares Force Majeure due to raw material shortage (source: SEC Filing)."

### Gate C: Market Proof (The Price)
*Is the price behaving like a bottleneck?*
- **Criteria**: Spot price > 3-Sigma above 12-month average, or extreme backwardation.
- **Example**: "Spot prices hit $10k per unit vs $2k normal average."

---

## 2. The Kill Question

The Engine must answer:
> **"Does a physical alternative exist that can be deployed within 30 days?"**

- If **YES** -> **REJECT**. (The bottleneck is leaky).
- If **NO** -> **PASS**. (The bottleneck is real).

---

## 3. Output Schema: VALIDATED_BOTTLENECK_CARD (YAML)

```yaml
validated_bottleneck_card:
  card_id: "UUID"
  bottleneck_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Evidence (2+ required)
  evidence_matrix:
    physical_proof: 
      status: "PASS"
      detail: "Zero available inventory across top 4 distributors."
    documented_proof:
      status: "PASS"
      detail: "DOE Federal Ban signed and effective today."
    market_proof:
      status: "PASS"
      detail: "Spot premiums hit 400% records."
      
  # The Kill Question
  kill_question_answer: "NO (Replacement cycle for factory build is 4 years)."
  
  # The Verdict
  status: "PASS" # PASS / REJECT
```

---

## 4. Mock Examples

### Mock 1: PASS (The Real Shortage)
- **Item**: 345kV Transformers.
- **A**: Inventory zero (Pass).
- **B**: DOE Ban (Pass).
- **C**: Spot prices up 500% (Pass).
- **Kill Question**: No alternative (Pass).
- **Result**: **PASS**.

### Mock 2: REJECT (The Expected Shortage)
- **Item**: Lithium.
- **A**: Inventory currently high (Fail).
- **B**: No current ban (Fail).
- **C**: Prices falling (Fail).
- **Reason**: People *expect* a shortage in 2027, but there is no bottleneck *today*.
- **Result**: **REJECT**. (Not a Hunter Topic).

---

## 5. Final Report
Step 51 is the **Reality Anchor**.
If the world is just talking about a problem, we wait.
When the world **Feels** the problem in their P&L, we hunt.
