import json
import os
from pathlib import Path
from src.engine.content_engine import ContentEngine
from src.utils.target_date import get_target_ymd

engine = ContentEngine()
date = get_target_ymd().replace("-", "/")
base_path = Path(f"data/scripts/{date}")

topics = [
    {"topic": "미-한 조선동맹 출범 및 수주 랠리", "stocks": [{"name": "HD현대중공업"}, {"name": "삼성중공업"}, {"name": "한화오션"}]},
    {"topic": "K-UAM 현대차-KAI 미래 모빌리티 동맹", "stocks": [{"name": "한국항공우주"}, {"name": "현대차"}, {"name": "베셀"}]},
    {"topic": "AI 보안 긴급출동! K-사이버보안 테마 발발", "stocks": [{"name": "안랩"}, {"name": "케이사인"}, {"name": "드림시큐리티"}]}
]

results = []
for i, t in enumerate(topics):
    print(f"Generating Insta cards for: {t['topic']}")
    # 강화된 프롬프트로 재생성
    slides = engine.generate_insta_cards(t)
    if slides:
        target_dir = base_path / f"Topic_{i+1}"
        target_dir.mkdir(parents=True, exist_ok=True)
        # 이미지 폴더도 함께 복사
        os.system(f"cp -r {base_path}/Round_3/assets {target_dir}/")
        
        (target_dir / "insta_cards.json").write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # content_log용 데이터 수집
        img_map = {"미-한 조선": "ship_cover.png", "K-UAM": "uam_cover.png", "보안": "cyber_cover.png"}
        custom_img = "cover.png"
        for k, v in img_map.items():
            if k in t['topic']:
                custom_img = v
                break
                
        results.append({
            "id": f"20260510_{i+1}",
            "date": "2026-05-10",
            "title": t['topic'],
            "custom_img": custom_img,
            "path": f"data/scripts/{date}/Topic_{i+1}"
        })
        print(f"Saved to {target_dir}/insta_cards.json")

# 최종 로그 업데이트
log_path = Path("data/history/content_log.json")
log_data = {"contents": results}
log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
