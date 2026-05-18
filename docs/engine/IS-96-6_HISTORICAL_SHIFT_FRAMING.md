# IS-96-6 HISTORICAL SHIFT FRAMING LAYER

**Version**: v1.0 (2026-02-04)
**Type**: Deterministic Decision Layer (No Generative AI)
**Source**: `src/topics/interpretation/historical_shift_framing.py`

## 1. Purpose
Upgrades standard interpretations into "Regime Shift" declarations when severity is high. This layer acts as a final "Gravity Check" before narrative generation.

## 2. Trigger Logic
A logic unit triggers a Historical Shift Frame if:
1.  **Interpretation Key** matches a defined Theme (see below).
2.  **AND** one of the following is true:
    - `confidence_score` >= 0.8
    - `hypothesis_jump.status` == "READY"

## 3. Supported Themes & Templates
The following templates are hardcoded and additive-only.

### A. LABOR_MARKET_SHIFT
- **Shift Type**: `LABOR_MARKET_REGIME_SHIFT`
- **Claim**: "This is not a trend; it is the collapse of a decades-old equilibrium between Capital and Labor."
- **Focus**: Erosion of White Collar Degree Premium vs. Rise of Body Sovereignty (Blue Collar).

### B. AI_INDUSTRIALIZATION
- **Shift Type**: `INDUSTRIAL_REVOLUTION_PHASE_SHIFT`
- **Claim**: "We are moving from the 'Software Era' (Zero Marginal Cost) to the 'Industrial AI Era' (High CapEx cost)."
- **Focus**: Compute as physical energy/steel constraint.

### C. INFRASTRUCTURE_SUPERCYCLE
- **Shift Type**: `CAPEX_CYCLE_INVERSION`
- **Claim**: "The era of 'Capital Light' growth is over; the era of 'Heavy Asset' dominance has begun."
- **Focus**: Interest rates vs. Physical necessity.

## 4. Output Contract
File: `data/decision/historical_shift_frame.json`
```json
{
  "target_sector": "PHYSICAL_AI_INFRA",
  "shift_type": "LABOR_MARKET_REGIME_SHIFT",
  "historical_claim": "...",
  "what_changed": ["...", "..."],
  "what_breaks_next": ["..."]
}
```

## 5. Narrative Integration
The `NarrativeSkeletonBuilder` (`is96-3`) consumes this frame:
- **Hook Override**: Prepend `[SHIFT_TYPE] {Historical Claim}` to the generated hook.
- **Era Block**: Adds `era_declaration_block` to the skeleton JSON.
