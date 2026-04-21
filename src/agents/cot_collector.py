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
    name = "COT"
    sensitivity = "LOW"
    ttl_minutes = 720

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

        # 52주 통계 계산 (지시서 #055)
        history_stats = self._calc_52w_stats()
        signals = self._calc_signals(results, history_stats)

        # [REFACTORED] Standardized Metadata Wrapper (#081)
        result_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "CFTC COT Report",
            "positions": results,
            "smart_money_signals": signals,
            "top_signal": self._get_top_signal(signals),
            "history_stats": history_stats
        }
        
        result = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "source_timestamp": None,
                "cache_hit": False,
                "ttl_policy_minutes": self.ttl_minutes,
                "freshness_status": "FRESH"
            },
            "data": result_data
        }

        output_path = self.output_dir / "cot.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  ✅ cot.json 저장 완료 ({len(results)}개 종목)")
        
        return {
            "agent": self.name,
            "process_success": True,
            "data_valid": True,
            "freshness_status": "FRESH",
            "result": result
        }

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

    def _calc_52w_stats(self) -> dict:
        """최근 52주 데이터를 수집하여 Z-score 및 Percentile 계산"""
        print("  📈 COT 52주 통계 산출 중 (금융 + 원자재)...")
        try:
            import cot_reports as cot
            current_year = datetime.now().year
            
            # 금융(TFF) 데이터 수집 및 통계
            df_cur_tff = cot.cot_year(current_year, "traders_in_financial_futures_fut")
            df_prev_tff = cot.cot_year(current_year - 1, "traders_in_financial_futures_fut")
            df_tff = pd.concat([df_prev_tff, df_cur_tff])
            
            # 원자재(Disaggregated) 데이터 수집 및 통계
            df_cur_dis = cot.cot_year(current_year, "disaggregated_fut")
            df_prev_dis = cot.cot_year(current_year - 1, "disaggregated_fut")
            df_dis = pd.concat([df_prev_dis, df_cur_dis])
            
            stats = {}
            
            # 금융 타겟
            tff_targets = [("SP500", "E-MINI S&P 500"), ("Nasdaq", "NASDAQ"), ("DXY", "U.S. DOLLAR INDEX"), ("US10Y", "10-YEAR T-NOTE")]
            for key, keyword in tff_targets:
                s = self._calculate_contract_stats(df_tff, keyword, "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All", "Leveraged Funds Longs", "Leveraged Funds Shorts")
                if s: stats[key] = s
                
            # 원자재 타겟
            dis_targets = [("WTI", "CRUDE OIL"), ("Gold", "GOLD")]
            for key, keyword in dis_targets:
                s = self._calculate_contract_stats(df_dis, keyword, "M_Money_Positions_Long_All", "M_Money_Positions_Short_All", "Money Manager Longs", "Money Manager Shorts")
                if s: stats[key] = s
            
            return stats
        except Exception as e:
            print(f"  ⚠️ COT 통계 계산 실패: {e}")
            return {}

    def _calculate_contract_stats(self, df, keyword, col_long_p, col_short_p, col_long_alt, col_short_alt) -> Optional[dict]:
        try:
            col_market = "Market_and_Exchange_Names" if "Market_and_Exchange_Names" in df.columns else "Market and Exchange Names"
            col_date = "Report_Date_as_YYYY-MM-DD" if "Report_Date_as_YYYY-MM-DD" in df.columns else "As of Date in Form YYYY-MM-DD"
            
            col_l = col_long_p if col_long_p in df.columns else col_long_alt
            col_s = col_short_p if col_short_p in df.columns else col_short_alt
            
            sub = df[df[col_market].str.contains(keyword, case=False, na=False)].copy()
            if sub.empty: return None
            
            sub[col_date] = pd.to_datetime(sub[col_date])
            sub = sub.sort_values(col_date).tail(52)
            
            sub["net"] = pd.to_numeric(sub[col_l], errors='coerce').fillna(0) - pd.to_numeric(sub[col_s], errors='coerce').fillna(0)
            
            current_net = sub["net"].iloc[-1]
            avg = sub["net"].mean()
            std = sub["net"].std()
            
            return {
                "z_score_52w": round((current_net - avg) / std, 2) if std > 0 else 0,
                "percentile_52w": round(sub["net"].rank(pct=True).iloc[-1] * 100, 1),
                "avg_52w": round(avg),
                "max_52w": round(sub["net"].max()),
                "min_52w": round(sub["net"].min())
            }
        except: return None

    def _calc_signals(self, positions: dict, history_stats: dict = None) -> list:
        signals = []
        for key, pos in positions.items():
            net_change = pos.get("net_change", 0)
            net        = pos.get("net", 0)
            prev_net   = pos.get("prev_net", 0)
            if prev_net == 0:
                continue

            change_pct = (net_change / abs(prev_net) * 100)
            
            # 52주 통계 매핑
            h_stats = history_stats.get(key, {}) if history_stats else {}

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
                    "percentile_52w": h_stats.get("percentile_52w", 0),
                    "z_score_52w": h_stats.get("z_score_52w", 0),
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
        result_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "positions": {},
            "smart_money_signals": [],
            "top_signal": None
        }
        result = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "source_timestamp": None,
                "cache_hit": False,
                "ttl_policy_minutes": self.ttl_minutes,
                "freshness_status": "UNKNOWN"
            },
            "data": result_data
        }
        return {
            "agent": self.name,
            "process_success": False,
            "data_valid": False,
            "freshness_status": "UNKNOWN",
            "result": result
        }

def run_collector(base_dir: Path) -> Path:
    from src.utils.target_date import get_target_ymd
    today = get_target_ymd().replace("-", "")
    out_dir = base_dir / "data" / "raw" / today
    out_dir.mkdir(parents=True, exist_ok=True)
    
    collector = COTCollector(output_dir=out_dir)
    collector.collect()
    return out_dir / "cot.json"

if __name__ == "__main__":
    run_collector(Path("."))
