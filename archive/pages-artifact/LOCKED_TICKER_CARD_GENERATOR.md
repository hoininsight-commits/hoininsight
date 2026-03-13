# LOCKED_TICKER_CARD_GENERATOR.md
# (Economic Hunter – Step 44)

## 0. Purpose
This engine is the **Publisher**.
It takes the raw structural logic (Trigger, Path, Bottleneck, Tickers) and finalizes it into the **Canonical Output**.

It answers:
> "If I only read one thing today, what is the *Single Truth*?"

It enforces **Readability**.
The User must understand the entire trade in **10 Seconds**.

---

## 1. Writing Rules (Strict)

### DO (Mandatory)
1.  **Follow the Flow**: Trigger -> Spender -> Bottleneck -> Ticker. (No jumping around).
2.  **Use Active Verbs**: "Forces", "Mandates", "Requires", "Blocks".
3.  **Cite New Reality**: "Effective Jan 1st...", "As of today...".
4.  **Keep it Dry**: Write like a Court Reporter, not a Blogger.

### DO NOT (Forbidden)
1.  **No Outlook**: "The outlook is positive." (Who cares?).
2.  **No "We Believe"**: (The Engine does not "Believe". It Measures).
3.  **No Valuation**: "Cheap", "Fair Value", "Upside". (Forbidden).
4.  **No Adjectives**: "Exciting", "Massive", "Huge". (Use numbers instead).

---

## 2. Output Schema (YAML)

The Final Artifact stored in the database.

```yaml
locked_ticker_card:
  card_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM:SS"
  
  # 1. The Trigger (Why Now?)
  trigger_block:
    event: "US Dept of Energy Import Ban on Chinese Transformers >69kV."
    effective_date: "2026-01-01"
    status: "IRREVERSIBLE_LAW"
    
  # 2. The Forced Capex (Who Spends?)
  pressure_block:
    spender: "US Regulated Utilities (PJM/ERCOT)."
    coercion: "Federal Reliability Mandate + Physical Blackout Risk."
    vector: "Immediate Capex Injection ($50B estimated)."
    
  # 3. The Bottleneck (Where does it go?)
  bottleneck_block:
    constriction: "Domestic Production Capacity."
    lead_time: "40+ Months (Sold out to 2029)."
    moat: "DOE Certification (High Barrier)."
    
  # 4. The Tickers (Who Owns it?)
  ticker_block:
    count: 2
    selection:
      - ticker: "HD Hyundai Electric"
        role: "Primary Beneficiary (Market Share Leader)"
      - ticker: "Hyosung Heavy Ind"
        role: "Secondary Beneficiary (Capacity Expansion)"
    
  # 5. Safety
  kill_switch:
    condition: "If US repeals DOE Ban or Copper Prices spike > $6/lb."
    
  # 6. Verdict
  final_verdict: "LOCKED"
```

---

## 3. Mock Examples

### GOOD Example (The Hunter)
> **Trigger**: Jan 1st DOE Ban prohibits Chinese transformers.
> **Force**: Utilities must replace 40% of grid hardware to avoid fines.
> **Bottleneck**: Non-China capacity is sold out for 4 years.
> **Tickers**: **HD Hyundai Electric** and **Hyosung** control 90% of certified supply.
> *Verdict*: **Professional. Structural. Inevitable.**

### BAD Example (The Gambler)
> **Trigger**: The grid is getting old and exciting.
> **Force**: Utilities will probably spend a lot of money soon.
> **Bottleneck**: Transformers are hard to get.
> **Tickers**: **HD Hyundai** is a great buy with 50% upside potential!
> *Verdict*: **REJECT**. (Vague, Probabilistic, Advisory, Hype).

---

## 4. The Final Check
Before publishing, ask:
* "If the Ticker price goes down 10% tomorrow, is this logic still true?"*
If **YES**, Publish.
If **NO**, Reject. (You wrote a momentum piece, not a structural piece).
