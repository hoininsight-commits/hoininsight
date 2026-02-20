# ISSUE_SIGNAL_FUSION.md
# (Economic Hunter – Step 37)

## 0. Purpose
This engine is the **Compressor**.
It takes the verified `STRUCTURAL_PATH_SNAPSHOT` (Step 35) + `PRESSURE_INDEX` (Step 36)
and fuses them into the **Final Issue Signal**.

It answers:
> "What is the One Question that defines this trade?"

It acts as the bridge between the **Logic Core** (Steps 1-36) and the **Broadcaster** (human operator).

---

## 1. The Fusion Pipeline

The Signal must survive this 4-stage gauntlet.

### Stage 1: Input Filter (Pressure Check)
- **Rule**: Input SPI (Step 36) must be **IMMINENT (6-7)** or **CRITICAL (8-10)**.
- *Action*: If SPI < 6, **DROP** immediately.

### Stage 2: Conflict Check (Duplicate Check)
- **Rule**: Compare against existing Active Signals (last 7 days).
- *Action*: If `Spender` + `Vector` matches an existing signal, **MERGE** (Update timestamp). Do not create duplicate.

### Stage 3: Templating (The Phrasing)
- **Rule**: Map the logic to one of the **5 Fixed Question Templates**.

### Stage 4: Compression (The Polish)
- **Rule**: Remove all adjectives. Remove all "I think". Max 20 words.

---

## 2. The 5 Question Templates (Fixed)

The Signal MUST be phrased as one of these questions.

### Template A: The Void (Shortage Focus)
**"Where will [Spender] find [Resource] when [Constraint] hits [Deadline]?"**
- *Use when*: Supply is zero.

### Template B: The Collision (Force Focus)
**"What happens to [Sector] when [Force A] collides with [Force B]?"**
- *Use when*: Two vectors oppose (e.g., Demand up, Supply down).

### Template C: The Reveal (Mechanism Focus)
**"Who actually controls [Asset] now that [Event] has changed the rules?"**
- *Use when*: A Moat has been activated.

### Template D: The Paradox (Gap Focus)
**"If [Official Intent] is true, why is [Asset Reality] behaving like this?"**
- *Use when*: Rhetoric contradicts Data.

### Template E: The Deadline (Time Focus)
**"Can [Actor] comply with [Law] without [Forced Action] by [Date]?"**
- *Use when*: A legal deadline is the primary force.

---

## 3. Output Schema: ISSUE_SIGNAL

```json
{
  "signal_id": "UUID",
  "snapshot_id": "UUID",
  "spi_score": 9,
  "signal_text": "Where will US Utilities find UHV Transformers when the Import Ban hits Jan 1st?",
  "template_used": "TEMPLATE_A",
  "status": "READY_TO_BROADCAST"
}
```

---

## 4. Mock Examples

### Mock 1: PASS (Template A)
- **Input**: Transformer Shortage (SPI=9).
- **Spender**: Utilities.
- **Resource**: Transformers.
- **Constraint**: Import Ban.
- **Signal**: "Where will US Utilities find Transformers when the Import Ban hits Jan 1st?"
- **Verdict**: **PASS**.

### Mock 2: FAIL (Low Pressure)
- **Input**: Consumer Discretionary (SPI=4).
- **Template**: "Can Consumers keep spending?"
- **Verdict**: **FAIL**. (SPI < 6. Dropped at Stage 1).

---

## 5. Absolute Prohibition
**Never** mention the Ticker in the Signal.
The Signal creates the **Hunger**.
The Ticker (Step 31) provides the **Food**.
Do not feed the user before they are hungry.
