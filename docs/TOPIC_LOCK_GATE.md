# TOPIC_LOCK_GATE.md
# (Economic Hunter – Step 34)

## 0. Purpose
This engine is the **Chief Editor**.
It takes the `PRE_TOPIC_CARD` (Step 33) which is "Speakable", and decides if it is "Must Speak".

It answers:
> "Is this story better told *today* than tomorrow?"
> "If we skip this, do we lose the alpha?"

It enforces **Scarcity**.
We only have 60 seconds. We cannot waste it on "Interesting but Late" stories.

---

## 1. Lock Logic (The 4 Filters)

A Topic is LOCKED only if it passes at least one of these High-Pressure filters.

### Logic 34-A: The Expiry Lock
*Usage: If we don't speak today, the deadline passes.*
- **Condition**: Deadline < 24 Hours.
- **Verdict**: **LOCK**.

### Logic 34-B: The Shock Lock
*Usage: If we don't speak today, we look slow.*
- **Condition**: Event size > 3-Sigma (e.g., War, Ban, Crash).
- **Verdict**: **LOCK**.

### Logic 34-C: The Structure Lock
*Usage: The trend has crossed the "Irreversible Point".*
- **Condition**: Law Signed (Irreversibility = 100%).
- **Verdict**: **LOCK**.

### Logic 34-D: The Uniqueness Lock
*Usage: Everyone is missing this.*
- **Condition**: Crowd Blindness Score (Step 21) = 5/5.
- **Verdict**: **LOCK**.

---

## 2. Rejection Rules (Hold for Later)

The Topic is **HELD** (Returned to Memory) if:

1.  **Duplicate**: We spoke about this yesterday, and no new *Step 1* trigger occurred.
2.  **Developing**: The event is "Active" but the *Result* is not yet final (e.g., "Voting in progress").
3.  **Crowded**: Everyone else is talking about it, and we have no unique angle (Blindness < 2).

---

## 3. Output Schema: LOCKED_TOPIC_CARD

```json
{
  "lock_id": "UUID",
  "pre_topic_id": "UUID",
  "final_headline": "US Power Grid Emergency declared.",
  "lock_logic": "34-A (Expiry Lock)",
  "urgency_score": 10,
  "verdict": "LOCKED"
}
```

---

## 4. Mock Examples

### Mock 1: LOCKED (34-C Structure Lock)
- **Input**: US Dept of Energy Import Ban Signed.
- **Question**: "What happens to the US Grid when Chinese transformers are banned?"
- **Check**: Is it irreversible? Yes (Signed Law).
- **Verdict**: **LOCKED**.

### Mock 2: HOLD (Developing)
- **Input**: Federal Reserve Meeting Minutes Released.
- **Question**: "Why is the Fed debating rate hikes again?"
- **Check**: Is it final? No (Minutes are just discussion, not a Decision).
- **Verdict**: **HOLD**. (Wait for the Decision).

---

## 5. Absolute Prohibition
**Never** Lock a topic just to fill the slot.
If there are NO Locked Topics today, the engine outputs **NO_TOPIC**.
Silence is better than Noise.
