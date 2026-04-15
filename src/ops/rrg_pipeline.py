import json
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analytics.rrg_engine import RRGEngine

def run_rrg_pipeline():
    print("🚀 [RRG Pipeline] Starting RRG analysis...")
    
    # 1. RRG 연산 수행
    engine = RRGEngine()
    result = engine.run(timeframe="1wk")
    
    # 2. 결과 JSON 저장 (Data 폴더)
    output_path = Path("data/rrg/output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 3. 대시보드 데이터 배포 (복사)
    dashboard_data_path = Path("docs/rrg_data.json")
    with open(dashboard_data_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 4. 로컬 실행을 위한 UI 데이터 주입 (CORS 우회)
    view_path = Path("docs/rrg_view.html")
    if view_path.exists():
        with open(view_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 데이터 주입용 문자열 생성
        data_json = json.dumps(result, ensure_ascii=False)
        injection_code = f"window.RRG_DATA = {data_json};"
        
        # 플레이스홀더 교체
        placeholder = "// [DATA_PLACEHOLDER]"
        if placeholder in content:
            new_content = content.replace(placeholder, injection_code)
            with open(view_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ [RRG Pipeline] UI 데이터 주입 완료: {view_path}")
        else:
            print("⚠️ [RRG Pipeline] 플레이스홀더를 찾지 못했습니다. fetch 모드로 동작합니다.")

    print(f"🏁 [RRG Pipeline] Pipeline finished successfully.")

if __name__ == "__main__":
    run_rrg_pipeline()
