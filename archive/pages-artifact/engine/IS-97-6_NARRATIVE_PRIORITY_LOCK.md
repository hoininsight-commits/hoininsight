# IS-97-6 NARRATIVE PRIORITY LOCK

**Version**: v1.0 (2026-02-04)
**Purpose**: Determinstically select one "Hero Topic".

## 1. Selection Philosophy
We do not publish "all available topics". We publish the **ONE** topic that structure demands right now.
Structure > Event.

## 2. Priority Logic
Score = `0.35*S + 0.2*B + 0.15*E + 0.15*T + 0.1*C`

### Factors
1. **Structural Weight (S)**
   - `STRUCTURAL_SHIFT` (1.0)
   - `REGIME_ACCELERATION` (0.8)
   - `CAPITAL_REPRICING` (0.6)
   - `BOTTLENECK_REVEAL` (0.5)

2. **Bottleneck Weight (B)**
   - `POWER/GRID` (1.0)
   - `SEMIS` (0.8)

3. **Evidence (E)** & **Timing (T)**
   - Boosts for recent events or high citation count.

## 3. Output
- **Hero Lock**: Status `LOCKED` if winner found. `NO_HERO_TODAY` if none eligible.
- **Hold Queue**: Top 5 runner-ups.
