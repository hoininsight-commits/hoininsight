# TICKER_KILL_SWITCH.md
# (Economic Hunter – Step 42)

## 0. Purpose
This engine is the **Executioner**.
It operates at the very last second, just before the script goes to production.

It answers:
> "Even if the thesis is right, is the Ticker **Toxic** right now?"

It enforces **Safety**.
We do not send users into a burning building, even if the building is structurally important.

---

## 1. Kill-Switch Conditions (The Poison List)

If ANY of these conditions are TRUE, the Ticker is **SILENCED** (Removed from script).

### Condition A: The Earnings Gamble
*Logic*: Is the company reporting earnings within 48 hours?
- **Rule**: If `Earnings_Date <= Now + 48h`: **KILL**.
- *Reason*: Earnings are a coin flip. We hunt structure, not gambling.

### Condition B: The Lawsuit/Fraud Alert
*Logic*: Is there an active DOJ/SEC investigation announced in the last 7 days?
- **Rule**: If `Active_Investigation == True`: **KILL**.
- *Reason*: Legal risk overrides structural benefit.

### Condition C: The Margin Crush
*Logic*: Has the price of their raw material spiked > 20% in 7 days?
- **Rule**: If `Input_Cost_Spike > 20%`: **KILL**.
- *Reason*: They might sell more widgets, but make zero profit.

### Condition D: The Liquidity Trap
*Logic*: Is daily volume < $5M?
- **Rule**: If `Avg_Daily_Vol < $5M`: **KILL**.
- *Reason*: Users cannot enter/exit safely.

---

## 2. Required Pass Conditions

For a ticker to survive, it must be:
1.  **Clean**: No events in A-D.
2.  **Solvent**: No imminent bankruptcy chatter.
3.  **Alive**: Trading is active (not halted).

---

## 3. Output Schema: TICKER_NOW_VALIDATION

```json
{
  "validation_id": "UUID",
  "ticker": "HD Hyundai Electric",
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "checks": {
    "earnings_risk": "SAFE (Next earnings: 45 days)",
    "legal_risk": "SAFE (No news)",
    "margin_risk": "SAFE (Copper flat)",
    "liquidity_risk": "SAFE ($50M ADT)"
  },
  "verdict": "PASS"
}
```

---

## 4. Mock Examples

### Mock 1: PASS
- **Ticker**: HD Hyundai Electric.
- **Check**:
  - Earnings: 2 months away.
  - Lawsuits: None.
  - Copper: Stable.
  - Volume: High.
- **Verdict**: **PASS**. (Ticker remains in Block 3).

### Mock 2: FAIL (Earnings Risk)
- **Ticker**: Nvidia.
- **Check**:
  - Earnings: **Tomorrow**.
  - Lawsuits: None.
- **Verdict**: **FAIL**. (Reason: "Earnings Gamble").
- **Action**: Remove Ticker from script. Keep the Structural Story, but do not name the company.

### Mock 3: FAIL (Liquidity)
- **Ticker**: Small Cap Miner X.
- **Check**:
  - Volume: $200k/day.
- **Verdict**: **FAIL**. (Reason: "Liquidity Trap").

---

## 5. Absolute Prohibition
**Never** override the Kill-Switch because "The story is too good".
If the Ticker dies, the Story can live on as a "Sector Story".
But the Ticker itself must vanish.
**Better to miss a gain than take a fatal loss.**
