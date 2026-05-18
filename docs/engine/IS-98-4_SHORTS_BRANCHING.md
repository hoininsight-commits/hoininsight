# IS-98-4 SHORTS BRANCHING LAYER

**Version**: v1.0 (2026-02-04)
**Purpose**: Branch a single Hero Topic into multiple distinct Shorts angles to maximize content diversity and distribution.

## 1. The 4 Angles
Every Hero Topic is deterministically branched into the following 4 perspectives:

| Angle | Name | Focus | Core Hook Style |
| :--- | :--- | :--- | :--- |
| **1** | **Macro Structural** | Large-scale paradigm shift | "The world is changing..." |
| **2** | **Pickaxe Alpha** | Specific company/bottleneck | "The real winner is..." |
| **3** | **Data Signal** | Precise number/evidentiary data | "Look at the numbers..." |
| **4** | **Risk/Contrarian** | Warning or counter-narrative | "Why experts are wrong..." |

## 2. Constraints (Deterministic)

### A. Citation Guard
- Any sentence classified as a "Factual Evidence" or "Data Claim" MUST have a corresponding reference in `evidence_citations.json`.
- If a sentence requires a citation but lacks one, it is **silently removed**. No "softening" or "hallucinating" replacements are allowed.

### B. Overlap Cap (30%)
- The word-level overlap (Jaccard similarity) between any two branched shorts must not exceed 30% (excluding boilerplate template structural text).
- This ensures that an operator can upload multiple shorts for the same topic without triggering platform duplication flags.

### C. Hypothesis Disclaimer
- For `HYPOTHESIS_JUMP` topic types, every branch MUST append the mandatory disclaimer:
  > "⚠️ 이건 확정이 아니라 '촉매 기반 가설'입니다."

## 3. Output
- `exports/shorts_angle_1.txt` ... `shorts_angle_4.txt`
- `data/decision/shorts_pack.json` (Structured output for automation)
