# VALUE_CHAIN_COMPRESSION_S49.md
# (Economic Hunter – Step 49)

## 0. Mission
This engine is the **Plumber**.
It takes the `STRUCTURAL_NECESSITY_CARD` (Step 48) and maps the **exact piping** of capital.

It answers:
> "Show me the money path in 3 steps or less."

It enforces **Efficiency**.
Structural Alpha decays with distance.
If the money has to touch 5 hands before it reaches the ticker, the Friction kills the trade.

---

## 1. The 3-Hop Rule (Strict)

The Value Chain MUST be described in exactly 3 nodes.

### Node 1: The Origin (The Payer)
*Who releases the capital?*
- Must be a specific entity with a confirmed budget.
- *Examples*: "US Utilities", "Maritime Shippers", "Department of Defense".

### Node 2: The Bridge (The Must-Item)
*What physical/legal object must be purchased?*
- Must be the specific bottleneck item.
- *Examples*: "345kV Transformers", "Scrubbers", "155mm Shells".

### Node 3: The Destination (The Collection Point)
*Who catches the capital?*
- Must be the final beneficiary (Manufacturer/Owner).
- *Examples*: "HD Hyundai Electric", "HMM", "Hanwha Aerospace".

---

## 2. Rejection Rules (Complexity Kill)

The Chain is **REJECTED** if:

1.  **Too Long (>3 Hops)**:
    - *Fail*: Gov -> Tax Credit -> Consumer -> Dealer -> Maker. (4 Steps).
    - *Fix*: Gov -> Defense Contract -> Maker. (3 Steps).
2.  **Too Abstract**:
    - *Fail*: Economy -> GDP Growth -> Tech Sector. (Vague).
3.  **Spillover Risk**:
    - *Fail*: Money flows to "Construction Companies" (Too many players).
    - *Pass*: Money flows to "The Only 2 Certified Vendors".

---

## 3. Output Schema: VALUE_CHAIN_CARD (YAML)

```yaml
value_chain_card:
  card_id: "UUID"
  necessity_id: "UUID"
  timestamp: "YYYY-MM-DDTHH:MM"
  
  # The 3-Hop Map
  chain:
    hop_1_origin: "US Regulated Utilities (Rate-Base)"
    hop_2_bridge: "345kV+ Power Transformers (Critical Hardware)"
    hop_3_destination: "Pure-Play Manufacturers (HD Hyundai, Hyosung)"
    
  # Logic Check
  distance_score: 3 # Ideal: 3
  friction_check: "LOW (Direct Procurement)"
  
  # The Verdict
  status: "PASS" # PASS / REJECT
  rejection_reason: null
```

---

## 4. Mock Examples

### Mock 1: PASS (Direct Injection)
- **Origin**: US Navy.
- **Bridge**: Unmanned Surface Vessels (USV).
- **Destination**: LIG Nex1 (Ghost Hunter).
- **Hops**: 3.
- **Verdict**: **PASS**.

### Mock 2: REJECT (Trickle Down)
- **Origin**: Fed Rate Cuts.
- **Bridge**: Lower Mortgage Rates.
- **Bridge 2**: More Housing Starts.
- **Destination**: Furniture Makers.
- **Hops**: 4 (Fed -> Rate -> House -> Furniture).
- **Verdict**: **REJECT**. (Too much leakage).

---

## 5. Final Report
Step 49 ensures we are standing right next to the **Fire Hose**.
If you are standing 3 miles downstream, you only get damp.
We want to get wet.
