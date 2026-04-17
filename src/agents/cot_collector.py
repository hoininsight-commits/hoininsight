# src/agents/cot_collector.py

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict



class COTCollector:
    """
    CFTC COT Report 수집기
    Leveraged Funds(헤지펀드) 포지션 변화로 스마트머니 방향 포착
    매주 금요일 15:30 ET 발표 / 화요일 기준 데이터
    """

    TARGET_CONTRACTS = {
        "WTI": "CRUDE OIL",
        "Gold": "GOLD",
        "SP500": "E-MINI S&P 500",
        "Nasdaq": "NASDAQ",
        "DXY": "U.S. DOLLAR INDEX",
        "US10Y": "10-YEAR T-NOTE",
    }

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def collect(self) -> dict:
        print("📊 COT Report 수집 시작...")

        try:
            import cot_reports as cot
        except ImportError:
            print("  ❌ cot_reports 라이브러리 없음 — pip install cot-reports")
            return self._empty_result()

        results = {}

        # Disaggregated (원자재: WTI, Gold)
        try:
            df_disagg = cot.cot_year(
                year=datetime.now().year,
                cot_report_type="disaggregated_fut"
            )
            results.update(self._parse_disaggregated(df_disagg))
            print("  ✅ Disaggregated 수집 완료")
        except Exception as e:
            print(f"  ❌ Disaggregated 수집 실패: {e}")

        # TFF (금융: S&P500, 나스닥, DXY, 국채)
        try:
            df_tff = cot.cot_year(
                year=datetime.now().year,
                cot_report_type="traders_in_financial_futures_fut"
            )
            results.update(self._parse_tff(df_tff))
            print("  ✅ TFF 수집 완료")
        except Exception as e:
            print(f"  ❌ TFF 수집 실패: {e}")

        signals = self._calc_signals(results)

        result = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "collected_at": datetime.now().isoformat(),
            "source": "CFTC COT Report",
            "positions": results,
            "smart_money_signals": signals,
            "top_signal": self._get_top_signal(signals)
        }

        output_path = self.output_dir / "cot.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  ✅ cot.json 저장 완료 ({len(results)}개 종목)")
        return result

    def _parse_disaggregated(self, df: pd.DataFrame) -> dict:
        results = {}
        for key, keyword in [("WTI", "CRUDE OIL"), ("Gold", "GOLD")]:
            try:
                # 실제 CSV 컬럼명 대응 (언더바 포함 및 필격명 보정)
                col_market = "Market_and_Exchange_Names" if "Market_and_Exchange_Names" in df.columns else "Market and Exchange Names"
                col_date = "Report_Date_as_YYYY-MM-DD" if "Report_Date_as_YYYY-MM-DD" in df.columns else "As of Date in Form YYYY-MM-DD"
                col_long = "M_Money_Positions_Long_All" if "M_Money_Positions_Long_All" in df.columns else "Money Manager Longs"
                col_short = "M_Money_Positions_Short_All" if "M_Money_Positions_Short_All" in df.columns else "Money Manager Shorts"

                mask = df[col_market].str.contains(
                    keyword, case=False, na=False
                )
                sub = df[mask].copy()
                if sub.empty:
                    continue
                sub = sub.sort_values(col_date).tail(2)
                if len(sub) < 2:
                    continue

                latest = sub.iloc[-1]
                prev = sub.iloc[-2]

                lev_long  = float(latest.get(col_long, 0) or 0)
                lev_short = float(latest.get(col_short, 0) or 0)
                prev_long  = float(prev.get(col_long, 0) or 0)
                prev_short = float(prev.get(col_short, 0) or 0)

                net       = lev_long - lev_short
                prev_net  = prev_long - prev_short
                net_change = net - prev_net

                results[key] = {
                    "long": int(lev_long),
                    "short": int(lev_short),
                    "net": round(net),
                    "prev_net": round(prev_net),
                    "net_change": round(net_change),
                    "direction": "LONG" if net > 0 else "SHORT",
                    "change_direction": "INCREASING" if net_change > 0 else "DECREASING",
                    "report_date": str(latest.get(col_date, "")),
                }
            except Exception as e:
                print(f"  ⚠️ {key} 파싱 실패: {e}")

        return results

    def _parse_tff(self, df: pd.DataFrame) -> dict:
        results = {}
        targets = [
            ("SP500",  "E-MINI S&P 500"),
            ("Nasdaq", "NASDAQ"),
            ("DXY",    "U.S. DOLLAR INDEX"),
            ("US10Y",  "10-YEAR T-NOTE"),
        ]
        for key, keyword in targets:
            try:
                # 실제 CSV 컬럼명 대응 (TFF용 언더바 및 필드명 보정)
                col_market = "Market_and_Exchange_Names" if "Market_and_Exchange_Names" in df.columns else "Market and Exchange Names"
                col_date = "Report_Date_as_YYYY-MM-DD" if "Report_Date_as_YYYY-MM-DD" in df.columns else "As of Date in Form YYYY-MM-DD"
                col_long = "Lev_Money_Positions_Long_All" if "Lev_Money_Positions_Long_All" in df.columns else "Leveraged Funds Longs"
                col_short = "Lev_Money_Positions_Short_All" if "Lev_Money_Positions_Short_All" in df.columns else "Leveraged Funds Shorts"

                mask = df[col_market].str.contains(
                    keyword, case=False, na=False
                )
                sub = df[mask].copy()
                if sub.empty:
                    continue
                sub = sub.sort_values(col_date).tail(2)
                if len(sub) < 2:
                    continue

                latest = sub.iloc[-1]
                prev   = sub.iloc[-2]

                lev_long  = float(latest.get(col_long, 0) or 0)
                lev_short = float(latest.get(col_short, 0) or 0)
                prev_long  = float(prev.get(col_long, 0) or 0)
                prev_short = float(prev.get(col_short, 0) or 0)

                net        = lev_long - lev_short
                prev_net   = prev_long - prev_short
                net_change = net - prev_net

                results[key] = {
                    "long": int(lev_long),
                    "short": int(lev_short),
                    "net": round(net),
                    "prev_net": round(prev_net),
                    "net_change": round(net_change),
                    "direction": "LONG" if net > 0 else "SHORT",
                    "change_direction": "INCREASING" if net_change > 0 else "DECREASING",
                    "report_date": str(latest.get(col_date, "")),
                }

            except Exception as e:
                print(f"  ⚠️ {key} 파싱 실패: {e}")

        return results

    def _calc_signals(self, positions: dict) -> list:
        signals = []
        for key, pos in positions.items():
            net_change = pos.get("net_change", 0)
            net        = pos.get("net", 0)
            prev_net   = pos.get("prev_net", 0)
            if prev_net == 0:
                continue

            change_pct = (net_change / abs(prev_net) * 100)

            if abs(change_pct) >= 20:
                signal_label = "STRONG"
            elif abs(change_pct) >= 10:
                signal_label = "MODERATE"
            else:
                signal_label = "WEAK"

            direction_flip = (
                (prev_net > 0 and net < 0) or
                (prev_net < 0 and net > 0)
            )

            if signal_label in ["STRONG", "MODERATE"] or direction_flip:
                signals.append({
                    "asset": key,
                    "signal_label": "FLIP" if direction_flip else signal_label,
                    "net_change": round(net_change),
                    "change_pct": round(change_pct, 1),
                    "direction": pos["direction"],
                    "change_direction": pos["change_direction"],
                    "description": self._build_description(
                        key, net_change, change_pct, direction_flip, pos
                    )
                })

        signals.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        return signals

    def _build_description(self, key, net_change, change_pct, direction_flip, pos) -> str:
        direction = "매수" if net_change > 0 else "매도"
        if direction_flip:
            old = "롱" if pos["prev_net"] > 0 else "숏"
            new = "롱" if pos["net"] > 0 else "숏"
            return (
                f"{key} 헤지펀드 포지션 {old}→{new} 전환 "
                f"(Net {pos['prev_net']:+,} → {pos['net']:+,})"
            )
        return (
            f"{key} 헤지펀드 {direction} {abs(net_change):,}계약 "
            f"({change_pct:+.1f}%) — 전주 대비 {pos['change_direction']}"
        )

    def _get_top_signal(self, signals: List) -> Optional[Dict]:
        for s in signals:
            if s["signal_label"] in ["FLIP", "STRONG"]:
                return s
        return signals[0] if signals else None

    def _empty_result(self) -> dict:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "collected_at": datetime.now().isoformat(),
            "positions": {},
            "smart_money_signals": [],
            "top_signal": None
        }
