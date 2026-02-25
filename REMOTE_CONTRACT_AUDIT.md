# Remote Contract Audit

## 1. Objective
Confirm the exact JSON contract served by GitHub Pages at `data/decision/today.json` to identify why the UI displays `N/A` for topics and determine the required SSOT alignment.

## 2. Remote Evidence (cURL over HTTPS)
- **Manifest**: `https://hoininsight-commits.github.io/hoininsight/data/decision/manifest.json` returns HTTP 200 and successful JSON evaluation. It correctly outlines `today.json` and legacy editorial fallbacks.
- **Today**: `https://hoininsight-commits.github.io/hoininsight/data/decision/today.json` returns HTTP 200.

## 3. The Contract Discrepancy
Inside `today.json`, the `top_topics` array exists and contains structural entries. However, printing `top_topics[0]` yields the following key fields:

```json
{
  "dataset_id": "risk_vix_fred",
  "score": 115,
  "intensity": null,
  "narrative_score": null
}
```

### Analysis
The backend engine correctly populates the mathematical `score` field (e.g., `115`). However, the UI expects either `narrative_score` or `intensity` to render the INT% badge. Since the Publisher script (`run_publish_ui_decision_assets.py`) merely passes the payload without explicitly mapping `score` to `intensity` (and because we removed the UI fake score generators), these natively evaluate to `null` and gracefully trigger "N/A".

## 4. Required SSOT Alignment
To strictly adhere to the "Publisher meets Contract" and "No Fake Data" rules without breaking engines:
1. Publisher must inject `intensity = score` when `score` is provided.
2. Publisher must enforce `narrative_score = null` when missing, validating the schema footprint.
