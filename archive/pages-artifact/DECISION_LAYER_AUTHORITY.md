# Decision Layer Authority

## Overview
The Decision Layer is the final gatekeeper for all content published to the dashboard.

## Authority Paths
- **Staging**: `data/decision/YYYY/MM/DD/final_decision_card.json`
- **Live SSOT**: `docs/data/decision/today.json`
- **Editorial**: `data/editorial/` -> `docs/data/decision/editorial/`

## Decision Artifacts
- `final_decision_card.json`: Contains the top topic, narrative score, and investment OS state.
- `editorial_selection_*.json`: Contains manual or AI-selected long/short picks.

## Decision Rules
1. **SSOT Rule**: No decision should be loaded by the UI unless it exists in `docs/data/decision/manifest.json`.
2. **Approval Rule**: Only topics marked as `APPROVED` or `SPEAKABLE_NOW` in `data/ops/` are eligible for primary card placement.
3. **Consistency Rule**: The `narrative_score` in the Decision Card must match the `final_narrative_score` in `narrative_intelligence_v2.json`.
