# Walkthrough - Phase 31 Isolation & Workflow Guard

Completed the isolation of Phase 31 (Learning/Narrative) from the production pipeline to ensure stability and separation of concerns.

## Changes Made

### 1. Execution Guard Implementation
Created a central guard utility and integrated it into all 12 narrative/learning modules:
- **Guard Module**: [guards.py](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/src/utils/guards.py)
- **Applied to**:
    - [youtube_watcher.py](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/src/narratives/youtube_watcher.py)
    - [transcript_ingestor.py](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/src/narratives/transcript_ingestor.py)
    - [narrative_analyzer.py](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/src/narratives/narrative_analyzer.py)
    - And 9 other modules in Phase 32-37.

### 2. Workflow Separation
Split the GitHub Actions workflows to isolate production and learning responsibilities:
- **Production Workflow**: [full_pipeline.yml](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/.github/workflows/full_pipeline.yml)
    - Set `ENABLE_LEARNING: false`.
    - Removed all Phase 31-37 steps and verifications.
    - Consolidated commit logic for production data and dashboard.
- **Learning Workflow**: [learning_pipeline.yml](file:///Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/.github/workflows/learning_pipeline.yml)
    - Set `ENABLE_LEARNING: true`.
    - Includes full Narrative/Learning pipeline (Phase 31-37).

## Phase 31 Isolation Policy
> [!IMPORTANT]
> **Isolation Policy v1.0**
> 1. Phase 31 logic is for **Learning/Analysis only** and MUST NOT run in the production pipeline.
> 2. All narrative modules MUST import and call `check_learning_enabled()` at their entry point.
> 3. Production pipeline (`full_pipeline.yml`) MUST keep `ENABLE_LEARNING` set to `false`.
> 4. Narrative outputs (proposals, etc.) are purely additive and do not affect Top 5 selection or scoring in production.

## Verification Results

### Local Guard Test
- **Mode: PROD (`ENABLE_LEARNING=false`)**
    - Result: `[GUARD] ENABLE_LEARNING is false or unset. Phase 31 execution skipped.`
    - Exit Code: 0 (Success/Skip)
- **Mode: LEARNING (`ENABLE_LEARNING=true`)**
    - Result: `[GUARD] ENABLE_LEARNING is true. Proceeding with Phase 31 execution.`
    - Action: Successfully processed YouTube sources and ingested transcripts.

### Workflow Configuration
- Verified `full_pipeline.yml` no longer contains narrative execution steps.
- Verified `learning_pipeline.yml` triggers on `workflow_dispatch` and a separate daily schedule.

## Operations Verification Report (Step 29)

### Live Dashboard Verification
- **Run ID**: PENDING (Pipeline Latency / User Action Required)
- **Artifact Verification**:
    - **Local**: SUCCESS. Manifest generator correctly flattens structure (`report_md` at root).
    - **Live (Repo)**: FAIL (Stale Data). Artifacts (`run_ts`) have not updated to reflect the latest run.
- **Cause Classification**: **CASE A** (Pipeline not executed or failed to commit).
- **Resolution**:
    - The code fixes in Step 28 are verified locally.
    - One successful run of `full_pipeline.yml` is required to refresh the live dashboard.
    - No further code changes are needed; only execution.
