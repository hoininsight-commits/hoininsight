# WHY_NOW_CONFIDENCE_SCORING.md
# (Economic Hunter – Step 15)

## 0. Purpose

This engine is the **Judge**.
It takes verified candidates (Step 14) and assigns a **Numerical Confidence Score (0–100)**.

This score determines:
- **LOCK**: "We will hunt this today."
- **WATCHLIST**: "Not enough pressure yet."
- **REJECT**: "Weak signal."

It does **NOT** predict success.
It predicts **Structural Inevitability**.

---

## 1. The Confidence Score Model (0–100)

Total Score = Sum of 5 Dimensions (Max 20 points each).

### 1. Trigger Clarity (Weight: 20)
- **20**: Signed Law / Regulatory Mandate / Physical Shock.
- **15**: Executive Order / CEO Official Guidance Update.
- **10**: MOU / "Planned" Announcement.
- **0–5**: Rumor / Media Report / Analyst View.

### 2. Irreversibility (Weight: 20)
- **20**: Breaking it requires legislative repeal or physical rebuilding.
- **15**: Breaking it creates massive financial penalty.
- **10**: Breaking it hurts reputation only.
- **0–5**: Easy to delay or cancel.

### 3. Forced Capital Magnitude (Weight: 20)
- **20**: Budget currently executing / Orders placed.
- **15**: Budget approved but not yet spent.
- **10**: "We will invest" (verbal commitment).
- **0–5**: "Considering investment".

### 4. Time Compression (Weight: 20)
- **20**: Action required within < 7 days.
- **15**: Action required within < 30 days.
- **10**: Action required within < 1 quarter.
- **0–5**: "Sometime next year" or "Long term".

### 5. Narrative Singularity (Weight: 20)
- **20**: This is the ONLY way to solve the problem (No alternative).
- **15**: Best way, but alternatives exist (expensive/slow).
- **10**: One of many options.
- **0–5**: Easily substituted.

---

## 2. Verdict Thresholds

| Score Range | Verdict | Action |
| :--- | :--- | :--- |
| **85 – 100** | **LOCK** | Promote to Locked Topic (Step 3/4 Start). |
| **60 – 84** | **WATCHLIST** | Hold in Pressure Building state. Monitor for +10 points. |
| **0 – 59** | **REJECT** | Return to Noise or discarded. |

*Constraint:* A score of 84 is a REJECT/WATCH, never a round-up LOCK.

---

## 3. Output Schema: WHY_NOW_CONFIDENCE_CARD

```json
{
  "packet_id": "UUID",
  "total_score": 90,
  "verdict": "LOCK",
  "dimensions": {
    "clarity": 20,
    "irreversibility": 20,
    "capital": 15,
    "time": 20,
    "singularity": 15
  },
  "score_reasoning": "Law signed (20), Cannot be repealed (20), Immediate deadline (20).",
  "missing_elements": "Capital is approved but contracts not yet signed (-5)."
}
```

---

## 4. Mock Examples

### Mock 1: LOCK (Score 95)
- **Subject**: New Environmental Regulation Enforcement.
- **Clarity**: 20 (Final Rule published).
- **Irreversibility**: 20 (Federal Law).
- **Capital**: 20 (Fines start next month).
- **Time**: 20 (Compliance date is in 3 days).
- **Singularity**: 15 (Only one tech solves it, but allowed to pay fine).
- **Result**: **95 -> LOCK**.

### Mock 2: WATCHLIST (Score 70)
- **Subject**: Big Tech AI Server Plan.
- **Clarity**: 15 (CEO Guidance).
- **Irreversibility**: 10 (Can delay if recession hits).
- **Capital**: 20 (Capex guid raised).
- **Time**: 15 (This quarter).
- **Singularity**: 10 (Multiple chip vendors).
- **Result**: **70 -> WATCHLIST**. (Need "Signed Contract" to boost Irreversibility).

### Mock 3: REJECT (Score 40)
- **Subject**: Analyst Upgrade on Sector X.
- **Clarity**: 5 (Opinion).
- **Irreversibility**: 0.
- **Capital**: 5.
- **Time**: 15.
- **Singularity**: 15.
- **Result**: **40 -> REJECT**.

---

## 5. Absolute Prohibition
**Never** adjust the score to fit a desired outcome.
If it feels like a LOCK but scores 80, it is **NOT A LOCK**.
The system trusts the score, not the feeling.
