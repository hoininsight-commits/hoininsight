import json
import logging
from pathlib import Path
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NarrativeStatus")

DATA_BASE = Path("data/narratives")
STATUS_BASE = DATA_BASE / "status"

def get_today_stats():
    now = datetime.now()
    y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    
    raw_dir = DATA_BASE / "raw" / "youtube" / y / m / d
    trans_dir = DATA_BASE / "transcripts" / y / m / d
    
    videos_detected = 0
    if raw_dir.exists():
        # Count video folders
        videos_detected = sum(1 for _ in raw_dir.iterdir() if _.is_dir())
        
    transcript_ok = 0
    transcript_skip = 0
    
    if trans_dir.exists():
        transcript_ok = sum(1 for x in trans_dir.glob("*.txt"))
        transcript_skip = sum(1 for x in trans_dir.glob("*_SKIP.json"))
        
    # Find latest video title if possible
    latest_video = "None"
    if videos_detected > 0:
        try:
            # Sort by date derived from folder structure? or creation time?
            # Folders are date based.
            all_videos = sorted(raw_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True)
            if all_videos:
                latest_dir = all_videos[0]
                meta = json.loads((latest_dir / "metadata.json").read_text(encoding="utf-8"))
                latest_video = meta.get("title", "Unknown")
        except:
            pass

    return {
        "date": f"{y}-{m}-{d}",
        "videos_detected": videos_detected,
        "transcript_ok": transcript_ok,
        "transcript_skip": transcript_skip,
        "latest_video": latest_video,
        "errors": 0 # Placeholder for now, hard to track async logs
    }

def record_status():
    stats = get_today_stats()
    
    now = datetime.now()
    y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    
    out_dir = STATUS_BASE / y / m / d
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "collection_status.json"
    
    out_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Status Recorded: {stats}")

if __name__ == "__main__":
    record_status()
