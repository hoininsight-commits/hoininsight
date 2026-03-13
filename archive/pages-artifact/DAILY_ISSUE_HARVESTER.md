# DAILY_ISSUE_HARVESTER.md
# (Economic Hunter – Step 8)

## 0. Purpose

This engine functions as the **Editor-in-Chief**.
It receives multiple verified candidates (Step 7 outputs)
and selects the **Top 1–3** items for the daily briefing.

- It does NOT create topics.
- It does NOT merge topics.
- It KILLS the weak to save the strong.

---

## 1. Input Requirements

Input: List of `LOCKED_TICKER_CARD` candidates.
Source: Output of Step 6 & 7.

---

## 2. Selection Logic (The 3 Filters)

### Filter A: Collision Rule (Capital Conflict)
If two topics target the **same capital source**, only ONE survives.

*Logic:*
- Topic A: "Govt must buy Missiles" (Security)
- Topic B: "Govt must buy Solar Panels" (Energy)
- If Budget is limited -> **Security > Energy** (Survival Rule).
- **Reject Topic B.** (Or Hold).

### Filter B: Time Pressure Score
Rank remaining topics by "Cost of Delay."

*Score Criteria:*
1.  **Immediate (Hours)**: Shock / Disaster / Crash -> **Score 10**
2.  **Deadline (Days)**: Policy Expiry / Voting day -> **Score 8**
3.  **Structural (Weeks)**: Supply Chain Break -> **Score 5**
4.  **Trend (Months)**: "Growth phase" -> **Score 1** (REJECT)

*Action:* Sort Descending.

### Filter C: Attention Budget Rule
Maximum daily capacity is **3 Slots**.

1.  **Slot 1 (The Lead)**: Highest Score.
2.  **Slot 2 (The Follow)**: Conflicting but valid, or #2 Score.
3.  **Slot 3 (The Edge)**: High Score but niche.

*Rule:* If Candidate #4 exists -> **DROP** (Do not save for later unless it triggers again).

---

## 3. Mandatory Rejection (The Waste Bin)

Even if slots are empty, REJECT if:

1.  **Narrative Overlap**: If Topic A and B tell 80% same story -> Keep stronger, Kill weaker.
2.  **Long-Term Theme**: "AI will grow for 10 years" -> **REJECT** (Not today's issue).
3.  **Nice-to-Know**: Interesting facts with no *actionable* pressure -> **REJECT**.

---

## 4. Example Scenario (5 Inputs -> 2 Outputs)

**Input Candidates:**
1.  **Topic A (War Outbreak)**: Ammo shortage. (Score 10)
2.  **Topic B (Fed Rate Decision)**: Tomorrow. (Score 9)
3.  **Topic C (AI Server)**: Backlog increase. (Score 5)
4.  **Topic D (EV Sales)**: Slightly better than expected. (Score 2)
5.  **Topic E (Bio Trial)**: Phase 1 pass. (Score 3)

**Processing:**
- **Collision**: None significant.
- **Scoring**: A(10) > B(9) > C(5) > E(3) > D(2).
- **Attention Cut**: Keep A, B, C. Drop D, E.
- **Final Review**:
    - Topic C (AI) is "Chronic" not "Acute" today? -> If A and B are huge, C might distract.
    - Decision: Keep A & B. (Focus).

**Output:**
- **Slot 1**: Topic A (War/Ammo)
- **Slot 2**: Topic B (Fed/Rates)
- **Discard**: C, D, E.

---

## 5. Output Format

[DAILY_HARVEST_RESULT]
- **Date**: YYYY-MM-DD
- **Selected Topics**:
  1. [TITLE] (Score: X)
  2. [TITLE] (Score: Y)
  3. (Empty)
- **Rejected Topics**:
  - [TITLE]: Reason (Score Low / Collision / Overlap)

---

## 6. Absolute Prohibitions

- "Participating Trophy" ❌ (No weak topics allowed)
- "Hedge" ❌ (Don't pick opposing views just to be safe)
- "Variety Pack" ❌ (Don't force diversity if Sector A is the only issue)

This engine creates
**Focus**, not Balance.
