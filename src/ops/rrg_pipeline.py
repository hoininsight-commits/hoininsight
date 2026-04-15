import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analytics.rrg_engine import RRGEngine
from src.analytics.dynamic_scanner import DynamicScanner

class RRGPipeline:
    def __init__(self):
        self.engine = RRGEngine()
        self.scanner = DynamicScanner()
        self.output_dir = Path("docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timeframes = ["1d", "1wk", "1mo"]
        self.modes = ["standard", "dynamic"]

    def run(self):
        print(f"🚀 [RRG Pipeline] Starting Advanced RRG Pipeline at {datetime.now()}")
        
        # 1. Dynamic Scanner 가동 (주도주 및 테마 추출)
        # 시장 상황에 따른 자동 Threshold 조절 로직 포함
        dynamic_themes = self.scanner.scan()
        
        # 2. 모든 조합(Mode x Timeframe)에 대해 데이터 생성
        dataset_summary = []
        
        for mode in self.modes:
            for tf in self.timeframes:
                print(f"  📊 Processing: Mode={mode}, Timeframe={tf}...")
                
                if mode == "standard":
                    # 기존 설정된 섹터 ETF 중심
                    result = self.engine.run(timeframe=tf)
                else:
                    # 스캐닝된 동적 테마 종목 중심
                    # 테마별로 종목들을 펼쳐서 엔진에 전달
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
                
                # 파일 저장 (rrg_mode_tf.json)
                filename = f"rrg_{mode}_{tf}.json"
                save_path = self.output_dir / filename
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                dataset_summary.append(filename)

        # 3. UI 플레이스홀더 업데이트 (기본값: Standard Weekly)
        self.update_ui_placeholder()
        
        print(f"🏁 [RRG Pipeline] Finished. Generated {len(dataset_summary)} datasets: {dataset_summary}")

    def update_ui_placeholder(self):
        """rrg_view.html 내부에 기본 데이터를 직접 주입하여 초기 로딩 가속화"""
        base_data_path = self.output_dir / "rrg_standard_1wk.json"
        ui_path = self.output_dir / "rrg_view.html"
        
        if not base_data_path.exists() or not ui_path.exists():
            return
            
        with open(base_data_path, "r", encoding="utf-8") as f:
            base_data = f.read()
            
        with open(ui_path, "r", encoding="utf-8") as f:
            ui_content = f.read()
            
        # 플레이스홀더 주석을 실제 데이터 할당 코드로 교체
        placeholder = "// [DATA_PLACEHOLDER]"
        replacement = f"window.RRG_DATA = {base_data};"
        
        if placeholder in ui_content:
            new_content = ui_content.replace(placeholder, replacement)
            with open(ui_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("  ✅ UI Placeholder updated with Standard-Weekly data.")

if __name__ == "__main__":
    RRGPipeline().run()
