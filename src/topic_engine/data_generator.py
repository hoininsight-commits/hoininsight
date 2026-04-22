import json
from typing import List, Dict

class DataSignalGenerator:
    """[TASK #100.2] 시장 데이터에서 결정론적으로 시그널 추출"""

    def __init__(self):
        pass

    def generate(self, market_data: Dict) -> List[Dict]:
        signals = []
        stats = market_data.get("data", {}).get("multi_period_stats", {})
        if not stats:
            return []

        # Helper to get stats safely
        def get_stat(key):
            return stats.get(key, {})

        # 1. Divergence: SP500 vs US10Y (Bond up, Stock up - rare liquidity injection)
        sp500 = get_stat("sp500")
        us10y = get_stat("us10y")
        if sp500 and us10y:
            sp_z = sp500.get("z_score_20d", 0)
            us_z = us10y.get("z_score_20d", 0)
            if sp_z > 1.5 and us_z < -1.5:
                signals.append({
                    "signal": "금리 하락 vs 주식 급등 (Liquidity Party)",
                    "metrics": ["US10Y", "SP500"],
                    "current": {"US10Y": us10y.get("current"), "SP500": sp500.get("current")},
                    "previous": {"US10Y": us10y.get("prev_1d"), "SP500": sp500.get("prev_1d")},
                    "change": {"US10Y": us10y.get("chg_5d"), "SP500": sp500.get("chg_5d")},
                    "signal_type": "DIVERGENCE",
                    "z_score": sp_z
                })

        # 2. Speed: KOSPI Extreme Move
        kospi = get_stat("kospi")
        if kospi:
            k_z = kospi.get("z_score_20d", 0)
            if abs(k_z) > 2.0:
                signals.append({
                    "signal": f"코스피 {'과열' if k_z > 0 else '공포'} (Z-score: {k_z:.2f})",
                    "metrics": ["KOSPI"],
                    "current": {"KOSPI": kospi.get("current")},
                    "previous": {"KOSPI": kospi.get("prev_1d")},
                    "change": {"KOSPI": kospi.get("chg_5d")},
                    "signal_type": "SPEED",
                    "z_score": k_z
                })

        # 3. Correlation: WTI vs DXY (Both up - Energy inflation)
        wti = get_stat("wti_oil")
        dxy = get_stat("dxy")
        if wti and dxy:
            wti_z = wti.get("z_score_20d", 0)
            dxy_z = dxy.get("z_score_20d", 0)
            if wti_z > 1.5 and dxy_z > 1.0:
                signals.append({
                    "signal": "유가-달러 동반 강세 (Energy Crisis Risk)",
                    "metrics": ["WTI", "DXY"],
                    "current": {"WTI": wti.get("current"), "DXY": dxy.get("current")},
                    "previous": {"WTI": wti.get("prev_1d"), "DXY": dxy.get("prev_1d")},
                    "change": {"WTI": wti.get("chg_5d"), "DXY": dxy.get("chg_5d")},
                    "signal_type": "CORRELATION",
                    "z_score": wti_z
                })

        return signals
