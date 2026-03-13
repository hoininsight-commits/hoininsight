# BOTTLENECK_IDENTIFICATION_S50.md
# (Economic Hunter – Step 50)

## 0. Mission
This engine is the **Narrower**.
It takes the `VALUE_CHAIN_CARD` (Step 49) and zooms in on **Node 2 (The Bridge)**.

It answers:
> "Why is this bridge the only way across the river?"

It enforces **Monopoly Physics**.
If the bridge is wide, there is no pricing power.
If the bridge is a tightrope, the owner sets the price.

---

## 1. Bottleneck Criteria (Strict)

The Bottleneck MUST satisfy at least **2 of these 4** conditions.

### A. Lead-Time (> 2 Years)
*Can a competitor build a new factory tomorrow?*
- **Criteria**: New capacity takes > 24 months to come online.
- *Example*: Shipbuilding Dock, High-Voltage Transformer Plant.

### B. Capacity Utilization (> 95%)
*Is the current bucket full?*
- **Criteria**: Current global supply is fully booked/contracted.
- *Example*: "Order book filled until 2029."

### C. Certification Barrier (The Moat)
*Is it illegal to use a substitute?*
- **Criteria**: Regulatory body (DOE, FDA, UL) mandates specific vendor list.
- *Example*: "DOE Critical Electric Infrastructure (CEI) certified only."

### D. Switching Cost (The Lock)
*Is it painful to change vendors?*
- **Criteria**: Changing vendor requires re-engineering or multi-year testing.
- *Example*: "Nuclear fuel rod design."

---

## 2. Extraction Rules

- **One and Only One**: You must identify exactly **ONE** bottleneck point.
  - If "Shipping" AND "Port Access" are both tight -> **Pick the Tighter One** (Port).
  - If 0 bottlenecks found -> **REJECT**.
- **No Conceptual Bottlenecks**:
  - *Fail*: "Lack of Innovation", "Labor Shortage" (Too vague).
  - *Pass*: "Welder Shortage certified for Nuclear Piping" (Specific).

---

## 3. Output Schema: BOTTLENECK_CARD (YAML)

```yaml
bottleneck_card:
  card_id: "UUID"
  chain_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Target (Node 2)
  target_item: "345kV+ Power Transformers"
  
  # The Proof (2+ Conditions)
  conditions:
    lead_time: "PASS (> 4 Years)"
    capacity: "PASS (Sold out to 2030)"
    certification: "PASS (DOE Ban on generic imports)"
    switching_cost: "FAIL (Standard specs)"
    
  # The Kill Question
  kill_answer: "Because it takes 4 years to build a factory, and the law bans imports today, supply is mathematically fixed for 48 months."
  
  # The Verdict
  status: "PASS"
```

---

## 4. Mock Examples

### Mock 1: PASS (The Perfect Squeeze)
- **Item**: LNG Transport Ships.
- **Lead Time**: 5 Years (Shipyards full).
- **Capacity**: 100% booked.
- **Result**: **PASS** (Conditions A + B met).

### Mock 2: REJECT (The Commodity)
- **Item**: Solar Panels.
- **Lead Time**: 3 Months (Glut).
- **Capacity**: 60% (Over-supply).
- **Certification**: High (Tariffs).
- **Result**: **REJECT**. (Only Condition C met. Need 2).

---

## 5. Final Report
Step 50 verifies the **Choke Point**.
No Choke Point = No Pricing Power = No Alpha.
We only hunt where the grip is tightest.
