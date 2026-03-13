# MULTI_SOURCE_TRIGGER_SCANNER.md
# (Economic Hunter – Step 12)

## 0. Purpose

This engine is the **Periscope** of the Economic Hunter.
It scans the horizon *before* a full Trigger Event occurs.

It detects:
- Hidden accumulation of pressure.
- Subtle changes in official language.
- Deadlines that are quietly approaching.

It does **NOT** create topics.
It feeds "Raw Potential" into the Why Now Gate (Step 1).

---

## 1. Input Source Definition

The Scanner monitors 4 distinct channels.

### Channel A: Official Speeches (The Voice)
- Inputs: Central Bank, G7 Leaders, Regulators, Key CEOs.
- Watch for: "New Words", "Dropped Words", "Tone Shift".

### Channel B: The Calendar (The Clock)
- Inputs: Laws coming into effect, Bond maturities, Elections, Earnings.
- Watch for: "D-30 Danger Zone", "Collision of Dates".

### Channel C: Pre-Capex Signals (The Wallet)
- Inputs: Bond issuance, Credit line expansion, Land purchase.
- Watch for: "Cash piling up before a project announcement."

### Channel D: Language Divergence (The Gap)
- Inputs: Media Headline vs. Official Statement.
- Watch for: "Media says A, Official Text says B." (Misunderstanding = Opportunity)

---

## 2. Detection Rules (Signal vs Noise)

A signal is valid ONLY if it implies **Future Forced Action**.

| Signal Type | Valid Logic | Invalid (Noise) |
| :--- | :--- | :--- |
| **Linguistic** | "We can no longer tolerate..." (Limit reached) | "We are monitoring..." (Passive) |
| **Temporal** | "Effective Jan 1st, regardless of..." (Fixed) | "Aiming for next year..." (Flexible) |
| **Financial** | "Secures $10B specifically for X" (Committed) | "Considering investment in X" (Vague) |

*Rule:* If the actor can back out without cost, it is NOISE.

---

## 3. Output States

Every scanned item falls into one bucket.

### [STATE: PRE-TRIGGER]
- **Definition**: A clear event is confirmed, but the "Trigger Moment" is imminent (not today).
- **Action**: Alert Operator to "Watch closely for D-Day."

### [STATE: PRESSURE_BUILDING]
- **Definition**: No discrete event yet, but multiple data points are converging.
- **Action**: Log in "Pressure Gauge" to track intensity.

### [STATE: NOISE]
- **Definition**: Routine news, opinion, or flexible plans.
- **Action**: Discard immediately.

---

## 4. What This Step MUST NOT Do (Prohibitions)

1.  **Never define a Topic**: "This looks like a Semiconductor theme" -> **FORBIDDEN**.
2.  **Never predict prices**: "Bond yields will rise" -> **FORBIDDEN**.
3.  **Never filter by preferences**: "I don't like Crypto so ignore it" -> **FORBIDDEN**.

The Scanner is an **Objective Radar**, not an Analyst.

---

## 5. Mock Examples

### Example 1 (PRE-TRIGGER)
- **Source**: White House Press Release.
- **Content**: "President to sign Executive Order on AI Safety next Tuesday."
- **Analysis**: Fixed date, Legal force.
- **Output**: `PRE-TRIGGER (D-5)`

### Example 2 (PRESSURE_BUILDING)
- **Source**: Federal Reserve Minutes.
- **Content**: "Several participants noted liquidity constraints are emerging." (New phrase added).
- **Analysis**: "Liquidity constraints" appeared for the first time. Warning sign.
- **Output**: `PRESSURE_BUILDING (Linguistic Shift)`

### Example 3 (NOISE)
- **Source**: CEO Interview on CNBC.
- **Content**: "We think the economy will improve fast."
- **Analysis**: Opinion, no commitment, no deadline.
- **Output**: `NOISE`
