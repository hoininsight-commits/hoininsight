# Topic Probability Engine

The Topic Probability Engine evaluates early-stage signals from the Radar Layer and ranks them based on their likelihood of becoming a viable content topic for HOIN Insight.

## Purpose
Radar captures a wide net of potential structural shifts. The Probability Engine provides a deterministic prioritization layer so that the Topic Formatter can focus on the signals with the highest relevance and "convertibility."

## Scoring Methodology
The engine uses a 100-point `probability_score` calculated as a weighted average of 6 factors:

| Factor | Weight | Description |
| :--- | :--- | :--- |
| **Radar Strength** | 20% | Derived from the signal's initial intensity (HIGH/MEDIUM/LOW). |
| **Why Now Score** | 20% | Evaluates critical keywords (Shock, Breakthrough, War, Merger) in the signal's timing explanation. |
| **Convertibility** | 20% | Heuristics on how easily the signal can be translated into a compelling narrative. |
| **Mentionable** | 15% | Direct links to tickers, names, or sectors in the `mentionables.json` whitelist. |
| **Structural Alignment** | 15% | Consistency with the current `Regime State` and `Timing Gear`. |
| **Evidence Density** | 10% | Presence of the signal across multiple high-authority sources or fact-first feeds. |

## Workflow Integration
1. **Radar** captures raw news/data spikes.
2. **Probability Engine** (this layer) ranks them against the current macro context.
3. **Topic Formatter** takes the top-ranked signal to generate video candidate metadata.

## Schema
- **Output**: `data/ops/topic_probability_ranking.json`
- **Fields**:
  - `probability_score`: 0 (low) to 100 (high)
  - `supporting_factors`: Factors that increased the score.
  - `risk_factors`: Potential inhibitors identified.
