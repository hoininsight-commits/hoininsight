import sys
import os
from pathlib import Path
from src.learning.deep_logic_analyzer import DeepLogicAnalyzer
from src.utils.knowledge_base import KnowledgeBase
# from termcolor import colored
def colored(text, color): return text

def main():
    # Target video ID (M&A Script)
    vid = "jZmDgdKmrb4"
    print(colored(f"[Manual Trigger] Starting analysis for {vid}...", "cyan"))
    
    # Initialize
    kb = KnowledgeBase(Path("."))
    analyzer = DeepLogicAnalyzer(kb)
    
    # Check text
    t_path = Path(f"data/narratives/transcripts/2026/01/21/{vid}.txt")
    if not t_path.exists():
        print(colored(f"[Error] Transcript not found at {t_path}", "red"))
        return

    # Check meta using "raw" path as mocked
    m_path = Path(f"data/narratives/raw/youtube/2026/01/21/{vid}.json")
    if not m_path.exists():
         print(colored(f"[Error] Metadata not found at {m_path}", "red"))
         return

    # Run Analysis (Mocking the 'item' dict structure expected by _generate_llm_analysis)
    # Actually DeepLogicAnalyzer usually takes a `candidate` item. 
    # But looking at source, `analyze_video` isn't a public method in previous contexts.
    # Let's check `process_candidates` or how `DeepLogicAnalyzer` is called.
    
    # Re-reading DeepLogicAnalyzer source suggests usage:
    # analyzer.analyze_deeply(candidate_item) or similar.
    # I'll optimistically assume I can construct a 'candidate' dict and fetch the transcript internally.
    
    candidate = {
        "video_id": vid,
        "title": "지금, 투자자들이 꼭 알아야 할 2026년 국내 정책 3가지",
        "published_at": "2026-01-20T00:00:00Z",
        "url": f"https://www.youtube.com/watch?v={vid}",
        # We need the transcript path logic to match or pass content?
        # Usually it loads from file based on Date/ID.
        # Let's rely on the method finding the file I just saved.
        "transcript_path": str(t_path) 
    }
    
    # We need to see strict method signature, but let's try calling inner method if needed.
    # Actually, `DeepLogicAnalyzer` likely has a method like `analyze_narrative(item)`.
    
    # Let's inspect the class during run or just trust the `_generate_llm_analysis` logic
    # which we saw takes `(transcript_text, metadata)`.
    
    transcript_text = t_path.read_text(encoding="utf-8")
    
    print(colored("[Info] Generating LLM Analysis...", "yellow"))
    try:
        # Accessing private method for direct trigger
        result = analyzer._generate_llm_analysis(transcript_text, candidate)
        
        if result:
            print(colored("[Success] Analysis Generated!", "green"))
            print(f"Result length: {len(result)}")
            
            # Create directory
            out_dir = Path("data/narratives/deep_analysis/2026/01/21")
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Save Report
            report_path = out_dir / f"video_{vid}_report.md"
            report_path.write_text(result, encoding="utf-8")
            print(colored(f"[Info] Report Saved to {report_path}", "green"))
            
            # Need to create a dummy entry for results json if we want dashboard integration,
            # but for now let's just save the MD.
        else:
            print(colored("[Error] No result returned.", "red"))

    except Exception as e:
        print(colored(f"[Exception] {e}", "red"))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
