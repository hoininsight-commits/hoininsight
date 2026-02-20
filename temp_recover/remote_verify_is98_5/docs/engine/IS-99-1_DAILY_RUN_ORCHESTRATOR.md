# IS-99-1 Daily Run Orchestrator & Artifact Exporter

This layer transforms the internal decision assets into human-readable and machine-readable operational outputs.

## 1. Goal
Convert `content_pack_multipack.json` into:
- `daily_upload_pack.md`: Human-readable briefing for manual copy-pasting.
- `daily_upload_pack.json`: Machine-readable package for automated pipeline tasks.
- `daily_upload_pack.csv`: Audit-trail for daily operations.

## 2. Orchestration Rules
- **No Logic Modification**: The orchestrator does not rewrite sentences or change tones. It merely selects and re-labels.
- **Fixed Structure**: 1 Long + 4 Shorts (as determined by IS-98-2a).

---

## 3. Governance Rule (Add-only)

This layer follows the **Add-only** principle. It creates files in the `exports/` directory without modifying any core sensing or interpretation logic.
