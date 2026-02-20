# NARRATIVE_COMPRESSION_ENGINE_18.md
# (Economic Hunter – Step 18)

## 0. Purpose

This engine is the **Final Compressor**.
It takes the filtered, fused, and gap-checked findings (Steps 1~17)
and reduces them to a **10-Second Insight**.

If it takes more than 10 seconds to explain,
it is not an Opportunity. It is a Lecture.
We do not lecture. We hunt.

---

## 1. The 10-Second Narrative Architecture

Every narrative must fit into the `ECONOMIC_HUNTER_NARRATIVE_CARD`.
It consists of exactly 4 components.

### 1. The One-Liner (The Arrow)
Structure: **"[Trigger]** has forced **[Structure]** to **[Action]**."
- *Constraint:* Max 15 words. No fluff.

### 2. The Sub-Line (The Reinforcement)
Structure: "**[Expectation]** was wrong because **[Reality]** is irreversible."
- *Constraint:* Explains the "Gap" (Step 17).

### 3. The Hidden Assumption (The Pivot)
Structure: "Market assumes **[A]**, but **[B]** is now the law."
- *Constraint:* Explicitly names the false belief.

### 4. The Kill-Switch (The Safety)
Structure: "Invalid only if **[Condition]**."
- *Constraint:* Binary outcome only.

---

## 2. The Economics Hunter Sentence Test

Before output, every narrative runs through this filter:

1.  **Does it mention a price target?** → **FAIL** (Reject).
2.  **Does it use future tense ("Will")?** → **FAIL** (Must use "Is" / "Has").
3.  **Is the victim/spender clear?** → **FAIL** (Must name the forced actor).
4.  **Is it boring?** → **FAIL** (Must imply tension).

---

## 3. Output Schema: ECONOMIC_HUNTER_NARRATIVE_CARD

```json
{
  "narrative_id": "UUID",
  "one_liner": "Headline text.",
  "sub_line": "Support text.",
  "hidden_assumption": "What market gets wrong.",
  "kill_switch": "What kills the trade.",
  "tone_grade": "URGENT / CLINICAL"
}
```

---

## 4. Mock Examples

### Mock A: POLICY-Driven (Lock)
- **One-Liner**: "IMO Carbon Mandate has forced Global Clean Tankers to zero capacity."
- **Sub-Line**: "Shipping rates are ignored, but the Replacement Cycle is legally mandatory."
- **Assumption**: "Market assumes Shipping is cyclic; but this is statutory survival."
- **Kill-Switch**: "Invalid only if IMO delays the 2027 deadline."

### Mock B: SPEECH-Driven (Watch)
- **One-Liner**: "Fed Chair's 'Panic Pivot' has forced Bond Markets to re-price liquidity."
- **Sub-Line**: "Inflation fear was wrong because Liquidity Crisis is irreversible."
- **Assumption**: "Market assumes Higher-for-Longer; but Fed admitted breakage."
- **Kill-Switch**: "Invalid only if next CPI prints above 4.0%."

### Mock C: SUPPLY-Driven (Lock)
- **One-Liner**: "AI Power Demand has forced US Utilities to bypass Buy-American laws."
- **Sub-Line**: "Domestic protectonism was wrong because Blackout Risk is irreversible."
- **Assumption**: "Market assumes Regulation blocks imports; but Physics overrides Regulation."
- **Kill-Switch**: "Invalid only if US DOE vetoes the emergency waivers."

---

## 5. Absolute Prohibitions

- **No "Hope"**: Don't say "We hope X happens." Say "X is happening."
- **No "Should"**: Don't say "Govt should spend." Say "Govt is spending."
- **No Jargon**: No "EBITDA", "RSI", "Fibonacci". Speak English.

The Narrative is not about **Finance**.
It is about **Force**.
