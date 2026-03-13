# EVIDENCE PACK SCHEMA (Step 3.3)

**Role:** The final structured output of Step 3. Represents a valid "LOCK CANDIDATE".
**Input:** Confirmed Bottleneck (from Module 3).
**Output:** Human-readable Evidence Pack.

---

## 1. Module 4: EVIDENCE_PACK_BUILDER

### Schema Definition
Any topic leaving Step 3 must adhere to this JSON-like structure.

```json
{
  "status": "LOCK_CANDIDATE",
  "one_liner": "Format: Today [event] -> [industry] must spend on [forced capex] -> money collapses to [1-3 bottlenecks].",
  "trigger": {
    "type": "Enum (POLICY | SHOCK | ...)",
    "event": "Description of the event",
    "timestamp": "YYYY-MM-DD"
  },
  "structural_flow": {
    "forced_capex": "What must be bought?",
    "value_chain": "[Spender] -> [Integrator] -> [Bottleneck]",
    "evidence": [
      "Proof 1 (Budget/Law)",
      "Proof 2 (Contract/Lead-time)"
    ]
  },
  "bottleneck": {
    "entities": ["Company A", "Company B"],
    "criteria_met": ["LEAD_TIME", "CAPACITY"],
    "evidence": [
      "Proof 1 (Sold out until 2027)",
      "Proof 2 (Only certified vendor)"
    ]
  },
  "kill_switch": "Single condition that invalidates this thesis (e.g., 'Law vetoed')"
}
```

---

## 2. Mock Examples (Validation)

### Example 1: POLICY_TRIGGER
*   **Context**: Government mandates green ships.
*   **One-liner**: "Today IMO regulations enforce carbon limits → Shipowners must replace old fleets → Money collapses to HD Hyundai (Capacity Locked)."
*   **Trigger**: `POLICY_TRIGGER` (IMO EEXI/CII Enforced 2024).
*   **Structural Flow**: Shipowners → New Eco-Ships → Engines/Ammonia Tanks.
*   **Bottleneck**: **HD Hyundai Heavy, Hanwha Ocean** (Duopoly in high-end eco-ships).
*   **Criteria**: `CAPACITY` (Docks full for 3 years), `LEAD_TIME`.
*   **Kill-switch**: Regulation delayed or scrapped.

### Example 2: SUPPLY_CHAIN_TRIGGER
*   **Context**: Power grid failure demands transformers.
*   **One-liner**: "Today US AI Data Center build-out hits power wall → Utilities must upgrade grid → Money collapses to HD Hyundai Electric (Transformer Shortage)."
*   **Trigger**: `SUPPLY_CHAIN_TRIGGER` (US Lead times hit 40 months).
*   **Structural Flow**: Hyperscalers → Utilities → Ultra-High Voltage Transformers.
*   **Bottleneck**: **HD Hyundai Electric, Hyosung Heavy** (Only vendors with capacity).
*   **Criteria**: `LEAD_TIME` (4 years backlog), `CERTIFICATION` (US Grid approved).
*   **Kill-switch**: US allows cheap Chinese transformer imports.

### Example 3: TECH_PHASE_TRIGGER (HBM)
*   **Context**: AI Training shifts to Inference/Training hybrid requiring memory bandwidth.
*   **One-liner**: "Today NVIDIA B100 launch requires HBM3E → CSPs must buy HBM stacks → Money collapses to SK Hynix (Yield Master)."
*   **Trigger**: `TECH_PHASE_TRIGGER` (NVIDIA Blackwell Release / HBM3E Standard).
*   **Structural Flow**: Big Tech → GPU Cluster → HBM Memory.
*   **Bottleneck**: **SK Hynix** (Technological Yield Monopoly).
*   **Criteria**: `YIELD/TECH_BARRIER`, `STANDARD LOCK-IN` (NVIDIA certified).
*   **Kill-switch**: Samsung catches up on HBM3E yield suddenly.

---

## 3. Human Comprehension Check (The 10-Second Rule)
If the **One-liner** cannot be read and understood by a layman in 10 seconds, the pack is marked **"COMPLEXITY_WARNING"** and downgraded.
