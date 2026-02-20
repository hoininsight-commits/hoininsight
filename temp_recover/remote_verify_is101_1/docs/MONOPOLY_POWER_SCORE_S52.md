# MONOPOLY_POWER_SCORE_S52.md
# (Economic Hunter – Step 52)

## 0. Mission
This engine is the **Leverage Meter**.
It takes the `TICKER_OCCUPANCY_CARD` (Step 51) and calculates the **Monopoly Power Score (0-100)**.

It answers:
> "Can these companies raise prices tomorrow without losing a single customer?"

It enforces **Pricing Power**.
If demand is high but the company can't raise prices (e.g., Fixed-price government contracts), the structural benefit is stolen by someone else.

---

## 1. Scoring Axes (0-25 Points Each)

### Axis A: Backlog Infinity (Scarcity)
*How long is the line?*
- **25 pts**: Backlog > 5 years / Fully sold out.
- **15 pts**: Backlog 2-3 years.
- **0 pts**: Order to delivery < 6 months.

### Axis B: Switching Friction (Stickiness)
*Can they walk away?*
- **25 pts**: Legal/Regulatory requirement to use THIS specific vendor.
- **10 pts**: High technical switching cost (Re-engineering).
- **0 pts**: Commodity choice.

### Axis C: Pricing Mechanism (Contract Type)
*Who has the upper hand?*
- **25 pts**: Escalation clauses (Cost-plus) or Spot pricing.
- **10 pts**: Flexible negotiations.
- **0 pts**: Fixed-price legacy contracts with no inflation protection.

### Axis D: Market Share Concentration (The Choke)
*Who else can build this?*
- **25 pts**: Top 2 control > 80% of specific segment.
- **10 pts**: Top 5 control > 60%.
- **0 pts**: Fragmented market.

---

## 2. Thresholds & Action

| Score | State | Action |
| :--- | :--- | :--- |
| **80 – 100** | **GOD MODE** | **ULTRA-LOCK**. (Structural Inevitability). |
| **60 – 79** | **STRONG** | **LOCK**. (Standard Hunter Play). |
| **< 60** | **DILUTED** | **REJECT**. (Too much competition or weak leverage). |

---

## 3. Output Schema: MONOPOLY_SCORE_CARD (YAML)

```yaml
monopoly_score_card:
  card_id: "UUID"
  occupancy_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Score
  ticker_scores:
    - ticker: "HD Hyundai Electric"
      metrics:
        backlog_infinity: 25
        switching_friction: 15
        pricing_mechanism: 20
        market_share: 25
      total_score: 85
      state: "GOD MODE"
      
  # The Logic
  leverage_proof: "Utilities cannot build the grid without 345kV transformers. Vendors are sold out until 2029. New contracts have 100% price escalation pass-through."
  
  # The Verdict
  status: "LOCKED"
```

---

## 4. Mock Examples

### Mock 1: GOD MODE (Score 85+)
- **Segment**: AI Foundry (TSMC) or Power Transformers (HD Hyundai).
- **Scarcity**: 5 Year Backlog.
- **Friction**: Billions in R&D / Regulation.
- **Pricing**: High leverage.
- **Result**: **LOCKED**.

### Mock 2: REJECT (Score < 60)
- **Segment**: Cloud Storage.
- **Scarcity**: Plentiful.
- **Friction**: Moderate (Data migration).
- **Pricing**: Constant price wars.
- **Result**: **REJECT**.

---

## 5. Final Report
Step 52 is the **Profit Gate**.
Revenue is vanity. Profit is sanity. **Pricing Power is Structural.**
We only hunt those who can command the flow.
