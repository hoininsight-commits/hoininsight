import json
import os
import yfinance as yf
from datetime import datetime
from pathlib import Path


class CollectorAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.output_dir = Path(f"data/raw/{self.today}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_market(self) -> dict:
        """시장 데이터 수집 — yfinance 기반"""
        print("📈 시장 데이터 수집 중...")

        data = {}

        # KOSPI
        try:
            kospi = yf.Ticker("^KS11")
            hist = kospi.history(period="2d")
            if len(hist) >= 2:
                data["kospi"] = round(float(hist["Close"].iloc[-1]), 2)
                data["kospi_1d_change"] = round(
                    (hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                    / hist["Close"].iloc[-2] * 100, 2
                )
            elif len(hist) == 1:
                data["kospi"] = round(float(hist["Close"].iloc[-1]), 2)
                data["kospi_1d_change"] = None
        except Exception as e:
            print(f"KOSPI 수집 실패: {e}")
            data["kospi"] = None
            data["kospi_1d_change"] = None

        # 외국인 수급 근사치 (거래량 변화 기반)
        try:
            kospi_data = yf.Ticker("^KS11")
            hist2 = kospi_data.history(period="2d")
            if len(hist2) >= 2:
                vol_change = float(hist2["Volume"].iloc[-1]) - float(hist2["Volume"].iloc[-2])
                data["kospi_foreign_net"] = round(vol_change / 1e8, 1)
            else:
                data["kospi_foreign_net"] = None
        except Exception as e:
            print(f"  수급 데이터 수집 실패: {e}")
            data["kospi_foreign_net"] = None

        # VIX
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="1d")
            if len(hist) > 0:
                data["vix"] = round(float(hist["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"VIX 수집 실패: {e}")
            data["vix"] = None

        # WTI
        try:
            wti = yf.Ticker("CL=F")
            hist = wti.history(period="1d")
            if len(hist) > 0:
                data["wti_oil"] = round(float(hist["Close"].iloc[-1]), 2)
        except Exception as e:
            print(f"WTI 수집 실패: {e}")
            data["wti_oil"] = None

        # 환율
        data["usd_krw"] = self._get_usd_krw()

        # 추가 수집 항목 (글로벌 지수, 원자재, 외환, 채권)
        tickers = {
            "sp500": "^GSPC",
            "nasdaq": "^IXIC",
            "nikkei": "^N225",
            "gold": "GC=F",
            "silver": "SI=F",
            "copper": "HG=F",
            "natgas": "NG=F",
            "brent": "BZ=F",
            "dxy": "DX-Y.NYB",
            "usd_jpy": "JPY=X",
            "usd_cny": "CNY=X",
            "us10y": "^TNX",
            "us2y": "^IRX",
            "kosdaq": "^KQ11"
        }

        print(f"📊 {len(tickers)}개 추가 지표 수집 시작...")
        for key, ticker in tickers.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1d", auto_adjust=True)
                if not hist.empty:
                    data[key] = round(float(hist["Close"].iloc[-1]), 2)
                else:
                    data[key] = None
            except Exception as e:
                print(f"  {key} ({ticker}) 수집 실패: {e}")
                data[key] = None

        # Fear & Greed (추후 실제 API 연동)
        data["fear_greed_index"] = self._get_fear_greed()

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": data
        }

        output_path = self.output_dir / "market.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

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

    def run(self):
        print(f"\n🚀 AGENT-01 COLLECTOR 시작 [{self.today}]")
        market = self.collect_market()
        macro = self.collect_macro()
        sentiment = self.collect_sentiment()
        print("✅ AGENT-01 완료\n")
        return {"market": market, "macro": macro, "sentiment": sentiment}


if __name__ == "__main__":
    agent = CollectorAgent()
    agent.run()
