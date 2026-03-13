# WHY_NOW_SENTENCE_GENERATOR.md
# (Economic Hunter – Step 38)

## 0. Purpose
This engine is the **Distiller**.
It takes the open-ended Question from Step 37 (Issue Signal) and crystallizes it into a specific **Statement of Fact**.

It answers:
> "In one sentence, what changed reality?"

It serves as the definitive caption for the entire trade.

---

## 1. The 4 Sentence Templates (Fixed)

The Output MUST follow one of these exact structures.

### Template A: The Time Stamp
**"As of [Date], [Event] has legally/physically mandated [Result]."**
- *Usage*: When a specific deadline or law is the trigger.
- *Example*: "As of Jan 1st, the DOE Ban has legally mandated the replacement of all Chinese transformers."

### Template B: The Mechanical Link
**"[Event] has effectively mandated [Action] by removing [Alternative]."**
- *Usage*: When a choice has been eliminated.
- *Example*: "The Suez Blockade has effectively mandated longer routes by removing the Red Sea option."

### Template C: The Era Shift
**"The era of [Old Reality] ended yesterday when [Event] occurred."**
- *Usage*: When a regime change is definitive.
- *Example*: "The era of cheap power ended yesterday when PJM Capacity Auction prices cleared 800% higher."

### Template D: The Physical Dictate
**"[Law/Physics] now dictates that [Actor] must [Action], regardless of price."**
- *Usage*: When price elasticity is zero.
- *Example*: "Grid physics now dictates that Utilities must buy heavy equipment, regardless of price."

---

## 2. Rejection Rules (Hard Kill)

The Sentence is **REJECTED** if:

1.  **Predictive**: "The ban *will likely* cause shortages." (Weak).
2.  **Opinionated**: "This is *good news* for domestic suppliers." (Editorial).
3.  **Vague**: "Recent events have changed things." (No specific trigger).
4.  **Complex**: Sentences with more than 2 commas or > 25 words.

---

## 3. Output Schema: WHY_NOW_SENTENCE

```json
{
  "wnsg_id": "UUID",
  "issue_signal_id": "UUID",
  "sentence_text": "As of Jan 1st, the DOE Ban has legally mandated the replacement of all Chinese transformers.",
  "template_used": "TEMPLATE_A",
  "logic_check": {
    "is_predictive": false,
    "has_date_or_event": true
  },
  "verdict": "PASS"
}
```

---

## 4. Mock Examples

### Mock 1: PASS (Template A)
- **Input**: Transformer Ban (Step 37 Signal).
- **Sentence**: "As of Jan 1st, the DOE Ban has legally mandated the replacement of all Chinese transformers."
- **Verdict**: **PASS**.

### Mock 2: FAIL (Predictive)
- **Input**: Consumer Spending Data.
- **Sentence**: "The weak retail sales suggest that the consumer will slow down soon."
- **Verdict**: **FAIL**. ("Suggest", "Will slow down").

---

## 5. Absolute Prohibition
**Never** use "Maybe", "Possibly", or "Could".
The Hunter deals in **Absolutes**.
If it's not absolute, it's not a Hunt.
