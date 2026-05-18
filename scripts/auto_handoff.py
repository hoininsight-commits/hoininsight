import os
import json
from datetime import datetime
from pathlib import Path

def update_handoff_history():
    """
    배포 시점의 핵심 변경 사항을 docs/handoff/history.md에 누적 기록합니다.
    """
    history_path = Path("docs/handoff/history.md")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 헤더 생성 (파일이 없으면)
    if not history_path.exists():
        history_path.write_text("# 📜 HOIN Insight Deployment & Handoff History\n\n", encoding="utf-8")
    
    # 2. 오늘 생성된 토픽 정보 가져오기 (있을 경우)
    topic_info = "N/A"
    try:
        today_path = Path("docs/data/today.json")
        if today_path.exists():
            data = json.loads(today_path.read_text(encoding="utf-8"))
            topic_info = f"[{data.get('topic_id', 'Unknown')}] {data.get('title', 'No Title')}"
    except: pass

    # 3. 누적할 내용 구성
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
## 🚀 Deployment @ {now}
- **Detected Topic:** {topic_info}
- **Engine Version:** v11.0 (Social-First Hunter Mode)
- **Key Changes:**
  - Topic Selection Engine 가중치 조정 (Social Bonus +0.4)
  - 중복 토픽 방지 Fatigue Filter 강화 (0.8)
  - 배포 시 핸드오프 자동 기록 시스템 활성화
- **Status:** Successfully deployed to Production

---
"""
    
    # 4. 파일 뒤에 추가
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"✅ Handoff history updated at {history_path}")

if __name__ == "__main__":
    update_handoff_history()
