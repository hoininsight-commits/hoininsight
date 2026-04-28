
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agents.learner_agent import LearnerAgent
from src.core.gemini_client import GeminiClient

def learn_specific_video(video_id, transcript_path):
    print(f"🚀 Targeted Learning for Video: {video_id}")
    agent = LearnerAgent()
    
    # Load transcript
    p = Path(transcript_path)
    if not p.exists():
        print(f"❌ Transcript not found at {transcript_path}")
        return

    content = p.read_text(encoding="utf-8")
    hunter_data = {
        "video_id": video_id,
        "date": "2026-04-27",
        "content": content
    }
    
    # 1. Find matching report (20260427)
    hoin_report = agent._find_matching_hoin_report("2026-04-27")
    if not hoin_report:
        print("⚠️ No matching HOIN report for 2026-04-27. Using baseline for comparison.")
        hoin_report = {"event": "Doosan Enerbility Analysis", "why_now": "SMR and Nuclear Export"}
    
    # 2. Perform Gap Analysis
    print("🧠 Performing Gap Analysis with Gemini...")
    result = agent._perform_gap_analysis(hunter_data, hoin_report)
    
    if result:
        # 3. Save to evolution log
        agent._save_evolution_log(video_id, result)
        print("✅ Evolution Log Updated Successfully!")
        print(f"DNA Patch: {result.get('dna_patch')}")
    else:
        print("❌ Analysis failed.")

if __name__ == "__main__":
    # Video ID: 20260427_2회차_경제사냥꾼_구독자_전용,_종목_분석__두산에너빌리티 (This is the filename stem)
    vid_id = "20260427_2회차_경제사냥꾼_구독자_전용,_종목_분석__두산에너빌리티"
    path = "data/transcripts/youtube/2026/04/27/20260427_2회차_경제사냥꾼_구독자_전용,_종목_분석__두산에너빌리티.txt"
    learn_specific_video(vid_id, path)
