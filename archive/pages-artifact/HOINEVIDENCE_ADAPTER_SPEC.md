# HOINEVIDENCE_ADAPTER_SPEC (v1.0)

## 1. Role
The **HoinEvidence Adapter** is the bridge between the real-time triggers of IssueSignal and the deep structural data of HoinEngine.

## 2. Integration Principle [READ-ONLY]
- **IssueSignal** queries HoinEngine data.
- **HoinEngine** pipeline remains untouched and unaware of IssueSignal's internal state.

## 3. Data Retrieval Map
The adapter will pull from the following canonical HoinEngine locations:

| Data Requirement | HoinEngine Source |
| :--- | :--- |
| **Macro Anchors** | `data/raw/macro/` (FRED, ECOS) |
| **Ticker Mapping** | `src/ops/entity_mapping_layer.py` outputs |
| **Bottleneck ID** | `data/pipeline/bottleneck_id_latest.json` |
| **Risk Metrics** | `src/ops/risk_sync_layer.py` data |
| **Anomaly State** | `data/analysis/deep_logic_results.json` |

## 4. Query Logic
1. **Trigger Keyword Match**: The adapter takes keywords from the IssueSignal trigger (Stage A) and matches them against HoinEngine's "Top-1 Topic" and "Bottleneck ID".
2. **Evidence Extraction**: It extracts the specific `ref_id` and `key_value` from HoinEngine evidence anchors to justify the IssueSignal narrative.
3. **Consistency Check**: If HoinEngine data contradicts the trigger (e.g., HoinEngine shows "Recovery" but trigger says "Shock"), the adapter triggers a **REJECT** signal for the content pack.

## 5. Security & Isolation
- The adapter uses standard file-system reads or read-only API calls.
- No write permissions are granted to the `src/issuesignal/` modules for any HoinEngine directories.
