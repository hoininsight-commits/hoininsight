import sys
from pathlib import Path
import json

# PYTHONPATH 설정
sys.path.append(str(Path.cwd()))

from src.engine.content_engine import ContentEngine

def recover_images():
    engine = ContentEngine()
    
    # Topic_8 데이터 로드
    topic_dir = Path("data/scripts/2026/05/10/Topic_8")
    signal_p = topic_dir / "signal.json"
    
    if not signal_p.exists():
        print(f"❌ {signal_p}를 찾을 수 없습니다.")
        return

    candidate = json.loads(signal_p.read_text())
    
    print(f"🚀 [RECOVERY] Topic_8 ({candidate.get('topic')}) 이미지 생성 시작...")
    success = engine.generate_visual_assets(candidate, topic_dir)
    
    if success:
        print("✅ [RECOVERY] 이미지 생성 완료! 대시보드를 새로고침해 보세요.")
    else:
        print("❌ [RECOVERY] 이미지 생성 실패.")

if __name__ == "__main__":
    recover_images()
