import json
import os
from pathlib import Path
from src.engine.content_engine import ContentEngine
from src.utils.target_date import get_target_ymd

engine = ContentEngine()
date = get_target_ymd().replace("-", "/")
base_path = Path(f"data/scripts/{date}")

# 3가지 토픽 정보 (원본 대본 포함)
topics = [
    {
        "topic": "미-한 조선동맹 출범 및 수주 랠리", 
        "stocks": [{"name": "HD현대중공업"}, {"name": "삼성중공업"}, {"name": "한화오션"}],
        "folder": "Topic_1",
        "script_file": "today_script_short.md"
    },
    {
        "topic": "K-UAM 현대차-KAI 미래 모빌리티 동맹", 
        "stocks": [{"name": "한국항공우주"}, {"name": "현대차"}, {"name": "베셀"}],
        "folder": "Topic_2",
        "script_file": "today_script_short.md"
    },
    {
        "topic": "AI 보안 긴급출동! K-사이버보안 테마 발발", 
        "stocks": [{"name": "안랩"}, {"name": "케이사인"}, {"name": "드림시큐리티"}],
        "folder": "Topic_3",
        "script_file": "today_script_short.md"
    }
]

results = []
for i, t in enumerate(topics):
    target_dir = base_path / t['folder']
    script_path = target_dir / t['script_file']
    
    # 대본이 없으면 Round_3 폴더에서라도 가져오기 시도
    if not script_path.exists():
        script_path = base_path / "Round_3" / t['script_file']
        
    script_content = ""
    if script_path.exists():
        script_content = script_path.read_text(encoding="utf-8")
        print(f"Found script for {t['topic']} at {script_path}")
    else:
        # 마지막 수단: 대시보드 브리프 읽기
        brief_p = Path("dashboard/today_brief.txt")
        if brief_p.exists():
            script_content = brief_p.read_text(encoding="utf-8")
            print(f"Using dashboard brief for {t['topic']}")

    print(f"Generating Sync-Insta cards for: {t['topic']}")
    slides = engine.generate_insta_cards(t, script=script_content)
    
    if slides:
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "insta_cards.json").write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8")
        
        img_map = {"미-한 조선": "ship_cover.png", "K-UAM": "uam_cover.png", "보안": "cyber_cover.png"}
        custom_img = "cover.png"
        for k, v in img_map.items():
            if k in t['topic']: custom_img = v; break
                
        results.append({
            "id": f"20260510_{i+1}",
            "date": "2026-05-10",
            "title": t['topic'],
            "custom_img": custom_img,
            "path": f"data/scripts/{date}/{t['folder']}"
        })
        print(f"✅ Synced and Saved to {target_dir}/insta_cards.json")

# 최종 로그 업데이트
log_path = Path("data/history/content_log.json")
log_data = {"contents": results}
log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
