
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
        # 1. Fetch Transcript (Try Ko, then En)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
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
                # If auto-generated exists
                try:
                    transcript = transcript_list.find_generated_transcript(['ko', 'en'])
                    lang = transcript.language_code
                except:
                    print(f"[Transcript] No suitable transcript found for {video_id}")
                    return None

        # 2. Fetch actual data
        transcript_data = transcript.fetch()
        
        # 3. Format as Text
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript_data)
        
        # 4. Save
        out_path = Path(output_dir) / "transcript.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text_formatted, encoding='utf-8')
        
        # Save metadata
        meta_path = Path(output_dir) / "transcript_meta.json"
        meta = {
            "video_id": video_id,
            "language": lang,
            "is_generated": transcript.is_generated,
            "downloaded_at": str(os.path.getmtime(out_path))
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        
        print(f"[Transcript] Saved for {video_id} ({lang})")
        return str(out_path)

    except Exception as e:
        print(f"[Transcript] Error fetching {video_id}: {e}")
        return None

if __name__ == "__main__":
    # Test with a known video ID if run directly
    import sys
    if len(sys.argv) > 1:
        vid = sys.argv[1]
        fetch_transcript(vid, f"data/raw/youtube/{vid}")
    else:
        print("Usage: python3 transcript_fetcher.py <video_id>")
