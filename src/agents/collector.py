import json
import os
import yfinance as yf
from datetime import datetime, timedelta
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

    def _get_wti(self) -> dict:
        """WTI 유가 수집 및 다중기간 변화율 계산 (거래일 기준 버그 수정)"""
        import yfinance as yf
        result = {
            "value": None,
            "1d_change": None,
            "5d_change": None,
            "20d_change": None,
            "history": None
        }
        try:
            wti = yf.Ticker("CL=F")
            hist = wti.history(period="1mo")  # 거래일 기준 충분한 데이터 확보
            if len(hist) >= 2:
                latest = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                result["value"] = round(latest, 2)
                result["1d_change"] = round((latest - prev) / prev * 100, 2)
                
                # 5일 변화율 — 거래일 기준 (iloc[-6] = 5거래일 전)
                if len(hist) >= 6:
                    prev_5d = float(hist["Close"].iloc[-6])
                    result["5d_change"] = round((latest - prev_5d) / prev_5d * 100, 2)
                
                # 20일 변화율
                if len(hist) >= 21:
                    prev_20d = float(hist["Close"].iloc[-21])
                    result["20d_change"] = round((latest - prev_20d) / prev_20d * 100, 2)
                
                # 히스토리 규격 맞춤 (기존 90일 대신 1개월치만 우선 제공)
                result["history"] = {
                    "current": result["value"],
                    "avg_90d": round(float(hist["Close"].mean()), 2),
                    "max_90d": round(float(hist["Close"].max()), 2),
                    "min_90d": round(float(hist["Close"].min()), 2),
                    "trend": list(hist["Close"].tail(30).round(2))
                }
                print(f"  WTI: {result['value']} (5d chg: {result['5d_change']}%)")
            elif len(hist) == 1:
                result["value"] = round(float(hist["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"WTI 수집 실패: {e}")
        return result

    def __init__(self):
        from src.core.gemini_client import GeminiClient
        self.today = datetime.now().strftime("%Y%m%d")
        self.output_dir = Path(f"data/raw/{self.today}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # base_dir 설정 (history 저장용)
        self.base_dir = Path(".")
        self.model_name = "gemini-flash-latest"
        from src.core.gemini_client import GeminiClient
        self.gemini = GeminiClient()
    
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
                t = yf.Ticker(ticker)
                # 최대 90일 데이터 수집 (WTI는 1개월치만 써서 정확도 높임)
                p = "1mo" if key == "wti_oil" else "90d"
                hist = t.history(period=p)
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
                ticker = yf.Ticker(ticker_symbol)
                # 90일치 히스토리 수집 (흐름 파악용)
                hist = ticker.history(period="90d")
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

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": data,
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
            # Bloomberg 공식 RSS 차단 → WSJ 대체 (무료, 안정적)
            {"name": "WSJ Markets", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},
            {"name": "WSJ Economy", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
            # Reuters 공식 RSS 2026년 3월 차단 → Financial Times 대체
            {"name": "FT Markets", "url": "https://www.ft.com/markets?format=rss"},
            # CNBC 유지
            {"name": "CNBC Economy", "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html"},
            {"name": "CNBC Finance", "url": "https://www.cnbc.com/id/10001147/device/rss/rss.html"},
            # 국내 유지
            {"name": "Yonhap English", "url": "https://en.yna.co.kr/RSS/news.xml"},
            {"name": "연합뉴스", "url": "https://www.yna.co.kr/rss/economy.xml"},
            {"name": "매일경제", "url": "https://www.mk.co.kr/rss/30100041/"},
            # 추가 — 한국경제 (국내 경제 보강)
            {"name": "한국경제", "url": "https://www.hankyung.com/feed/economy"},
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
                
                # 에러 메시지 처리
                if "RESULT" in json_resp and json_resp["RESULT"].get("CODE") != "INFO-000":
                    print(f"  ⚠️ ECOS {stat_code} API 에러: {json_resp['RESULT'].get('MESSAGE')}")
                    return None, None
                    
                rows = json_resp.get("StatisticSearch", {}).get("row", [])
                if rows:
                    # 가장 최근 데이터 리턴
                    latest_val = float(rows[-1]["DATA_VALUE"].replace(",", ""))
                    latest_date = rows[-1].get("TIME", "알수없음")
                    return latest_val, latest_date
            except Exception as e:
                print(f"  ❌ ECOS {stat_code} 실패: {e}")
            return None, None

        today = datetime.now()
        ym = today.strftime("%Y%m")
        # 발표 지연을 고려하여 검색 범위 내역을 180일(약 6개월)로 확대
        ym_start = (today - timedelta(days=180)).strftime("%Y%m")

        # 지표별 수집 및 로그 출력 강화
        indicators = {
            "kr_base_rate":    ("722Y001", "M", "0101000"),
            "kr_cpi":          ("901Y009", "M", "0"),
            "kr_m2":           ("161Y005", "M", "BBHS00"),
            "kr_unemployment": ("901Y027", "M", "I61BC"),
            "kr_export":       ("901Y118", "M", "T002"),
            "kr_import":       ("901Y118", "M", "T004"),
        }


        data = {}
        for key, (code, cycle, item) in indicators.items():
            val, date = fetch_ecos(code, cycle, ym_start, ym, item)
            data[key] = val
            if val is not None:
                print(f"  ✅ {key}: {val} (최신 데이터 날짜: {date})")
            else:
                print(f"  [MISSING] {key}: 최근 6개월 내 데이터 없음 (또는 API 오류)")

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
            is_bullish = any(bk in report_nm for bk in bullish_keywords)
            
            if is_news_relevant or is_bullish:
                disclosures.append({
                    "company": corp_name,
                    "title": report_nm,
                    "type": "NEWS_RELEVANT" if is_news_relevant else "BULLISH",
                    "link": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row['rcept_no']}",
                    "date": row['rcept_dt']
                })
                
                # 섹터 가중치 계산
                sector = stock_to_sector.get(corp_name)
                if sector:
                    sector_hits[sector] = sector_hits.get(sector, 0) + (2 if is_bullish else 1)

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": {
                "disclosures": disclosures,
                "themes": sorted(sector_hits.items(), key=lambda x: x[1], reverse=True)
            }
        }

        output_path = self.output_dir / "dart.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ dart.json 저장 완료 (공시 {len(disclosures)}건 캡처)")
        return result

    def run_all(self):
        """전체 수집 프로세스 실행 (v7.0 통합)"""
        print(f"\n🚀 HOIN COLLECTOR v7.0 통합 엔진 가동 [{self.today}]")
        
        market = self.collect_market()
        macro = self.collect_macro()
        sentiment = self.collect_sentiment()
        fred = self.collect_fred()
        ecos = self.collect_ecos()
        consensus = self.collect_consensus()
        
        # 뉴스 기반 정밀 타격 공시 수집
        keywords = self.extract_news_keywords(sentiment)
        dart = self.collect_dart(keywords)
        
        # COT 스마트머니 수집
        from src.agents.cot_collector import COTCollector
        cot = COTCollector(output_dir=self.output_dir)
        cot.collect()

        
        print(f"\n✨ 모든 데이터 수집 완료! (data/raw/{self.today})")


if __name__ == "__main__":
    CollectorAgent().run_all()
