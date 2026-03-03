#!/usr/bin/env python3
import json
import logging
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

class StructuralRegimeLayer:
    """
    Phase 23: Structural Regime Layer
    Defines the market's structural state (Regime) based on rules.
    No-Behavior-Change: Pure state definition for UI/Decision context.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("StructuralRegime")
        self.ymd_dash = datetime.now().strftime("%Y-%m-%d")

    def _get_latest_csv_value(self, relative_path: str) -> float:
        csv_path = self.base_dir / relative_path
        if not csv_path.exists():
            return None
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: return None
                
                # Find 'value' column index
                try:
                    val_idx = header.index('value')
                except ValueError:
                    # Fallback for manual or older schemas
                    val_idx = 2 if 'entity' in header else 1

                lines = list(reader)
                if not lines: return None
                
                # Filter out empty lines or footer comments if any
                valid_lines = [l for l in lines if len(l) > val_idx and l[val_idx].strip()]
                if not valid_lines: return None
                
                last_line = valid_lines[-1]
                return float(last_line[val_idx])
        except Exception as e:
            self.logger.error(f"Failed to read CSV {csv_path}: {e}")
            return None

    def run(self):
        self.logger.info(f"Running Structural Regime Layer for {self.ymd_dash}...")

        # 1. Fetch Key Indicators
        ffr = self._get_latest_csv_value("data/curated/rates/fed_funds.csv")
        m2 = self._get_latest_csv_value("data/curated/liquidity/m2_usa.csv")
        vix = self._get_latest_csv_value("data/curated/risk/vix.csv")
        yc = self._get_latest_csv_value("data/curated/derived/rates/yield_curve_10y_2y.csv")
        cpi = self._get_latest_csv_value("data/curated/inflation/cpi_usa.csv")

        # 2. Rule-Based Regime Determination
        # Liquidity State
        liquidity_state = "NEUTRAL"
        if ffr is not None and ffr > 3.0: liquidity_state = "TIGHTENING"
        elif ffr is not None and ffr < 1.5: liquidity_state = "EASING"

        # Policy State
        policy_state = "NEUTRAL"
        if ffr is not None and ffr > 3.5: policy_state = "RESTRICTIVE"
        elif ffr is not None and ffr < 1.0: policy_state = "ACCOMMODATIVE"

        # Risk State
        risk_state = "NEUTRAL"
        if vix is not None and vix > 22: risk_state = "RISK_OFF"
        elif vix is not None and vix < 15: risk_state = "RISK_ON"

        # Yield Curve State
        yc_state = "NORMAL"
        if yc is not None and yc < 0: yc_state = "INVERTED"

        # Inflation Trend
        inflation_trend = "STABLE"
        if cpi is not None and cpi > 3.0: inflation_trend = "STICKY"
        elif cpi is not None and cpi < 2.0: inflation_trend = "DISINFLATION"

        # 3. Evidence Generation
        evidence = []
        if ffr is not None:
            evidence.append({"indicator": "rates_fed_funds_fred", "observation": f"정책금리 {ffr}% 수준", "direction": "HIGH" if ffr > 3 else "LOW"})
        if yc is not None:
            evidence.append({"indicator": "yield_curve_10y_2y", "observation": f"장단기 금리차 {yc:.2f}", "direction": "INVERTED" if yc < 0 else "NORMAL"})
        if vix is not None:
            evidence.append({"indicator": "risk_vix_fred", "observation": f"VIX 지수 {vix:.1f}", "direction": "VOLATILE" if vix > 20 else "STABLE"})

        # 4. Summary Generation
        one_liner = "거시지표 혼조세 속 구조적 변동성 구간"
        if policy_state == "RESTRICTIVE" and liquidity_state == "TIGHTENING":
            one_liner = "긴축 기조 강화 및 유동성 축소 지속"
        elif risk_state == "RISK_OFF":
            one_liner = "시장 공포심리 확산에 따른 안전자산 선호 강화"

        # 5. Output Construction
        pack = {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "date_kst": self.ymd_dash,
            "regime": {
                "liquidity_state": liquidity_state,
                "policy_state": policy_state,
                "risk_state": risk_state,
                "inflation_trend": inflation_trend,
                "yield_curve_state": yc_state
            },
            "evidence": evidence,
            "regime_summary": {
                "one_liner": one_liner,
                "structural_bias": "섹터별 차별화 및 금리 민감도 확대",
                "risk_note": "지표 발표에 따른 체제 전환(Regime Shift) 가능성 상존"
            }
        }

        out_path = self.base_dir / "data_outputs/ops/regime_state.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding='utf-8')
        
        self.logger.info(f"Successfully generated regime state: {liquidity_state}/{policy_state}.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    StructuralRegimeLayer(Path(".")).run()
