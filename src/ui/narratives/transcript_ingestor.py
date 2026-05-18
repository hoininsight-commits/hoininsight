import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TranscriptIngestor")

import time
import random
from src.utils.guards import check_learning_enabled

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

RAW_BASE = Path("youtube_data/raw")
TRANSCRIPT_BASE = Path("youtube_data/transcripts")
STATUS_BASE = Path("youtube_data/status")

def _get_target_videos():
    """traverse RAW_BASE to find metadata files."""
    targets = []
    if not RAW_BASE.exists():
        return targets
        
    for meta_path in RAW_BASE.glob("**/**/**/**/metadata.json"):
        targets.append(meta_path)
    return targets

def ingest_transcript(meta_path: Path):
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        vid_id = meta["video_id"]
        
        # Determine paths
        # meta_path: data/raw/youtube/YYYY/MM/DD/vid_id/metadata.json
        # relative: YYYY/MM/DD/vid_id/metadata.json
        rel = meta_path.relative_to(RAW_BASE)
        # parts: (YYYY, MM, DD, vid_id, metadata.json)
        parts = rel.parts
        if len(parts) < 4:
            return # Should not happen based on glob
            
        y, m, d = parts[0], parts[1], parts[2]
        
        out_dir = TRANSCRIPT_BASE / y / m / d
        out_txt = out_dir / f"{vid_id}.txt"
        out_skip = out_dir / f"{vid_id}_SKIP.json"
        
        if out_txt.exists() or out_skip.exists():
            return # Already processed
            
        logger.info(f"Processing: {vid_id} - {meta.get('title', 'No Title')}")
        
        full_text = ""
        
        try:
            # First attempt: youtube-transcript-api (Classic mode for v1.2.3)
            # v1.2.3 uses instance methods for list()
            transcript_list = YouTubeTranscriptApi().list(vid_id)
            
            # Find ko or en transcript
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
            full_text = " ".join([entry.text for entry in data])
            
        except Exception as api_err:
            logger.warning(f"youtube-transcript-api failed for {vid_id}, trying yt-dlp fallback: {api_err}")
            # Fallback: yt-dlp
            try:
                import subprocess
                # Extract subtitles as text using yt-dlp
                # --skip-download: don't download video
                # --write-auto-subs: get auto-generated if manual missing
                # --sub-lang: try ko then en
                # --get-subs-only: self explanatory
                
                # Setup Cookies if available
                cookies_path = Path("youtube_cookies.txt")
                
                # Ensure output directory exists
                out_dir.mkdir(parents=True, exist_ok=True)
                
                cmd = [
                    "python3", "-m", "yt_dlp",
                    "--skip-download",
                    "--write-auto-subs",
                    "--write-subs",
                    "--sub-lang", "ko,en.*",
                    "--convert-subs", "vtt",
                    "--output", f"{out_dir}/{vid_id}",
                    f"https://www.youtube.com/watch?v={vid_id}"
                ]
                
                if cookies_path.exists() and cookies_path.stat().st_size > 0:
                    logger.info("Using youtube_cookies.txt for yt-dlp")
                    cmd.insert(3, "--cookies")
                    cmd.insert(4, str(cookies_path))
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # yt-dlp saves as vid_id.ko.vtt or vid_id.en.vtt etc.
                vtt_files = list(out_dir.glob(f"{vid_id}.*.vtt"))
                if vtt_files:
                    vtt_file = vtt_files[0]
                    vtt_content = vtt_file.read_text(encoding="utf-8")
                    
                    # Very simple VTT to text conversion (removing timestamps and tags)
                    import re
                    # Remove WEBVTT header
                    text = re.sub(r'^WEBVTT.*?\n', '', vtt_content, flags=re.DOTALL)
                    # Remove timestamps
                    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', text)
                    # Remove HTML-like tags
                    text = re.sub(r'<.*?>', '', text)
                    # Clean up multiple spaces/newlines
                    full_text = re.sub(r'\n+', ' ', text).strip()
                    
                    # Cleanup VTT file
                    vtt_file.unlink()
                else:
                    raise Exception("No VTT files found after yt-dlp run")
                    
            except Exception as ytdlp_err:
                logger.error(f"Both methods failed for {vid_id}. yt-dlp error: {ytdlp_err}")
                # Do not create SKIP file for generic errors to allow retry
                return

        # Save success
        if full_text:
            out_dir.mkdir(parents=True, exist_ok=True)
            out_txt.write_text(full_text, encoding="utf-8")
            logger.info(f"[SUCCESS] Saved transcript for {vid_id}")
        else:
            # If we reached here without text, it's effectively a NoTranscriptFound
            logger.warning(f"No transcript content extracted for {vid_id}")
            out_dir.mkdir(parents=True, exist_ok=True)
            skip_info = {
                "video_id": vid_id,
                "reason": "No transcript content found",
                "timestamp": datetime.now().isoformat()
            }
            out_skip.write_text(json.dumps(skip_info, ensure_ascii=False, indent=2), encoding="utf-8")
            
    except Exception as e:
        logger.error(f"Failed to process {meta_path}: {e}")

def run_ingestor():
    if os.environ.get("SKIP_GUARD", "false").lower() != "true":
        check_learning_enabled()
    targets = _get_target_videos()
    logger.info(f"Found {len(targets)} videos to check.")
    
    for meta_path in targets:
        ingest_transcript(meta_path)
        # Random sleep to avoid 429
        wait_time = random.uniform(2, 5)
        logger.info(f"Waiting {wait_time:.2f}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    run_ingestor()
