# PRE_TOPIC_GENERATOR.md
# (Economic Hunter – Step 33)

## 0. Purpose
This engine is the **Inquisitor**.
It operates immediately after the Trigger is fused (Step 32) but *before* the structural analysis begins.

It answers:
> "How do we phrase this problem as a **Question** that forces the listener to beg for the answer?"

It enforces **Mystery**.
If you give the Ticker now, the story is over.
You must first sell the **Problem**.

---

## 1. Question Logic (The 4 Types)

The output must be a single sentence phrased as a question (or implied question).

### Logic 33-A: The Logic Gap
*Usage: When Intent contradicts Reality.*
- **Syntax**: "If [Official] says [Intent], why does [Data] show [Opposite]?"
- *Example*: "If the Fed says inflation is fixed, why is Treasury cash balance at zero?"

### Logic 33-B: The Time Collision
*Usage: When a Deadline meets a Constraints.*
- **Syntax**: "What happens on [Date] when [Force] collides with [Immovable Object]?"
- *Example*: "What happens on Jan 1st when the Carbon Mandate collides with a zero-capacity shipyard?"

### Logic 33-C: The Mechanism Reveal
*Usage: When a hidden rule is activated.*
- **Syntax**: "Who actually controls the supply of [Asset] now that [Event] has passed?"
- *Example*: "Who actually controls the US Power Grid now that Chinese imports are banned?"

### Logic 33-D: The Silent Force
*Usage: When massive capital moves quietly.*
- **Syntax**: "Why is [Actor] quietly hoarding [Resource] while the market watches [Noise]?"
- *Example*: "Why are Hyperscalers quietly buying nuclear land permits while the market watches NVIDIA?"

---

## 2. Rejection Rules (Hard Kill)

The Question is **HELD** (Not Speakable) if:

1.  **Predictive**: "Will the Fed cut rates?" (We don't know -> **HOLD**).
2.  **Ticker Reveal**: "Is HD Hyundai a buy?" (Analysis revealed too early -> **HOLD**).
3.  **Vague**: "What is going on with Gold?" (No tension -> **HOLD**).
4.  **Complex**: "Given X, Y, and Z, should we consider...?" (Too long -> **HOLD**).

---

## 3. Output Schema: PRE_TOPIC_CARD

```json
{
  "pre_topic_id": "UUID",
  "fusion_id": "UUID",
  "question_text": "If the US Government just banned the only supplier of Transformers, where will the hardware come from?",
  "logic_type": "33-C (Mechanism Reveal)",
  "compliance": {
    "no_tickers": true,
    "no_prediction": true
  },
  "verdict": "SPEAKABLE"
}
```

---

## 4. Mock Examples

### Mock 1: SPEAKABLE (33-B Time Collision)
- **Input**: US Dept of Energy Import Ban (Effective Jan 1).
- **Question**: "What happens to the US Power Grid on Jan 1st when the only available supply of transformers becomes illegal?"
- **Verdict**: **SPEAKABLE**. (High tension, no ticker).

### Mock 2: HOLD (Predictive)
- **Input**: Oil Price Volatility.
- **Question**: "Is Oil going to $100 next month?"
- **Verdict**: **HOLD**. (Gambling logic. Not structural).

---

## 5. Absolute Prohibition
**Never** answer the question in Step 33.
Step 33 is the **Tease**.
The Answer comes in Step 30 (Structure) and Step 31 (Ticker).
