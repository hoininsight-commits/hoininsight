import json
import os
import yfinance as yf
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CollectorAgent:

    def _get_kospi(self) -> dict:
        import yfinance as yf
        result = {"kospi": None, "kospi_1d_change": None, "history": None}
        
        tickers_to_try = ["^KS11", "KS11.KS", "000001.KS"]
        
        for ticker in tickers_to_try:
            try:
                t = yf.Ticker(ticker)
                # 90일 히스토리 수집 (버그 수정: 6000대 값 추적 및 히스토리 보존)
                hist = t.history(period="90d")
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
        import yfinance as yf
        result = {"value": None, "history": None}
        for ticker in ["GC=F", "GLD", "IAU"]:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="90d")
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
        import yfinance as yf
        result = {"value": None, "history": None}
        # 1. DX-Y.NYB 시도
        try:
            t = yf.Ticker("DX-Y.NYB")
            hist = t.history(period="90d")
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
            series = fred.get_series("DTWEXBGS", observation_start=(datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d'))
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
        import yfinance as yf
        result = {"value": None, "history": None}
        try:
            t = yf.Ticker("^GSPC")
            hist = t.history(period="90d")
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
            series = fred.get_series("SP500", observation_start=(datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d'))
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
        import yfinance as yf
        result = {"value": None, "history": None}
        try:
            t = yf.Ticker("^IXIC")
            hist = t.history(period="90d")
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

    def __init__(self):
        from src.core.gemini_client import GeminiClient
        self.today = datetime.now().strftime("%Y%m%d")
        self.output_dir = Path(f"data/raw/{self.today}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # base_dir 설정 (history 저장용)
        self.base_dir = Path(".")
        self.gemini = GeminiClient()

        # 외국인 수급 (별도 계산)
        data["kospi_foreign_net"] = self._get_kospi_foreign_vol()
        data["fear_greed_index"] = self._get_fear_greed()
        data["usd_krw"] = data.get("usd_krw", 1380.0)

        # 5. 로컬 v4.0 지능형 통계 계산 (Z-score 등) 통합
        multi_stats = {}
        stats_tickers = {
            "KOSPI": "^KS11", "VIX": "^VIX", "WTI": "CL=F", "USD_KRW": "KRW=X",
            "S&P500": "^GSPC", "NASDAQ": "^IXIC", "DXY": "DX-Y.NYB", "US10Y": "^TNX"
        }
        import numpy as np
        for name, ticker_code in stats_tickers.items():
            try:
                t = yf.Ticker(ticker_code)
                hist = t.history(period="1mo")
                if len(hist) >= 6:
                    c_val = float(hist["Close"].iloc[-1])
                    p_5d = float(hist["Close"].iloc[-6])
                    chg_5d = round(((c_val - p_5d) / p_5d) * 100, 2)
                    returns = hist["Close"].pct_change().dropna()
                    if len(returns) >= 5:
                        m_ret, s_ret = returns.mean(), returns.std()
                        c_ret = (c_val - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]
                        zscore = round((c_ret - m_ret) / s_ret, 2) if s_ret > 0 else 0
                    else: zscore = 0
                    multi_stats[name] = {"current": round(c_val, 2), "change_5d_pct": chg_5d, "zscore_5d": zscore}
            except: pass
        data["fear_greed_index"] = self._get_fear_greed()
        data["usd_krw"] = data.get("usd_krw", 1380.0) # 위 stats_tickers에서 수집됨

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": data,
            "multi_period_stats": multi_stats,
            "history_90d": history_90d
        }

        # 오늘 데이터 저장
        output_path = self.output_dir / "market.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 90일 히스토리 별도 저장 (Detector/Analyst 참조용)
        history_dir = self.base_dir / "data/raw/history"
        history_dir.mkdir(parents=True, exist_ok=True)
        (history_dir / "market_90d.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

        print(f"✅ market.json (히스토리+통계 포함) 저장 완료: {output_path}")
        return result

    def _get_kospi_foreign_vol(self) -> float:
        try:
            kospi = yf.Ticker("^KS11")
            hist = kospi.history(period="2d")
            if len(hist) >= 2:
                vol_change = float(hist["Volume"].iloc[-1]) - float(hist["Volume"].iloc[-2])
                return round(vol_change / 1e8, 1)
        except:
            pass
        return 0.0

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
            print(f"  Fear&Greed 수집 실패, 기본값 사용: {e}")
        return 25.0  # fallback

    def _get_usd_krw(self) -> float:
        """환율 수집"""
        try:
            krw = yf.Ticker("KRW=X")
            hist = krw.history(period="1d")
            if len(hist) > 0:
                return round(float(hist["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"환율 수집 실패: {e}")
        return 1380.0  # fallback

    def collect_macro(self) -> dict:
        """거시경제 데이터 — FRED/ECOS API 연동"""
        print("🏦 거시경제 데이터 수집 중...")
        import os, requests
        from fredapi import Fred

        data = {}

        # FRED에서 미국 기준금리
        try:
            fred = Fred(api_key=os.getenv('FRED_API_KEY'))
            series = fred.get_series('FEDFUNDS')
            data['us_fed_rate'] = round(float(series.dropna().iloc[-1]), 4)
            print(f"  us_fed_rate: {data['us_fed_rate']}")
        except Exception as e:
            print(f"  us_fed_rate 수집 실패: {e}")
            data['us_fed_rate'] = None

        # ECOS에서 한국 기준금리
        try:
            api_key = os.getenv('ECOS_API_KEY')
            from datetime import datetime, timedelta
            today = datetime.now()
            ym = today.strftime("%Y%m")
            ym_prev = (today - timedelta(days=60)).strftime("%Y%m")
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/1/722Y001/M/{ym_prev}/{ym}/0101000"
            resp = requests.get(url, timeout=10)
            rows = resp.json().get("StatisticSearch", {}).get("row", [])
            if rows:
                data['korea_base_rate'] = float(rows[-1]["DATA_VALUE"].replace(",", ""))
                print(f"  korea_base_rate: {data['korea_base_rate']}")
            else:
                data['korea_base_rate'] = None
        except Exception as e:
            print(f"  korea_base_rate 수집 실패: {e}")
            data['korea_base_rate'] = None

        # ECOS에서 한국 M2
        try:
            api_key = os.getenv('ECOS_API_KEY')
            url = f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/1/101Y004/M/{ym_prev}/{ym}/BBIA00"
            resp = requests.get(url, timeout=10)
            rows = resp.json().get("StatisticSearch", {}).get("row", [])
            if rows:
                data['korea_m2'] = float(rows[-1]["DATA_VALUE"].replace(",", ""))
                print(f"  korea_m2: {data['korea_m2']}")
            else:
                data['korea_m2'] = None
        except Exception as e:
            print(f"  korea_m2 수집 실패: {e}")
            data['korea_m2'] = None

        # 금리차 파생
        if data.get('us_fed_rate') and data.get('korea_base_rate'):
            data['rate_diff'] = round(data['us_fed_rate'] - data['korea_base_rate'], 4)
        else:
            data['rate_diff'] = None

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "source": "FRED + ECOS API",
            "data": data
        }

        output_path = self.output_dir / "macro.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ macro.json 저장 완료: {output_path}")
        return result

    def collect_sentiment(self) -> dict:
        """뉴스/감성 데이터 — 글로벌 경제 RSS 실제 수집"""
        print("📰 글로벌 뉴스 데이터 수집 중...")
        import feedparser
        import requests

        headlines = []
        rss_feeds = [
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss"},
            {"name": "Reuters", "url": "https://feeds.reuters.com/reuters/businessNews"},
            {"name": "CNBC", "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html"},
            {"name": "Yonhap English", "url": "https://en.yna.co.kr/RSS/economy.xml"},
            {"name": "연합뉴스", "url": "https://www.yna.co.kr/rss/economy.xml"},
            {"name": "매일경제", "url": "https://www.mk.co.kr/rss/30000001/"},
        ]

        for feed in rss_feeds:
            try:
                # requests로 먼저 가져온 뒤 feedparser로 파싱 (차단 방지)
                resp = requests.get(feed["url"], timeout=10, 
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
                if resp.status_code == 200:
                    d = feedparser.parse(resp.content)
                    items = d.entries[:10]  # 각 채널당 상위 10개
                    for entry in items:
                        headlines.append({
                            "title": entry.get("title", "").strip(),
                            "summary": entry.get("summary", "")[:200].strip(),
                            "link": entry.get("link", ""),
                            "source": feed["name"],
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    print(f"  RSS 응답 오류 ({feed['name']}): {resp.status_code}")
            except Exception as e:
                print(f"  RSS 수집 실패 ({feed['name']}): {e}")

        # 권위자 키워드 탐지
        authority_keywords = [
            "버핏", "이재용", "머스크", "파월", "이창용", "트럼프", "바이든",
            "Buffett", "Powell", "Elon Musk", "Fed", "Treasury", "Biden", "Trump"
        ]
        authority_signals = []
        for h in headlines:
            for kw in authority_keywords:
                if kw.lower() in h["title"].lower():
                    authority_signals.append({
                        "person": kw,
                        "action": h["title"],
                        "source": h["source"],
                        "timestamp": h["timestamp"]
                    })
                    break

        print(f"  총 뉴스 {len(headlines)}개, 권위자 관련 {len(authority_signals)}개 포착")

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": {
                "news_headlines": headlines,
                "authority_signals": authority_signals
            }
        }

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
        today = datetime.now()
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

        major_surprises = sorted([e for e in result_events if abs(e.get("surprise_pct", 0)) > 10], key=lambda x: abs(x.get("surprise_pct", 0)), reverse=True)[:5]
        output = {"date": self.today, "collected_at": datetime.now().isoformat(), "source": "FRED API", "total_events": len(result_events), "major_surprises": major_surprises, "all_events": result_events}
        output_path = self.output_dir / "consensus.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ consensus.json 저장 완료 (서프라이즈 {len(major_surprises)}개)")
        return output
    def collect_fred(self) -> dict:
        """FRED API 기반 거시 데이터 수집"""
        print("📊 FRED 데이터 수집 중...")
        from fredapi import Fred
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
        for key, series_id in series_map.items():
            try:
                series = fred.get_series(series_id)
                data[key] = round(float(series.dropna().iloc[-1]), 4)
                print(f"  {key}: {data[key]}")
            except Exception as e:
                print(f"  {key} 수집 실패: {e}")
                data[key] = None

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "source": "FRED API",
            "data": data
        }

        output_path = self.output_dir / "fred.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ fred.json 저장 완료: {output_path}")
        return result

    def collect_ecos(self) -> dict:
        """한국은행 ECOS API 기반 데이터 수집"""
        print("🏦 ECOS 데이터 수집 중...")
        import requests

        api_key = os.getenv('ECOS_API_KEY')
        base_url = "https://ecos.bok.or.kr/api"

        def fetch_ecos(stat_code, cycle, start, end, item_code=""):
            try:
                url = f"{base_url}/StatisticSearch/{api_key}/json/kr/1/1/{stat_code}/{cycle}/{start}/{end}"
                if item_code:
                    url += f"/{item_code}"
                resp = requests.get(url, timeout=10)
                json_resp = resp.json()
                rows = json_resp.get("StatisticSearch", {}).get("row", [])
                if rows:
                    return float(rows[-1]["DATA_VALUE"].replace(",", ""))
            except Exception as e:
                print(f"  ECOS {stat_code} 실패: {e}")
            return None

        from datetime import datetime, timedelta
        today = datetime.now()
        ym = today.strftime("%Y%m")
        ym_prev = (today - timedelta(days=30)).strftime("%Y%m")

        data = {
            "kr_base_rate":    fetch_ecos("722Y001", "M", ym_prev, ym, "0101000"),
            "kr_cpi":          fetch_ecos("901Y009", "M", ym_prev, ym, "0"),
            "kr_m2":           fetch_ecos("101Y004", "M", ym_prev, ym, "BBIA00"),
            "kr_unemployment": fetch_ecos("901Y027", "M", ym_prev, ym, "L1200301"),
            "kr_export":       fetch_ecos("901Y015", "M", ym_prev, ym, "T10"),
            "kr_import":       fetch_ecos("901Y015", "M", ym_prev, ym, "T11"),
        }

        for k, v in data.items():
            print(f"  {k}: {v}")

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "source": "ECOS API (한국은행)",
            "data": data
        }

        output_path = self.output_dir / "ecos.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ ecos.json 저장 완료: {output_path}")
        return result

    def extract_news_keywords(self, sentiment_data: dict) -> list:
        """뉴스 헤드라인에서 DART 검색용 키워드 추출 (v4.5)"""
        print("🧠 뉴스 기반 추적 키워드 추출 중...")
        from src.core.sector_map import SECTOR_STOCK_MAP
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

        # 2. 룰 기반 추출 (Fallback: 가동성 보장)
        for h in headlines:
            for sector, info in SECTOR_STOCK_MAP.items():
                if sector in h or any(kw in h for kw in info.get("keywords", [])):
                    keywords.add(sector)
                for name in info.get("names", []):
                    if name in h:
                        keywords.add(name)
        
        final_keywords = list(keywords)[:7] # 최대 7개 타격
        print(f"  최종 추적 키워드: {final_keywords}")
        return final_keywords

    def collect_dart(self, keywords: list = []) -> dict:
        """DART 공시 데이터 수집 - 뉴스 기반 정밀 타격 모드 (v4.5)"""
        print(f"📋 DART 뉴스 기반 정밀 분석 중... (관심사: {keywords})")
        import OpenDartReader
        from src.core.sector_map import SECTOR_STOCK_MAP
        from datetime import datetime, timedelta

        api_key = os.getenv('OPENDART_API_KEY')
        dart = OpenDartReader(api_key)
        
        today = datetime.now()
        bgn_de = (today - timedelta(days=7)).strftime("%Y%m%d")
        
        try:
            df = dart.list(start=bgn_de)
            if df.empty:
                return {"date": self.today, "data": {"disclosures": [], "themes": []}}
        except Exception as e:
            print(f"  DART 수집 실패: {e}")
            return {"date": self.today, "data": {"disclosures": [], "themes": []}}

        # 핵심 공시 필터
        bullish_keywords = ["단일판매", "공급계약", "시설투자", "특허권", "무상증자", "자기주식취득"]
        
        disclosures = []
        sector_hits = {}
        
        # 종목명 -> 섹터 매핑용 사전
        stock_to_sector = {}
        for sector, info in SECTOR_STOCK_MAP.items():
            for name in info["names"]:
                stock_to_sector[name] = sector

        for _, row in df.iterrows():
            corp_name = row['corp_name']
            report_nm = row['report_nm']
            
            # 뉴스 맥락과 일치하는지 확인
            is_news_relevant = any(kw in corp_name or kw in report_nm for kw in keywords)
            # 호재성 공시인지 확인
            is_bullish = any(bw in report_nm for bw in bullish_keywords)
            
            if is_news_relevant or is_bullish:
                sector = stock_to_sector.get(corp_name, "기타/신규")
                disclosures.append({
                    "company": corp_name,
                    "report": report_nm,
                    "sector": sector,
                    "date": row['rcept_dt'],
                    "relevancy": "HIGH" if is_news_relevant else "NORMAL"
                })
                
                if sector != "기타/신규":
                    sector_hits[sector] = sector_hits.get(sector, 0) + 1

        active_themes = []
        for sector, count in sector_hits.items():
            if count >= 1: # 공격적 모드: 1건만 있어도 고려
                active_themes.append({
                    "sector": sector,
                    "count": count,
                    "strength": 8.5 if any(d["relevancy"] == "HIGH" for d in disclosures if d["sector"] == sector) else 6.5,
                    "reason": f"뉴스 맥락 일치 및 {count}건의 주요 공시 감지"
                })

        print(f"  총 {len(disclosures)}개 정밀 수집, {len(active_themes)}개 테마 포착")

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "source": "DART (뉴스 기반 정밀 타격)",
            "data": {
                "disclosures": disclosures,
                "themes": active_themes,
                "count": len(disclosures)
            }
        }

        output_path = self.output_dir / "dart.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result

    def run(self):
        print(f"\n🚀 AGENT-01 COLLECTOR 시작 [{self.today}]")
        
        # 1. 뉴스 및 거시 지표 수집
        sentiment = self.collect_sentiment()
        keywords = self.extract_news_keywords(sentiment)
        
        market = self.collect_market()
        macro = self.collect_macro()
        fred = self.collect_fred()
        ecos = self.collect_ecos()
        consensus = self.collect_consensus()
        
        # 2. 공시 데이터 수집
        dart = self.collect_dart(keywords)
        
        print("✅ AGENT-01 완료\n")
        return {
            "market": market,
            "macro": macro,
            "sentiment": sentiment,
            "fred": fred,
            "ecos": ecos,
            "consensus": consensus,
            "dart": dart,
        }


if __name__ == "__main__":
    agent = CollectorAgent()
    agent.run()
