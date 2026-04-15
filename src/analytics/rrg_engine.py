import json
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class RRGEngine:
    def __init__(self, config_path: str = "data/rrg/config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.benchmark_sym = self.config["benchmark"]["symbol"]
        self.assets = self.config["assets"]
        self.params = self.config["params"]

    def fetch_historical_data(self, symbols: list, timeframe: str = "1wk", period: str = "2y"):
        """벤치마크 및 자산 시계열 데이터 수집"""
        all_symbols = [self.benchmark_sym] + symbols
        print(f"[RRG] Fetching data for {len(all_symbols)} symbols ({timeframe})...")
        
        data = yf.download(all_symbols, period=period, interval=timeframe, progress=False)
        return data["Close"]

    def calculate_rrg(self, df_prices: pd.DataFrame, asset_list: list, timeframe: str = "1wk"):
        """RRG 지표 계산 및 평활화(Smoothing) 적용"""
        benchmark_price = df_prices[self.benchmark_sym]
        rrg_results = {}
        
        # 주기별 평활화 윈도우 설정
        smoothing_window = {
            "1d": 5,   # Daily: 5일 MA
            "1wk": 4,  # Weekly: 4주 MA
            "1mo": 3   # Monthly: 3개월 MA (사용자 지시사항 반영)
        }.get(timeframe, 1)

        for asset in asset_list:
            sym = asset["symbol"]
            name = asset.get("name", sym)
            
            if sym not in df_prices.columns: continue
            
            # 1. RS-Ratio 계산
            rs = df_prices[sym] / benchmark_price
            rs_sma = rs.rolling(window=self.params["window_ratio"]).mean()
            rs_ratio = (rs / rs_sma) * 100
            
            # 2. RS-Momentum 계산
            rs_ratio_sma = rs_ratio.rolling(window=self.params["window_momentum"]).mean()
            rs_momentum = (rs_ratio / rs_ratio_sma) * 100
            
            # 3. 좌표 평활화(Smoothing) 적용 - 지시사항 반영
            # RS-Ratio와 RS-Momentum 각각에 대해 이동평균 적용
            rs_ratio_smoothed = rs_ratio.rolling(window=smoothing_window).mean()
            rs_momentum_smoothed = rs_momentum.rolling(window=smoothing_window).mean()
            
            # 결과 저장
            tail_len = self.params["tail_length"]
            valid_data = pd.DataFrame({
                "rs_ratio": rs_ratio_smoothed,
                "rs_momentum": rs_momentum_smoothed
            }).dropna()
            
            if len(valid_data) >= tail_len:
                last_points = valid_data.tail(tail_len).to_dict("records")
                dates = valid_data.index[-tail_len:].strftime("%Y-%m-%d").tolist()
                for i in range(len(last_points)):
                    last_points[i]["date"] = dates[i]
                
                rrg_results[sym] = {
                    "name": name,
                    "points": last_points
                }
        
        return rrg_results

    def run(self, timeframe: str = "1wk", dynamic_assets: list = None):
        """전체 프로세스 실행 (Standard 또는 Dynamic 모드 지원)"""
        asset_list = dynamic_assets if dynamic_assets else self.assets
        symbols = [a["symbol"] for a in asset_list]
        
        # 데이터 수집 (기간은 주기에 따라 자동 조정 가능)
        period = "2y" if timeframe == "1mo" else "1y"
        df_prices = self.fetch_historical_data(symbols, timeframe=timeframe, period=period)
        
        results = self.calculate_rrg(df_prices, asset_list, timeframe=timeframe)
        
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "benchmark": self.config["benchmark"],
            "timeframe": timeframe,
            "data": results,
            "mode": "dynamic" if dynamic_assets else "standard"
        }
        return output

if __name__ == "__main__":
    engine = RRGEngine()
    # Weekly Standard 검증
    res = engine.run(timeframe="1wk")
    print(f"✅ RRG 연산 완료 (Timeframe: {res['timeframe']}, Mode: {res['mode']})")

if __name__ == "__main__":
    # 간단한 가동 테스트
    engine = RRGEngine()
    res = engine.run()
    save_path = Path("data/rrg/output.json")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"[OK] RRG 연산 완료. 저정 경로: {save_path}")
