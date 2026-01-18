
from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys

def get_transcript(video_id):
    try:
        # Try fetching Korean first, then English
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except:
            transcript = transcript_list.find_transcript(['en'])
            
        fetched = transcript.fetch()
        full_text = " ".join([t['text'] for t in fetched])
        
        # Save to file
        output_path = f"data/narratives/transcripts/2026/01/18/feat_comparison_{video_id}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"Success: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_transcript("Iek--w00kr4")
