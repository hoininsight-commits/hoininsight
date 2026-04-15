import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analytics.rrg_engine import RRGEngine
from src.analytics.dynamic_theme_scanner import DynamicThemeScanner
from src.analytics.radar_analyzer import RadarAnalyzer

class RRGPipeline:
    def __init__(self):
        self.engine = RRGEngine()
        # 고도화된 스캐너 및 분석기 적용
        self.scanner = DynamicThemeScanner()
        self.radar_analyzer = RadarAnalyzer(self.engine)
        
        self.output_dir = Path("docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timeframes = ["1d", "1wk", "1mo"]
        self.modes = ["standard", "dynamic", "radar"] # radar 모드 추가

    def run(self):
        print(f"🚀 [RRG Pipeline] Starting Advanced RRG Pipeline at {datetime.now()}")
        
        # 1. Dynamic Scanner 가동 (지능형 테마 추출)
        # Anomaly Detection 및 AI Naming 로직 포함
        dynamic_themes = self.scanner.scan_with_radar()
        
        # 2. 모든 조합(Mode x Timeframe)에 대해 데이터 생성
        dataset_summary = []
        
        for mode in self.modes:
            for tf in self.timeframes:
                try:
                    print(f"  📊 Processing: Mode={mode}, Timeframe={tf}...")
                    
                    if mode == "standard":
                        result = self.engine.run(timeframe=tf)
                    
                    elif mode == "dynamic":
                        dynamic_assets = []
                        for theme, stocks in dynamic_themes.items():
                            for s in stocks:
                                dynamic_assets.append({
                                    "symbol": s["symbol"],
                                    "name": f"{s['name']} ({theme})"
                                })
                        
                        if not dynamic_assets:
                            print(f"    ⚠️ No dynamic assets found for {tf}. Skipping.")
                            continue
                        result = self.engine.run(timeframe=tf, dynamic_assets=dynamic_assets)
                    
                    elif mode == "radar":
                        if not dynamic_themes:
                            print(f"    ⚠️ No dynamic themes found for {tf}. Skipping.")
                            continue
                        result = self.radar_analyzer.analyze_themes(dynamic_themes, timeframe=tf)
                    
                    # 파일 저장 (rrg_mode_tf.json)
                    if result:
                        filename = f"rrg_{mode}_{tf}.json"
                        save_path = self.output_dir / filename
                        with open(save_path, "w", encoding="utf-8") as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        
                        dataset_summary.append(filename)
                except Exception as e:
                    print(f"  ❌ Error processing Mode={mode}, Timeframe={tf}: {e}")
                    continue

        # 3. UI 업데이트 (Weekly 기준으로 최적화)
        print(f"🏁 [RRG Pipeline] Finished. Generated {len(dataset_summary)} datasets: {dataset_summary}")

if __name__ == "__main__":
    # 실행 시 Weekly를 기본으로 하며 모든 타임프레임 생성
    RRGPipeline().run()
