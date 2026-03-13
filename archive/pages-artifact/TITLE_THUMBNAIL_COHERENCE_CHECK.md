# TITLE_THUMBNAIL_COHERENCE_CHECK.md
# (Economic Hunter – Step 28)

## 0. Purpose
This engine is the **Final Quality Control**.
It places the Title (Step 26) and Thumbnail (Step 27) side-by-side.

It answers:
> "Do these two assets tell **One Story**?"
> "Or do they say the same thing twice?"

**The Golden Rule**:
**Thumbnail = The Problem (State).**
**Title = The Cause (Logic).**

---

## 1. The 3-Step Coherence Test

A Pair MUST pass all 3 checks.

### Check A: The Redundancy Test
- **Fail Condition**: The text in the Title is visually repeated in the Thumbnail.
- *Example (Fail)*: Title says "Transformer Shortage" and Thumbnail shows text "SHORTAGE".
- *Rule*: **Zero Text on Thumbnail.** The Image handles the Noun, Title handles the Verb.

### Check B: The Complementarity Test
- **Pass Condition**: The Thumbnail creates a *Question* that the Title *Answers*.
- *Example (Pass)*:
    - **Thumb**: A darkened city grid (Question: Why is it dark?).
    - **Title**: "40-Month Lead Times force US Utilities to Ration Power." (Answer: Shortage).

### Check C: The Tonal Match
- **Pass Condition**: Both share the same "Hunter Grade" (Serious/Structural).
- *Fail Condition*: Serious Title + Cartoon Thumbnail. Or Crisis Thumbnail + Hype Title.

---

## 2. Title Types & Rules (Contextual)

How the Title interacts with the Image.

| Title Formula (Step 26) | Best Thumbnail Type (Step 27) | Logic |
| :--- | :--- | :--- |
| **Formula A (Collision)** | **Type A (Collision)** | Visual and Text match impact. |
| **Formula B (Time-Force)** | **Type D (Barrier)** | Title says "Force", Image shows "The Wall". |
| **Formula C (Mechanism)** | **Type B (Void)** | Title says "Mechanism", Image shows "The Missing Piece". |
| **Formula D (Gap)** | **Type C (Scale)** | Title says "Reality Gap", Image shows "Imbalance". |

---

## 3. Output Schema: TITLE_THUMBNAIL_LOCK_SPEC

```json
{
  "lock_spec_id": "UUID",
  "topic_id": "UUID",
  "final_package": {
    "title_text": "...",
    "thumbnail_logic": "...",
    "coherence_verdict": "PASS"
  },
  "visual_verb_pairing": {
    "visual_state": "Empty Warehouse (The Void)",
    "verbal_cause": "Import Ban (The Force)"
  }
}
```

---

## 4. Mock Examples

### Mock 1: PASS (Perfect Complement)
- **Topic**: UHV Transformer Shortage.
- **Thumbnail (State)**: A massive, dark electrical substation silhouetted against a grey sky. One empty concrete pad in the foreground. (Type B: Void).
- **Title (Cause)**: "US DOE Ban forces Utilities into a 4-Year Wait." (Formula B: Time-Force).
- **Coherence**:
    - *Redundancy*: None. Image shows absence; Title explains why.
    - *Complement*: Image asks "Where is it?"; Title says "Banned and delayed."
    - *Verdict*: **PASS**.

### Mock 2: REJECT (Redundant & Weak)
- **Topic**: UHV Transformer Shortage.
- **Thumbnail (State)**: A picture of a transformer with a red arrow going down and text "CRISIS".
- **Title (Cause)**: "Transformer Crisis is here: Supply Chain Broken."
- **Coherence**:
    - *Redundancy*: **FAIL**. "Crisis" is in both title and image text.
    - *Complement*: **FAIL**. Both just scream "Bad thing". No structural logic.
    - *Verdict*: **REJECT**. (Reason: Redundant and low-quality visual).

---

## 5. Absolute Prohibition
**Never** allow a "Mystery Meat" thumbnail.
If the image is just a generic stock photo of people shaking hands, **KILL IT**.
The image must be a **Specific Structural Object**.
