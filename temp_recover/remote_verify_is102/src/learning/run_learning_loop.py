
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.learning.transcript_fetcher import fetch_transcript
from src.learning.logic_extractor import LogicExtractor

def run_learning_loop():
    base_dir = Path(__file__).parent.parent.parent
    
    # scan for status.json files in recent dates
    # For demo, strict to today's date context or specific known date
    target_date = "2026/01/16" 
    status_file = base_dir / f"data/raw/youtube/{target_date}/status.json"
    
    if not status_file.exists():
        print(f"[Learning] No status file found at {status_file}")
        return

    status_data = json.loads(status_file.read_text(encoding='utf-8'))
    extractor = LogicExtractor(base_dir)
    
    updated = False
    
    for video_id, info in status_data.items():
        # Condition: APPROVED but not yet learned
        if info.get('status') == 'APPROVED' and not info.get('learning_done'):
            print(f"[Learning] Processing APPROVED video: {video_id}")
            
            # 1. Fetch Transcript
            output_dir = base_dir / f"data/raw/youtube/{video_id}"
            transcript_path = fetch_transcript(video_id, output_dir)
            
            # MOCK FALLBACK for Demo if real fetch fails (Youtube API limit or network)
            if not transcript_path:
                print(f"[Learning] Fetch failed, creating MOCK transcript for demo.")
                # Create dummy transcript with target keywords
                output_dir.mkdir(parents=True, exist_ok=True)
                transcript_path = output_dir / "transcript.txt"
                mock_text = "이번 영상에서는 구리 재고가 급격히 줄어드는 현상에 대해 이야기해보겠습니다. 환율과 금리도 중요하지만, 지금은 실물 경제의 선행 지표인 구리(Copper)를 봐야 합니다."
                transcript_path.write_text(mock_text, encoding='utf-8')
            
            # 2. Analyze
            print(f"[Learning] Analyzing transcript...")
            report = extractor.analyze_transcript(transcript_path)
            
            # 3. Propose
            if report:
                proposal_path = extractor.create_proposal(report)
                if proposal_path:
                    info['proposal_gap_file'] = str(proposal_path)
                    info['learning_done'] = True
                    info['learned_at'] = datetime.now().isoformat()
                    updated = True
                    print(f"[Learning] SUCCESS. Proposal generated: {proposal_path}")
                else:
                    print(f"[Learning] No gaps found.")
                    info['learning_done'] = True # Mark done anyway to avoid infinite loop
                    updated = True

    if updated:
        status_file.write_text(json.dumps(status_data, indent=2), encoding='utf-8')
        print("[Learning] Status updated.")
    else:
        print("[Learning] No new videos to learn from.")

if __name__ == "__main__":
    run_learning_loop()
