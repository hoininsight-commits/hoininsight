
import os
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def fetch_transcript(video_id, output_dir):
    """
    Fetches transcript for a given video_id and saves it to output_dir.
    Tries Korean ('ko') first, then English ('en').
    Returns path to transcript file if successful, else None.
    """
    try:
        # First attempt: youtube-transcript-api
        transcript_list = YouTubeTranscriptApi().list(video_id)
        
        transcript = None
        lang = 'unknown'
        
        try:
            transcript = transcript_list.find_transcript(['ko'])
            lang = 'ko'
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
                lang = 'en'
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                    lang = transcript.language_code
                except:
                    pass

        if transcript:
            transcript_data = transcript.fetch()
            formatter = TextFormatter()
            text_formatted = formatter.format_transcript(transcript_data)
        else:
            raise Exception("No suitable transcript found via API")

    except Exception as api_err:
        print(f"[Transcript] API failed for {video_id}, trying yt-dlp: {api_err}")
        try:
            import subprocess
            import re
            
            cmd = [
                "python3", "-m", "yt_dlp",
                "--skip-download",
                "--write-auto-subs",
                "--sub-lang", "ko,en.*",
                "--convert-subs", "vtt",
                "--output", f"{output_dir}/{video_id}",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            vtt_files = list(Path(output_dir).glob(f"{video_id}.*.vtt"))
            if vtt_files:
                vtt_file = vtt_files[0]
                vtt_content = vtt_file.read_text(encoding="utf-8")
                lang = vtt_file.suffixes[0].replace('.', '')
                
                text = re.sub(r'^WEBVTT.*?\n', '', vtt_content, flags=re.DOTALL)
                text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', text)
                text = re.sub(r'<.*?>', '', text)
                text_formatted = re.sub(r'\n+', ' ', text).strip()
                vtt_file.unlink()
            else:
                return None
        except Exception as ytdlp_err:
            print(f"[Transcript] Both methods failed: {ytdlp_err}")
            return None

    # Save
    if text_formatted:
        out_path = Path(output_dir) / "transcript.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text_formatted, encoding='utf-8')
        
        meta_path = Path(output_dir) / "transcript_meta.json"
        meta = {
            "video_id": video_id,
            "language": lang,
            "downloaded_at": str(os.path.getmtime(out_path))
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        
        print(f"[Transcript] Saved for {video_id} ({lang})")
        return str(out_path)
    
    return None

if __name__ == "__main__":
    # Test with a known video ID if run directly
    import sys
    if len(sys.argv) > 1:
        vid = sys.argv[1]
        fetch_transcript(vid, f"data/raw/youtube/{vid}")
    else:
        print("Usage: python3 transcript_fetcher.py <video_id>")
