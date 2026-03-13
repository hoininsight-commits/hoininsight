# MULTI_TRIGGER_FUSION.md
# (Economic Hunter – Step 16)

## 0. Purpose

This engine acts as the **Pressure Chamber**.
It takes individual `WHY_NOW_CANDIDATE` packets (Step 14/15) and attempts to **Fuse** them.

It enforces the "Rule of Two":
> "One signal is an anomaly.
> Two orthogonal signals are a trend.
> Three are a law."

This step ensures that a Topic is not reliant on a single point of failure (e.g., one politician's speech).

---

## 1. Fusion Rules (The Convexity Test)

Fusion ONLY occurs if triggers meet ALL 3 criteria.

### Rule A: Orthogonality (Source Diversity)
Triggers must come from **different Reality Layers**.
- **Layer 1 (The Law)**: Legislation, Regulation, Court Ruling.
- **Layer 2 (The Mouth)**: CEO Guidance, Central Bank Speech.
- **Layer 3 (The Physics)**: Inventory Data, Lead Times, Prices, Disasters.

*Valid Fusion*: Layer 1 + Layer 3 (Law + Shortage).
*Invalid Fusion*: Layer 2 + Layer 2 (CEO A + CEO B). *Note: This is "confirmation", not "fusion".*

### Rule B: Time Convergence Window
Triggers must occur within a strict window to be considered "related pressure".
- **Macro/Policy**: Window < 14 Days.
- **Earnings/Corporate**: Window < 7 Days.
- **Shock/Disaster**: Window < 24 Hours.

### Rule C: Capital Vector Alignment
Triggers must force money into the **Same Bucket**.
- Trigger A forces buying "Transformers".
- Trigger B forces buying "Grid Reliability equipment".
- **Result**: ALIGNED.

- Trigger A forces "AI Chips".
- Trigger B forces "Power Plants".
- **Result**: RELATED but NOT FUSED (Supply Chain vs Energy). *Keep separate.*

---

## 2. Fusion Score Model

**Fused Score = (Max Individual Score) + (Fusion Bonus)**

### Base Score
Highest score among input candidates (e.g., Candidate A=80, B=60 → Base=80).

### Fusion Bonus
- **+10 Points**: Two Different Layers (e.g., Law + Data).
- **+20 Points**: Three Different Layers (Law + Speech + Data).
- **+5 Points**: Same Layer but Independent Actors (e.g., US Govt + EU Govt).

### Multipliers
- **x0.5 Penalty**: If vectors are slightly divergent.
- **x0.0 Kill**: If vectors oppose (e.g., Law says Buy, Budget says Cut).

---

## 3. Verdict Thresholds (Post-Fusion)

| Fused Score | Verdict | Action |
| :--- | :--- | :--- |
| **≥ 95** | **DIAMOND LOCK** | Unshakable thesis. Immediate priority. |
| **85 – 94** | **PLATINUM LOCK** | Standard high-conviction hunt. |
| **60 – 84** | **WATCHLIST** | Strong but maybe missing a Layer. |
| **< 60** | **DISBAND** | Fusion failed. Treat inputs individually. |

---

## 4. Output Schema: FUSED_WHY_NOW_CARD

```json
{
  "fusion_id": "UUID",
  "primary_vector": "Grid Infrastructure Capex",
  "input_packets": ["Packet_ID_A", "Packet_ID_B"],
  "layer_composition": ["LAYER_1_LAW", "LAYER_3_PHYSICS"],
  "time_delta_hours": 48,
  "base_score": 85,
  "fusion_bonus": 10,
  "final_fused_score": 95,
  "verdict": "DIAMOND LOCK"
}
```

---

## 5. Mock Examples

### Mock 1: DIAMOND LOCK (Score 100)
- **Signal A (Layer 1)**: US DOE issues "Grid National Security Order" (Score 80).
- **Signal B (Layer 3)**: Transformer Lead Times hit record 150 weeks (Score 85).
- **Checks**: Orthogonal? Yes. Window? <24h. Vector? Same (Grid).
- **Math**: Max(80,85) + 15 (Bonus) = **100**.
- **Result**: **DIAMOND LOCK**.

### Mock 2: WATCHLIST (Score 75)
- **Signal A (Layer 2)**: CEO of Tech Co says "We need more power." (Score 65).
- **Signal B (Layer 2)**: CEO of Utility Co says "Demand is high." (Score 60).
- **Checks**: Orthogonal? No (Speech + Speech). Same Layer Bonus (+5).
- **Math**: Max(65,60) + 5 = **70**.
- **Result**: **WATCHLIST**. (Needs Law or Data to fuse upgrade).

### Mock 3: REJECT (Logic Break)
- **Signal A**: Govt mandates EV sales.
- **Signal B**: Govt cuts EV subsidy budget.
- **Checks**: Vectors Opposed (Mandate vs Budget Cut).
- **Result**: **FUSION FAILED**. (Conflict).

---

## 6. Absolute Prohibitions

- **Forced Fitting**: Don't fuse "Apple Earnings" with "Fed Rate Cut" just because they happened same day. **Must share Capital Vector.**
- **Double Counting**: Don't fuse "Bloomberg Report" with "Reuters Report" on same event. That is **One Signal**.
