# IS-99-2 GitHub Actions Daily Scheduler

This layer automates the daily execution of the HOIN Engine and ensures that operational artifacts are generated and stored consistently.

## 1. Automation Schedule
- **Time**: 08:00 Asia/Seoul (KST)
- **UTC Equivalent**: 23:00 UTC (Previous Day)
- **Frequency**: Daily

## 2. Trigger Options
- **Scheduled**: Runs automatically at the defined cron time.
- **Manual (workflow_dispatch)**: Allows manual triggering via the GitHub Actions UI.
  - `commit_back`: A boolean flag (default `false`) to determine if generated exports should be committed back to the `main` branch.

## 3. Artifacts & Outputs
- **GHA Artifacts**: All runs upload the `exports/` and `data/decision/` directories as a ZIP artifact named `daily-content-pack`.
- **Commit-back**: If enabled, `exports/daily_upload_pack.md/json/csv` are pushed to `origin/main`.

## 4. Governance Rule (Add-only)
The scheduler only manages the execution flow. It does not modify upstream sensing, interpretation, or constitutional documents (`DATA_COLLECTION_MASTER.md`, etc.).
