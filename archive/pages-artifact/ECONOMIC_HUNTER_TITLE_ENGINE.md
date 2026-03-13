# ECONOMIC_HUNTER_TITLE_ENGINE.md
# (Economic Hunter – Step 26)

## 0. Purpose
This engine is the **Headline Architect**.
It converts the Narrative Frame (Step 25) into a single, high-impact Title line.

It does **NOT** use Clickbait.
It uses **Structure**.
A good title is a logic bomb, not a promise of wealth.

---

## 1. The 4 Title Formulas (Fixed)

Every Final Title must follow exactly ONE of these patterns.

### Formula A: The Structural Collision
**"When [Force] meets [Immovable Object], [Result] is inevitable."**
- *Example:* "When AI Power Demand meets Grid Obsolescence, Capacity rationing is inevitable."

### Formula B: The Time-Force Mandate
**"[Deadline] forces [Actor] to [Action] regardless of price."**
- *Example:* "Jan 1st Carbon Deadline forces EU Shipping to scrap fleets regardless of price."

### Formula C: The Mechanism Reveal
**"[Trigger] has quietly activated [Bottleneck] mechanism."**
- *Example:* "US Import Ban has quietly activated the Non-China Transformer Monopoly."

### Formula D: The Reality Gap
**"Market expects [X], but [Data] proves [Y] is broken."**
- *Example:* "Market expects Soft Landing, but Treasury Cash Balance proves Liquidity is broken."

---

## 2. Forbidden Phrases (Hard Rejection)

If any of these appear, the Title is **KILLED**.

- **Hype**: "Boom", "Explosion", "Skyrocket", "Jackpot".
- **Advice**: "Buy", "Sell", "Accumulate", "Top Pick".
- **Hope**: "Potential", "Could", "Should", "Hopeful".
- **Vague**: "Big Changes", "Major Shift", "New Trend". (Be Specific).

---

## 3. Output Schema: TITLE_BLOCK

```json
{
  "title_id": "UUID",
  "narrative_id": "UUID",
  "candidates": [
    {
      "text": "...",
      "formula": "FORMULA_B",
      "verdict": "KEEP"
    },
    {
      "text": "...",
      "formula": "NONE",
      "verdict": "REJECT",
      "reason": "Contains Hype ('Boom')."
    }
  ],
  "final_title": "..."
}
```

---

## 4. Mock Selection Process

**Topic**: UHV Transformer Shortage.

### Candidate 1
- **Text**: "Transformer Supercycle: Why HD Hyundai Will Boom."
- **Formula**: None (Hype).
- **Verdict**: **REJECT**. (Reason: "Boom" is hype, "Will" is prediction).

### Candidate 2
- **Text**: "US Grid Crisis creates huge opportunity for investors."
- **Formula**: None (Advice).
- **Verdict**: **REJECT**. (Reason: "Opportunity for investors" is advisory).

### Candidate 3
- **Text**: "40-Month Lead Times force US Utilities to bypass Buy-American Laws."
- **Formula**: **Formula B (Time-Force)**.
- **Verdict**: **KEEP**. (Reason: Structural, specific, present tense).

**Final Selection**: Candidate 3.

---

## 5. Absolute Prohibition
**Never** write a title that you would see on a YouTube thumbnail.
Write a title that you would see on a **Intelligence Briefing**.
User attention is earned by **Respect**, not Tricks.
