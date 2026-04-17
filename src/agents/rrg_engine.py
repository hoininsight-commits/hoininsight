import json
import os
import sys
import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

# ── 섹터별 구성 종목 매핑 ───────────────────────────────────────────────────
# 각 섹터 클릭 시 drill-down 대상이 되는 Top 15 구성 종목
SECTOR_COMPONENTS = {
    "Technology": {
        "benchmark": "XLK",
        "components": {
            "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA",
            "AVGO": "Broadcom", "ORCL": "Oracle", "CRM": "Salesforce",
            "AMD": "AMD", "ADBE": "Adobe", "CSCO": "Cisco",
            "ACN": "Accenture", "IBM": "IBM", "INTC": "Intel",
            "INTU": "Intuit", "NOW": "ServiceNow", "QCOM": "Qualcomm"
        }
    },
    "Financials": {
        "benchmark": "XLF",
        "components": {
            "JPM": "JP Morgan", "BAC": "Bank of America", "WFC": "Wells Fargo",
            "GS": "Goldman Sachs", "MS": "Morgan Stanley", "BLK": "BlackRock",
            "SCHW": "Schwab", "C": "Citigroup", "AXP": "American Express",
            "SPGI": "S&P Global", "CB": "Chubb", "PGR": "Progressive",
            "MMC": "Marsh McLennan", "ICE": "ICE", "CME": "CME Group"
        }
    },
    "Healthcare": {
        "benchmark": "XLV",
        "components": {
            "LLY": "Eli Lilly", "UNH": "UnitedHealth", "JNJ": "J&J",
            "ABBV": "AbbVie", "MRK": "Merck", "ABT": "Abbott",
            "TMO": "Thermo Fisher", "DHR": "Danaher", "AMGN": "Amgen",
            "PFE": "Pfizer", "MDT": "Medtronic", "ISRG": "Intuitive Surgical",
            "SYK": "Stryker", "GILD": "Gilead", "BMY": "Bristol-Myers"
        }
    },
    "Consumer Disc": {
        "benchmark": "XLY",
        "components": {
            "AMZN": "Amazon", "TSLA": "Tesla", "HD": "Home Depot",
            "MCD": "McDonald's", "NKE": "Nike", "LOW": "Lowe's",
            "SBUX": "Starbucks", "TJX": "TJX", "BKNG": "Booking",
            "CMG": "Chipotle", "GM": "General Motors", "F": "Ford",
            "ROST": "Ross Stores", "ORLY": "O'Reilly", "AZO": "AutoZone"
        }
    },
    "Energy": {
        "benchmark": "XLE",
        "components": {
            "XOM": "ExxonMobil", "CVX": "Chevron", "COP": "ConocoPhillips",
            "EOG": "EOG Resources", "SLB": "Schlumberger", "MPC": "Marathon Petroleum",
            "PXD": "Pioneer Natural", "PSX": "Phillips 66", "VLO": "Valero",
            "OXY": "Occidental", "HAL": "Halliburton", "DVN": "Devon Energy",
            "HES": "Hess", "BKR": "Baker Hughes", "FANG": "Diamondback"
        }
    },
    "Industrials": {
        "benchmark": "XLI",
        "components": {
            "GE": "GE Aerospace", "RTX": "Raytheon", "HON": "Honeywell",
            "UNP": "Union Pacific", "CAT": "Caterpillar", "DE": "Deere",
            "BA": "Boeing", "LMT": "Lockheed Martin", "UPS": "UPS",
            "FDX": "FedEx", "ETN": "Eaton", "EMR": "Emerson",
            "PH": "Parker Hannifin", "NOC": "Northrop Grumman", "GD": "General Dynamics"
        }
    },
    "Materials": {
        "benchmark": "XLB",
        "components": {
            "LIN": "Linde", "APD": "Air Products", "SHW": "Sherwin-Williams",
            "FCX": "Freeport-McMoRan", "NEM": "Newmont", "NUE": "Nucor",
            "ECL": "Ecolab", "DOW": "Dow", "IP": "International Paper",
            "MLM": "Martin Marietta", "VMC": "Vulcan Materials", "PPG": "PPG Industries",
            "ALB": "Albemarle", "CF": "CF Industries", "MOS": "Mosaic"
        }
    },
    "Real Estate": {
        "benchmark": "XLRE",
        "components": {
            "PLD": "Prologis", "AMT": "American Tower", "EQIX": "Equinix",
            "CCI": "Crown Castle", "PSA": "Public Storage", "O": "Realty Income",
            "WELL": "Welltower", "DLR": "Digital Realty", "AVB": "AvalonBay",
            "EQR": "Equity Residential", "SPG": "Simon Property", "VTR": "Ventas",
            "ARE": "Alexandria RE", "BXP": "BXP", "MAA": "Mid-America Apt"
        }
    },
    "Consumer Staples": {
        "benchmark": "XLP",
        "components": {
            "PG": "Procter & Gamble", "KO": "Coca-Cola", "PEP": "PepsiCo",
            "COST": "Costco", "WMT": "Walmart", "PM": "Philip Morris",
            "MO": "Altria", "MDLZ": "Mondelez", "CL": "Colgate",
            "GIS": "General Mills", "KHC": "Kraft Heinz", "STZ": "Constellation",
            "SYY": "Sysco", "HSY": "Hershey", "KR": "Kroger"
        }
    },
    "Utilities": {
        "benchmark": "XLU",
        "components": {
            "NEE": "NextEra Energy", "SO": "Southern Co", "DUK": "Duke Energy",
            "AEP": "AEP", "SRE": "Sempra", "D": "Dominion Energy",
            "EXC": "Exelon", "PCG": "PG&E", "XEL": "Xcel Energy",
            "ED": "Con Edison", "WEC": "WEC Energy", "ES": "Eversource",
            "ETR": "Entergy", "FE": "FirstEnergy", "AES": "AES Corp"
        }
    },
    "Communication": {
        "benchmark": "XLC",
        "components": {
            "META": "Meta", "GOOGL": "Alphabet A", "GOOG": "Alphabet C",
            "NFLX": "Netflix", "DIS": "Disney", "CMCSA": "Comcast",
            "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobile",
            "EA": "Electronic Arts", "TTWO": "Take-Two", "WBD": "Warner Bros",
            "PARA": "Paramount", "OMC": "Omnicom", "IPG": "IPG"
        }
    }
}

class RRGEngine:
    def __init__(self, benchmark="^GSPC", period="2y", interval="1wk", window=14):
        self.benchmark_ticker = benchmark
        self.period = period
        self.interval = interval
        self.window = window
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 디폴트 자산 풀 (미국 섹터 ETF 및 주요 자산)
        self.assets = {
            "Technology": "XLK",
            "Financials": "XLF",
            "Healthcare": "XLV",
            "Consumer Disc": "XLY",
            "Energy": "XLE",
            "Industrials": "XLI",
            "Materials": "XLB",
            "Real Estate": "XLRE",
            "Consumer Staples": "XLP",
            "Utilities": "XLU",
            "Communication": "XLC",
            "Gold": "GLD",
            "Bitcoin": "BTC-USD"
        }
        
    def fetch_data(self, ticker):
        """특정 종목의 시계열 데이터를 가져옵니다."""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=self.period, interval=self.interval)
            # 불필요한 열 제거, 종가만 유지
            if not hist.empty and 'Close' in hist.columns:
                return hist['Close']
            return None
        except Exception as e:
            print(f"[{ticker}] 데이터 수집 실패: {e}")
            return None

    def calculate_rrg(self):
        print(f"📊 벤치마크({self.benchmark_ticker}) 기준 RRG 데이터 산출 중...")
        
        # 1. 벤치마크 데이터 수집
        bench_close = self.fetch_data(self.benchmark_ticker)
        if bench_close is None or bench_close.empty:
            raise ValueError("Benchmak 데이터를 가져오지 못했습니다.")
            
        results = []
        
        # 2. 각 자산별 RS-Ratio, RS-Momentum 계산
        for asset_name, ticker in self.assets.items():
            print(f"  - {asset_name} ({ticker}) 계산 중...")
            asset_close = self.fetch_data(ticker)
            if asset_close is None or asset_close.empty:
                continue
                
            # 인덱스(날짜) 맞추기
            df = pd.DataFrame({'Asset': asset_close, 'Benchmark': bench_close}).dropna()
            if len(df) < self.window * 2:
                print(f"    데이터 구간이 부족하여 {asset_name} 스킵합니다.")
                continue
                
            # 2-1. RS (Relative Strength) 계산
            df['RS'] = df['Asset'] / df['Benchmark']
            
            # 2-2. JdK RS-Ratio 계산 (Z-score 기반 표준화 확장)
            # RS를 100 중심으로 퍼지게 만듭니다. Z-Score * 5로 범위 85~115 정도로 조정
            rs_mean = df['RS'].rolling(window=self.window).mean()
            rs_std = df['RS'].rolling(window=self.window).std()
            df['RS_Ratio'] = 100 + (((df['RS'] - rs_mean) / rs_std) * 5)
            
            # 2-3. JdK RS-Momentum 계산
            # RS-Ratio 자체의 모멘텀(마찬가지로 이동평균과의 편차 Z-score)
            rs_ratio_mean = df['RS_Ratio'].rolling(window=self.window).mean()
            rs_ratio_std = df['RS_Ratio'].rolling(window=self.window).std()
            df['RS_Momentum'] = 100 + (((df['RS_Ratio'] - rs_ratio_mean) / rs_ratio_std) * 5)
            
            # 결측치 제거 후 최근 과거 궤적(Tail) 추출
            df_clean = df.dropna()
            if df_clean.empty:
                continue
                
            # 최근 10개 포인트(상하좌우 궤적용)
            tail_points = df_clean.tail(15)
            
            history = []
            for date, row in tail_points.iterrows():
                history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "rs_ratio": round(row['RS_Ratio'], 2),
                    "rs_momentum": round(row['RS_Momentum'], 2)
                })
                
            results.append({
                "name": asset_name,
                "ticker": ticker,
                "history": history
            })
            
        return results

    def calculate_drilldown(self):
        """섹터별 구성 종목의 RRG 데이터를 계산합니다 (섹터 ETF 기준)."""
        print("🔍 Drill-down 데이터 산출 중...")
        drilldown = {}

        for sector_name, sector_info in SECTOR_COMPONENTS.items():
            benchmark_ticker = sector_info["benchmark"]
            components = sector_info["components"]
            print(f"  📂 [{sector_name}] 벤치마크: {benchmark_ticker}, 종목 수: {len(components)}")

            # 벤치마크(섹터 ETF) 데이터 수집
            bench_close = self.fetch_data(benchmark_ticker)
            if bench_close is None or bench_close.empty:
                print(f"    ⚠ {benchmark_ticker} 벤치마크 수집 실패, 스킵")
                continue

            sector_assets = []
            for ticker, name in components.items():
                asset_close = self.fetch_data(ticker)
                if asset_close is None or asset_close.empty:
                    continue

                df = pd.DataFrame({'Asset': asset_close, 'Benchmark': bench_close}).dropna()
                if len(df) < self.window * 2:
                    continue

                # RS-Ratio / RS-Momentum 계산
                df['RS'] = df['Asset'] / df['Benchmark']
                rs_mean = df['RS'].rolling(window=self.window).mean()
                rs_std = df['RS'].rolling(window=self.window).std()
                df['RS_Ratio'] = 100 + (((df['RS'] - rs_mean) / rs_std) * 5)

                rs_ratio_mean = df['RS_Ratio'].rolling(window=self.window).mean()
                rs_ratio_std = df['RS_Ratio'].rolling(window=self.window).std()
                df['RS_Momentum'] = 100 + (((df['RS_Ratio'] - rs_ratio_mean) / rs_ratio_std) * 5)

                df_clean = df.dropna()
                if df_clean.empty:
                    continue

                tail_points = df_clean.tail(15)

                # 현재가 & 등락률 추출
                current_price = round(float(df_clean['Asset'].iloc[-1]), 2)
                prev_price = float(df_clean['Asset'].iloc[-2]) if len(df_clean) >= 2 else current_price
                change_pct = round((current_price - prev_price) / prev_price * 100, 2) if prev_price else 0.0

                history = []
                for date, row in tail_points.iterrows():
                    history.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "rs_ratio": round(row['RS_Ratio'], 2),
                        "rs_momentum": round(row['RS_Momentum'], 2)
                    })

                # 최신 RS 값
                latest = tail_points.iloc[-1]
                sector_assets.append({
                    "name": name,
                    "ticker": ticker,
                    "current_price": current_price,
                    "change_pct": change_pct,
                    "rs_ratio": round(latest['RS_Ratio'], 2),
                    "rs_momentum": round(latest['RS_Momentum'], 2),
                    "history": history
                })

            drilldown[sector_name] = {
                "benchmark": benchmark_ticker,
                "assets": sector_assets
            }
            print(f"    ✅ {len(sector_assets)}개 종목 완료")

        return drilldown

    def save_drilldown_json(self, drilldown_data):
        """Drill-down 데이터를 JSON으로 저장합니다."""
        output_dir = Path("docs/data")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "rrg_drilldown_data.json"

        payload = {
            "last_updated": datetime.now().isoformat(),
            "interval": self.interval,
            "sectors": drilldown_data
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"✅ Drill-down 데이터 저장 완료: {output_file}")

    def save_to_json(self, rrg_assets):
        output_dir = Path("docs/data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "rrg_data.json"
        
        payload = {
            "last_updated": datetime.now().isoformat(),
            "reference_index": self.benchmark_ticker,
            "interval": self.interval,
            "assets": rrg_assets
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            
        print(f"✅ RRG 데이터 저장 완료: {output_file}")


if __name__ == "__main__":
    mode = "--drilldown" if "--drilldown" in sys.argv else "--rrg"
    try:
        engine = RRGEngine(benchmark="^GSPC", period="2y", interval="1wk")

        if mode == "--drilldown":
            print("🔍 Drill-down 모드 실행")
            drilldown_data = engine.calculate_drilldown()
            engine.save_drilldown_json(drilldown_data)
            print("🎉 Drill-down 데이터 생성 완료")
        else:
            print("📊 섹터 RRG 모드 실행")
            assets_data = engine.calculate_rrg()
            engine.save_to_json(assets_data)
            print("🎉 RRG 모듈 실행이 성공적으로 완료되었습니다.")

        # 두 모드 모두 실행하려면 --all 플래그 사용
        if "--all" in sys.argv:
            print("\n📊 전체 섹터 RRG 모드 추가 실행")
            assets_data = engine.calculate_rrg()
            engine.save_to_json(assets_data)
            drilldown_data = engine.calculate_drilldown()
            engine.save_drilldown_json(drilldown_data)
            print("🎉 전체 모드 완료")

    except Exception as e:
        print(f"❌ RRG 산출 오류: {e}")
