# Conflict Rule Definition (Phase 15B Forensics)

This document defines the current conditions under which `conflict_flag` and `escalation_flag` are triggered in the HOIN Engine.

## 1. Conflict Detection Patterns (`conflict_flag`)

The `conflict_flag` is set to `True` if any of the following semantic or statistical patterns are matched.

### A. Semantic Patterns (Keyword-based)
These patterns require the simultaneous detection of specific keywords in the normalized text (Title + Rationale).

| Pattern Name | Logic | Keywords Required |
| :--- | :--- | :--- |
| **Tightening_Inflow** | `Tightening` AND `Inflow` | (QT, TIGHTENING, HAWKISH, RATE HIKE) AND (INFLOW, BUY, LONG) |
| **Easing_Drain** | `Easing` AND `Drain` | (QE, EASING, DOVISH, RATE CUT) AND (OUTFLOW, DRAIN, SELL, SHORT) |
| **Supply_Demand_Gap** | `SupplyExp` AND `DemandWeak` | (SUPPLY INCREASE, GLUT) AND (DEMAND WEAKNESS, SLOWDOWN) |
| **Earnings_Price_Conflict**| `StrongEarnings` AND `PriceDecline` | (EARNINGS SURPRISE, PROFIT) AND (PRICE DECLINE, CRASH, BEAR) |
| **Policy_Inv_Tension** | `RegPressure` AND `InvSurge` | (REGULATION, BAN, MANDATE) AND (INVESTMENT, FUNDING) |
| **GeoRisk_Rally** | `GeoRisk` AND `AssetRally` | (WAR, CONFLICT, RISK) AND (RALLY, SURGE, BULL) |
| **Macro_Price_Divergence**| `MacroEvent` AND (`PriceDecline` OR `AssetRally`) | (FOMC, CPI, GDP, DATA) AND (CRASH, BEAR OR RALLY, BULL) |

### B. Statistical Patterns
These patterns rely on historical persistence and intensity changes.

| Pattern Name | Logic |
| :--- | :--- |
| **Persistence_Drop** | `matches >= 3` AND `Current Intensity <= (Last Intensity - 15)` |
| **Escalation_Low_Intensity** | `Current Intensity < 50` AND `escalation_flag == True` |

---

## 2. Escalation Detection Patterns (`escalation_flag`)

The `escalation_flag` is a prerequisite for some conflict patterns and affects the final narrative score.

| Rule Name | Logic |
| :--- | :--- |
| **Rule 1: Sequential Hike** | Intensity (Today) > Intensity (T-1) > Intensity (T-2) |
| **Rule 2: High Persistence** | Topic has appeared for at least 3 days (`len(matches) >= 3`) |
| **Rule 3: Sharp Spike** | Intensity (Today) >= (Intensity (T-1) + 10) |

---

## 3. Expectation Gap Levels

Affects `video_ready` status and final scoring bonus.

- **Moderate**: Gap Score >= 3
- **Strong**: Gap Score >= 6 (Bonus +4.0 to Narrative Score)

**Scoring Components:**
- Delta from 7-day avg >= 15: +2 pts
- Sudden jump from last occurrence >= 12: +2 pts
- Persistence >= 3 with sudden shift >= 10: +2 pts
- Narrative Score Jump >= 10: +1 pt
