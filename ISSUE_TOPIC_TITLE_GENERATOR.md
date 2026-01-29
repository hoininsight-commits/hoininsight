# ISSUE_TOPIC_TITLE_GENERATOR.md
# (Economic Hunter – Step 39)

## 0. Purpose
This engine is the **Headline Writer**.
It processes the `WHY_NOW_SENTENCE` (Step 38) into the final **Topic Title**.

It answers:
> "How do we make the user click without lying?"

It enforces **Density**.
Max 60 characters. Every word must carry weight.
No "Wait and See". Only "Read Now".

---

## 1. Title Compression Rules

1.  **Length Limit**: Max 60 Characters.
2.  **Noun Priority**: Must include the specific Asset or Mechanism (e.g., "Grid", "Ban", "Copper").
3.  **Verb Power**: Must use active, forceful verbs ("Breaks", "Forces", "Bans").
4.  **No Filler**: Remove "The", "A", "Is", "Are" where possible.

---

## 2. The 5 Title Templates (Fixed)

The Title MUST follow one of these high-impact patterns.

### Template A: The Collision (Noun vs Noun)
**"[Force] meets [Immovable Object]: [Result]"**
- *Example*: "Grid Demand meets Import Ban: Shortage"

### Template B: The Action (Actor + Verb)
**"[Actor] Forces [Action] on [Sector]"**
- *Example*: "DOE Forces Decoupling on Utilities"

### Template C: The Mechanism (Hidden Rule)
**"The Quiet [Mechanism] Behind [Event]"**
- *Example*: "The Quiet Capacity Law Behind the Spike"

### Template D: The Deadline (Time Force)
**"[Date] Deadline Triggers [Result]"**
- *Example*: "Jan 1st Deadline Triggers Compliance Shock"

### Template E: The Paradox (Confusion)
**"Why [Reality] Contradicts [Intent]"**
- *Example*: "Why Grid Capex Contradicts Soft Landing"

---

## 3. Rejection Rules (Hard Kill)

The Title is **REJECTED** if:

1.  **Clickbait**: "You won't believe..." (Cheap).
2.  **Question Mark**: "Is the Grid Broken?" (Weak. State it). *Exception: Template E*.
3.  **Ticker Symbol**: "NVDA is a Buy" (Forbidden. Sell the Problem).
4.  **All Caps**: "CRITICAL ALERT" (Unprofessional).

---

## 4. Output Schema: TOPIC_TITLE

```json
{
  "title_id": "UUID",
  "wnsg_id": "UUID",
  "title_text": "Jan 1st Ban Triggers Transformer Crisis",
  "template_used": "TEMPLATE_D",
  "char_count": 38,
  "compliance": {
    "no_hype": true,
    "no_tickers": true
  },
  "verdict": "PASS"
}
```

---

## 5. Mock Examples

### Mock 1: PASS (Template D)
- **Input**: "As of Jan 1st, the DOE Ban has legally mandated the replacement of all Chinese transformers."
- **Title**: "Jan 1st Ban Triggers Transformer Crisis"
- **Verdict**: **PASS**. (Short, Punchy, Accurate).

### Mock 2: FAIL (Hype)
- **Input**: Consumer spending is slowing down.
- **Title**: "Consumer Crash Imminent: Get Out Now!"
- **Verdict**: **FAIL**. (Hype words: "Crash", "Get Out Now").

---

## 6. Absolute Prohibition
**Never** promise what you cannot deliver.
If the Title says "Crisis", the Report must show the **Fire**.
If the Title says "Opportunity", the Report must show the **Check**.
