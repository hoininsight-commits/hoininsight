# SCRIPT_OPENING_STRUCTURE.md
# (Economic Hunter – Step 29)

## 0. Purpose
This engine is the **Hook Master**.
It owns the first 15 seconds of the Hunter's voice.

Its goal is NOT to inform.
Its goal is to **Disarm**.
It must break the listener's existing mental model before planting a new one.

> "You cannot fill a cup that is already full.
> First, empty the cup."

---

## 1. The 3-Layer Opening Stack (Fixed)

The first 15 seconds must follow this exact sequence.

### Layer 1: The Contrast (0–5s)
*Pit the Consensus against the Anomaly.*
- **Syntax**: "While the market is obsessed with [Noise], a quiet [Force] has just activated."
- **Goal**: Create dissonance. "Am I looking at the wrong thing?"

### Layer 2: The Mechanism (5–10s)
*Reveal the immovable force.*
- **Syntax**: "This isn't a prediction. It is a [Law/Physical/Mathematical] certainty triggered by [Event]."
- **Goal**: Remove opinion. Establish authority.

### Layer 3: The Stake (10–15s)
*Define the cost of ignorance.*
- **Syntax**: "The capital displacement is inevitable, and it is flowing to exactly one place."
- **Goal**: Create urgency without hype.

---

## 2. Rejection Patterns (Hard Kill)

If the opening contains any of these, it is **REJECTED**.

1.  **The Data Dump**: "Yesterday, CPI printed 3.2%..." (Boring. Save for Block 2).
2.  **The Ticker Drop**: "Nvidia is a great stock..." (Salesy. Save for Block 4).
3.  **The Forecast**: "I think the market will go up..." (Opinion. Forbidden).
4.  **The Trivia Question**: "Did you know that..." (YouTuber style. Forbidden).
5.  **The Lecture**: "Today we are going to discuss..." (Professor style. Forbidden).

---

## 3. Output Schema: SCRIPT_OPENING_LOCK_SPEC

```json
{
  "opening_id": "UUID",
  "topic_id": "UUID",
  "stack_content": {
    "layer_1_contrast": "While investors chase AI apps, the physical grid has collapsed.",
    "layer_2_mechanism": "This isn't an opinion. It is a DOE Mandate effective today.",
    "layer_3_stake": "The flow of capital is now legal, not optional."
  },
  "compliance_check": {
    "no_tickers": true,
    "no_numbers": true,
    "no_forecasts": true
  },
  "verdict": "LOCK"
}
```

---

## 4. Mock Examples

### Mock 1: LOCK (Perfect Stack)
- **Topic**: Transformer Shortage.
- **Layer 1 (Contrast)**: "While everyone argues about Soft Landing, the US Power Grid has quietly declared a State of Emergency."
- **Layer 2 (Mechanism)**: "This is not a drill. It is a federal order activating emergency procurement authority."
- **Layer 3 (Stake)**: "Billions of dollars must now be spent on hardware that simply does not exist."
- **Verdict**: **LOCK**. (Cognitive dissonance -> Authority -> Urgency).

### Mock 2: REJECT (Common Errors)
- **Topic**: Transformer Shortage.
- **Opening**: "HD Hyundai Electric is up 20% because transformers are in short supply. You should buy it."
- **Analysis**:
    - *Error A*: Mentions Ticker ("HD Hyundai") -> **FAIL**.
    - *Error B*: Mentions Number ("20%") -> **FAIL**.
    - *Error C*: Gives Advice ("You should buy") -> **FAIL**.
- **Verdict**: **REJECT**. (Sounds like a stock tip, not a structural shift).

---

## 5. Absolute Prohibition
**Never** start with "Hello" or "Welcome".
Start with the **Conflict**.
The Hunter does not greet. The Hunter **hunts**.
