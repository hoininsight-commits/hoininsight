# IS-97-5 WHY-MUST RANKING LAYER

**Version**: v1.0 (2026-02-04)
**Type**: Deterministic Ranking Logic
**Source**: `src/topics/mentionables/why_must_ranking.py`

## 1. Philosophy: "Pickaxe Priority"
We do **not** rank entities by price appreciation potential or popularity.
We rank by **Structural Necessity** (Why-Must).
"If this entity disappears, does the thematic system collapse?"

## 2. Scoring Model (0.0 ~ 1.0)
Final Score = `0.35*B + 0.2*T + 0.2*E + 0.15*R + 0.1*C`

### A. BottleneckScore (B) - 35%
Hardcoded hierarchy based on physical constraints:
- **1.0**: `POWER_STORAGE`, `COOLING`, `GRID_INFRA` (Physics Layer)
- **0.8**: `SEMIS` (Compute Layer)
- **0.7**: `PICKS_SHOVELS` (Equipment)
- **0.4**: `FINANCIAL` (Capital)

### B. TimelineProximity (T) - 20%
- **0.9**: Standard Active Signal
- **0.2**: `HYPOTHESIS_JUMP (HOLD)` - "Too early" penalty.

### C. EvidenceStrength (E) - 20%
- Boosts for Official Stats / Gov Docs.

### D. Reliability (R) - 15%
- From Source Registry.
- **< 0.4**: Immediate DROP.

### E. CrossThemeReuse (C) - 10%
- Boosts entities that solve bottlenecks across multiple active themes (e.g. Copper for AI + Green).

## 3. Deduplication
- **Rule**: Max 2 entities per `Role`.
- **Logic**: Sort by Final Score, keep top 2, drop rest with reason "Duplicate Role cap exceeded".

## 4. Output
`data/decision/mentionables_ranked.json`
