# IS-98-3 SCRIPT FINALIZATION LAYER

**Version**: v1.0 (2026-02-04)
**Purpose**: Transform deterministic narrative assets into final Shorts/Long scripts.

## 1. Philosophy
The engine dictates the script. The operator reads it.
Tone is "Economic Hunter": Confidence based on Structure, not hype.

## 2. Templates
Located in `registry/templates/script_templates_v1.yml`.

### Shorts (~60s)
1. **HOOK**: Punchy, counter-intuitive.
2. **CLAIM**: The Structural Declaration.
3. **EVIDENCE**: 3-Eye list.
4. **PICKAXE**: Top 2 companies (Why-Must).
5. **CLOSE**: "Invest in structure".

### Long (~3-5m)
1. **INTRO**: Context and Sector.
2. **MECHANISM**: Why the price/structure is moving.
3. **WHY NOW**: Detailed 3-Eye expansion.
4. **DEEP DIVE**: Focus on the Dominant Eye (e.g. Rigidity).
5. **PICKAXE**: Detailed company roles.
6. **RISK**: Counter-arguments.
7. **OUTRO**: Final conviction.

## 3. Citation Guard
- Every major assertion must be backed by the `evidence_citations` or marked as Hypothesis.
- `HYPOTHESIS_JUMP` topics include a mandatory disclaimer.

## 4. Output
- `exports/final_script_shorts.txt`
- `exports/final_script_long.txt`
