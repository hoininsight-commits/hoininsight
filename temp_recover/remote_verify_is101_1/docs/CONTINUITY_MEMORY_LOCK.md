# CONTINUITY_MEMORY_LOCK.md
# (Economic Hunter – Step 10)

## 0. Purpose

This engine governs the "Time-Dimension" of a Topic.
It prevents the engine from treating a 3-month structural trend
as a "New Topic" every single day.

It answers:
> "Is this a new story,
> or an escalation of yesterday's story?"

---

## 1. Topic Continuity States (State Machine)

Every Locked Topic must occupy exactly ONE state.

| State | Definition | Transition Condition |
| :--- | :--- | :--- |
| **FLASH** | Initial Lock (Day 1). Powerful but unproven longevity. | Entry Point. |
| **PERSISTENT** | Re-triggered within 7 days. Narrative is holding. | Trigger Count ≥ 2 AND Kill-Switch Safe. |
| **ESCALATING** | Pressure intensity increased. New "Forced Spender" added. | Structural Necessity Upgrade (e.g., Budget increase). |
| **COOLING** | No new triggers for >14 days. Still valid, but quiet. | Time Decay > 14 days without Trigger. |
| **INVALIDATED** | Killed by rules. Dead forever. | Kill-Switch Activates OR TTL Expires. |

---

## 2. Memory Lock Schema (The Black Box)

When a topic is LOCKED, it is serialized into this immutable record.

```json
{
  "topic_id": "UUID_v4",
  "headline": "Must-Have Headline",
  "birth_date": "YYYY-MM-DD",
  "last_trigger_date": "YYYY-MM-DD",
  "continuity_state": "FLASH",
  "trigger_history": [
    {"date": "...", "type": "EVENT", "intensity": "HIGH"}
  ],
  "structural_core": {
    "forced_spender": "Government / Utility",
    "bottleneck_tickers": ["Ticker A", "Ticker B"],
    "kill_switch_condition": "Specific Invalidating Logic"
  },
  "re_trigger_hash": "Hash(Spender + Bottleneck + Capex)"
}
```

---

## 3. Re-Trigger Detector (New vs Continuation)

New incoming candidates are checked against Active Memory (Persistent/Escalating).

### Logic Rule
If `Candidate.re_trigger_hash` == `Memory.re_trigger_hash`:
→ **MERGE** into existing Topic.
→ Update State (e.g., FLASH -> PERSISTENT).
→ Append Trigger History.

Else:
→ **CREATE** New Topic.

### Explicit Rejection
- If a candidate creates a NEW topic that is 90% similar to an existing one but barely different -> **FORCE MERGE**.
- Do not dilute the narrative with duplicates.

---

## 4. Dashboard Display Rules

How Continuity appears to the Human Operator.

### Rule A: The "New" Badge
Only **FLASH** or **ESCALATING** topics get the "NEW" badge.
**PERSISTENT** topics appear as "Ongoing Structural Trends."

### Rule B: The "Dead" Zone
**INVALIDATED** topics must NOT appear on the main dashboard.
They are archived in the "Graveyard" section.

### Rule C: Context Stacking
When displaying a PERSISTENT topic, show the **Original Trigger** AND the **Latest Trigger**.
> "Started 14 days ago by [Event A], Escalated today by [Event B]."

---

## 5. Mock Example (3-Day Lifecycle)

### Day 1 (FLASH)
- **Even**: US Grid Emergency declared.
- **Action**: LOCK "Transformer Shortage".
- **State**: FLASH.
- **Dash**: "🔥 NEW: US Grid requires Transformers."

### Day 3 (PERSISTENT/ESCALATING)
- **Event**: HD Hyundai Electric announces $5B order.
- **Action**: RE-TRIGGER.
- **State**: ESCALATING (Evidence confirmed).
- **Dash**: "📈 ESCALATING: Transformer Shortage confirmed by $5B Order."

### Day 20 (COOLING)
- **Event**: None.
- **State**: COOLING.
- **Dash**: "❄️ MONITOR: Transformer Shortage (Quiet)."

---

## 6. Absolute Prohibitions

- Zombie Topics (Keeping dead topics alive on dash) ❌
- Duplicate Topics (Same logic, different headline) ❌
- "Reminder" Topics (No new trigger, just re-posting) ❌

This engine ensures
**Accumulation of Truth**, not Noise.
