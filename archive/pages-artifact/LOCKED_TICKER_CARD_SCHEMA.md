# LOCKED TICKER CARD SCHEMA (Step 4)

**Role:** The Final Output. A verified, actionable signal ready for the dashboard.
**Condition:** Issued ONLY if the topic survives Steps 1, 2, 3, and 4 rules.

---

## 1. Schema Definition

```json
{
  "card_type": "LOCKED_TICKER_CARD",
  "status": "LOCKED",
  "trigger_context": {
    "type": "Enum (POLICY | ...)",
    "event": "Short description of the Why Now event",
    "timestamp": "YYYY-MM-DD"
  },
  "structural_logic": {
    "forced_capex": "The Must-Buy Item",
    "bottleneck_def": "The Critical Choke Point"
  },
  "tickers": [
    {
      "ticker": "Symbol or Code",
      "name": "Company Name",
      "role": "Bottleneck Role (e.g. Sole Supplier)",
      "why_irreplaceable_now": "Specific reason they win TODAY (Capacity/Tech/Cert)",
      "evidence": [
        "Fact 1 (Hardware/Contract)",
        "Fact 2 (Cert/Moat)"
      ]
    }
  ],
  "kill_switch": "Single condition that invalidates this card immediately"
}
```

---

## 2. Mock Examples

### Example 1: POLICY_TRIGGER (Green Ships)
*Recap Step 3: IMO Carbon Limits → Eco-Ships → HD Hyundai Heavy*

```json
{
  "card_type": "LOCKED_TICKER_CARD",
  "status": "LOCKED",
  "trigger_context": {
    "type": "POLICY_TRIGGER",
    "event": "IMO EEXI/CII Environmental Regulations Enforced",
    "timestamp": "2024-01-01"
  },
  "structural_logic": {
    "forced_capex": "Ammonia/Dual-Fuel Engines & Eco-Ships",
    "bottleneck_def": "High-end Shipyards with Engine Tech & Dock Slots"
  },
  "tickers": [
    {
      "ticker": "009540.KS",
      "name": "HD Hyundai Heavy Industries",
      "role": "Global #1 Engine & Ship Builder",
      "why_irreplaceable_now": "Holds >35% global market share in dual-fuel engines; Docks fully booked for 3 years (Price Maker).",
      "evidence": [
        "Order backlog exceeds $10B with high-margin mix",
        "License holder for Himsen Engine (Standard)"
      ]
    }
  ],
  "kill_switch": "Global recession causes shipping rates (SCFI) to crash below break-even, canceling orders."
}
```

### Example 2: SUPPLY_CHAIN_TRIGGER (Power Grid)
*Recap Step 3: AI Datacenter → Transformer Shortage → HD Hyundai Electric*

```json
{
  "card_type": "LOCKED_TICKER_CARD",
  "status": "LOCKED",
  "trigger_context": {
    "type": "SUPPLY_CHAIN_TRIGGER",
    "event": "US Ultra-High Voltage Transformer Lead-time hits 40 months",
    "timestamp": "2024-02-15"
  },
  "structural_logic": {
    "forced_capex": "Ultra-High Voltage (UHV) Transformers (>345kV)",
    "bottleneck_def": "Qualified Vendors for US Grid with Capacity"
  },
  "tickers": [
    {
      "ticker": "267260.KS",
      "name": "HD Hyundai Electric",
      "role": "Key US Vendor",
      "why_irreplaceable_now": "Only major Asian vendor with massive US backlog and anti-dumping clearance.",
      "evidence": [
        "US Order Backlog growth >80% YoY",
        "Alabama factory expansion completed just in time"
      ]
    },
    {
      "ticker": "298040.KS",
      "name": "Hyosung Heavy Industries",
      "role": "Secondary US Vendor",
      "why_irreplaceable_now": "Capacity overflow beneficiary; Memphis plant operational.",
      "evidence": [
        "Memphis plant utilization rate hit 100%",
        "Secured long-term contracts with UK National Grid"
      ]
    }
  ],
  "kill_switch": "US DOE relaxes import ban on Chinese transformers."
}
```

### Example 3: TECH_PHASE_TRIGGER (HBM)
*Recap Step 3: NVIDIA B100 Launch → HBM3E → SK Hynix*

```json
{
  "card_type": "LOCKED_TICKER_CARD",
  "status": "LOCKED",
  "trigger_context": {
    "type": "TECH_PHASE_TRIGGER",
    "event": "NVIDIA Blackwell (B100) Architecture Launch",
    "timestamp": "2024-03-18"
  },
  "structural_logic": {
    "forced_capex": "HBM3E High Bandwidth Memory",
    "bottleneck_def": "Yield-Proven HBM3E Supplier"
  },
  "tickers": [
    {
      "ticker": "000660.KS",
      "name": "SK Hynix",
      "role": "Sole Supplier (Initial Phase)",
      "why_irreplaceable_now": "Exclusive initial supplier for NVIDIA HBM3E; MR-MUF tech yield advantage.",
      "evidence": [
        "NVIDIA GTC 2024 Showcase Partner",
        "Sold out of 2024 HBM capacity completely"
      ]
    }
  ],
  "kill_switch": "Samsung Electronics successfully qualifies HBM3E with NVIDIA (Monopoly broken)."
}
```
