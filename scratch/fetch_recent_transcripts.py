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
        # Fixed: entry['text'] -> entry['text'] was actually correct for some versions, 
        # but let's check transcript_ingestor.py again. 
        # Actually in transcript_ingestor.py it's entry.text? 
        # Wait, I'll use both as a fallback.
        try:
            return " ".join([entry['text'] for entry in data])
        except:
            return " ".join([entry.text for entry in data])
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
    return None

def save_video(vid_id, title, date_str):
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

def main():
    # May 12th
    may12_videos = [
        {"id": "u1dLZEZ_xfE", "title": "현시점 외국인들이 '2026 주도주'로 찍었다는 ‘핵심 종목' TOP3"},
        {"id": "yM42z2iAjyA", "title": "지금 알아둬야 할 '코스피+나스닥'이 추가 상승 전 보냈던 '신호 3가지'"}
    ]
    
    # May 11th
    may11_videos = [
        {"id": "G11iu17c2OQ", "title": "'꼭 보세요' 미중 정상회담 이후 한국 '반도체·원전주'가 중요해지는 이유"},
        {"id": "8jTt6PuIk4U", "title": "삼성전자·SK하이닉스 폭등 이후, 다음 상승장 시작될 수 있다는 '미래 산업' 정체"},
        {"id": "FUMMZhDe3c4", "title": "925% 오른 광통신주 지금이라도 사야 될까?"},
        {"id": "zUENeEKuDPk", "title": "월가에서, 이번 주 '주식시장'이 역대급 시장이 될거라는 이유"},
        {"id": "OxvFKsbTzds", "title": "경제사냥꾼 구독자 전용, 종목 분석 현대차"},
        {"id": "p4s2kchMHmA", "title": "오늘 로봇주 상장 하나에 시장이 완전 뒤집힌 이유"}
    ]
    
    print("Collecting May 12th videos...")
    for v in may12_videos:
        save_video(v['id'], v['title'], "20260512")
        
    print("\nCollecting May 11th videos...")
    for v in may11_videos:
        save_video(v['id'], v['title'], "20260511")

if __name__ == "__main__":
    main()
