# UI Menu & Data Authority

## Dashboard Data mapping
| Dashboard Menu | Data Source Authority Path |
| :--- | :--- |
| **Decision Surface** | `docs/data/decision/today.json` |
| **Regime State** | `docs/data/ops/regime_state.json` |
| **Investment OS** | `docs/data/ops/investment_os_state.json` |
| **Timing Layer** | `docs/data/ops/timing_state.json` |
| **Stock Linkage** | `docs/data/ops/stock_linkage_pack.json` |
| **Decision Logs** | `docs/data/decision/manifest.json` |

## Authority Rules
- **Direct Access Prohibited**: UI components must never access `data/` or `data_outputs/` directly via HTTP. Use `docs/data/` alias.
- **Fail-Safe Loading**: `docs/ui/utils.js` (or equivalent) must handle 404s gracefully, returning `N/A` or grayed-out states for missing assets.
- **Version Control**: Every data artifact must include a `generated_at` (UTC) and `schema_version` tag.
