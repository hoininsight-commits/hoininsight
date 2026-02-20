# IS-66 Editorial Mode Implementation Plan

## Goal
Transform the dashboard into an "Operator's Edit Mode" where content candidates are immediately visible, script-ready, and actionable, even if they don't meet the strict `TRUST_LOCKED` criteria.

## User Review Required
- **New Status:** `EDITORIAL_CANDIDATE` (Between `HOLD` and `TRUST_LOCKED`).
- **Script Structure:** 5-step (Definition, Surface, Misread, Structural Force, Conclusion).
- **Dashboard Layout:** Top section now lists "Content Candidates" (1-3 items) instead of a single pinned topic or silence.

## Proposed Changes

### [IssueSignal] Logic Update
#### [MODIFY] src/issuesignal/run_issuesignal.py
- Update `determine_final_status` (or equivalent logic block):
    - Check for `EDITORIAL_CANDIDATE` criteria if not `TRUST_LOCKED`.
    - Criteria: `HARD_FACT >= 1` AND `WHY_NOW exists` AND (`Corporate` OR `Capital` OR `Bottleneck`).
- Ensure `DecisionCard` can hold multiple "Candidates" if we decide to export list, OR just ensure the *primary* candidate and potential secondary ones are saved. 
    - *Note:* The user wants "1~3 topics". Currently `final_decision_card.json` represents *the* decision. I might need to augment `final_decision_card.json` to include `candidates_list` or modify `top_topics` in `today.json`.
    - *Plan:* `run_issuesignal.py` currently selects ONE. I should modify it to populate `editorial_candidates` list in the `DecisionCard` output containing top 3 filtered by the new criteria.

#### [MODIFY] src/issuesignal/script_lock_engine.py
- Update `generate` to produce the **5-step structure**.
- Ensure tone is strictly Korean declarative.

### [Dashboard] UI Overhaul
#### [MODIFY] src/dashboard/dashboard_generator.py
- **Top Section:** Rename to "📌 오늘의 콘텐츠 후보 (EDITORIAL VIEW)".
- **Logic:**
    - Read `editorial_candidates` from `final_card` (or `top_topics` if mapped there).
    - Render cards for up to 3 candidates.
    - Each card: Title, WhyNow, Badge (`EDITORIAL` or `LOCKED`), Collapsible Script.
- **Terminology:** Replace all remaining English terms (SPEAK/WATCH/HOLD/SILENT) with Korean equivalents in the UI rendering map.

## Verification Plan
1. **Unit Test:** `tests/verify_is66_editorial_logic.py` - Verify status classification and script generation.
2. **Visual Check:** Generate dashboard and verify "Content Candidates" section appears with Korean UI.
