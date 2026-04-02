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
        """공포탐욕지수 — 추후 CNN API 스크래핑 구현"""
        # TODO: CNN Fear & Greed Index 실시간 수집
        return 25.0  # 임시값

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
        """뉴스/감성 데이터 — 추후 RSS 파싱 연동"""
        print("📰 뉴스 데이터 수집 중...")

        data = {
            "news_headlines": [],
            "authority_signals": []
        }

        # TODO: 네이버 뉴스 RSS 파싱

        result = {
            "date": self.today,
            "collected_at": datetime.now().isoformat(),
            "data": data
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
