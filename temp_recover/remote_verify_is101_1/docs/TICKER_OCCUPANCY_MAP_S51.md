# TICKER_OCCUPANCY_MAP_S51.md
# (Economic Hunter – Step 51)

## 0. Mission
This engine is the **Registrar**.
It takes the `BOTTLENECK_CARD` (Step 50) and maps it to the specific **Corporate Entities** (Tickers) that physically own or operate that bottleneck.

It answers:
> "We found the treasure chest (Bottleneck). Who holds the **Key**?"

It enforces **Purity**.
The Hunter does not buy "Exposure". The Hunter buys **Occupancy**.
If the ticker only gets 5% of its revenue from the bottleneck, it is **Noise**.

---

## 1. Ticker Occupancy Rules (Strict)

A ticker is allowed ONLY if it survives this 4-step gauntlet.

### Rule A: Revenue Dominance (The 50% Rule)
*Is this their main business?*
- **Criteria**: >= 50% of EBITDA or Revenue must be directly derived from the bottleneck item.
- **Exception**: Global giants (e.g., Samsung, Mitsui) are only allowed if they have **Absolute Market Share (>70%)** in the bottleneck.

### Rule B: No Middlemen (The Maker Rule)
*Do they add value, or just pass paper?*
- **Criteria**: Must be the Manufacturer, IP Owner, or Physical Operator.
- **Forbidden**: Retailers, Distributors, Resellers, Consultants.

### Rule C: Ticker Limit (1–3 Only)
*Is the bottleneck truly tight?*
- **Criteria**: If you find > 3 companies with equal occupancy, the bottleneck is too wide.
- **Action**: **REJECT** the topic as a "Generic Industry".

### Rule D: Financial Life-Support
*Is the company dying for other reasons?*
- **Criteria**: Must be currently trading (Not delisted) and Solvent (No default).

---

## 2. Rejection Rules (Filter)

1.  **Diluted Play**: "Company A makes transformers, but 90% of their money comes from making toasters." -> **REJECT**.
2.  **Sector ETF Logic**: "Here are 10 companies that might benefit." -> **REJECT**.
3.  **Ambiguous Link**: "They are 'exploring' this sector." -> **REJECT**.

---

## 3. Output Schema: TICKER_OCCUPANCY_CARD (YAML)

```yaml
ticker_occupancy_card:
  card_id: "UUID"
  bottleneck_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The Occupants
  occupants:
    - ticker: "HD Hyundai Electric"
      occupancy_proof: "Controls 60% of US 345kV Transformer supply via Alabama plant."
      segment_weight: "95% (Pure Play Power Equipment)"
      
    - ticker: "Hyosung Heavy Ind"
      occupancy_proof: "Top 3 global supplier of UHV equipment with dedicated US facility."
      segment_weight: "70% (Power Systems + Construction)"
      
  # The Analysis
  count: 2
  is_concentrated: true # Must be true
  
  # The Verdict
  status: "LOCKED" # LOCKED / REJECT 
```

---

## 4. Mock Examples

### Mock 1: PASS (The Pure Play)
- **Bottleneck**: HBM (High Bandwidth Memory).
- **Tickers**: SK Hynix (First Mover + Dominant Capacity).
- **Result**: **PASS**.

### Mock 2: REJECT (The Diluted Play)
- **Bottleneck**: Copper Mining.
- **Tickers**: Rio Tinto, BHP, Freeport.
- **Analysis**: Copper is only 20-30% of Rio/BHP revenue. Too many players.
- **Result**: **REJECT**. (Go deeper to the *Smelter* or *Refiner* bottleneck instead).

---

## 5. Final Report
Step 51 is the moment we cross from "Economic Phenomenon" to **"Actionable Asset"**.
If the link is weak, the trade is weak.
We hunt for the **Bottle Neck Owner**.
