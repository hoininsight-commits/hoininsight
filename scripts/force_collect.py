import json
import os
import re
from pathlib import Path
from datetime import datetime
from src.ui.narratives.transcript_ingestor import ingest_transcript
from src.utils.telegram_notifier import TelegramNotifier
from src.utils.target_date import get_now_kst

def force_collect(vid_id, title):
    print(f"🚀 Forcing collection for: {vid_id}")
    
    # 1. Fake metadata for ingestion
    y, m, d = "2026", "04", "30"
    save_dir = Path("data/raw/youtube") / y / m / d / vid_id
    save_dir.mkdir(parents=True, exist_ok=True)
    
    meta_path = save_dir / "metadata.json"
    payload = {
        "video_id": vid_id,
        "source_id": "youtube_economic_hunter_forced",
        "title": title,
        "published_at": f"{y}-{m}-{d}T15:00:00Z",
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "channel_name": "경제사냥꾼",
        "collected_at": get_now_kst().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 2. Ingest Transcript
    ingest_transcript(meta_path)
    
    # 3. Rename and Send
    transcript_dir = Path("data/transcripts/youtube") / y / m / d
    legacy_txt_path = transcript_dir / f"{vid_id}.txt"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
    new_name = f"{y}{m}{d}_1회차_{safe_title}.txt"
    new_path = transcript_dir / new_name
    
    if legacy_txt_path.exists():
        legacy_txt_path.rename(new_path)
        content = new_path.read_text(encoding="utf-8")
        
        # 4. Telegram Send
        msg = f"📺 *[유튜브 최신 영상 강제 수집]*\n\n"
        msg += f"📌 *제목*: {title}\n"
        msg += f"⏰ *회차*: 수동 수집\n"
        msg += f"🔗 [영상 링크]({payload['url']})\n\n"
        msg += f"📜 *스크립트 전문*:\n{content}"
        
        notifier = TelegramNotifier(target="TRANSCRIPT")
        notifier.send_message_in_chunks(msg)
        print("✅ Success! Sent to Telegram.")
    else:
        print("❌ Failed to get transcript.")

if __name__ == "__main__":
    force_collect("M3ARK7KWypE", "총합 4,430% 급상승장 만든 '젠슨황'이 다음으로 콕찝은 '신사업' 정체는?!")
