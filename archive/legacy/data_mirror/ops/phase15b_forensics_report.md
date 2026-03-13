# Phase 15B Conflict Logic Forensics Report

## 1. Executive Summary

The investigation into the 0% `conflict_flag` activation rate reveals that the issue is primarily driven by **overly restrictive mandatory multi-signal conditions** combined with **sparse semantic descriptions** in the incoming data. 

While the logic itself is functional (as proven by forced tests), real-world topics rarely contain the specific combination of opposing keywords required to trigger a "Conflict" pattern within a single topic card.

## 2. Evidence Analysis

### A) Logic Gate Restrictiveness (A)
Current patterns (e.g., `Tightening_Inflow`, `GeoRisk_Rally`) use a strict `AND` logic between two keyword sets. 
- **Example**: A topic about "FED Rate Hike" only triggers `Tightening`. To trigger a conflict, it *must* also mention an "Inflow" or "Buy" signal in the same text block. 
- **Observation**: In the last 7 days (384 topics), only **33.3%** of topics matched more than one structural axis, and even fewer matched the specific opposing pairs required for conflict.

### B) Data Sparsity & Direction Convergence (B, C)
The intermediate values in `conflict_mid_values.json` show that for most anomaly-driven topics:
- `inflation_level`, `rate_direction`, etc., are often detected in isolation.
- `asset_price_direction` is frequently missing because the system categorizes it as a "Macro" anomaly rather than a "Market" move, even if the price is affected.
- Directional convergence (all signals pointing the same way) is common, but "Conflict" by definition requires divergence, which is semantically rarer in raw automated summaries.

## 3. Forced Experiment Results

| Scenario | Result | Matched Pattern |
| :--- | :--- | :--- |
| CPI Spike + Rate Hike | **True** | `Macro_Price_Divergence` |
| VIX Spike + Index Crash | **True** | `GeoRisk_Rally` (Semantic Overlap) |
| Yield Curve Inversion | **False** | None |

- **Insight**: Case 2 triggered because "VIX **Surge**" matched the `AssetRally` keyword `SURGE`, highlighting a semantic collision where a "risk surge" is treated as a "price rally".

## 4. Conclusion & Recommendations

### Root Cause
- **Primary**: The logic requires a "Perfect Storm" of semantic matching (Pattern A) that the current narrative generation (sparse 1-2 sentence rationales) doesn't provide.
- **Secondary**: Input values aren't "None", but they are "Single-Axis", making "Cross-Axis Conflict" theoretically impossible for them.

### Non-Structural Improvements (Allowed)
1. **Keyword Normalization (Done)**: Already improved in Phase 15, which slightly increased detection but didn't solve the "AND" gate bottleneck.
2. **Context Enrichment**: If the Topic Generator (upstream) included more comparative data (e.g., "despite X, Y happened"), the current Conflict logic would trigger more frequently.
3. **Semantic Disambiguation**: Refine keywords like `SURGE` or `CRASH` to be axis-specific to avoid false positives (like VIX Surge triggering Rally pattern).

### Final Status
The Conflict Detection system is **not broken**, but it is **over-engineered** for the current level of narrative detail provided by the engine. It is a "Stamina" issue where the logic is waiting for a signal that is currently being filtered out or simplified upstream.

**No structural change is recommended at this layer until the upstream narrative richness is increased.**
