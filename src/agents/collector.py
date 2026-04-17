import json
import os
import yfinance as yf
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CollectorAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.output_dir = Path(f"data/raw/{self.today}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_market(self) -> dict:
        """시장 데이터 수집 — yfinance 기반 + 통계 계산"""
        print("📈 시장 데이터 수집 중...")

        data = {}
        multi_stats = {}

        # 수집 대상 지표 (별칭: 티커) — 통계 계산용
        stats_tickers = {
            "KOSPI": "^KS11",
            "VIX": "^VIX",
            "WTI": "CL=F",
            "USD_KRW": "KRW=X",
            "S&P500": "^GSPC",
            "NASDAQ": "^IXIC",
            "DXY": "DX-Y.NYB",
            "US10Y": "^TNX"
        }

        import numpy as np

        for name, ticker in stats_tickers.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1mo")
                if len(hist) >= 6:
                    current_val = float(hist["Close"].iloc[-1])
                    prev_5d_val = float(hist["Close"].iloc[-6])
                    
                    # 데이터 저장 (기존 필드 유지용)
                    data[name.lower()] = round(current_val, 2)
                    
                    # 5일 변화율
                    chg_5d = round(((current_val - prev_5d_val) / prev_5d_val) * 100, 2)
                    
                    # Z-score 계산 (최근 21거래일 기준)
                    returns = hist["Close"].pct_change().dropna()
                    if len(returns) >= 5:
                        mean_ret = returns.mean()
                        std_ret = returns.std()
                        current_ret = (current_val - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]
                        zscore = round((current_ret - mean_ret) / std_ret, 2) if std_ret > 0 else 0
                    else:
                        zscore = 0
                    
                    multi_stats[name] = {
                        "current": round(current_val, 2),
                        "change_5d_pct": chg_5d,
                        "zscore_5d": zscore
                    }
                elif not hist.empty:
                    data[name.lower()] = round(float(hist["Close"].iloc[-1]), 2)
            except Exception as e:
                print(f"  {name} 통계 수집 실패: {e}")

        # 기타 추가 지표 (통계 미계산)
        other_tickers = {
            "nikkei": "^N225",
            "gold": "GC=F",
            "silver": "SI=F",
            "copper": "HG=F",
            "natgas": "NG=F",
            "brent": "BZ=F",
            "usd_jpy": "JPY=X",
            "usd_cny": "CNY=X",
            "us2y": "^IRX",
            "kosdaq": "^KQ11"
        }

        for key, ticker in other_tickers.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1d", auto_adjust=True)
                if not hist.empty:
                    data[key] = round(float(hist["Close"].iloc[-1]), 2)
            except Exception as e:
                print(f"  {key} 수집 실패: {e}")

        # KOSPI 추가 정보
        try:
            k = yf.Ticker("^KS11")
            h = k.history(period="2d")
            if len(h) >= 2:
                data["kospi_1d_change"] = round(((h["Close"].iloc[-1] - h["Close"].iloc[-2]) / h["Close"].iloc[-2]) * 100, 2)
                vol_change = float(h["Volume"].iloc[-1]) - float(h["Volume"].iloc[-2])
                data["kospi_foreign_net"] = round(vol_change / 1e8, 1)
        except: pass

        # WTI 추가 정보 (Collector API 호환용)
        try:
            w = yf.Ticker("CL=F")
            h = w.history(period="2d")
            if len(h) >= 2:
                data["wti_1d_change"] = round(((h["Close"].iloc[-1] - h["Close"].iloc[-2]) / h["Close"].iloc[-2]) * 100, 2)
        except: pass

        data["fear_greed_index"] = self._get_fear_greed()
        data["usd_krw"] = data.get("usd_krw", 1380.0) # 위 stats_tickers에서 수집됨

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": data,
            "multi_period_stats": multi_stats
        }

        output_path = self.output_dir / "market.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ market.json 저장 완료 (통계 포함): {output_path}")
        return result

        print(f"✅ market.json 저장 완료: {output_path}")
        return result

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
        """거시경제 데이터 — 추후 ECOS/FRED 연동"""
        print("🏦 거시경제 데이터 수집 중...")

        data = {
            "korea_base_rate": 2.75,   # TODO: ECOS API
            "us_fed_rate": 4.25,        # TODO: FRED API
            "rate_diff": 1.50,
            "korea_m2": 4565,           # TODO: ECOS API
            "korea_cpi": 2.1,
            "us_cpi": 3.4,
        }

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "source": "임시값 (ECOS/FRED API 연동 전)",
            "data": data
        }

        output_path = self.output_dir / "macro.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ macro.json 저장 완료: {output_path}")
        return result

    def collect_sentiment(self) -> dict:
        """뉴스/감성 데이터 — 경제 RSS 실제 수집"""
        print("📰 뉴스 데이터 수집 중...")

        headlines = []

        try:
            import requests
            from xml.etree import ElementTree as ET

            rss_urls = [
                "https://www.yna.co.kr/rss/economy.xml",  # 연합뉴스 경제
                "https://www.mk.co.kr/rss/30000001/",     # 매일경제
            ]

            for url in rss_urls:
                try:
                    resp = requests.get(url, timeout=5,
                        headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code == 200:
                        root = ET.fromstring(resp.content)
                        items = root.findall(".//item")[:5]
                        for item in items:
                            title = item.findtext("title", "")
                            if title:
                                headlines.append({
                                    "title": title.strip(),
                                    "source": url.split("/")[2],
                                    "timestamp": datetime.now().isoformat()
                                })
                except Exception as e:
                    print(f"  RSS 수집 실패 ({url}): {e}")

        except Exception as e:
            print(f"  뉴스 수집 실패: {e}")

        # 권위자 키워드 탐지
        authority_keywords = [
            "버핏", "이재용", "머스크", "파월", "이창용",
            "트럼프", "바이든", "한국은행", "연준", "Fed"
        ]
        authority_signals = []
        for h in headlines:
            for kw in authority_keywords:
                if kw in h["title"]:
                    authority_signals.append({
                        "person": kw,
                        "action": h["title"],
                        "source": h["source"],
                        "timestamp": h["timestamp"]
                    })
                    break

        print(f"  뉴스 {len(headlines)}개, 권위자 신호 {len(authority_signals)}개")

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
        경제지표 컨센서스 수집
        FRED API 기반으로 최근 발표된 주요 지표의
        실제치 vs 이전치 비교로 서프라이즈 계산
        """
        print("📅 컨센서스 데이터 수집 중 (FRED 기반)...")
        import os
        from fredapi import Fred
        from datetime import datetime, timedelta

        fred = Fred(api_key=os.getenv("FRED_API_KEY"))
        today = datetime.now()
        result_events = []

        # 주요 경제지표 목록 (series_id, 이름, 단위)
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
                # 최근 3개월 데이터
                end = today
                start = today - timedelta(days=90)
                series = fred.get_series(series_id, start, end)
                series = series.dropna()

                if len(series) < 2:
                    continue

                current_val  = float(series.iloc[-1])
                previous_val = float(series.iloc[-2])
                current_date = series.index[-1].strftime("%Y-%m-%d")

                # 전기 대비 변화
                change = round(current_val - previous_val, 4)
                change_pct = round(
                    (current_val - previous_val) / abs(previous_val) * 100, 2
                ) if previous_val != 0 else 0

                # 서프라이즈 판단
                # 12개월 평균 변화율을 컨센서스 대리값으로 사용
                if len(series) >= 12:
                    recent_changes = [
                        float(series.iloc[i] - series.iloc[i-1])
                        for i in range(-12, -1)
                        if abs(i) < len(series)
                    ]
                    avg_change = sum(recent_changes) / len(recent_changes) if recent_changes else 0
                    surprise = round(change - avg_change, 4)
                    surprise_pct = round(
                        (change - avg_change) / abs(avg_change) * 100, 2
                    ) if avg_change != 0 else 0
                else:
                    surprise = 0
                    surprise_pct = 0

                event = {
                    "series_id":     series_id,
                    "event":         name,
                    "unit":          unit,
                    "date":          current_date,
                    "actual":        current_val,
                    "previous":      previous_val,
                    "change":        change,
                    "change_pct":    change_pct,
                    "surprise":      surprise,
                    "surprise_pct":  surprise_pct,
                    "has_actual":    True,
                    "surprise_direction": "BEAT" if surprise > 0 else "MISS"
                }
                result_events.append(event)

                if abs(surprise_pct) > 20:
                    print(f"  🚨 서프라이즈 {name}: {previous_val}→{current_val} ({surprise_pct:+.1f}%)")
                else:
                    print(f"  ✅ {name}: {current_val} (변화: {change:+.4f})")

            except Exception as e:
                print(f"  ❌ {series_id} 수집 실패: {e}")

        # 서프라이즈 큰 것 정렬
        major_surprises = sorted(
            [e for e in result_events if abs(e.get("surprise_pct", 0)) > 10],
            key=lambda x: abs(x.get("surprise_pct", 0)),
            reverse=True
        )[:5]

        output = {
            "date":               self.today,
            "collected_at":       datetime.now().isoformat(),
            "source":             "FRED API",
            "total_events":       len(result_events),
            "events_with_actual": len(result_events),
            "major_surprises":    major_surprises,
            "all_events":         result_events
        }

        output_path = self.output_dir / "consensus.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ consensus.json 저장 완료 ({len(result_events)}개 지표, 주요 서프라이즈 {len(major_surprises)}개)")
        return output

    def run(self):
        print(f"\n🚀 AGENT-01 COLLECTOR 시작 [{self.today}]")
        market = self.collect_market()
        macro = self.collect_macro()
        sentiment = self.collect_sentiment()
        consensus = self.collect_consensus()
        print("✅ AGENT-01 완료\n")
        return {
            "market": market,
            "macro": macro,
            "sentiment": sentiment,
            "consensus": consensus
        }


if __name__ == "__main__":
    agent = CollectorAgent()
    agent.run()
