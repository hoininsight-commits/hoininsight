# ECONOMIC_HUNTER_NARRATIVE_FRAME.md
# (Economic Hunter – Step 25)

## 0. Purpose
This engine is the **Final Typesetter**.
It takes the LOCKED_TOPIC (Step 24) and formats it into the **Canonical Narrative Frame**.

This frame is rigid.
It forces every story to sound the same:
**Logical. Structural. Inevitable.**

---

## 1. The 6-Block Narrative Structure (Fixed)

Every Hunter Report MUST contain these 6 blocks in order.

### Block 1: The Context (The Misunderstanding)
*Start with what the market is getting wrong.*
- **Question**: "What does the crowd believe today?"
- **Syntax**: "While the market focuses on [Noise], the real structural shift is ignored."

### Block 2: The Trigger (The Event)
*State the undeniable fact that changed reality.*
- **Question**: "What happened yesterday that cannot be undone?"
- **Syntax**: "As of [Date], [Event] has legally/physically mandated [Result]."

### Block 3: The Mechanism (The Force)
*Trace the path of forced capital.*
- **Question**: "Who is forced to spend money?"
- **Syntax**: "[Actor] has no choice but to inject capital into [Sector]."

### Block 4: The Target (The Bottleneck)
*Identify the specific beneficiary.*
- **Question**: "Who catches the money?"
- **Syntax**: "This capital flows exclusively to [Bottleneck Tickers] due to [Moat]."

### Block 5: The Action (The Conclusion)
*State the logical conclusion.*
- **Question**: "What is the inevitable outcome?"
- **Syntax**: "The repricing of [Target] is now a mathematical certainty."

### Block 6: The Kill-Switch (The Risk)
*Define the invalidation condition.*
- **Question**: "When are we wrong?"
- **Syntax**: "Invalid only if [Condition] occurs."

---

## 2. Hard Rejection Rules (Forbidden Phrases)

If any of these appear, the Frame is **BROKEN** and must be rewritten.

1.  **Hype**: "Skyrocket", "Moon", "Huge Potential". (Use "Structural Shift").
2.  **Ambiguity**: "We think", "It seems", "Likely". (Use "The data shows").
3.  **Future Tense**: "Will", "Going to". (Use Present Tense: "Is forcing").
4.  **Emotions**: "Exciting", "Scary", "Worrying". (Use "Critical", "Systemic").

---

## 3. Output Schema: NARRATIVE_BLOCK

```json
{
  "frame_id": "UUID",
  "topic_id": "UUID",
  "blocks": {
    "context": "Market thinks shipping is dead.",
    "trigger": "IMO Carbon Law effective Jan 1.",
    "mechanism": "Owners must scrap old ships.",
    "target": "HD Hyundai Mipo (Only builder).",
    "action": "Order book is full until 2028.",
    "kill_switch": "If IMO repeals law."
  },
  "tone_validation": "PASSED"
}
```

---

## 4. Mock Example (LOCKED Topic)

**Topic**: UHV Transformer Shortage.

- **Block 1 (Context)**: "While investors chase AI software margins, the physical grid required to run them has hit a wall."
- **Block 2 (Trigger)**: "The US DOE confirmed yesterday that lead times for UHV transformers have exceeded 40 months."
- **Block 3 (Mechanism)**: "US Utilities are now legally mandated to secure 5-year supply contracts to prevent blackouts."
- **Block 4 (Target)**: "This panic capital is funneling directly to **HD Hyundai Electric** and **Hyosung**, the only certified non-Chinese vendors."
- **Block 5 (Action)**: "With capacity sold out until 2029, pricing power has shifted entirely to the supplier."
- **Block 6 (Kill-Switch)**: "Invalid only if the US lifts the import ban on Chinese transformers."

---

## 5. Absolute Prohibition
**Never** vary the structure to be "creative".
Reliability comes from **Repetition**.
The Operator should know exactly where to look for the "Why".
