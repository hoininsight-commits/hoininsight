import json
import numpy as np
from datetime import datetime
from pathlib import Path
from src.analytics.rrg_engine import RRGEngine

class RadarAnalyzer:
    """
    RRG 데이터를 테마 단위로 클러스터링하고 선점형 시그널(가속도 등)을 추출하는 분석기
    """
    def __init__(self, rrg_engine: RRGEngine):
        self.engine = rrg_engine

    def analyze_themes(self, themes_group, timeframe="1wk"):
        """
        1. 개별 종목 RRG 연산 수행
        2. 테마별로 그룹화 및 평균값 산출
        3. 가속도(Angle Change) 계산
        """
        # 모든 종목 리스트 평탄화
        all_symbols = []
        for stocks in themes_group.values():
            all_symbols.extend(stocks)
            
        print(f"📊 [Radar Analyzer] Computing RRG for {len(all_symbols)} stocks...")
        
        # 개별 종목 RRG 연산 (기존 엔진 활용)
        individual_res = self.engine.run(timeframe=timeframe, dynamic_assets=all_symbols)
        ind_data = individual_res["data"]
        
        # 테마별 집계
        theme_results = {}
        for theme_name, stocks in themes_group.items():
            theme_points = []
            
            # 각 종목의 포인트들 수집 (날짜별로 정렬되어 있다고 가정)
            stock_points_list = []
            for s in stocks:
                sym = s['symbol']
                if sym in ind_data:
                    stock_points_list.append(ind_data[sym]["points"])
            
            if not stock_points_list: continue
            
            # 날짜별 평균 계산 (최소 tail_length만큼의 데이터가 있는 시점만)
            tail_len = len(stock_points_list[0])
            for i in range(tail_len):
                sum_ratio = 0
                sum_mom = 0
                count = 0
                date = stock_points_list[0][i]["date"]
                
                for sp in stock_points_list:
                    if i < len(sp):
                        sum_ratio += sp[i]["rs_ratio"]
                        sum_mom += sp[i]["rs_momentum"]
                        count += 1
                
                if count > 0:
                    theme_points.append({
                        "date": date,
                        "rs_ratio": sum_ratio / count,
                        "rs_momentum": sum_mom / count
                    })
            
            # 가속도(Acceleration) 및 방향성(Direction) 계산
            if len(theme_points) >= 3:
                theme_results[theme_name] = {
                    "name": theme_name,
                    "points": theme_points,
                    "metrics": self.calculate_metrics(theme_points),
                    "stock_count": len(stocks)
                }
                
        return {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "benchmark": self.engine.config["benchmark"],
            "timeframe": timeframe,
            "data": theme_results,
            "mode": "radar"
        }

    def calculate_metrics(self, points):
        """추세 가속도 및 벡터 방향성 산출"""
        p3 = points[-1] # 현재
        p2 = points[-2] # 직전
        p1 = points[-3] # 그 전
        
        # 벡터 계산
        v2 = np.array([p3["rs_ratio"] - p2["rs_ratio"], p3["rs_momentum"] - p2["rs_momentum"]])
        v1 = np.array([p2["rs_ratio"] - p1["rs_ratio"], p2["rs_momentum"] - p1["rs_momentum"]])
        
        # 1. 가속도 (벡터 길이의 변화량)
        accel = np.linalg.norm(v2) - np.linalg.norm(v1)
        
        # 2. 방향 각도 (1시 방향 근접도)
        # 45도(북동향)일 때 1시 방향이라고 가정
        angle = np.arctan2(v2[1], v2[0]) * 180 / np.pi
        
        # 3. 선점 신호 (Improving 영역 + 1시 방향 상승 가속)
        is_improving = p3["rs_ratio"] < 100 and p3["rs_momentum"] > 100
        is_heading_ne = 20 <= angle <= 70 # 1시 방향 근처
        is_anticipation = is_improving and is_heading_ne and accel > 0
        
        return {
            "acceleration": float(accel),
            "angle": float(angle),
            "is_anticipation": bool(is_anticipation)
        }

if __name__ == "__main__":
    from src.analytics.dynamic_theme_scanner import DynamicThemeScanner
    scanner = DynamicThemeScanner()
    themes = scanner.scan_with_radar()
    
    engine = RRGEngine()
    analyzer = RadarAnalyzer(engine)
    radar_data = analyzer.analyze_themes(themes)
    
    print(f"📡 [Radar] Cluster execution done. Themes: {list(radar_data['data'].keys())}")
