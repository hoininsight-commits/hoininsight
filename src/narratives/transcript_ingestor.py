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

from src.utils.guards import check_learning_enabled

RAW_BASE = Path("data/narratives/raw/youtube")
TRANSCRIPT_BASE = Path("data/narratives/transcripts")
STATUS_BASE = Path("data/narratives/status")

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
        # meta_path: data/narratives/raw/youtube/YYYY/MM/DD/vid_id/metadata.json
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
        
        try:
            # First attempt: youtube-transcript-api
            transcript_list = YouTubeTranscriptApi().list(vid_id)
            
            try:
                transcript = transcript_list.find_manually_created_transcript(['ko'])
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en', 'en-US'])
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
                
                cmd = [
                    "python3", "-m", "yt_dlp",
                    "--skip-download",
                    "--write-auto-subs",
                    "--sub-lang", "ko,en.*",
                    "--convert-subs", "vtt",
                    "--output", f"{out_dir}/{vid_id}",
                    f"https://www.youtube.com/watch?v={vid_id}"
                ]
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
    check_learning_enabled()
    targets = _get_target_videos()
    logger.info(f"Found {len(targets)} videos to check.")
    
    for meta_path in targets:
        ingest_transcript(meta_path)

if __name__ == "__main__":
    run_ingestor()
