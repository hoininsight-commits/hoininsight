import json
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.utils.target_date import get_now_kst, get_target_ymd, get_current_round
from pathlib import Path
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup

load_dotenv()


class CollectorAgent:
    
    def _fetch_yahoo_chart(self, ticker: str, range_str: str = "90d") -> "pd.DataFrame":
        """
        Direct Yahoo Chart API fetcher using requests.
        Ensures bypass of yfinance library blocks.
        """
        import requests
        import pandas as pd
        headers = {"User-Agent": "Mozilla/5.0"}
        # Fallback between query1 and query2
        for host in ["query1", "query2"]:
            url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={range_str}"
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    res = data["chart"]["result"][0]
                    timestamps = res.get("timestamp", [])
                    indicators = res.get("indicators", {}).get("quote", [{}])[0]
                    adj_close = res.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
                    
                    df = pd.DataFrame({
                        "Close": indicators.get("close", []),
                        "Adj Close": adj_close if adj_close else indicators.get("close", []),
                        "Volume": indicators.get("volume", []),
                    }, index=pd.to_datetime(timestamps, unit="s"))
                    
                    # Cleanup: remove nulls
                    df = df.dropna()
                    if not df.empty:
                        return df
            except:
                continue
        return pd.DataFrame()

    def _get_kospi(self) -> dict:
        import yfinance as yf
        result = {"kospi": None, "kospi_1d_change": None, "history": None}
        
        tickers_to_try = ["^KS11", "KS11.KS", "000001.KS"]
        
        for ticker in tickers_to_try:
            try:
                hist = self._fetch_yahoo_chart(ticker, "90d")
                if len(hist) >= 2:
                    latest = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    # 값 유효성 검사 (KOSPI는 2500 이상이어야 함)
                    if latest > 2500:
                        result["kospi"] = round(latest, 2)
                        result["kospi_1d_change"] = round(
                            (latest - prev) / prev * 100, 2
                        )
                        result["history"] = {
                            "current": result["kospi"],
                            "avg_90d": round(float(hist["Close"].mean()), 2),
                            "max_90d": round(float(hist["Close"].max()), 2),
                            "min_90d": round(float(hist["Close"].min()), 2),
                            "trend": list(hist["Close"].tail(30).round(2))
                        }
                        print(f"  KOSPI ({ticker}): {result['kospi']}")
                        return result
                    else:
                        print(f"  {ticker} 값 이상: {latest} (건너뜀)")
            except Exception as e:
                print(f"  {ticker} 실패: {e}")
        
        print("  KOSPI 수집 전부 실패")
        return result

    def _get_gold(self) -> dict:
        result = {"value": None, "history": None}
        for ticker in ["GC=F", "GLD", "IAU"]:
            try:
                hist = self._fetch_yahoo_chart(ticker, "90d")
                if not hist.empty:
                    val = round(float(hist["Close"].iloc[-1]), 2)
                    if ticker in ["GLD", "IAU"]:
                        val = round(val * 10, 2)
                        hist["Close"] = hist["Close"] * 10 # ETF 히스토리도 보정
                    
                    if val > 1000:
                        result["value"] = val
                        result["history"] = {
                            "current": val,
                            "avg_90d": round(float(hist["Close"].mean()), 2),
                            "max_90d": round(float(hist["Close"].max()), 2),
                            "min_90d": round(float(hist["Close"].min()), 2),
                            "trend": list(hist["Close"].tail(30).round(2))
                        }
                        print(f"  gold ({ticker}): {val}")
                        return result
            except Exception as e:
                print(f"  gold {ticker} 실패: {e}")
        return result

    def _get_dxy(self) -> dict:
        result = {"value": None, "history": None}
        # 1. DX-Y.NYB 시도
        try:
            hist = self._fetch_yahoo_chart("DX-Y.NYB", "90d")
            if not hist.empty:
                val = round(float(hist["Close"].iloc[-1]), 2)
                if 85 <= val <= 130:
                    result["value"] = val
                    result["history"] = {
                        "current": val,
                        "avg_90d": round(float(hist["Close"].mean()), 2),
                        "max_90d": round(float(hist["Close"].max()), 2),
                        "min_90d": round(float(hist["Close"].min()), 2),
                        "trend": list(hist["Close"].tail(30).round(2))
                    }
                    print(f"  dxy (DX-Y.NYB): {val}")
                    return result
        except: pass

        # 2. FRED fallback
        try:
            from fredapi import Fred
            fred = Fred(api_key=os.getenv("FRED_API_KEY"))
            # DTWEXBGS (Nominal Broad US Dollar Index) - DXY와 유사
            from datetime import timedelta
            series = fred.get_series("DTWEXBGS", observation_start=(get_now_kst() - timedelta(days=100)).strftime('%Y-%m-%d'))
            if not series.empty:
                val = round(float(series.dropna().iloc[-1]), 2)
                series_clean = series.dropna()
                result["value"] = val
                result["history"] = {
                    "current": val,
                    "avg_90d": round(float(series_clean.mean()), 2),
                    "max_90d": round(float(series_clean.max()), 2),
                    "min_90d": round(float(series_clean.min()), 2),
                    "trend": list(series_clean.tail(30).round(2))
                }
                print(f"  dxy (FRED): {val}")
                return result
        except Exception as e:
            print(f"  dxy FRED 실패: {e}")
        return result

    def _get_sp500(self) -> dict:
        result = {"value": None, "history": None}
        try:
            hist = self._fetch_yahoo_chart("^GSPC", "90d")
            if not hist.empty:
                val = round(float(hist["Close"].iloc[-1]), 2)
                if val > 5000:
                    result["value"] = val
                    result["history"] = {
                        "current": val,
                        "avg_90d": round(float(hist["Close"].mean()), 2),
                        "max_90d": round(float(hist["Close"].max()), 2),
                        "min_90d": round(float(hist["Close"].min()), 2),
                        "trend": list(hist["Close"].tail(30).round(2))
                    }
                    print(f"  sp500 (^GSPC): {val}")
                    return result
        except: pass

        try:
            from fredapi import Fred
            fred = Fred(api_key=os.getenv("FRED_API_KEY"))
            from datetime import timedelta
            series = fred.get_series("SP500", observation_start=(get_now_kst() - timedelta(days=100)).strftime('%Y-%m-%d'))
            if not series.empty:
                series_clean = series.dropna()
                val = round(float(series_clean.iloc[-1]), 2)
                result["value"] = val
                result["history"] = {
                    "current": val,
                    "avg_90d": round(float(series_clean.mean()), 2),
                    "max_90d": round(float(series_clean.max()), 2),
                    "min_90d": round(float(series_clean.min()), 2),
                    "trend": list(series_clean.tail(30).round(2))
                }
                print(f"  sp500 (FRED): {val}")
                return result
        except Exception as e:
            print(f"  sp500 FRED 실패: {e}")
        return result

    def _get_nasdaq(self) -> dict:
        result = {"value": None, "history": None}
        try:
            hist = self._fetch_yahoo_chart("^IXIC", "90d")
            if not hist.empty:
                val = round(float(hist["Close"].iloc[-1]), 2)
                if val > 15000:
                    result["value"] = val
                    result["history"] = {
                        "current": val,
                        "avg_90d": round(float(hist["Close"].mean()), 2),
                        "max_90d": round(float(hist["Close"].max()), 2),
                        "min_90d": round(float(hist["Close"].min()), 2),
                        "trend": list(hist["Close"].tail(30).round(2))
                    }
                    print(f"  nasdaq (^IXIC): {val}")
                    return result
        except Exception as e:
            print(f"  nasdaq 실패: {e}")
        return result

    def _get_vix(self) -> dict:
        result = {"value": None, "history": None}
        try:
            hist = self._fetch_yahoo_chart("^VIX", "90d")
            if not hist.empty:
                val = round(float(hist["Close"].iloc[-1]), 2)
                result["value"] = val
                result["history"] = {
                    "current": val,
                    "avg_90d": round(float(hist["Close"].mean()), 2),
                    "max_90d": round(float(hist["Close"].max()), 2),
                    "min_90d": round(float(hist["Close"].min()), 2),
                    "trend": list(hist["Close"].tail(30).round(2))
                }
                print(f"  vix (^VIX): {val}")
                return result
        except Exception as e:
            print(f"  vix 실패: {e}")
        return result

    def _get_wti(self) -> dict:
        """WTI 유가 수집 및 다중기간 변화율 계산 (거래일 기준 버그 수정)"""
        result = {
            "value": None,
            "1d_change": None,
            "5d_change": None,
            "20d_change": None,
            "history": None
        }
        try:
            hist = self._fetch_yahoo_chart("CL=F", "31d")
            if not hist.empty:
                # 최근 2일 데이터 확보
                if len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    prev1 = float(hist["Close"].iloc[-2])
                    result["value"] = round(current, 2)
                    result["1d_change"] = round((current - prev1) / prev1 * 100, 2)

                # 5일, 20일 관찰 (데이터 충분 시)
                if len(hist) >= 6:
                    prev5 = float(hist["Close"].iloc[-6])
                    result["5d_change"] = round((current - prev5) / prev5 * 100, 2)
                
                if len(hist) >= 21:
                    prev20 = float(hist["Close"].iloc[-21])
                    result["20d_change"] = round((current - prev20) / prev20 * 100, 2)

                # 히스토리 30일
                result["history"] = {
                    "current": result["value"],
                    "avg_90d": round(float(hist["Close"].mean()), 2),
                    "max_90d": round(float(hist["Close"].max()), 2),
                    "min_90d": round(float(hist["Close"].min()), 2),
                    "trend": list(hist["Close"].tail(30).round(2))
                }
                print(f"  wti (CL=F): {result['value']} ({result['1d_change']}% )")
                return result
        except Exception as e:
            print(f"WTI 수집 실패: {e}")
        return result

    def __init__(self):
        from src.core.gemini_client import GeminiClient
        from src.utils.target_date import get_target_ymd, get_now_kst, get_current_round, get_standard_path_prefix
        self.today = get_target_ymd().replace("-", "")
        self.round = os.environ.get("HOIN_TARGET_ROUND", str(get_current_round()))
        self.path_prefix = get_standard_path_prefix()
        self.output_dir = Path("data/raw") / self.path_prefix
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # base_dir 설정 (history 저장용)
        self.base_dir = Path(".")
        self.model_name = "gemini-flash-latest"
        from src.core.gemini_client import GeminiClient
        self.gemini = GeminiClient()

    def _wrap_data(self, data: dict, ttl_minutes: int, source_timestamp: str = None) -> dict:
        """모든 수집 데이터를 메타데이터와 함께 래핑 (#081)"""
        return {
            "metadata": {
                "collected_at": get_now_kst().isoformat(),
                "source_timestamp": source_timestamp,
                "cache_hit": False,
                "ttl_policy_minutes": ttl_minutes,
                "freshness_status": "FRESH" if data is not None else "UNKNOWN"
            },
            "data": data
        }
    
    def _calculate_multi_period_stats(self, data: dict) -> dict:
        """
        수집된 지표들의 다중기간 통계 계산
        5일/20일/60일 평균, 변화율, Z-score 계산
        """
        import yfinance as yf
        import numpy as np
    
        stats = {}
    
        # 계산할 지표와 티커 매핑
        ticker_map = {
            "usd_krw":  "KRW=X",
            "gold":     "GC=F",
            "wti_oil":  "CL=F",
            "vix":      "^VIX",
            "us10y":    "^TNX",
            "dxy":      "DX-Y.NYB",
            "sp500":    "^GSPC",
            "kospi":    "^KS11",
        }
    
        for key, ticker in ticker_map.items():
            try:
                # 최대 90일 데이터 수집 (WTI는 1개월치만 써서 정확도 높임)
                p = "31d" if key == "wti_oil" else "90d"
                hist = self._fetch_yahoo_chart(ticker, p)
                if len(hist) < 5:
                    continue
    
                closes = hist["Close"].dropna().values
                current = float(closes[-1])
    
                # 기간별 평균
                avg_5d  = float(np.mean(closes[-5:])) if len(closes) >= 5 else None
                avg_20d = float(np.mean(closes[-20:])) if len(closes) >= 20 else None
                avg_60d = float(np.mean(closes[-60:])) if len(closes) >= 60 else None
    
                # 기간별 변화율
                chg_5d  = round((current - closes[-6]) / closes[-6] * 100, 2) \
                          if len(closes) >= 6 else None
                chg_20d = round((current - closes[-21]) / closes[-21] * 100, 2) \
                          if len(closes) >= 21 else None
    
                # 20일 Z-score (표준편차 기반 이탈도)
                if len(closes) >= 20:
                    mean_20 = float(np.mean(closes[-20:]))
                    std_20  = float(np.std(closes[-20:]))
                    z_score = round((current - mean_20) / std_20, 2) \
                              if std_20 > 0 else 0
                else:
                    z_score = None
    
                # 5일 최고/최저
                high_5d = float(np.max(closes[-5:])) if len(closes) >= 5 else None
                low_5d  = float(np.min(closes[-5:])) if len(closes) >= 5 else None
    
                stats[key] = {
                    "current":  round(current, 4),
                    "avg_5d":   round(avg_5d, 4)  if avg_5d  else None,
                    "avg_20d":  round(avg_20d, 4) if avg_20d else None,
                    "avg_60d":  round(avg_60d, 4) if avg_60d else None,
                    "chg_5d":   chg_5d,
                    "chg_20d":  chg_20d,
                    "z_score_20d": z_score,
                    "high_5d":  round(high_5d, 4) if high_5d else None,
                    "low_5d":   round(low_5d, 4)  if low_5d  else None,
                }
                print(f"  stats {key}: z={z_score}, chg5d={chg_5d}%")
    
            except Exception as e:
                print(f"  stats {key} 실패: {e}")
    
        return stats

    def collect_market(self) -> dict:
        """시장 데이터 수집 — yfinance 기반 (90일 히스토리 포함 v7.0)"""
        print("📈 시장 데이터 수집 및 90일 히스토리 분석 중...")

        data = {}
        history_90d = {}

        # 1. KOSPI 수집 고도화 (v4.5 버그 수정)
        kospi_data = self._get_kospi()
        data["kospi"] = kospi_data["kospi"]
        data["kospi_1d_change"] = kospi_data["kospi_1d_change"]
        if kospi_data["history"]:
            history_90d["kospi"] = kospi_data["history"]
                    
        # 2. 핵심 지표 고도화 수집
        gold_data = self._get_gold()
        data["gold"] = gold_data["value"]
        if gold_data["history"]: history_90d["gold"] = gold_data["history"]

        dxy_data = self._get_dxy()
        data["dxy"] = dxy_data["value"]
        if dxy_data["history"]: history_90d["dxy"] = dxy_data["history"]

        sp500_data = self._get_sp500()
        data["sp500"] = sp500_data["value"]
        if sp500_data["history"]: history_90d["sp500"] = sp500_data["history"]

        nasdaq_data = self._get_nasdaq()
        data["nasdaq"] = nasdaq_data["value"]
        if nasdaq_data["history"]: history_90d["nasdaq"] = nasdaq_data["history"]

        # WTI 수집 (v5.5 버그 수정 반영)
        wti_data = self._get_wti()
        data["wti_oil"] = wti_data["value"]
        data["wti_1d_change"] = wti_data["1d_change"]
        data["wti_5d_change"] = wti_data["5d_change"]
        data["wti_20d_change"] = wti_data["20d_change"]
        if wti_data["history"]: history_90d["wti_oil"] = wti_data["history"]

        # 3. 나머지 티커들 수집 (v7.0)
        other_tickers = {
            "vix": "^VIX",
            "us10y": "^TNX",
            "brent": "BZ=F",
            "usd_krw": "KRW=X"
        }

        for key, ticker_symbol in other_tickers.items():
            try:
                # 90일치 히스토리 수집 (흐름 파악용)
                hist = self._fetch_yahoo_chart(ticker_symbol, "90d")
                if not hist.empty:
                    # 오늘 데이터
                    data[key] = round(float(hist["Close"].iloc[-1]), 2)
                    
                    # 90일 히스토리 저장 (추세 분석용)
                    history_90d[key] = {
                        "current": data[key],
                        "avg_90d": round(float(hist["Close"].mean()), 2),
                        "max_90d": round(float(hist["Close"].max()), 2),
                        "min_90d": round(float(hist["Close"].min()), 2),
                        "trend": list(hist["Close"].tail(30).round(2)) # 최근 30일 종가 추이
                    }
                else:
                    data[key] = None
            except Exception as e:
                print(f"  {key} ({ticker_symbol}) 수집 실패: {e}")
                data[key] = None

        # 4. 수집 데이터 유효성 검사 (v4.0 추가)
        from datetime import timedelta
        validation_rules = {
            "kospi": (2500, 10000),
            "gold": (3000, 8000),
            "dxy": (85, 120),
            "sp500": (5000, 15000),
            "nasdaq": (15000, 40000),
            "vix": (5, 90),
            "wti_oil": (30, 200),
            "usd_krw": (1000, 2000),
        }

        print("  === 데이터 유효성 검증 ===")
        for key, (min_val, max_val) in validation_rules.items():
            val = data.get(key)
            if val is None:
                print(f"  ⚠️ {key}: None")
            elif not (min_val <= val <= max_val):
                print(f"  🔴 {key}: {val} (범위 이탈! {min_val}~{max_val})")
                data[key] = None  # 이상값 None 처리
            else:
                print(f"  ✅ {key}: {val}")

        # 외국인 수급 (별도 계산)
        data["kospi_foreign_net"] = self._get_kospi_foreign_vol()
        data["fear_greed_index"] = self._get_fear_greed()
        data["usd_krw"] = data.get("usd_krw", 1380.0)

        # 다중기간 통계 추가 (v5.0)
        data["multi_period_stats"] = self._calculate_multi_period_stats(data)

        result_data = {
            "date": self.today,
            "data": data,
            "history_90d": history_90d
        }
        
        # [REFACTORED] Wrap with metadata (Market: HIGH sensitivity -> 30m)
        result = self._wrap_data(result_data, ttl_minutes=30)

        # 오늘 데이터 저장
        output_path = self.output_dir / "market.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 90일 히스토리 별도 저장 (Detector/Analyst 참조용)
        history_dir = self.base_dir / "data/raw/history"
        history_dir.mkdir(parents=True, exist_ok=True)
        (history_dir / "market_90d.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

        print(f"✅ market.json (메타데이터 포함) 저장 완료: {output_path}")
        return result

    def _get_kospi_foreign_vol(self) -> float:
        try:
            hist = self._fetch_yahoo_chart("^KS11", "5d")
            if len(hist) >= 2:
                vol_change = float(hist["Volume"].iloc[-1]) - float(hist["Volume"].iloc[-2])
                val = round(vol_change / 1e8, 1)
                return val if val != 0.0 else None
        except:
            pass
        return None

    def _get_fear_greed(self) -> float:
        """Alternative.me Fear & Greed Index 실제 수집"""
        try:
            import requests
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                value = float(data["data"][0]["value"])
                print(f"  Fear&Greed: {value} (실제)")
                return value
        except Exception as e:
            print(f"  Fear&Greed 수집 실패, UNKNOWN 처리: {e}")
        return None  # No more fallback 25.0

    def _get_usd_krw(self) -> float:
        """환율 수집"""
        try:
            hist = self._fetch_yahoo_chart("KRW=X", "5d")
            if len(hist) > 0:
                return round(float(hist["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"환율 수집 실패: {e}")
        return None  # No more fallback 1380.0

    def collect_macro(self) -> dict:
        """거시경제 데이터 — FRED/ECOS 통합 수집 (v3.0 교정)"""
        print("🏦 거시경제 데이터 수집 중...")
        
        # FRED와 ECOS 개별 수집기 실행 결과 활용
        fred_result = self.collect_fred()
        ecos_result = self.collect_ecos()
        consensus_result = self.collect_consensus()

        combined_data = {}
        if fred_result.get("data"):
            combined_data.update(fred_result["data"])
        if ecos_result.get("data"):
            combined_data.update(ecos_result["data"])

        # 금리차 계산
        fed = combined_data.get("fed_rate")
        kr = combined_data.get("kr_base_rate")
        if fed is not None and kr is not None:
            combined_data["rate_diff"] = round(fed - kr, 4)
        else:
            combined_data["rate_diff"] = None

        result_data = {
            "date": self.today,
            "source": "FRED + ECOS API (Integrated)",
            "data": combined_data,
            "major_surprises": consensus_result.get("data", {}).get("major_surprises", [])
        }

        # [REFACTORED] Wrap with metadata (Macro: LOW sensitivity -> 720m (12h))
        result = self._wrap_data(result_data, ttl_minutes=720)

        output_path = self.output_dir / "macro.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ macro.json 통합 저장 완료: {output_path}")
        return result

    def collect_sentiment(self) -> dict:
        """뉴스/감성 데이터 — 글로벌 경제 RSS 실제 수집"""
        print("📰 글로벌 뉴스 데이터 수집 중...")
        import feedparser
        import requests
        from concurrent.futures import ThreadPoolExecutor

        headlines = []
        rss_feeds = [
            # 글로벌 경제/금융 (월가 및 거시경제)
            {"name": "FT Markets",      "url": "https://www.ft.com/markets?format=rss"},
            {"name": "CNBC Economy",    "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html"},
            {"name": "CNBC Finance",    "url": "https://www.cnbc.com/id/10001147/device/rss/rss.html"},
            {"name": "Yahoo Finance",   "url": "https://finance.yahoo.com/news/rssindex"},
            {"name": "Investing.com",   "url": "https://www.investing.com/rss/news_25.rss"},
            # IB 리포트 / 애널리스트 등급·목표주가 변경 전용
            {"name": "MarketBeat",      "url": "https://www.marketbeat.com/rss/analyst-ratings/"},
            {"name": "Benzinga Analyst","url": "https://www.benzinga.com/feeds/analyst-ratings"},
            {"name": "Seeking Alpha",   "url": "https://seekingalpha.com/market-currents.xml"},
            # 국내 주요 경제지 (실물 경제 및 시장)
            {"name": "Yonhap English",  "url": "https://en.yna.co.kr/RSS/news.xml"},
            {"name": "연합뉴스",          "url": "https://www.yna.co.kr/rss/economy.xml"},
            {"name": "한국경제",          "url": "https://www.hankyung.com/feed/economy"},
            {"name": "매일경제",          "url": "https://www.mk.co.kr/rss/30100041/"},
        ]

        def fetch_rss_worker(feed):
            feed_headlines = []
            try:
                # 타임아웃을 7초로 조정하여 지연 피드 차단
                resp = requests.get(feed["url"], timeout=7, 
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
                if resp.status_code == 200:
                    d = feedparser.parse(resp.content)
                    now = get_now_kst()
                    for entry in d.entries[:50]:
                        # [FRESHNESS FILTER] 7일 이내 뉴스만 수집
                        pub_date = entry.get("published_parsed")
                        date_prefix = ""
                        if pub_date:
                            dt = datetime(*pub_date[:6], tzinfo=timezone.utc)
                            if (now - dt).days > 7:
                                continue
                            date_prefix = f"[{dt.strftime('%Y-%m-%d')}] "
                        else:
                            # 날짜 정보가 없으면 오늘 날짜로 표시 (리스크 감수)
                            date_prefix = f"[{now.strftime('%Y-%m-%d')}] "

                        feed_headlines.append({
                            "title": date_prefix + entry.get("title", "").strip(),
                            "summary": entry.get("summary", "")[:1000].strip(), # 1000자로 확장하여 디테일 보존
                            "link": entry.get("link", ""),
                            "source": feed["name"],
                            "timestamp": get_now_kst().isoformat(),
                            "is_deep_scraped": False # 본문 스크래핑 여부 마킹
                        })
            except Exception as e:
                print(f"  [RSS ERROR] {feed['name']}: {e}")
            return feed_headlines

        # 5개 스레드로 뉴스 병렬 수집
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_rss_worker, rss_feeds))
            for res in results:
                headlines.extend(res)

        print(f"  총 뉴스 {len(headlines)}개 원시 데이터 수집 완료 (정제 대기 중)")
        
        result_data = {
            "date": self.today,
            "data": {
                "news_headlines": headlines
            }
        }

        # [REFACTORED] Wrap with metadata (Sentiment: HIGH sensitivity -> 30m)
        result = self._wrap_data(result_data, ttl_minutes=30)

        output_path = self.output_dir / "sentiment.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ sentiment.json 저장 완료: {output_path}")
        return result

    def collect_consensus(self) -> dict:
        """
        경제지표 컨센서스 수집 (FRED API 기반 서프라이즈 계산)
        """
        print("📅 컨센서스 데이터 수집 중 (FRED 기반)...")
        import os
        from fredapi import Fred
        from datetime import datetime, timedelta

        fred = Fred(api_key=os.getenv("FRED_API_KEY"))
        today = get_now_kst()
        result_events = []

        indicators = [
            ("CPIAUCSL",    "미국 CPI",           "전월비"),
            ("CPILFESL",    "미국 Core CPI",       "전월비"),
            ("PCEPI",       "미국 PCE",            "전월비"),
            ("PCEPILFE",    "미국 Core PCE",       "전월비"),
            ("PAYEMS",      "미국 비농업고용",      "천명"),
            ("UNRATE",      "미국 실업률",          "%"),
            ("FEDFUNDS",    "미국 기준금리",        "%"),
            ("RETAILSL",    "미국 소매판매",        "전월비"),
            ("INDPRO",      "미국 산업생산",        "전월비"),
            ("GDP",         "미국 GDP",            "분기"),
            ("T10Y2Y",      "10Y-2Y 금리스프레드", "bp"),
            ("BAMLH0A0HYM2","HY 스프레드",         "bp"),
        ]

        for series_id, name, unit in indicators:
            try:
                end = today
                start = today - timedelta(days=90)
                series = fred.get_series(series_id, start, end).dropna()
                if len(series) < 2: continue
                current_val, p_val = float(series.iloc[-1]), float(series.iloc[-2])
                change = round(current_val - p_val, 4)
                if len(series) >= 12:
                    recent_changes = [float(series.iloc[i] - series.iloc[i-1]) for i in range(-12, -1) if abs(i) < len(series)]
                    avg_chg = sum(recent_changes) / len(recent_changes) if recent_changes else 0
                    surprise = round(change - avg_chg, 4)
                    surprise_pct = round((change - avg_chg) / abs(avg_chg) * 100, 2) if avg_chg != 0 else 0
                else: surprise, surprise_pct = 0, 0
                result_events.append({
                    "series_id": series_id, "event": name, "unit": unit, "date": series.index[-1].strftime("%Y-%m-%d"),
                    "actual": current_val, "previous": p_val, "change": change, "surprise": surprise, "surprise_pct": surprise_pct,
                    "has_actual": True, "surprise_direction": "BEAT" if surprise > 0 else "MISS"
                })
            except: pass

        major_surprises = [e for e in result_events if abs(e["surprise_pct"]) > 10]
        
        result_data = {
            "date": get_now_kst().strftime("%Y%m%d"),
            "source": "FRED API",
            "total_events": len(result_events),
            "major_surprises": major_surprises,
            "all_events": result_events
        }
        
        # [REFACTORED] Wrap with metadata (Consensus: LOW sensitivity -> 720m)
        result = self._wrap_data(result_data, ttl_minutes=720)

        output_path = self.output_dir / "consensus.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ consensus.json 저장 완료 (서프라이즈 {len(major_surprises)}개)")
        return result

    def collect_fred(self) -> dict:
        """FRED API 기반 거시 데이터 수집 (병렬화 v2.0)"""
        print("📊 FRED 데이터 수집 중...")
        from fredapi import Fred
        from concurrent.futures import ThreadPoolExecutor
        fred = Fred(api_key=os.getenv('FRED_API_KEY'))

        series_map = {
            "fed_rate":         "FEDFUNDS",
            "us2y":             "DGS2",
            "us10y_fred":       "DGS10",
            "spread_10y2y":     "T10Y2Y",
            "sofr":             "SOFR",
            "m2_us":            "M2SL",
            "mmf_balance":      "WRMFSL",
            "ig_spread":        "BAMLC0A0CM",
            "hy_spread":        "BAMLH0A0HYM2",
            "financial_stress": "STLFSI4",
            "unemployment":     "UNRATE",
            "nfp":              "PAYEMS",
            "cpi_us":           "CPIAUCSL",
            "pce_core":         "PCEPILFE",
        }

        data = {}
        
        def fetch_single_fred(key, series_id):
            try:
                series = fred.get_series(series_id)
                val = round(float(series.dropna().iloc[-1]), 4)
                return key, val
            except Exception as e:
                print(f"  {key} 수집 실패: {e}")
                return key, None

        # 10개 스레드로 병렬 수집
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_key = {executor.submit(fetch_single_fred, k, s): k for k, s in series_map.items()}
            for future in future_to_key:
                key, val = future.result()
                data[key] = val
                if val is not None:
                    print(f"  {key}: {val}")

        result_data = {
            "date": self.today,
            "source": "FRED API",
            "data": data
        }

        # [REFACTORED] Wrap with metadata (FRED: LOW sensitivity -> 720m)
        result = self._wrap_data(result_data, ttl_minutes=720)

        output_path = self.output_dir / "fred.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ fred.json 저장 완료: {output_path}")
        return result

    def collect_ecos(self) -> dict:
        """한국은행 ECOS API 기반 데이터 수집 (병렬화 v2.0)"""
        print("🏦 ECOS 데이터 수집 중...")
        import requests
        from concurrent.futures import ThreadPoolExecutor

        api_key = os.getenv('ECOS_API_KEY')
        base_url = "https://ecos.bok.or.kr/api"

        def fetch_ecos_worker(key, stat_code, cycle, item_code, start, end):
            try:
                # ECOS URL Format: /STAT_CODE/CYCLE/START/END/ITEM_CODE
                url = f"{base_url}/StatisticSearch/{api_key}/json/kr/1/100/{stat_code}/{cycle}/{start}/{end}"
                if item_code and item_code != "0":
                    url += f"/{item_code}"
                resp = requests.get(url, timeout=10)
                json_resp = resp.json()
                
                if "RESULT" in json_resp and json_resp["RESULT"].get("CODE") != "INFO-000":
                    return key, None, None
                    
                rows = json_resp.get("StatisticSearch", {}).get("row", [])
                if rows:
                    latest_val = float(rows[-1]["DATA_VALUE"].replace(",", ""))
                    latest_date = rows[-1].get("TIME", "알수없음")
                    return key, latest_val, latest_date
            except:
                pass
            return key, None, None

        today = get_now_kst()
        ym = today.strftime("%Y%m")
        ym_start = (today - timedelta(days=180)).strftime("%Y%m")

        indicators = {
            "kr_base_rate":    ("722Y001", "M", "0101000"),
            "kr_cpi":          ("901Y009", "M", "0"),
            "kr_m2":           ("161Y005", "M", "BBHS00"),
            "kr_unemployment": ("901Y027", "M", "I61BC"),
            "kr_export":       ("901Y118", "M", "T002"),
            "kr_import":       ("901Y118", "M", "T004"),
        }

        data = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(fetch_ecos_worker, k, *v, ym_start, ym) for k, v in indicators.items()]
            for future in futures:
                k, val, date = future.result()
                data[k] = val
                if val is not None:
                    print(f"  ✅ {k}: {val} (최신 데이터 날짜: {date})")
                else:
                    print(f"  [MISSING] {k}")

        result_data = {
            "date": self.today,
            "source": "ECOS API",
            "data": data
        }

        # [REFACTORED] Wrap with metadata (ECOS: LOW sensitivity -> 720m)
        result = self._wrap_data(result_data, ttl_minutes=720)

        output_path = self.output_dir / "ecos.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ ecos.json 저장 완료: {output_path}")
        return result

    def extract_news_keywords(self, sentiment_data: dict) -> list:
        """뉴스 헤드라인에서 DART 검색용 키워드 추출 (v4.5)"""
        print("🧠 뉴스 기반 추적 키워드 추출 중...")
        # Local import removed (Deprecated v24.0)
        headlines = [h.get("title", "") for h in sentiment_data.get("data", {}).get("news_headlines", [])]
        
        if not headlines:
            return []

        keywords = set()
        
        # 1. AI 기반 추출 시도 (Primary)
        try:
            prompt = (
                "다음 뉴스 헤드라인들을 분석하여 DART 공시 시스템에서 '수주'나 '투자' 여부를 "
                "추적할만한 핵심 산업군, 섹터, 혹은 특정 기업명 5개를 JSON 리스트로 추출해줘. "
                f"뉴스: {headlines[:10]}"
            )
            resp = self.gemini.call_json(prompt)
            if isinstance(resp, list):
                keywords.update(resp)
                print(f"  AI 추출 키워드: {resp}")
        except Exception as e:
            print(f"  AI 키워드 추출 실패 (한도초과 등): {e}")

        # 2. 룰 기반 추출 (v24.0: Deprecated - AI extraction preferred)
        # 낡은 sector_map 대신 헤드라인에서 직접 명사 추출 등 보완 가능하나 현재는 AI 신뢰도 높음
        pass
        
        final_keywords = list(keywords)[:7] # 최대 7개 타격
        print(f"  최종 추적 키워드: {final_keywords}")
        return final_keywords

    def collect_dart(self, keywords: list = []) -> dict:
        """DART 공시 데이터 수집 - 뉴스 기반 정밀 타격 모드 (v4.5 Optimized)"""
        print(f"📋 DART 뉴스 기반 정밀 분석 중... (관심사: {keywords})")
        import time
        import OpenDartReader
        # Local import removed (Deprecated v24.0)

        api_key = os.getenv('OPENDART_API_KEY')
        if not api_key:
            print("  ⚠️ OPENDART_API_KEY가 없습니다.")
            return {"date": self.today, "data": {"disclosures": [], "themes": []}}
            
        dart = OpenDartReader(api_key)
        
        today = get_now_kst()
        # [OPTIMIZED] 검색 범위를 7일에서 3일로 단축 (API 부하 감소)
        bgn_de = (today - timedelta(days=3)).strftime("%Y%m%d")
        
        try:
            df = dart.list(start=bgn_de)
            if df is None or df.empty:
                return {"date": self.today, "data": {"disclosures": [], "themes": []}}
        except Exception as e:
            print(f"  DART 수집 실패: {e}")
            return {"date": self.today, "data": {"disclosures": [], "themes": []}}

        disclosures = []
        sector_hits = {}
        processed_count = 0
        # [QUOTA GUARD] 상세 문서 추출(dart.document)은 하루 할당량이 적으므로 한 세션당 최대 15건으로 제한
        MAX_DETAILED_DOCS = 15
        
        # 종목명 -> 섹터 매핑
        # [v24.0] Legacy sector mapping removed
        sectors = []
        def get_sector_for_corp(corp_name):
            return sectors[0] if sectors else None

        # 최신순 정렬 (이미 되어있을 확률이 높지만 보장)
        df = df.sort_values(by='rcept_dt', ascending=False)

        for _, row in df.iterrows():
            corp_name = row['corp_name']
            report_nm = row['report_nm']
            
            # [NEW] Agnostic Filter: 인간이 지정한 호재 단어 대신, 
            # 단순히 트렌드 키워드(keywords)와 관련된 기업의 공시만 수집
            is_news_relevant = False
            if keywords:
                is_news_relevant = any(str(kw).lower() in corp_name.lower() or str(kw).lower() in report_nm.lower() for kw in keywords)
            else:
                is_news_relevant = True # 키워드가 없으면 최신순 수집
            
            if is_news_relevant:
                amount_info = "수치 확인 중"
                
                # [OPTIMIZED] 상세 수치 추출은 할당량 내에서만 수행
                if processed_count < MAX_DETAILED_DOCS:
                    try:
                        # API 호출 간 지연 및 재시도 로직 (안정성 강화)
                        doc_html = None
                        for retry in range(2):
                            try:
                                time.sleep(0.5)
                                doc_html = dart.document(row['rcept_no'])
                                if doc_html: break
                            except Exception as de:
                                if "014" in str(de):
                                    print(f"  ℹ️ DART {row['rcept_no']} 문서 존재하지 않음 (014). 건너뜁니다.")
                                    break
                                time.sleep(1.0)
                        
                        if doc_html:
                            processed_count += 1
                            soup = BeautifulSoup(doc_html, "xml")
                            doc_text = soup.get_text(separator=" ", strip=True)
                            
                            # 정규표현식으로 수치 포착
                            match = re.search(r'(계약금액|투자금액|금액|자금).*?([\d,]+)\s*(원|백만원|억원|조원|달러)', doc_text, re.DOTALL)
                            if match:
                                amount_info = f"{match.group(2)} {match.group(3)}"
                                pct_match = re.search(r'(매출액|자산).*?대비.*?([\d.]+\s*%)', doc_text, re.DOTALL)
                                if pct_match:
                                    amount_info += f" ({pct_match.group(1)} 대비 {pct_match.group(2)})"
                    except Exception as e:
                        print(f"  ⚠️ DART 상세 추출 실패 ({corp_name}): {str(e)[:50]}")
                
                disclosures.append({
                    "company": corp_name,
                    "title": report_nm,
                    "amount": amount_info,
                    "type": "NEWS_RELEVANT" if is_news_relevant else "BULLISH",
                    "link": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}",
                    "date": row['rcept_dt']
                })
                
                sector = get_sector_for_corp(corp_name)
                if sector:
                    sector_hits[sector] = sector_hits.get(sector, 0) + (2 if is_bullish else 1)
                
                # 결과값이 충분히 모였으면 중단 (리포트 가독성 및 성능)
                if len(disclosures) >= 30:
                    break

        result_data = {
            "date": self.today,
            "data": {
                "disclosures": disclosures,
                "themes": sorted(sector_hits.items(), key=lambda x: x[1], reverse=True)
            }
        }

        # [REFACTORED] Wrap with metadata (DART: MID sensitivity -> 120m)
        result = self._wrap_data(result_data, ttl_minutes=120)

        output_path = self.output_dir / "dart.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ dart.json 저장 완료 (공시 {len(disclosures)}건 캡처, 상세분석 {processed_count}건)")
        return result

    def run(self):
        """전체 수집 프로세스 실행 (v3.0 modular)"""
        print(f"\n🚀 AGENT-01 COLLECTOR v3.0 시작 [{self.today}]")
        from src.agents.collectors.collector_runner import CollectorRunner
        runner = CollectorRunner(output_dir=self.output_dir)
        return runner.run_all()


if __name__ == "__main__":
    CollectorAgent().run()
