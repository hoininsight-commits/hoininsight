# STRUCTURAL_NECESSITY_CHECK_S48.md
# (Economic Hunter – Step 48)

## 0. Mission
This engine is the **Structural Engineer**.
It takes the `WHY_NOW_CARD` (Step 47) and stress-tests the **Path of Capital**.

It answers:
> "We know they *must* act today (Why Now).
> But can they *solve* it cheaply or bypass the bottleneck?"

It enforces **Inescapability**.
If there is a cheap detour, the Capital will take it. Only inescapable paths yield structural alpha.

---

## 1. The 3 Gates (Strict)

A Card must pass ALL THREE gates to generate a `STRUCTURAL_NECESSITY_CARD`.

### Gate 1: Survival / Compliance (The Motivation)
*Is the spending optional?*
- **PASS**: "Action required to avoid Jail, Fine, or Physical Collapse."
- **FAIL**: "Action required to grow revenue, improve efficiency, or follow a trend."
- *Constraint*: Growth is NOT Structural. Compliance IS Structural.

### Gate 2: Budgeted Reality (The Wallet)
*Does the money actually exist?*
- **PASS**: "Budget approved", "Emergency funds released", "Consumer wallets coerced (Gas/Food)".
- **FAIL**: "Future stimulus expected", "Projected earnings will fund this".

### Gate 3: No Detour (The Geometry)
*Can they use a substitute or delay?*
- **PASS**: "Physics/Law bans the substitute (e.g., Copper, Non-China Transformers)."
- **FAIL**: "They could switch to Aluminum", "They could import from Vietnam".

---

## 2. The Kill Sentence Test

The Engine must attempt to write the **Kill Sentence**:
> **"If [Actor] does not spend capital on [Target], [Existential Consequence] occurs immediately."**

- If the consequence is merely "Lower Profits" -> **REJECT**.
- If the consequence is "Blackout", "Fine", "Shutdown", "War Loss" -> **PASS**.

---

## 3. Output Schema: STRUCTURAL_NECESSITY_CARD (YAML)

```yaml
structural_necessity_card:
  card_id: "UUID"
  why_now_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Stress Test
  gates:
    motivation: "PASS (Compliance - DOE Ban)"
    wallet: "PASS (Rate-based recovery approved by FERC)"
    geometry: "PASS (No substitute for 345kV Transformers)"
    
  # The Logic
  kill_sentence: "If US Utilities do not spend capital on Domestic Transformers, immediate grid reliability fines and physical blackouts occur."
  
  # The Verdict
  status: "PASS" # PASS / HOLD / REJECT
  rejection_reason: null
```

---

## 4. Mock Examples

### Mock 1: PASS (The Grid)
- **Motivation**: Fines/Blackouts (Survival).
- **Wallet**: Rate-payer backed (Guaranteed).
- **Geometry**: Tech barrier + Import Ban (No Detour).
- **Kill Sentence**: "If they don't buy, the grid fails."
- **Result**: **PASS**.

### Mock 2: REJECT (The EV Dream)
- **Motivation**: Market Share (Growth).
- **Wallet**: Depends on Consumer Debt (Uncertain).
- **Geometry**: Consumers can buy ICE cars (Detour exists).
- **Kill Sentence**: "If they don't buy EVs, GM loses market share." (Weak).
- **Result**: **REJECT**.

---

## 5. Final Report
Step 48 confirms that the **River of Money** has high banks and no leaks.
If the banks are low (Growth), the river floods and dissipates.
If the banks are high (Necessity), the river drives the turbine.
