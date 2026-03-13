# Implementation Plan - Step 71: Economic Hunter Narrative Layer

## Goal Description
Implement the **Economic Hunter Narrative Layer** to transform raw "Structural Top-1" topics into compelling, operator-centric narratives (scripts) using the empirically derived 4-step structure (Hook, Tension, Hunt, Action). This replaces the basic `IssueSignalNarrativeBuilder`.

## User Review Required
> [!IMPORTANT]
> **Deterministic Templates**: The system will use strict string templates for the "Hook" and "Action" sections to avoid LLM hallucinations. This might result in slightly repetitive phrasing across different days, but guarantees structural consistency.

## Proposed Changes

### [OPS] Operation Modules

#### [NEW] [src/ops/economic_hunter_narrator.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/ops/economic_hunter_narrator.py)
A new class `EconomicHunterNarrator` that replaces `IssueSignalNarrativeBuilder`.
*   **Input**: `data/ops/structural_top1_today.json`
*   **Logic**:
    *   **Rule 1 (Hook)**: Generates a counter-intuitive question using the `title`.
    *   **Rule 2 (Tension)**: Explains the `structure_type` mechanics using `one_line_summary`.
    *   **Rule 3 (The Hunt)**: Formats `structural_drivers` into a numbered evidence list.
    *   **Rule 4 (Action)**: Combines `why_now` and `risk_factor` into a trading call.
*   **Output**: `data/ops/issue_signal_narrative_today.json` and `.md`.

#### [MODIFY] [src/engine.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/engine.py)
*   Replace the execution of `IssueSignalNarrativeBuilder` with `EconomicHunterNarrator`.

### [DASHBOARD] UI Updates

#### [MODIFY] [src/dashboard/dashboard_generator.py](file:///Users/jihopa/.gemini/antigravity/scratch/HoinInsight/src/dashboard/dashboard_generator.py)
*   Update the "Top-1 Narrative" section in the modal to strictly follow the 4-step structure.
*   Ensure the UI renders the "Hook" as a headline and "Action" as a highlighted box.

## Verification Plan

### Automated Tests
*   **Dry Run**: Execute `python3 src/ops/economic_hunter_narrator.py` manually.
*   **Output Check**: Verify `data/ops/issue_signal_narrative_today.md` contains all 4 headers: "The Hook", "Core Tension", "The Hunt", "Action".

### Manual Verification
*   **Dashboard Check**: Open the generated dashboard and verify the Top-1 modal displays the new narrative format correctly without `None` or broken strings.
