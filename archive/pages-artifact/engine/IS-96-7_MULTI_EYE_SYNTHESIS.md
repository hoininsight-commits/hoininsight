# IS-96-7 MULTI-EYE TOPIC SYNTHESIS

**Version**: v1.0 (2026-02-04)
**Purpose**: Synthesize multiple independent signals into ONE high-conviction topic.

## 1. Philosophy: "The 3-Eye Rule"
A topic is considered a valid "Economic Hunter" theme ONLY IF it is confirmed by at least **3 distinct lenses (Eyes)**.
- Price alone is a spike.
- Policy alone is a promise.
- Price + Policy + Labor is a **STRUCTURE**.

## 2. Input: 7 Eye Types
| Eye Type | Source Signal | Description |
|---|---|---|
| **PRICE** | `PRICE_MECHANISM_SHIFT` | Rigidity, Spread, Backlog |
| **POLICY** | `KR_POLICY`, Gov Tags | Regulations, Budgets |
| **CAPITAL** | `CAPEX`, `FLOW`, `ETF` | Money Moving |
| **LABOR** | `LABOR_SHIFT` | Employment Gap, Wage Premium |
| **AUTHORITY** | `CEO_SPEECH`, `INSTITUTION` | Decision Maker Statements |
| **SCHEDULE** | `EARNINGS`, `IPO` | Fixed Time Events |
| **EVENT** | `MERGER`, `LAWSUIT` | Sudden Catalysts |

## 3. Synthesis Logic
- **Input**: All `interpretation_units` from IS-96-x layers.
- **Grouping**: By `Target Sector`.
- **Gating**: `Count(Unique Eyes) >= 3`.
  - Less than 3 eyes = **DROP** (Suppressed).
  - Duplicate eyes (e.g. 3 Price signals) count as **1 Eye**.

## 4. Topic Classification
- **STRUCTURAL_SHIFT**: Price + Labor + Policy
- **REGIME_ACCELERATION**: Authority + Schedule + Capital
- **CAPITAL_REPRICING**: Price + Capital + Event
- **BOTTLENECK_REVEAL**: Price + Authority + Labor

## 5. Output
`data/decision/synthesized_topics.json`
