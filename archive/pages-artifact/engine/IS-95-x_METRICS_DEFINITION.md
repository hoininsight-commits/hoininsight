# IS-95-x: LABOR SHIFT LAYER - METRICS DEFINITION

**Theme**: AI Industrialization → Labor Market Shift
**Version**: v1.0 (2026-02-04)

## 1. LABOR_SHIFT_GAP (Structural Unemployment Gap)
**Formula**: `(Unemployment_Bachelors_Degree - Unemployment_High_School)`
**Units**: Percentage Points (%)
**Interpretation**:
- **Standard**: Bachelors rate is usually lower than High School rate. Gap is typically negative (e.g., -2.0%).
- **Shift Signal**: Gap **narrows** (becomes less negative, e.g., -1.0%) or **flips** (positive).
- **Why**: Indicates "Degree Premium" is eroding. White-collar roles (degree-heavy) are being automated/frozen while blue-collar (non-degree) demand remains stable or grows.
**Missing Data**: If either series is unavailable, return `NaN`.

## 2. YOUTH_WHITE_COLLAR_DROP (Youth Entry Bottleneck)
**Formula**: `Employment_Population_Ratio_20_24 (Current) - Employment_Population_Ratio_20_24 (12-Month Moving Average)`
**Units**: Percentage Points (%)
**Interpretation**:
- **Negative Value**: Youth employment is deteriorating relative to its own recent trend.
- **Signal**: Rapid drop < -1.5% in 3 months triggers "Entry Level Freeze" warning.
- **Why**: AI automation often hits entry-level white-collar jobs first ("Junior Developer", "Analyst"), disproportionately affecting the 20-25 cohort.

## 3. BLUE_COLLAR_WAGE_PREMIUM (Body-Sovereignty Index)
**Formula**: `(Construction_Wages_YoY_Growth) - (Total_Private_Wages_YoY_Growth)`
**Units**: Percentage Points (%)
**Interpretation**:
- **Positive**: Construction wages are growing faster than the overall market.
- **Signal**: > +1.0% indicates strong physical labor demand relative to general labor.
- **Why**: AI cannot dig holes or pull cables. Physical infrastructure buildout (Datacenters, Power) drives physical wage inflation while AI deflates cognitive wage inflation.

## 4. DC_CAPEX_MOMENTUM (Physical Buildout Velocity)
**Formula**: `(Construction_Spending_Data_Center_Current / Construction_Spending_Data_Center_YearAgo) - 1`
**Units**: YoY Growth Rate (%)
**Interpretation**:
- **Baseline**: > 0% is growth.
- **Signal**: > 15% YoY indicates "Hyper-scale Buildout".
- **Why**: Verifies that the AI narrative is backed by physical ground-breaking, not just GPU sales.
