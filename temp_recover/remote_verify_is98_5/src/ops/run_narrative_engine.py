import sys
from pathlib import Path
import json
from datetime import datetime

# Adjust path to find src
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ops.narrative.candidate_detector import CandidateDetector
from src.ops.narrative.topic_selector import TopicSelector
from src.ops.narrative.script_generator import ScriptGenerator

def main():
    base_dir = Path(".")
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = base_dir / "data/output" / today.replace("-","/")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[Narrative Engine] Starting for date: {today}")
    
    # 1. Detection
    print("[Step 1] Detecting Candidates...")
    detector = CandidateDetector(base_dir)
    candidates_result = detector.detect_all(today)
    
    # Save Candidates
    cand_path = output_dir / "candidates.json"
    cand_path.write_text(json.dumps(candidates_result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f" -> Saved candidates to {cand_path}")
    
    # 2. Selection
    print("[Step 2] Selecting Topics...")
    selector = TopicSelector()
    narrative_topics = selector.select_topics(candidates_result)
    
    # 3. Script Generation
    print("[Step 3] Generating Scripts...")
    gen = ScriptGenerator()
    final_output = gen.generate_scripts(narrative_topics)
    
    # Save Narrative Topics
    topic_path = output_dir / "narrative_topics.json"
    topic_path.write_text(json.dumps(final_output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f" -> Saved narrative topics to {topic_path}")
    
    print("[Narrative Engine] Completed Successfully.")

if __name__ == "__main__":
    main()
