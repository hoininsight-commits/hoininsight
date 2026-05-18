import os
import json
import re
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import subprocess

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
        try:
            transcript = transcript_list.find_manually_created_transcript(['ko'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['ko'])
            except:
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    transcript = next(iter(transcript_list))
        
        data = transcript.fetch()
        try:
            return " ".join([entry['text'] for entry in data])
        except:
            return " ".join([entry.text for entry in data])
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
    return None

def save_video(vid_id, title, date_str):
    if not date_str.startswith("202605"):
        return
    
    y, m, d = date_str[:4], date_str[4:6], date_str[6:8]
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
    file_name = f"{date_str}_1회차_{safe_title}.txt"
    out_dir = Path("youtube_data/transcripts") / y / m / d
    out_path = out_dir / file_name
    
    if out_path.exists():
        print(f"Already exists: {file_name}")
        return
        
    content = fetch_transcript(vid_id)
    if content:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"✅ Saved: {file_name}")
        
        # Metadata
        raw_dir = Path("youtube_data/raw") / y / m / d / vid_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "video_id": vid_id,
            "title": title,
            "published_at": f"{y}-{m}-{d}T00:00:00Z",
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "collected_at": datetime.now().isoformat()
        }
        (raw_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(f"❌ Failed to get transcript for {vid_id}")

def get_may_list(url):
    print(f"Fetching list from {url}...")
    cmd = ["python3", "-m", "yt_dlp", "--print", "%(id)s|%(title)s|%(upload_date)s", "--playlist-end", "60", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    
    may_videos = []
    for line in lines:
        if "|" in line:
            parts = line.split("|")
            if len(parts) == 3:
                vid_id, title, date = parts
                if date.startswith("202605"):
                    may_videos.append({"id": vid_id, "title": title, "date": date})
    return may_videos

def main():
    videos = get_may_list("https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/videos")
    shorts = get_may_list("https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/shorts")
    
    all_may = videos + shorts
    print(f"\nTotal May entries to process: {len(all_may)}")
    
    for v in all_may:
        save_video(v['id'], v['title'], v['date'])

if __name__ == "__main__":
    main()
