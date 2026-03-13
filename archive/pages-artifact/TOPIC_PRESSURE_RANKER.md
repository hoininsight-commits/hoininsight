# TOPIC_PRESSURE_RANKER.md
# (Economic Hunter – Step 21)

## 0. Purpose
This engine is the **Final Gatekeeper**.
It takes all validated, fused, and structured topics and forces them to compete.

It answers:
> "If we can only speak about 3 things today,
> which ones are mathematically unavoidable?"

It ensures we never publish "filler" content.
**Zero Topics** is a valid and respected outcome.

---

## 1. The Pressure Score Model (4 Axes)

Total Score = Sum of 4 Axes (0–5 each). Max 20 Points.

### Axis A: Time Pressure (The Clock)
- **5 (Critical)**: Action required in < 24 hours / Tonight.
- **4 (Urgent)**: Action required this week.
- **3 (Pending)**: Action required this month.
- **1–2 (Drifting)**: Sometime this quarter/year.
- **0 (Static)**: No deadline.

### Axis B: Capital Force (The Wallet)
- **5 (Existential)**: "Spend or Die" / "Spend or Blackout".
- **4 (Mandatory)**: "Spend to comply with Law".
- **3 (Strategic)**: "Spend to capture market share".
- **1–2 (Optional)**: "Spend for efficiency".
- **0 (None)**: No clear buyer.

### Axis C: Structural Visibility (The Bottleneck)
- **5 (Single Point)**: Only 1–2 companies control the chokepoint.
- **4 (Oligopoly)**: 3–4 companies control it.
- **3 (Sector)**: A whole industry benefits.
- **1–2 (Diffuse)**: Benefits are spread widely.
- **0 (Unknown)**: No clear beneficiary.

### Axis D: Crowd Blindness (The Alpha)
- **5 (Ignored)**: Media/Consensus is talking about something else entirely.
- **4 (Niche)**: Only industry insiders are discussing it.
- **3 (Aware)**: Known, but impact underestimated.
- **1–2 (Crowded)**: Everyone knows it (Front page).
- **0 (Consensus)**: "Priced In".

---

## 2. Survival Thresholds

| Total Score | Verdict | Action |
| :--- | :--- | :--- |
| **15 – 20** | **FINAL** | **Publish**. Immediate Priority. |
| **12 – 14** | **WATCH** | Keep in reserve. Monitor next trigger. |
| **0 – 11** | **DROP** | Not enough pressure. Discard. |

---

## 3. Tie-Break & Forced Drop Rules

### The "Top 3" Rule
The engine allows a Maximum of **3 FINAL** topics.
If 4+ topics score ≥ 15:

1.  **Sort by Axis D (Blindness)**: Prefer the least crowded trade.
2.  **Then Sort by Axis A (Time)**: Prefer the most urgent.
3.  **Then Sort by Axis B (Capital)**: Prefer the biggest spender.

*The loser is downgraded to WATCH, regardless of score.*

### The "Zero Trust" Rule
If **NO** topic scores ≥ 15:
- Output: **ZERO FINAL TOPICS**.
- Narrative: "No actionable structural pressure today."
- *Do not lower the bar to fill the space.*

---

## 4. Output Schema: DAILY_TOPIC_RANK

```json
{
  "date": "YYYY-MM-DD",
  "final_slots_filled": 1,
  "ranked_list": [
    {
      "topic_id": "UUID",
      "headline": "...",
      "scores": {"time": 5, "capital": 5, "structure": 5, "blindness": 4},
      "total_score": 19,
      "verdict": "FINAL (Slot 1)"
    },
    {
      "topic_id": "UUID",
      "headline": "...",
      "scores": {"time": 3, "capital": 4, "structure": 4, "blindness": 2},
      "total_score": 13,
      "verdict": "WATCH"
    }
  ]
}
```

---

## 5. Mock Examples

### Scenario A: The Single Hunter Day
- **Topic**: "US Grid Emergency"
    - Time: 5 (Tonight)
    - Capital: 5 (Blackout risk)
    - Structure: 5 (Transformers)
    - Blindness: 4 (AI crowds ignoring utilities)
    - **Total: 19**
- **Result**: **1 FINAL Topic**.

### Scenario B: The Crowded Day (Tie-Break)
- **Topic A (War)**: Score 18 (Blindness 5).
- **Topic B (Fed)**: Score 16 (Blindness 1).
- **Topic C (Tech)**: Score 15 (Blindness 2).
- **Topic D (Bio)**: Score 15 (Blindness 5).
- **Selection**:
    1. Topic A (18)
    2. Topic D (15, Blindness 5) - *Wins tie-break vs C*
    3. Topic B (16) - *High score keeps it alive*
    - *Topic C is DROPPED to WATCH despite score 15, because slot limit.*

---

## 6. Absolute Prohibition
**Never** manually boost a score to save a favorite topic.
If it scores 14, let it go.
The Discipline **is** the Edge.
