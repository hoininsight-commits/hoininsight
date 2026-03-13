# IS-29: IssueSignal & HoinEngine Unified Dashboard Spec

## 1. Overview
The goal of IS-29 is to create a unified "Ops UI" that provides visibility into both IssueSignal decision-making and the underlying HoinEngine evidence that supports those decisions. This integration enables operators to quickly verify high-trust signals against historical and structural data.

## 2. Information Architecture
The dashboard will be organized into three primary tabs:

### TAB 1: IssueSignal (Existing)
- **Purpose**: Real-time operational view of the IssueSignal engine.
- **Content**:
  - Global counters (TRUST_LOCKED, TRIGGER, etc.)
  - Top Trust-Locked Insights
  - Watchlist (PRE_TRIGGER)
  - Reject Logs

### TAB 2: Hoin Evidence (New)
- **Purpose**: Raw visibility into HoinEngine's recent artifacts.
- **Content**:
  - Latest Final Decision Card (`data/decision/.../final_decision_card.json`)
  - Latest Structural Snapshots (`data/snapshots/memory/`)
  - Operational Health Metadata (`data/ops/health_today.json`)

### TAB 3: Link View (New / Core Integration)
- **Purpose**: Side-by-side mapping of IssueSignal cards to HoinEngine evidence.
- **Content**:
  - A unified table where each IssueSignal card is paired with relevant evidence.
  - Expandable "Evidence Drawers" for each row.
  - Filters for Status, Trigger Type, and Evidence Presence.

## 3. Data Integration & Linking Logic
The dashboard builder will pre-compute links using strict, deterministic rules:

1.  **Ticker Search**: Matches IssueSignal tickers against entities in HoinEngine snapshots.
2.  **Structural Hash**: Matches `topic_key` or `structural_hash` if available in both datasets.
3.  **Conservative Phrasing**: Matches trigger types or key phrases if tickers/hashes are missing.
4.  **Fallback**: If no match is found, label as `NO_HOIN_EVIDENCE (read-only)`.

## 4. Technical Implementation
- **Data Source**: Purely file-based (JSON/YAML artifacts).
- **Backend**: Updated `src/issuesignal/dashboard/loader.py` to aggregate Hoin artifacts.
- **Frontend**: Updated `src/issuesignal/dashboard/renderer.py` using Vanilla CSS/JS for tab switching and drawers.
- **Output**:
  - `data/dashboard/issuesignal/index.html` (Unified UI)
  - `data/dashboard/issuesignal/unified_dashboard.json` (Structured data for the UI)

## 5. Build Process
Integrated into `src/issuesignal/run_issuesignal.py`. Running the main IssueSignal pipeline will automatically refresh the unified dashboard assets.

## 6. Verification
`tests/verify_is29_unified_dashboard.py` will validate:
- Presence of all required tabs.
- Successful data loading even with missing Hoin files.
- Linkage logic consistency.
