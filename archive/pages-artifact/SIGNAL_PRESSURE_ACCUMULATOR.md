# SIGNAL_PRESSURE_ACCUMULATOR.md
# (Economic Hunter – Step 46)

## 0. Mission
This engine is the **Magnet**.
It takes isolated `ISSUE_SIGNAL_CARDs` (Step 45) and pulls them together into **Pressure Clusters**.

It answers:
> "Is this a stray bullet, or a firing squad?"
> "Do we have enough *density* to ignite a topic?"

It enforces **Critical Mass**.
A single signal is an anecdote. A cluster of signals is a **Trend**.

---

## 1. Clustering Conditions (The Gravity)

Signals are grouped into a `PRESSURE_CLUSTER` if they meet **Time Proximity (<= 72h)** AND at least one of these matches:

### A. Actor Match
*Same entity taking multiple actions.*
- **Example**: EPA issues rule (Decision) + EPA sets deadline (Schedule).

### B. Domain Match
*Different actors sharing a target.*
- **Example**: US bans import (Trade) + EU bans usage (Climate) -> Target: "Supply Chain".

### C. Vector Match
*Different domains sharing a direction.*
- **Example**: Treasury issuance spikes (Fiscal) + Fed halts QT (Monetary) -> Vector: "Liquidity Injection".

---

## 2. Pressure Scoring (0-10 Scale)

Calculate `pressure_score` to determine escalation.

### Base Weights (Per Signal)
- **DECISION (Type A)**: +3 Points.
- **CONSTRAINT (Type B)**: +2 Points.
- **SCHEDULE (Type C)**: +1 Point.

### Multipliers (Cluster Coherence)
- **High Coherence**: Signals reinforce each other (e.g., Ban + Shortage). **x 1.5**
- **Low Coherence**: Signals are orthogonal but related. **x 1.0**

### Thresholds
| Score | State | Action |
| :--- | :--- | :--- |
| **>= 6** | **IGNITE** | **ESCALATE to Step 47**. (We have ignition). |
| **3 - 5** | **SIMMER** | **HOLD**. (Wait for more signals). |
| **< 3** | **DISSIPATE** | **DROP**. (Not enough pressure). |

---

## 3. Output Schema: PRESSURE_CLUSTER (YAML)

```yaml
pressure_cluster:
  cluster_id: "UUID"
  timestamp_opened: "YYYY-MM-DDTHH:MM"
  last_updated: "YYYY-MM-DDTHH:MM"
  
  # The Signals involved
  signals:
    - signal_id: "UUID_1" (Type: DECISION, Weight: 3)
    - signal_id: "UUID_2" (Type: CONSTRAINT, Weight: 2)
    
  # The Glue
  clustering_logic: "DOMAIN_MATCH (Target: Transformer Supply)"
  
  # The Score
  scoring_breakdown:
    raw_sum: 5
    coherence: 1.5
    final_score: 7.5
    
  state: "IGNITE" # IGNITE / SIMMER / DISSIPATE
```

---

## 4. Mock Examples

### Mock 1: IGNITE (Score 7.5)
- **Signal 1**: DOE Bans Transformers (Decision, +3).
- **Signal 2**: HHI Lead Times hit 5 years (Constraint, +2).
- **Cluster**: Domain Match (Transformers). Coherence: High (Ban causes Shortage).
- **Math**: (3 + 2) * 1.5 = **7.5**.
- **Result**: **IGNITE**.

### Mock 2: SIMMER (Score 4)
- **Signal 1**: Fed Governors speech mentions pausing pauses (Noise -> Weak Decision?? No, Step 45 filtered opinions).
- **Signal 1** (Real): Fed Balance Sheet expands $10B (Constraint, +2).
- **Signal 2**: Treasury announces Auction (Schedule, +1).
- **Cluster**: Vector Match (Liquidity). Coherence: Low (Routine).
- **Math**: (2 + 1) * 1.0 = **3.0**.
- **Result**: **SIMMER**. (Keep watching).

---

## 5. Final Report
The Accumulator does not judge *quality*.
It judges **Weight**.
It pushes the heavy piles forward and lets the light piles drift away.
