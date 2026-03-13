# TOPIC_LANGUAGE_HUMANIZER.md
# (Economic Hunter – Step 22)

## 0. Purpose
This engine is the **Universal Translator**.
It takes the cold, mathematical output of the Pressure Ranker (Step 21)
and converts it into natural, high-impact language for the human operator.

It does **NOT** add flair.
It adds **Clarity**.
It translates "Inevitability" into "Sentences".

---

## 1. The Humanizer Role
The Humanizer's job is to ensure the output sounds like:
- An Engineer explaining a machine.
- NOT a Salesman selling a stock.

**Tone**: Clinical, Urgent, Mechanical, Final.

---

## 2. The 5-Step Narrative Structure (Fixed)

Every Humanized Brief must follow this exact flow:

### 1. Opening Shock (The Hook)
State the irreversible fact that contradicts the market's mood.
- *Template:* "While the market debates [X], [Y] has essentially broken."

### 2. Why Now (The Trigger)
Explain the specific event that forces action today.
- *Template:* "The [Trigger Event] confirmed that [Action] is no longer optional."

### 3. Structural Flow (The Money)
Identify the forced spender and their constraint.
- *Template:* "[Actor] is legally/physically mandated to deploy capital into [Sector]."

### 4. Bottleneck Focus (The Target)
Identify the specific chokepoint where money gets stuck.
- *Template:* "This capital funnel collides with a supply cliff at [Bottleneck]."

### 5. Closing Line (The Verdict)
State the inevitability without promising profit.
- *Template:* "The displacement of capital is now mathematical."

---

## 3. Forbidden Language List (Strict)

If any of these words appear, the Brief is **REJECTED**.

- **Prediction**: "Will go up", "Target price", "Forecast", "Expect".
- **Valuation**: "Cheap", "Undervalued", "P/E", "Discount".
- **Persuasion**: "Buy", "Opportunity", "Don't miss out", "Promising".
- **Emotion**: "Exciting", "Worrying", "Great", "Terrible".

*Permitted*: "Forced", "Mandated", "Inevitable", "Restricted", "Sold out".

---

## 4. Output Schema: HUMANIZED_TOPIC_BRIEF

```json
{
  "brief_id": "UUID",
  "topic_id": "UUID",
  "headline": "...",
  "narrative_steps": {
    "opening": "...",
    "trigger": "...",
    "flow": "...",
    "bottleneck": "...",
    "closing": "..."
  },
  "tone_check": "PASSED"
}
```

---

## 5. Mock Examples

### Mock A: Green Energy Mandate
- **Opening**: "While the market prices in a delay, the EU Carbon Border Mechanism has legally activated."
- **Trigger**: "Brussels confirmed yesterday that no extensions will be granted beyond Jan 1st."
- **Flow**: "European importers are now mandated to secure non-carbon aluminum or pay punitive tariffs."
- **Bottleneck**: "This demand force hits a supply chain with zero spare hydro-smelting capacity."
- **Closing**: "The repricing of low-carbon aluminum is now a function of law, not sentiment."

### Mock B: Sovereign Tech War
- **Opening**: "While investors focus on software margins, the physical silicon supply chain has fractured."
- **Trigger**: "The Export Control expansion explicitly prohibits below-14nm tools to opponent nations."
- **Flow**: "State-backed foundries are forced to localized equipment procurement immediately."
- **Bottleneck**: "Domestic equipment vendors are the only available option, regardless of yield."
- **Closing**: "The shift in capital allocation is structural and unresponsive to price."

---

## 6. Absolute Prohibition
**Never** try to make the reader feel "good".
Make them feel **informed**.
The feeling of inevitability is the only emotion allowed.
