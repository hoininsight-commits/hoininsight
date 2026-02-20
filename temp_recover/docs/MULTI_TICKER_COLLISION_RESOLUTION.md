# MULTI_TICKER_COLLISION_RESOLUTION.md
# (Economic Hunter – Step 43)

## 0. Purpose
This engine is the **Compressor**.
It takes the list of "Safe" tickers (Step 42) and forces them to fight for the podium.

It answers:
> "We have 5 good companies. Which 1 (or 2) actually OWN the bottleneck?"

It enforces **Concentration**.
The Hunter does not buy ETFs. The Hunter buys **Monopolies**.
If you keep 4 tickers, you don't have a thesis. You have a **Sector List**.

---

## 1. Collision Scoring Dimensions (0-10 Points Each)

Every ticker is scored on its **Structural Dominance**.

### Axis 1: Cash-First (Payment Hierarchy)
- **10**: Paid upfront (Deposits required).
- **5**: Paid on delivery.
- **0**: Paid 90 days net (Vendor financing).

### Axis 2: Lead-Time Power (Scarcity)
- **10**: Start-up time for new competition > 3 years (e.g., Foundry, Shipyard).
- **5**: Start-up time 1-2 years.
- **0**: Start-up time < 6 months (Software).

### Axis 3: Installed-Base Lock-in (Stickiness)
- **10**: Impossible to switch (Proprietary standard).
- **5**: Painful to switch (Training costs).
- **0**: Costless to switch (Commodity).

### Axis 4: Capacity Gate (Share of Growth)
- **10**: Controls >50% of new capacity coming online.
- **5**: Controls 20-50%.
- **0**: Tiny share (Price taker).

### Axis 5: Substitution Friction (Physics)
- **10**: Physics prohibits alternative (e.g., Copper for conduction).
- **5**: Regulatory barrier prohibits alternative.
- **0**: Generic substitute available.

---

## 2. Forced Collapse Algorithms

After scoring, rank tickers by **Total Score**.

### Algorithm A: The Monopoly Cut (Target: 1)
*Usage: If Ticker #1 is > 20% ahead of Ticker #2.*
- **Action**: **KEEP #1**. **DROP ALL OTHERS**.
- *Rationale*: There is only one King.

### Algorithm B: The Duopoly Split (Target: 2)
*Usage: If Ticker #1 and #2 are close (< 10% gap) and together control > 70% of market.*
- **Action**: **KEEP #1 and #2**. **DROP OTHERS**.
- *Rationale*: Coke and Pepsi. Boeing and Airbus.

### Algorithm C: The Triopoly Limit (Target: 3)
*Usage: If top 3 are close.*
- **Action**: **KEEP Top 3**.
- *Constraint*: **STRICT LIMIT**.

### Algorithm D: The Sector Reject (Target: 0)
*Usage: If 4 or more tickers are within 10% score of each other.*
- **Action**: **REJECT ENTIRE TOPIC**.
- *Rationale*: This is a "Sector Rally", not a "Bottleneck Hunt". The thesis is too diffuse.

---

## 3. Output Schema (YAML)

```yaml
collision_resolution:
  resolution_id: "UUID"
  step42_validation_id: "UUID"
  scoring_matrix:
    - ticker: "HD Hyundai Electric"
      scores: [10, 10, 5, 8, 10]
      total: 43
      rank: 1
    - ticker: "Hyosung Heavy Ind"
      scores: [8, 10, 5, 7, 10]
      total: 40
      rank: 2
    - ticker: "LS Electric"
      scores: [5, 5, 2, 4, 10]
      total: 26
      rank: 3
  algorithm_applied: "ALGORITHM_B_DUOPOLY"
  final_selection:
    - "HD Hyundai Electric"
    - "Hyosung Heavy Ind"
  rejected_tickers:
    - "LS Electric (Score too low)"
  final_verdict: "PASS"
```

---

## 4. Mock Examples

### Mock 1: PASS (Duopoly)
- **Top 2**: HD Hyundai (43), Hyosung (40).
- **Next**: LS Electric (26).
- **Score Gap**: Large drop-off after #2.
- **Result**: **KEEP Top 2**. This is a **Duopoly**.

### Mock 2: REJECT (Sector Play)
- **Topic**: Construction Materials.
- **Tickers**: Cement A (30), Steel B (29), Wood C (30), Brick D (28).
- **Analysis**: No one dominates. 4 companies are equal.
- **Result**: **REJECT**. "Sector Play".
- **Logic**: If you can't pick the winner, the structural force is weak.

---

## 5. Absolute Prohibition
**Never** output 4 tickers.
The number 4 is the death of the Hunter.
If you have 4, you have 0.
