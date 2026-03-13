# EXPECTATION_GAP_DETECTOR.md
# (Economic Hunter – Step 17)

## 0. Purpose
This engine is the **Vibe Check**.
It measures the distance between "What the Market Thinks" (Expectation) and "What Just Happened" (Reality).

The Economic Hunter hunts **Anomalies**, not Consensus.
- If Reality matches Expectation → **NO TRADE** (Priced In).
- If Reality contradicts Expectation → **GAME ON** (Repricing Imminent).

---

## 1. The Indices

### Index A: Expectation (E) — "The Market Price"
Measures how bullish/bearish the crowd is *before* the trigger.
- **Sentiment**: Media Tone (Positive/Negative).
- **Positioning**: Recent Price Action (Up/Down).
- **Consensus**: Analyst Estimates (High/Low).

*Score (0-10)*:
- 0: Total Despair / Ignored.
- 5: Neutral / Mixed.
- 10: Euphoria / "Priced for Perfection".

### Index B: Reality (R) — "The Hard Trigger"
Measures the undeniable impact of the *Trigger*.
- **Force**: Legal/Physical necessity.
- **Magnitude**: Size of capital flow ($).
- **Duration**: Irreversibility timeline.

*Score (0-10)*:
- 0: No Impact / Noise.
- 5: Moderate Change.
- 10: Systemic Shock / Game Changer.

---

## 2. The Gap Formula

**GAP SCORE = Reality (R) - Expectation (E)**

### Scenario A: The Hunter's Zone (Positive Gap)
- **R(10) - E(2) = +8**: Massive Shock on Ignored Sector. (Best)
- **R(8) - E(5) = +3**: Strong Event on Neutral Sector. (Good)

### Scenario B: The Priced-In Zone (Zero Gap)
- **R(10) - E(10) = 0**: Great News, but everyone knew it. (Pass)
- **R(2) - E(2) = 0**: Boring News on Boring Sector. (Pass)

### Scenario C: The Trap Zone (Negative Gap)
- **R(5) - E(10) = -5**: "Sell the News". Good news, but crowd expected Great news. (Kill)

---

## 3. Verdict Thresholds

| Gap Score | Verdict | Action |
| :--- | :--- | :--- |
| **+5 to +10** | **DIAMOND LOCK** | **Immediate Hunt**. Market is asleep at the wheel. |
| **+2 to +4** | **WATCHLIST** | Good potential. Monitor for price reaction. |
| **-1 to +1** | **REJECT** | Priced In. No alpha. |
| **< -1** | **SHORT/AVOID** | Disappointment or Trap. Kill Topic. |

---

## 4. Kill Rules (Immediate Downgrade)

1.  **Already Trending**: If Price is up >20% in last 5 days → Max Gap capped at +2. (Late to party).
2.  **Front Page News**: If Topic is on Main Page of 3 major outlets → Increase E-Score by +5. (Crowded).
3.  **Analyst Unanimity**: If 100% of analysts say "Buy" → Expectation E is locked at 10. (Gap likely negative).

---

## 5. Output Schema: EXPECTATION_GAP_CARD

```json
{
  "gap_id": "UUID",
  "topic": "UHV Transformer Shortage",
  "expectation_score": 2,
  "expectation_reason": "Sector ignored, boring utility stocks flat YTD.",
  "reality_score": 9,
  "reality_reason": "DOE Ban (Law) + Record Lead Times (Shock).",
  "gap_score": 7,
  "verdict": "DIAMOND LOCK",
  "kill_factors": "None (No media coverage yet)."
}
```

---

## 6. Mock Examples

### Mock 1: DIAMOND LOCK (Gap +7)
- **Topic**: Maritime Carbon Regulation (IMO).
- **Expectation (E=2)**: Shipping stocks ignored, perceived as cyclical/dead.
- **Reality (R=9)**: International Law mandates engine replacement by Jan 1.
- **Gap**: 9 - 2 = **+7**.
- **Result**: **LOCK**. (Market hasn't priced the forced capex).

### Mock 2: WATCHLIST (Gap +3)
- **Topic**: Next-Gen AI Chip Launch.
- **Expectation (E=7)**: Everyone loves AI, stocks are high.
- **Reality (R=10)**: New chip is genuinely revolutionary (3x perf).
- **Gap**: 10 - 7 = **+3**.
- **Result**: **WATCH**. (Good news, but room for upside is squeezed).

### Mock 3: REJECT (Gap 0)
- **Topic**: Fed Cut Anticipation.
- **Expectation (E=10)**: Market 100% certain of 25bp cut. Prices ATH.
- **Reality (R=10)**: Fed cuts 25bp.
- **Gap**: 10 - 10 = **0**.
- **Result**: **REJECT**. (Classic "Sell the news").

---

## 7. Absolute Prohibition
**Never** conflate "Good Company" with "Good Gap".
A great company with E=10 has **No Gap**.
The Hunter hunts the **Gap**, not the Company.
