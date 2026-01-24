# TOPIC_DECISION_GATE_v1.0 (CONTENT LAYER)

## 0. PURPOSE (DO NOT MODIFY)
This layer exists to ensure:
- **At least one content-worthy topic is produced every run/day.**
- It is **NOT** a replacement for HOIN ENGINE Structural/Anomaly logic.
- It is a **parallel, separate output stream**.

> Structural Engine may output "no topic" (valid).
> Content Topic Gate must output **TOP 1 always** (no "none").

---

## 1. NON-GOALS
This layer does NOT:
- Predict market direction
- Recommend stocks
- Produce anomaly levels (L2/L3/L4)
- Use Z-score as a gating requirement
- Reuse Structural "Insight Script" templates
- Auto-map leaders (e.g., "Tightening -> banks") as default outputs

---

## 2. REQUIRED OUTPUTS
The Gate must generate:
1) **Candidates >= 3** (question-form)
2) **Top 1** selected (forced; no empty state)
3) An output object containing:
   - Title (short)
   - Question (why-form)
   - Why people are confused
   - Key reasons (2~3)
   - Numbers (0~3) — optional
   - Risk (1)
   - Confidence (LOW/MEDIUM/HIGH) meaning "content-worthiness"
   - Optional handoff flag to Structural (boolean only)

---

## 3. EXECUTION STEPS (LOCKED)
### STEP 1 — Candidate Generation (min 3)
Generate candidates from "market scenes" that trigger confusion:
- earnings_up_price_down
- index_up_sector_down
- good_news_price_down
- bad_news_price_up
- policy_announced_market_inverse
- narrative_shift

Candidates must be written as **questions**.

### STEP 2 — Ranking (content value)
Rank by:
- confusion/hook strength
- explainability with 2~3 datapoints
- timeliness (why now)
- simplicity (can explain with minimal evidence)

### STEP 3 — Forced Selection
Pick TOP 1 ALWAYS.
"no topic" is forbidden.

### STEP 4 — Loose Validation (optional)
Try to attach 0~3 numbers (from existing daily snapshot).
If numbers are missing:
- still output TOP 1
- set confidence LOWER

### STEP 5 — Optional Handoff Flag
Only set `handoff_to_structural=true` if:
- evidence refs indicate **2+ distinct data axes**
- and at least 2 numbers (or equivalent objective evidence) exist

This does NOT create/modify structural topics.
It only marks a handoff candidate.

---

## 4. HARD PROHIBITIONS (GUARDRAILS)
- No L-levels (L2/L3/L4) in Gate output.
- No Z-score fields in Gate output.
- No Structural anomaly logic references in Gate output.
- No automatic "theme leader" mapping in Gate output.
- No reuse of Structural "Insight Script" template blocks.
- Topic entity must not be unrelated to evidence refs.

---

## 5. STORAGE (MUST SEPARATE)
Gate outputs must be stored separately from Structural outputs:
- `data/topics/gate/YYYY/MM/DD/topic_gate_candidates.json`
- `data/topics/gate/YYYY/MM/DD/topic_gate_output.json`

Structural outputs remain unchanged.

---

## 6. FINAL LOCKED SENTENCE
> Content Topic Gate exists to force topic selection for content,
> while Structural Engine preserves strict anomaly/WHY_NOW discipline.
