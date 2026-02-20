# ISSUE_SIGNAL_INTAKE_LAYER.md
# (Economic Hunter – Step 45)

## 0. Mission
This engine is the **Filter Feeder**.
It ingests the raw noise of the world (Speeches, PDF Documents, Press Releases) and outputs standardized **Structure**.

It answers:
> "Did something **Official** actually happen?"

It does **NOT** think.
It **Catalogs**.
It strips away the commentary and preserves the **primary source artifact**.

---

## 1. Allowed Signal Types

Raw inputs must be classified into one of these 3 buckets. anything else is **NOISE**.

### Type A: DECISION (The Gavel)
*An official body made a ruling.*
- **Examples**: Rate Cut, Court Ruling, Permit Approval, Sanction List Update.
- **Criteria**: Must be *Signed* and *Effective*.

### Type B: CONSTRAINT (The Wall)
*A physical or legal limit was hit.*
- **Examples**: "Inventory hit 0", "Port Closing", "Lead times > 50 weeks".
- **Criteria**: Must be *Quantitative* and *Verifiable*.

### Type C: SCHEDULE (The Clock)
*A fixed future event is locked.*
- **Examples**: "Maturity Date: Jan 1", "Compliance Deadline: Dec 31".
- **Criteria**: Must have a specific *Date*.

---

## 2. Strict Rules (The Filter)

### Do NOT Generate Topics
- Input: "Fed cuts rates."
- Output: "Signal: Fed cuts rates." (NOT "This assumes a boom...").

### Do NOT Select Tickers
- Input: "Nvidia announces chip."
- Output: "Signal: New Chip Announced." (NOT "Buy Nvidia").

### Do NOT Apply Why Now
- Just record the event. The *Why Now Engine* (Step 38) will judge it later.

### Opinions Must Be Rejected
- "Analyst says..." -> **DROP**.
- "Senator thinks..." -> **DROP**.
- "Sources say..." -> **DROP**. (Unless widely corroborated).

---

## 3. Status Rules

We classify signals based on their potential to trigger the Hunter.

| Status | Condition | Action |
| :--- | :--- | :--- |
| **ESCALATE** | Can satisfy `WHY_NOW` (Step 38). Structural. | Pass to Step 1. |
| **WATCH** | Interesting but incomplete (e.g., "Draft Bill"). | Store in Memory. |
| **DROP** | Noise / Opinion / Forecast. | Delete. |

---

## 4. Output Schema: ISSUE_SIGNAL_CARD (YAML)

```yaml
issue_signal_card:
  signal_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM:SS"
  source: 
    type: "GOVT_DOC"
    origin: "US Department of Energy"
    url: "energy.gov/press/..."
  
  signal_type: "CONSTRAINT" # DECISION / CONSTRAINT / SCHEDULE
  
  content:
    headline: "DOE issues immediate ban on 69kV+ Transformer Imports."
    key_fact: "Effective Date: 2026-01-01."
    quote: "All non-compliant orders must be cancelled."
    
  judgement:
    is_opinion: false
    is_forecast: false
    structural_impact: "HIGH"
    
  status: "ESCALATE" # ESCALATE / WATCH / DROP
```

---

## 5. Mock Examples

### Mock 1: ESCALATE (Type A: Decision)
- **Input**: "Press Release: EPA finalizes tailpipe emissions rule for 2027."
- **Analysis**: Official? Yes. Decision? Yes.
- **Signal**: `type: DECISION`, `status: ESCALATE`.

### Mock 2: DROP (Opinion)
- **Input**: "Article: Why the EPA rule will fail."
- **Analysis**: Official? No. Commentary? Yes.
- **Signal**: `type: NOISE`, `status: DROP`.

---

## 6. Final Report
The output of Step 45 is a stream of **Cards**.
It is not a Story.
It is a **Deck of Facts**.
