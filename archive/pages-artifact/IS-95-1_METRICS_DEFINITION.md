# IS-95-1 Derived Metrics Definition

This document defines the calculation methods and logical purposes of the new derived metrics introduced in the IS-95-1 expansion.

## 1. Policy & Structural Money Flow (KR)

### `policy_commitment_score` (0.0 - 1.0)
- **Definition**: Quantitative measure of government's verbal/roadmap commitment.
- **Inputs**: Frequency of official mentions, budget allocation announcements, timeline specificity.
- **Logic**: Higher if specific dates and USD/KRW amounts are mentioned in official gazettes.

### `policy_execution_gap`
- **Definition**: Difference between announced budget/plan and actual execution.
- **Inputs**: Govt budget execution rate, actual contract volumes.
- **Logic**: High gap indicates "verbal only" policy, low gap indicates "structural shift" implementation.

---

## 2. Index & Global Inclusion Layer

### `passive_inflow_expectation`
- **Definition**: Estimated mandatory capital inflow from global passive funds.
- **Inputs**: MSCI/WGBI weighting projections, total assets under management (AUM) of tracking funds.
- **Logic**: Calculated as `Market_Cap * Weighting_Change * Tracking_AUM`.

### `index_event_countdown`
- **Definition**: Distance to the next major index review/rebalancing event.
- **Logic**: Used to gauge the "Why Now" intensity as the event approaches.

---

## 3. Flow & Rotation Layer

### `rotation_signal_score`
- **Definition**: Detects capital shifting between styles (Growth/Value) or sizes (Large/Mid/Small).
- **Inputs**: Relative strength(RS) of sector ETFs, net buy volumes.
- **Logic**: High score when one sector's RS breaks 20-day highs while others decline.

### `flow_from_to_map`
- **Definition**: Mapping of lead-lag relationships in the value chain.
- **Logic**: e.g., Large Cap Semiconductor surge -> Component/Sub-supplier flow detected within 2-3 days.

---

## 4. Pretext Validation Layer

### `pretext_score`
- **Definition**: Validates if there is a fundamental "pretext" for capital inflow beyond price.
- **Logic**: `sum(Dividend_Yield_Z, Buyback_Yield_Z, Sector_RS_Z)`.

### `value_trap_risk_flag`
- **Definition**: Flags stocks that are cheap but lack a "Pretext" or "Execution" signal.
- **Logic**: TRUE if `PBR < 0.5` AND `policy_execution_gap > high`.

---

## 5. Earnings Verification Layer

### `earnings_shock_flag`
- **Definition**: Binary flag for deviation from consensus.
- **Logic**: TRUE if `|Actual - Consensus| > 2 * Standard_Deviation`.

### `post_earnings_reaction_score`
- **Definition**: Market's interpretation of the earnings.
- **Logic**: Price change vs. Earnings surprise direction. (e.g., Earnings Up + Price Down = Negative Interpretation).

### `fundamental_confirmation`
- **Definition**: Final bridge between "Pretext" and "Reality".
- **Logic**: Validates if the "Pretext" (e.g., AI expansion) is showing up in actual revenue/guidance.
