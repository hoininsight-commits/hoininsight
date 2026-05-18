import json
import os
import re
from pathlib import Path

RAW_BASE = Path("data/raw/youtube")
TRANSCRIPT_BASE = Path("data/transcripts/youtube")

def migrate():
    count = 0
    # 모든 metadata.json 탐색
    for meta_path in RAW_BASE.glob("**/**/**/**/metadata.json"):
        try:
            # meta_path: data/raw/youtube/YYYY/MM/DD/vid_id/metadata.json
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            vid_id = meta["video_id"]
            title = meta["title"]
            # published_at: 2026-04-30T10:00:00Z
            published_at = meta["published_at"]
            
            y, m, d = published_at[:4], published_at[5:7], published_at[8:10]
            
            # 새 파일명 규칙 (회차는 정보를 알 수 없으므로 기본 1회차로 설정)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
            new_name = f"{y}{m}{d}_1회차_{safe_title}.txt"
            
            target_dir = TRANSCRIPT_BASE / y / m / d
            legacy_path = target_dir / f"{vid_id}.txt"
            new_path = target_dir / new_name
            
            if legacy_path.exists() and not new_path.exists():
                print(f"✅ Migrating: {legacy_path.name} -> {new_name}")
                legacy_path.rename(new_path)
                count += 1
        except Exception as e:
            print(f"❌ Error processing {meta_path}: {e}")
            
    print(f"\n✨ Migration complete. Total renamed: {count}")

if __name__ == "__main__":
    migrate()
