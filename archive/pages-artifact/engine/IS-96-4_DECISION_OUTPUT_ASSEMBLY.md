# IS-96-4 Decision Output Assembly Layer

This document defines the **Decision Output Assembly Layer**, which standardizes and persists the results of the complete IS-96 interpretive pipeline.

## 1. Aggregation Purpose

The Decision Output Assembly Layer takes the fragmented outputs from Interpretation (IS-96-1), Speakability (IS-96-2), and Narrative Skeleton (IS-96-3) and bundles them into high-integrity data assets. This ensures that downstream consumers (Dashboard, Telegram, TTS Engines) have a single source of truth for the engine's "Decision".

---

## 2. Output Schema & Files

The layer generates three primary JSON files in `data/decision/`:

### 2-1. `interpretation_units.json`
- **Source**: IS-96-1
- **Content**: Raw structural interpretations, evidence tags, and derived metrics.
- **Scope**: Multi-sector interpretations for the daily run.

### 2-2. `speakability_decision.json`
- **Source**: IS-96-2
- **Content**: `READY/HOLD/DROP` mapping for each interpretation unit, including deterministic reasons.

### 2-3. `narrative_skeleton.json`
- **Source**: IS-96-3
- **Content**: Structurally formatted script skeletons (HOOK, CLAIM, etc.) for `READY` and `HOLD` topics.

---

## 3. Persistence Policy

- **Atomic Writes**: All three files must be updated simultaneously during a pipeline run to prevent cross-layer desynchronization.
- **Add-only History**: Each run should ideally timestamp the outputs or append to a daily log (standard project pattern).
- **No Manual Edits**: These files are system-generated and must not be manually modified to maintain the audit trail from sensing to decision.

---

## 4. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates a new output directory and files but does not interfere with the logic of previous sensing or signaling layers. It serves as the final "Handover" point to the communication layer.
