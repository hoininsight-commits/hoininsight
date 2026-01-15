import os
import json
import logging
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TranscriptIngestor")

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
            # Fetch List
            # API seems to require instantiation in this version
            api = YouTubeTranscriptApi()
            transcript_list = api.list(vid_id)
            
            # Try to fetch manually created korean, then auto-generated korean, then english...
            # The API's 'find_transcript' is useful
            try:
                # 1. Manually created KO
                transcript = transcript_list.find_manually_created_transcript(['ko'])
            except:
                try:
                    # 2. Generated KO
                    transcript = transcript_list.find_generated_transcript(['ko'])
                except:
                    try:
                        # 3. Any EN
                        transcript = transcript_list.find_transcript(['en', 'en-US'])
                    except:
                        # 4. Fallback: Translation to Korean? Or just first available?
                        # Let's take first available and fail if none
                        transcript = next(iter(transcript_list))
            
            # Fetch actual text
            # Transcript object has .fetch() method returning objects in v1.2.3
            data = transcript.fetch()
            # data is a FetchedTranscript object which is iterable yielding FetchedTranscriptSnippet
            # verify if data is list or object. 'data' comes from .fetch() which in _api.py returns FetchedTranscript.
            # FetchedTranscript likely implements __iter__.
            # Snippet has .text attribute.
            full_text = " ".join([entry.text for entry in data])
            
            # Save
            out_dir.mkdir(parents=True, exist_ok=True)
            out_txt.write_text(full_text, encoding="utf-8")
            logger.info(f"[SUCCESS] Saved transcript for {vid_id}")
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # No captions available
            logger.warning(f"No transcript for {vid_id}: {e}")
            out_dir.mkdir(parents=True, exist_ok=True)
            skip_info = {
                "video_id": vid_id,
                "reason": "No transcript available",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            out_skip.write_text(json.dumps(skip_info, ensure_ascii=False, indent=2), encoding="utf-8")
            
        except Exception as e:
            logger.error(f"Error fetching transcript for {vid_id}: {e}")
            # Do not create SKIP file for generic errors (network etc) to allow retry
            # Unless it's persistent? For now, we allow retry next run.
            
    except Exception as e:
        logger.error(f"Failed to process {meta_path}: {e}")

def run_ingestor():
    targets = _get_target_videos()
    logger.info(f"Found {len(targets)} videos to check.")
    
    for meta_path in targets:
        ingest_transcript(meta_path)

if __name__ == "__main__":
    run_ingestor()
