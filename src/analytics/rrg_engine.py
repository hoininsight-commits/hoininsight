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

    def fetch_historical_data(self, timeframe: str = "1wk", period: str = "2y"):
        """벤치마크 및 자산 시계열 데이터 수집"""
        symbols = [self.benchmark_sym] + [a["symbol"] for a in self.assets]
        print(f"[RRG] Fetching data for {len(symbols)} symbols...")
        
        data = yf.download(symbols, period=period, interval=timeframe, progress=False)
        return data["Close"]

    def calculate_rrg(self, df_prices: pd.DataFrame):
        """RRG 지표(RS-Ratio, RS-Momentum) 계산"""
        benchmark_price = df_prices[self.benchmark_sym]
        rrg_results = {}

        for asset in self.assets:
            sym = asset["symbol"]
            name = asset["name"]
            
            # 1. RS-Ratio 계산 (Price Relative / its 14-period SMA)
            rs = df_prices[sym] / benchmark_price
            rs_sma = rs.rolling(window=self.params["window_ratio"]).mean()
            
            # 표준화: 100을 중심으로 정규화 (Price Relative가 평균 대비 얼마나 높은지)
            rs_ratio = (rs / rs_sma) * 100
            
            # 2. RS-Momentum 계산 (RS-Ratio의 변화율을 다시 표준화)
            # RS-Ratio의 14기간 이동평균 대비 현재 값
            rs_ratio_sma = rs_ratio.rolling(window=self.params["window_momentum"]).mean()
            rs_momentum = (rs_ratio / rs_ratio_sma) * 100
            
            # 결과 저장 (최신 데이터 및 꼬리 데이터 포함)
            tail_len = self.params["tail_length"]
            valid_data = pd.DataFrame({
                "rs_ratio": rs_ratio,
                "rs_momentum": rs_momentum
            }).dropna()
            
            if len(valid_data) >= tail_len:
                last_points = valid_data.tail(tail_len).to_dict("records")
                # 날짜 정보 추가
                dates = valid_data.index[-tail_len:].strftime("%Y-%m-%d").tolist()
                for i in range(len(last_points)):
                    last_points[i]["date"] = dates[i]
                
                rrg_results[sym] = {
                    "name": name,
                    "points": last_points
                }
        
        return rrg_results

    def run(self, timeframe: str = "1wk"):
        """전체 프로세스 실행 및 결과 반환"""
        df_prices = self.fetch_historical_data(timeframe=timeframe)
        results = self.calculate_rrg(df_prices)
        
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "benchmark": self.config["benchmark"],
            "timeframe": timeframe,
            "data": results
        }
        return output

if __name__ == "__main__":
    # 간단한 가동 테스트
    engine = RRGEngine()
    res = engine.run()
    save_path = Path("data/rrg/output.json")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"[OK] RRG 연산 완료. 저정 경로: {save_path}")
