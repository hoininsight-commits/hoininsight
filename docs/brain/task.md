# HoinInsight Restoration and Enhancement Tasks

- [x] **Fix CoinGecko BTC Collector** <!-- id: 0 -->
    - [x] Analyze `src/collectors/coingecko_btc.py` for API response structure assumptions. <!-- id: 1 -->
    - [x] Implement robust parsing for `last_updated_at` (fallback to current time if missing). <!-- id: 2 -->
    - [x] Add error handling for missing keys in the response. <!-- id: 3 -->
- [x] **Verify Pipeline Robustness** <!-- id: 4 -->
    - [x] Ensure `soft_fail` works for VIX (confirmed in logs & config). <!-- id: 5 -->
    - [x] Confirm BTC fix resolves the critical `output checks failed` error. <!-- id: 6 -->
- [x] **Phase 29: Narrative Drift Detection**
    - [x] Implement `NarrativeDriftDetector` (Acceleration/Saturation/Decay).
    - [x] Integrate drift signals into `daily_brief.md`.
    - [x] Add verification step to pipeline.
- [x] **Phase 30: Automated Insight Publishing**
    - [x] Create `ContentGenerator` for Script/Shotlist.
    - [x] Update pipeline to generate content artifacts.
    - [x] Verification checks for content generation.
- [x] **Auto Collection Expansion v1**
    - [x] Expand registry with 6 new axes (Indices, FX, Rates, Commodities, Metals, Crypto).
    - [x] Implement generic soft-fail collectors and normalizers.
    - [x] Verification for registry expansion.
- [x] **Insight Dashboard v1**
    - [x] Create `DashboardGenerator` for file-based status and HTML dashboard.
    - [x] Integrate dashboard generation into pipeline.
    - [x] Artifact upload setup.
- [x] **Dashboard Deployment v1**
    - [x] Create `deploy_dashboard.yml` for GitHub Pages.
    - [x] Configure manual/automated deployment to `gh-pages` branch.
    - [x] Fix: Enable GitHub Pages settings via CLI (User Request).
- [x] **Insight Dashboard v2**
    - [x] Redesign for "Data Collection Health" (Category-based status).
    - [x] Implement OK/SKIP/FAIL logic.
    - [x] Fix: Add missing `requests` dependency to `pyproject.toml`.
    - [x] Fix: Correct function signatures for collectors and normalizers.
- [x] **Dashboard v2 JSON-based Status Tracking**
    - [x] Modify `run_collect.py` to record collection status to JSON.
    - [x] Update `dashboard_generator.py` to read from JSON instead of file checks.
    - [x] Verify in CI pipeline and deploy to GitHub Pages.
- [x] **Fix Remaining Dashboard Failures**
    - [x] Implement mock fallback for `stooq_vix.py`.
    - [x] Implement mock fallback for derived normalizers.
    - [x] Update `run_normalize.py` to record status in JSON.
    - [x] Verify clean run in CI and deploy.
- [x] **Refine Dashboard Status Logic**
    - [x] Detect "mock" source in `run_collect.py` and set SKIP status.
    - [x] Preserve SKIP status in `run_normalize.py`.
    - [x] Preserve SKIP status in `run_normalize.py`.
    - [x] Verify SKIP status on deployed dashboard.

- [x] **Auto Schedule v1**
    - [x] Refactor `run_collect` and `run_normalize` to accept category filter.
    - [x] Update `engine.py` to support category filtering.
    - [x] Create `run_pipeline.py` CLI entrypoint with Axis mapping.
    - [x] Create split GitHub Actions workflows (Crypto, FX, US Markets, Backfill).
    - [x] Validate schedules and execution.

- [x] **Dashboard UI Revamp (v5: Architecture Layout)**
    - [x] Implement Main Process Flow (Scheduler -> Engine -> Output).
    - [x] Implement Right Sidebar (Detailed Data Intake Status).
- [x] **Dashboard Localization (v5.1)**
    - [x] Translate all UI labels to Korean.
    - [x] Regenerate and Verify.

- [x] **Dashboard Feature: Show Content Topic**
    - [x] Extract topic title from Meta Topics or Script.
    - [x] Display in 'Content Generation' node.
    - [x] Click-to-open Modal for full script content (No truncation).
    - [x] Screenshot & Review.

- [x] **Batch Timing Optimization v1**
    - [x] Create `data/ops/workflow_runtime_v1.json` (Profile Data).
    - [x] Calculate optimal schedules (Overlap/Buffer analysis).
    - [x] Update Workflow YAMLs (Cron & Comments).
    - [x] Implement Verification Log logic in Engine.
    - [x] Verify & Report.

- [x] **Ops Upgrade v1: Core Dataset & Reliability**
    - [x] Implement Core Dataset Resolver (`src/ops/core_dataset.py`).
    - [x] Implement Regime Confidence Logic (`src/ops/regime_confidence.py`).
    - [x] Integrate Confidence into `daily_brief.md`.
    - [x] Add Core Health Widget & Confidence Badge to Dashboard.
    - [x] Add CI Verify Steps for Core Dataset Confidence.
    - [x] Local Verification & Screenshot Proof.

- [x] **Ops Upgrade v1.1: Confidence-Based Content Gate** <!-- id: 7 -->
    - [x] Create `src/ops/content_gate.py` (Rule Engine). <!-- id: 8 -->
    - [x] Update `src/reporters/content_generator.py` to enforce gate (Skip/Cautious). <!-- id: 9 -->
    - [x] Update `src/reporters/daily_report.py` to show Content Status. <!-- id: 10 -->
    - [x] Update `src/dashboard/dashboard_generator.py` (Status Card & Tooltip). <!-- id: 11 -->
    - [x] Add CI Verify Step for Content Control. <!-- id: 12 -->
    - [x] Verify & Commit. <!-- id: 13 -->

- [x] **Ops Upgrade v1.2: Content Preset (Depth Auto-Adjust)** <!-- id: 14 -->
    - [x] Create `src/ops/content_preset_selector.py`. <!-- id: 15 -->
    - [x] Update `src/reporters/content_generator.py` to apply presets (BRIEF/STANDARD/DEEP). <!-- id: 16 -->
    - [x] Update `src/reporters/daily_report.py` to show Content Preset. <!-- id: 17 -->
    - [x] Update `src/dashboard/dashboard_generator.py` to show Preset Badge. <!-- id: 18 -->
    - [x] Add CI Verification Step for Content Preset. <!-- id: 19 -->
    - [x] Verify & Commit. <!-- id: 20 -->

- [x] **Fix Dashboard CI Failure** <!-- id: 21 -->
    - [x] Investigate `Generate Insight Dashboard` failure in Run #40. <!-- id: 22 -->
    - [x] Fix handling of empty/soft-failed datasets in dashboard generator. <!-- id: 23 -->
    - [x] Verify fix with new CI run (Run #43). <!-- id: 24 -->
    - [x] Automate Dashboard Deployment (Trigger `deploy_dashboard.yml` on pipeline completion). <!-- id: 25 -->

- [x] **Ops Upgrade v1.3: CI Reliability (Switch to yfinance)** <!-- id: 26 -->
    - [x] Update `pyproject.toml` to add `yfinance`. <!-- id: 27 -->
    - [x] Migrate `stooq_spx.py` to use `yfinance` (`^GSPC`). <!-- id: 28 -->
    - [x] Migrate `stooq_vix.py` to use `yfinance` (`^VIX`). <!-- id: 29 -->
    - [x] Migrate `stooq_kospi.py` to use `yfinance` (`^KS11`). <!-- id: 30 -->
    - [x] Local verify of modified collectors. <!-- id: 31 -->
    - [x] Deploy and verify full green board in CI (Verified Clean Run #46). <!-- id: 32 -->

- [x] **Ops Upgrade v1.4: Normalizer Fixes (yfinance Compatibility)** <!-- id: 33 -->
    - [x] Fix path mismatch in `spx_curated.py`, `vix_curated.py`, `kospi_curated.py`. <!-- id: 34 -->
    - [x] Fix path and key mismatch in `btc_curated.py` (close vs price_usd). <!-- id: 35 -->
    - [x] Fix path and key mismatch in `us10y_curated.py` (close vs yield_pct). <!-- id: 36 -->
    - [x] Local Verification (CSVs generated). <!-- id: 37 -->
    - [x] Deploy and Verify (Run #49). <!-- id: 38 -->

- [x] **Ops Upgrade v1.4.1: Dashboard Reliability (Run #50 & #51)**
    - [x] Fix Dashboard FAIL status by checking data file existence.
    - [x] Fix Regime Confidence FAIL status by checking data file existence.
    - [x] Verify Green Status.

- [x] **Ops Upgrade v1.5: Full yfinance Migration (FX & Metals)** <!-- id: 39 -->
    - [x] Migrate `exchangerate_usdkrw.py` to yfinance (`KRW=X`). <!-- id: 40 -->
    - [x] Migrate `goldapi_xau.py` to yfinance (`GC=F`). <!-- id: 41 -->
    - [x] Migrate `goldapi_xag.py` to yfinance (`SI=F`). <!-- id: 42 -->
    - [x] Update normalizers (`usdkrw`, `xau`, `xag`) for new paths/keys. <!-- id: 43 -->
    - [x] Verify Full Green Dashboard. <!-- id: 44 -->

- [x] **Phase 31-A: YouTube Watcher & Transcript Ingestion** <!-- id: 45 -->
    - [x] Create `registry/narrative_sources.yml` with "경제사냥꾼". <!-- id: 46 -->
    - [x] Create `src/narratives/youtube_watcher.py` (New video detection). <!-- id: 47 -->
    - [x] Create `src/narratives/transcript_ingestor.py` (Captions/Desc). <!-- id: 48 -->
    - [x] Create `src/narratives/narrative_status.py` (Status tracking). <!-- id: 49 -->
    - [x] Add `youtube-transcript-api` to `pyproject.toml`. <!-- id: 50 -->
    - [x] Update `full_pipeline.yml` to run watcher/ingestor and verify. <!-- id: 51 -->
    - [x] Verify execution and data persistence. <!-- id: 52 -->

- [x] **Ops Upgrade v1.6: Status Standardization** <!-- id: 53 -->
    - [x] Define SUCCESS (Core OK) / PARTIAL (Derived Fail) rules. <!-- id: 54 -->
    - [x] Normalize Narrative Status (`INGESTION_OK`). <!-- id: 55 -->
    - [x] Integrate `latest_video` metadata. <!-- id: 56 -->
    - [x] Add CI Verification for Status Integrity. <!-- id: 57 -->

