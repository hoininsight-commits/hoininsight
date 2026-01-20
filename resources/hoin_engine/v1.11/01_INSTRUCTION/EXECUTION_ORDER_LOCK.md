# EXECUTION_ORDER_LOCK.md

EXECUTION ORDER (IMMUTABLE)

1. Identify active data signals from DATA_COLLECTION_MASTER.
2. Match signals to BASELINE_SIGNALS.
3. Apply ANOMALY_DETECTION_LOGIC combinations.
4. Classify WHY_NOW_TRIGGER_TYPE.
5. Assign anomaly level (L1~L4).
6. Generate WHY_NOW explanation.

FAIL CONDITION
- If step 3 fails → STOP.
- If anomaly level < L2 → STOP.
