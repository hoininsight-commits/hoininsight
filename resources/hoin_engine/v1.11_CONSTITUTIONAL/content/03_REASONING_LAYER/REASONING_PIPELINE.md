# REASONING_PIPELINE.md

## PIPELINE OVERVIEW
1. **Signal Aggregation**: Macro / Market / Policy / Structural data
2. **Threshold Detection**: Z-Score > 2.0 or Percentile Breach
3. **Multi-Signal Confirmation**: Cross-Asset Verification
4. **Capital Validation**: Volume / RS / Funding Flow Check

---

## [MANDATORY OUTPUT RULES] (v1.12 Add-on)

All analysis outputs must include the following sections to ensure "Self-Evolution":

### 1. WHY_NOW Structure
- Must cite **Specific Trigger Type** (e.g., Structural+Capital).
- Must ban "News-driven" reasoning in favor of "State-driven" reasoning.

### 2. State & Level
- Must declare **Current Anomaly Level** (L1~L4) based on `ANOMALY_LEVEL_RULES.md`.
- **Pre-M&A Checks**: If Structural-Capital branch is active, verify S-L1~S-L4 progression.

### 3. [DATA ACTION] (Expansion Request)
- **Question**: "Does this analysis require new data sensors to be automated next time?"
- **Answer Format**:
    - **YES**: List specific data points to add to `DATA_COLLECTION_MASTER`.
    - **NO**: Existing sensors are sufficient.
- **Rule**: Do not ask for "News/Rumors". Ask for "Hard Data/Metrics" only.

### 4. [LOGIC ACTION] (System Patch)
- **Question**: "Did the engine fail to detect this without the script?"
- **Answer Format**:
    - **YES**: Propose new logic rules for `ANOMALY_DETECTION_LOGIC`.
    - **NO**: Logic handled it correctly.

---

## NO OUTPUT CONDITION
- If capital movement is not observable (Volume/RS absent).
- If the event is purely political noise without price detection (P-L1).
