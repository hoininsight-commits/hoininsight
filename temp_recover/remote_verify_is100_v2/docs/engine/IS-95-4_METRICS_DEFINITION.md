# IS-95-4 PRICE MECHANISM METRICS DEFINITION

**Purpose**: Define deterministic formulas for Structural Pricing Power.

## 1. PRICE_RIGIDITY_SCORE (0.0 ~ 1.0)
Measures how resistant prices are to downward pressure.
- **Formula**: `(SpreadRatio * 0.4) + (BacklogYears * 0.1) + (Utilization * 0.5)`
- **Interpretation**:
  - `> 0.8`: Absolute Rigidity (Seller sets price).
  - `< 0.5`: Buyers market.

## 2. PRICING_POWER_TRANSFER (Trend)
Detects the shift of margin from buyer to supplier.
- **Formula**: `SupplierMargin - BuyerMargin`
- **Trend**: Positive delta over 3 periods = Transfer Confirmed.

## 3. SUPPLY_INELASTICITY_SCORE (0.0 ~ 1.0)
Measures physical inability to increase supply.
- **Formula**: `(LeadTime / 12 months) * 0.2 + (CapacityUtilization > 0.95 ? 0.5 : 0) + (AllocationFlag ? 0.3 : 0)`

## 4. BUYER_DEPENDENCY_INDEX (0.0 ~ 1.0)
Measures Lock-in.
- **Formula**: `Concentration * 0.5 + (TechLockIn ? 0.3 : 0) + (CertRequired ? 0.2 : 0)`
