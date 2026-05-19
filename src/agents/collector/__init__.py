import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.utils.target_date import get_now_kst, get_target_ymd, get_current_round, get_standard_path_prefix

load_dotenv()


class CollectorAgent:

    def __init__(self):
        from src.core.gemini_client import GeminiClient
        self.today = get_target_ymd().replace("-", "")
        self.round = os.environ.get("HOIN_TARGET_ROUND", str(get_current_round()))
        self.path_prefix = get_standard_path_prefix()
        self.output_dir = Path("data/raw") / self.path_prefix
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_dir = Path(".")
        self.gemini = GeminiClient()

    # ── 공유 헬퍼 ──────────────────────────────────────────

    def _fetch_yahoo_chart(self, ticker: str, range_str: str = "90d") -> pd.DataFrame:
        import requests
        headers = {"User-Agent": "Mozilla/5.0"}
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
                    df = df.dropna()
                    if not df.empty:
                        return df
            except Exception:
                continue
        return pd.DataFrame()

    def _wrap_data(self, data: dict, ttl_minutes: int, source_timestamp: str = None) -> dict:
        return {
            "metadata": {
                "collected_at": get_now_kst().isoformat(),
                "source_timestamp": source_timestamp,
                "cache_hit": False,
                "ttl_policy_minutes": ttl_minutes,
                "freshness_status": "FRESH" if data is not None else "UNKNOWN",
            },
            "data": data,
        }

    def _get_kospi(self) -> dict:
        result = {"kospi": None, "kospi_1d_change": None, "history": None}
        for ticker in ["^KS11", "KS11.KS", "000001.KS"]:
            try:
                hist = self._fetch_yahoo_chart(ticker, "90d")
                if len(hist) >= 2:
                    latest = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    if latest > 2500:
                        result["kospi"] = round(latest, 2)
                        result["kospi_1d_change"] = round((latest - prev) / prev * 100, 2)
                        result["history"] = {
                            "current": result["kospi"],
                            "avg_90d": round(float(hist["Close"].mean()), 2),
                            "max_90d": round(float(hist["Close"].max()), 2),
                            "min_90d": round(float(hist["Close"].min()), 2),
                            "trend": list(hist["Close"].tail(30).round(2)),
                        }
                        return result
            except Exception as e:
                print(f"  {ticker} 실패: {e}")
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
                        hist["Close"] = hist["Close"] * 10
                    if val > 1000:
                        result["value"] = val
                        result["history"] = {
                            "current": val,
                            "avg_90d": round(float(hist["Close"].mean()), 2),
                            "max_90d": round(float(hist["Close"].max()), 2),
                            "min_90d": round(float(hist["Close"].min()), 2),
                            "trend": list(hist["Close"].tail(30).round(2)),
                        }
                        return result
            except Exception as e:
                print(f"  gold {ticker} 실패: {e}")
        return result

    def _get_dxy(self) -> dict:
        result = {"value": None, "history": None}
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
                        "trend": list(hist["Close"].tail(30).round(2)),
                    }
                    return result
        except Exception:
            pass
        try:
            from fredapi import Fred
            fred = Fred(api_key=os.getenv("FRED_API_KEY"))
            series = fred.get_series("DTWEXBGS", observation_start=(get_now_kst() - timedelta(days=100)).strftime("%Y-%m-%d"))
            if not series.empty:
                s = series.dropna()
                val = round(float(s.iloc[-1]), 2)
                result["value"] = val
                result["history"] = {"current": val, "avg_90d": round(float(s.mean()), 2),
                                     "max_90d": round(float(s.max()), 2), "min_90d": round(float(s.min()), 2),
                                     "trend": list(s.tail(30).round(2))}
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
                    result["history"] = {"current": val, "avg_90d": round(float(hist["Close"].mean()), 2),
                                         "max_90d": round(float(hist["Close"].max()), 2),
                                         "min_90d": round(float(hist["Close"].min()), 2),
                                         "trend": list(hist["Close"].tail(30).round(2))}
                    return result
        except Exception:
            pass
        return result

    def _get_nasdaq(self) -> dict:
        result = {"value": None, "history": None}
        try:
            hist = self._fetch_yahoo_chart("^IXIC", "90d")
            if not hist.empty:
                val = round(float(hist["Close"].iloc[-1]), 2)
                if val > 15000:
                    result["value"] = val
                    result["history"] = {"current": val, "avg_90d": round(float(hist["Close"].mean()), 2),
                                         "max_90d": round(float(hist["Close"].max()), 2),
                                         "min_90d": round(float(hist["Close"].min()), 2),
                                         "trend": list(hist["Close"].tail(30).round(2))}
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
                result["history"] = {"current": val, "avg_90d": round(float(hist["Close"].mean()), 2),
                                     "max_90d": round(float(hist["Close"].max()), 2),
                                     "min_90d": round(float(hist["Close"].min()), 2),
                                     "trend": list(hist["Close"].tail(30).round(2))}
        except Exception as e:
            print(f"  vix 실패: {e}")
        return result

    def _get_wti(self) -> dict:
        result = {"value": None, "1d_change": None, "5d_change": None, "20d_change": None, "history": None}
        try:
            hist = self._fetch_yahoo_chart("CL=F", "31d")
            if not hist.empty and len(hist) >= 2:
                current = float(hist["Close"].iloc[-1])
                prev1 = float(hist["Close"].iloc[-2])
                result["value"] = round(current, 2)
                result["1d_change"] = round((current - prev1) / prev1 * 100, 2)
                if len(hist) >= 6:
                    result["5d_change"] = round((current - float(hist["Close"].iloc[-6])) / float(hist["Close"].iloc[-6]) * 100, 2)
                if len(hist) >= 21:
                    result["20d_change"] = round((current - float(hist["Close"].iloc[-21])) / float(hist["Close"].iloc[-21]) * 100, 2)
                result["history"] = {"current": result["value"], "avg_90d": round(float(hist["Close"].mean()), 2),
                                     "max_90d": round(float(hist["Close"].max()), 2),
                                     "min_90d": round(float(hist["Close"].min()), 2),
                                     "trend": list(hist["Close"].tail(30).round(2))}
        except Exception as e:
            print(f"  wti 실패: {e}")
        return result

    def _get_kospi_foreign_vol(self) -> float:
        try:
            hist = self._fetch_yahoo_chart("^KS11", "5d")
            if len(hist) >= 2:
                val = round((float(hist["Volume"].iloc[-1]) - float(hist["Volume"].iloc[-2])) / 1e8, 1)
                return val if val != 0.0 else None
        except Exception:
            pass
        return None

    def _get_fear_greed(self) -> float:
        try:
            import requests
            resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
            if resp.status_code == 200:
                return float(resp.json()["data"][0]["value"])
        except Exception as e:
            print(f"  Fear&Greed 실패: {e}")
        return None

    def _calculate_multi_period_stats(self, data: dict) -> dict:
        import numpy as np
        stats = {}
        ticker_map = {
            "usd_krw": "KRW=X", "gold": "GC=F", "wti_oil": "CL=F",
            "vix": "^VIX", "us10y": "^TNX", "dxy": "DX-Y.NYB",
            "sp500": "^GSPC", "kospi": "^KS11",
        }
        for key, ticker in ticker_map.items():
            try:
                p = "31d" if key == "wti_oil" else "90d"
                hist = self._fetch_yahoo_chart(ticker, p)
                if len(hist) < 5:
                    continue
                closes = hist["Close"].dropna().values
                current = float(closes[-1])
                avg_5d = float(np.mean(closes[-5:])) if len(closes) >= 5 else None
                avg_20d = float(np.mean(closes[-20:])) if len(closes) >= 20 else None
                chg_5d = round((current - closes[-6]) / closes[-6] * 100, 2) if len(closes) >= 6 else None
                chg_20d = round((current - closes[-21]) / closes[-21] * 100, 2) if len(closes) >= 21 else None
                if len(closes) >= 20:
                    mean_20 = float(np.mean(closes[-20:]))
                    std_20 = float(np.std(closes[-20:]))
                    z_score = round((current - mean_20) / std_20, 2) if std_20 > 0 else 0
                else:
                    z_score = None
                stats[key] = {
                    "current": round(current, 4),
                    "avg_5d": round(avg_5d, 4) if avg_5d else None,
                    "avg_20d": round(avg_20d, 4) if avg_20d else None,
                    "chg_5d": chg_5d, "chg_20d": chg_20d,
                    "z_score_20d": z_score,
                    "high_5d": round(float(np.max(closes[-5:])), 4) if len(closes) >= 5 else None,
                    "low_5d": round(float(np.min(closes[-5:])), 4) if len(closes) >= 5 else None,
                }
            except Exception as e:
                print(f"  stats {key} 실패: {e}")
        return stats

    # ── 수집 메서드 (서브 에이전트가 호출) ──────────────────

    def collect_market(self) -> dict:
        print("📈 시장 데이터 수집 중...")
        data = {}
        history_90d = {}

        kospi_data = self._get_kospi()
        data["kospi"] = kospi_data["kospi"]
        data["kospi_1d_change"] = kospi_data["kospi_1d_change"]
        if kospi_data["history"]:
            history_90d["kospi"] = kospi_data["history"]

        for getter, key in [(self._get_gold, "gold"), (self._get_dxy, "dxy"),
                            (self._get_sp500, "sp500"), (self._get_nasdaq, "nasdaq")]:
            d = getter()
            data[key] = d["value"]
            if d["history"]:
                history_90d[key] = d["history"]

        wti = self._get_wti()
        data["wti_oil"] = wti["value"]
        data["wti_1d_change"] = wti["1d_change"]
        data["wti_5d_change"] = wti["5d_change"]
        data["wti_20d_change"] = wti["20d_change"]
        if wti["history"]:
            history_90d["wti_oil"] = wti["history"]

        for key, ticker in {"vix": "^VIX", "us10y": "^TNX", "brent": "BZ=F", "usd_krw": "KRW=X"}.items():
            try:
                hist = self._fetch_yahoo_chart(ticker, "90d")
                if not hist.empty:
                    data[key] = round(float(hist["Close"].iloc[-1]), 2)
                    history_90d[key] = {"current": data[key],
                                        "avg_90d": round(float(hist["Close"].mean()), 2),
                                        "max_90d": round(float(hist["Close"].max()), 2),
                                        "min_90d": round(float(hist["Close"].min()), 2),
                                        "trend": list(hist["Close"].tail(30).round(2))}
                else:
                    data[key] = None
            except Exception as e:
                print(f"  {key} 실패: {e}")
                data[key] = None

        data["kospi_foreign_net"] = self._get_kospi_foreign_vol()
        data["fear_greed_index"] = self._get_fear_greed()
        data["multi_period_stats"] = self._calculate_multi_period_stats(data)

        result_data = {"date": self.today, "data": data, "history_90d": history_90d}
        result = self._wrap_data(result_data, ttl_minutes=30)
        output_path = self.output_dir / "market.json"
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        hist_dir = self.base_dir / "data/raw/history"
        hist_dir.mkdir(parents=True, exist_ok=True)
        (hist_dir / "market_90d.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ market.json 저장")
        return result

    def collect_fred(self) -> dict:
        print("📊 FRED 데이터 수집 중...")
        from fredapi import Fred
        from concurrent.futures import ThreadPoolExecutor
        fred = Fred(api_key=os.getenv("FRED_API_KEY"))
        series_map = {
            "fed_rate": "FEDFUNDS", "us2y": "DGS2", "us10y_fred": "DGS10",
            "spread_10y2y": "T10Y2Y", "sofr": "SOFR", "m2_us": "M2SL",
            "mmf_balance": "WRMFSL", "ig_spread": "BAMLC0A0CM",
            "hy_spread": "BAMLH0A0HYM2", "financial_stress": "STLFSI4",
            "unemployment": "UNRATE", "nfp": "PAYEMS",
            "cpi_us": "CPIAUCSL", "pce_core": "PCEPILFE",
        }
        data = {}

        def fetch_one(kv):
            key, sid = kv
            try:
                return key, round(float(fred.get_series(sid).dropna().iloc[-1]), 4)
            except Exception as e:
                print(f"  {key} 실패: {e}")
                return key, None

        with ThreadPoolExecutor(max_workers=10) as ex:
            for key, val in ex.map(fetch_one, series_map.items()):
                data[key] = val
                if val is not None:
                    print(f"  {key}: {val}")

        result = self._wrap_data({"date": self.today, "source": "FRED API", "data": data}, ttl_minutes=720)
        (self.output_dir / "fred.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ fred.json 저장")
        return result

    def collect_ecos(self) -> dict:
        print("🏦 ECOS 데이터 수집 중...")
        import requests
        from concurrent.futures import ThreadPoolExecutor
        api_key = os.getenv("ECOS_API_KEY")
        base_url = "https://ecos.bok.or.kr/api"
        today = get_now_kst()
        ym = today.strftime("%Y%m")
        ym_start = (today - timedelta(days=180)).strftime("%Y%m")

        def fetch_ecos(kv):
            key, (stat_code, cycle, item_code) = kv
            try:
                url = f"{base_url}/StatisticSearch/{api_key}/json/kr/1/100/{stat_code}/{cycle}/{ym_start}/{ym}"
                if item_code and item_code != "0":
                    url += f"/{item_code}"
                rows = requests.get(url, timeout=10).json().get("StatisticSearch", {}).get("row", [])
                if rows:
                    return key, float(rows[-1]["DATA_VALUE"].replace(",", ""))
            except Exception:
                pass
            return key, None

        indicators = {
            "kr_base_rate": ("722Y001", "M", "0101000"), "kr_cpi": ("901Y009", "M", "0"),
            "kr_m2": ("161Y005", "M", "BBHS00"), "kr_unemployment": ("901Y027", "M", "I61BC"),
            "kr_export": ("901Y118", "M", "T002"), "kr_import": ("901Y118", "M", "T004"),
        }
        data = {}
        with ThreadPoolExecutor(max_workers=6) as ex:
            for key, val in ex.map(fetch_ecos, indicators.items()):
                data[key] = val
                print(f"  {'✅' if val else '[MISSING]'} {key}: {val}")

        result = self._wrap_data({"date": self.today, "source": "ECOS API", "data": data}, ttl_minutes=720)
        (self.output_dir / "ecos.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ ecos.json 저장")
        return result

    def collect_consensus(self) -> dict:
        print("📅 컨센서스 데이터 수집 중...")
        from fredapi import Fred
        fred = Fred(api_key=os.getenv("FRED_API_KEY"))
        today = get_now_kst()
        result_events = []
        for series_id, name, unit in [
            ("CPIAUCSL", "미국 CPI", "전월비"), ("CPILFESL", "미국 Core CPI", "전월비"),
            ("PAYEMS", "미국 비농업고용", "천명"), ("UNRATE", "미국 실업률", "%"),
            ("FEDFUNDS", "미국 기준금리", "%"), ("T10Y2Y", "10Y-2Y 금리스프레드", "bp"),
        ]:
            try:
                series = fred.get_series(series_id, today - timedelta(days=90), today).dropna()
                if len(series) < 2:
                    continue
                current_val, p_val = float(series.iloc[-1]), float(series.iloc[-2])
                change = round(current_val - p_val, 4)
                if len(series) >= 12:
                    recent = [float(series.iloc[i] - series.iloc[i - 1]) for i in range(-12, -1)]
                    avg_chg = sum(recent) / len(recent) if recent else 0
                    surprise = round(change - avg_chg, 4)
                    surprise_pct = round((change - avg_chg) / abs(avg_chg) * 100, 2) if avg_chg != 0 else 0
                else:
                    surprise, surprise_pct = 0, 0
                result_events.append({"series_id": series_id, "event": name, "unit": unit,
                                      "actual": current_val, "previous": p_val, "change": change,
                                      "surprise": surprise, "surprise_pct": surprise_pct,
                                      "surprise_direction": "BEAT" if surprise > 0 else "MISS"})
            except Exception:
                pass

        major_surprises = [e for e in result_events if abs(e.get("surprise_pct", 0)) > 10]
        result_data = {"date": today.strftime("%Y%m%d"), "source": "FRED API",
                       "total_events": len(result_events), "major_surprises": major_surprises,
                       "all_events": result_events}
        result = self._wrap_data(result_data, ttl_minutes=720)
        (self.output_dir / "consensus.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ consensus.json 저장 (서프라이즈 {len(major_surprises)}개)")
        return result

    def collect_sentiment(self) -> dict:
        print("📰 뉴스 데이터 수집 중...")
        import feedparser
        import requests
        from concurrent.futures import ThreadPoolExecutor
        rss_feeds = [
            # 글로벌 경제/금융
            {"name": "FT Markets",      "url": "https://www.ft.com/markets?format=rss"},
            {"name": "CNBC Economy",    "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html"},
            {"name": "Yahoo Finance",   "url": "https://finance.yahoo.com/news/rssindex"},
            # IB 리포트 / 애널리스트 등급·목표주가 변경 전용
            {"name": "MarketBeat",      "url": "https://www.marketbeat.com/rss/analyst-ratings/"},
            {"name": "Benzinga Analyst","url": "https://www.benzinga.com/feeds/analyst-ratings"},
            {"name": "Seeking Alpha",   "url": "https://seekingalpha.com/market-currents.xml"},
            # 국내 경제지
            {"name": "Yonhap English",  "url": "https://en.yna.co.kr/RSS/news.xml"},
            {"name": "연합뉴스",          "url": "https://www.yna.co.kr/rss/economy.xml"},
            {"name": "한국경제",          "url": "https://www.hankyung.com/feed/economy"},
            {"name": "매일경제",          "url": "https://www.mk.co.kr/rss/30100041/"},
        ]

        def fetch_rss(feed):
            items = []
            try:
                resp = requests.get(feed["url"], timeout=7, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    now = get_now_kst()
                    for entry in feedparser.parse(resp.content).entries[:50]:
                        pub = entry.get("published_parsed")
                        if pub:
                            pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                            pub_date_str = pub_dt.strftime("%Y-%m-%d")
                            pub_iso = pub_dt.isoformat()
                        else:
                            pub_date_str = now.strftime("%Y-%m-%d")
                            pub_iso = now.isoformat()
                        prefix = f"[{pub_date_str}] "
                        items.append({
                            "title": prefix + entry.get("title", "").strip(),
                            "summary": entry.get("summary", "")[:1000].strip(),
                            "source": feed["name"],
                            "link": entry.get("link", ""),
                            "pubDate": pub_iso,
                        })
            except Exception as e:
                print(f"  [RSS] {feed['name']}: {e}")
            return items

        headlines = []
        with ThreadPoolExecutor(max_workers=5) as ex:
            for items in ex.map(fetch_rss, rss_feeds):
                headlines.extend(items)

        print(f"  뉴스 {len(headlines)}개 수집")
        result = self._wrap_data({"date": self.today, "data": {"news_headlines": headlines}}, ttl_minutes=30)
        (self.output_dir / "sentiment.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ sentiment.json 저장")
        return result

    def extract_news_keywords(self, sentiment_data: dict) -> list:
        headlines = [h.get("title", "") for h in sentiment_data.get("data", {}).get("news_headlines", [])]
        if not headlines or not self.gemini:
            return []
        try:
            prompt = (f"다음 뉴스 헤드라인들을 분석하여 DART 공시 시스템에서 추적할 핵심 산업군/기업명 5개를 "
                      f"JSON 리스트로 추출해줘. 뉴스: {headlines[:10]}")
            resp = self.gemini.call_json(prompt)
            return resp[:7] if isinstance(resp, list) else []
        except Exception:
            return []

    def collect_dart(self, keywords: list = None) -> dict:
        if keywords is None:
            keywords = []
        print(f"📋 DART 수집 중... (키워드: {keywords})")
        import time
        import OpenDartReader
        api_key = os.getenv("OPENDART_API_KEY")
        if not api_key:
            print("  ⚠️ OPENDART_API_KEY 없음")
            return {"date": self.today, "data": {"disclosures": [], "themes": []}}
        dart = OpenDartReader(api_key)
        today = get_now_kst()
        bgn_de = (today - timedelta(days=3)).strftime("%Y%m%d")
        try:
            df = dart.list(start=bgn_de)
            if df is None or df.empty:
                return {"date": self.today, "data": {"disclosures": [], "themes": []}}
        except Exception as e:
            print(f"  DART 실패: {e}")
            return {"date": self.today, "data": {"disclosures": [], "themes": []}}

        disclosures = []
        processed = 0
        df = df.sort_values(by="rcept_dt", ascending=False)
        for _, row in df.iterrows():
            corp_name, report_nm = row["corp_name"], row["report_nm"]
            is_relevant = (any(str(kw).lower() in corp_name.lower() or str(kw).lower() in report_nm.lower()
                               for kw in keywords) if keywords else True)
            if is_relevant:
                amount_info = "수치 확인 중"
                if processed < 15:
                    try:
                        time.sleep(0.5)
                        doc_html = dart.document(row["rcept_no"])
                        if doc_html:
                            processed += 1
                            doc_text = BeautifulSoup(doc_html, "xml").get_text(separator=" ", strip=True)
                            match = re.search(r"(계약금액|투자금액|금액|자금).*?([\d,]+)\s*(원|백만원|억원|조원|달러)", doc_text, re.DOTALL)
                            if match:
                                amount_info = f"{match.group(2)} {match.group(3)}"
                    except Exception:
                        pass
                disclosures.append({"company": corp_name, "title": report_nm, "amount": amount_info,
                                    "link": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}",
                                    "date": row["rcept_dt"]})
                if len(disclosures) >= 30:
                    break

        result = self._wrap_data({"date": self.today, "data": {"disclosures": disclosures, "themes": []}}, ttl_minutes=120)
        (self.output_dir / "dart.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ dart.json 저장 ({len(disclosures)}건)")
        return result

    # ── 진입점 ──────────────────────────────────────────────

    def run(self):
        print(f"\n🚀 AGENT-01 COLLECTOR 시작 [{self.today}]")
        from src.agents.collector.collector_runner import CollectorRunner
        runner = CollectorRunner(output_dir=self.output_dir)
        return runner.run_all()


if __name__ == "__main__":
    CollectorAgent().run()
