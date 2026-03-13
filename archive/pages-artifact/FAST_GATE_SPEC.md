# FAST_GATE_SPEC (v1.0)

## 1. Purpose
The **Fast Why-Now Gate** is the primary filter in Step A of the IssueSignal workflow. It determines if a captured signal is actionable *immediately*.

## 2. Gate Criteria

### 2-1. The 72h Window
- **Rule**: The signal must have originated or reached an escalation peak within the last **72 hours**.
- **Rationale**: Markets move fast; stale news is noise. Older signals are relegated to "Archive" unless a new catalyst appears.

### 2-2. Irreversibility
- **Rule**: The event described in the signal must be **irreversible** or represent a definitive shift in state.
- **Example**: A rumor of a tariff is HOLD; an official signing of the tariff is READY.

### 2-3. Forced Capital Sentence Completion
Each signal passing the gate must be able to complete this logical sentence:
> "Because of **[SIGNAL]**, capital is now **FORCED** to move from **[A]** to **[B]** to resolve **[BOTTLENECK]**."

If this sentence cannot be completed with high confidence, the gate status is **REJECT**.

## 3. Output Statuses
- **READY**: Proceeds to Stage B (HoinEngine Evidence Ingestion).
- **HOLD**: Kept in the Issue Pool for 24-48h awaiting further confirmation.
- **REJECT**: Permanently discarded from the active workflow.

## 4. Logical Constraints
- **Redundancy**: If a similar signal is already in Stage B or published, the status is REJECT (Deduplication).
- **Entropy**: Signals with highly contradictory data points are HOLD until resolution.
