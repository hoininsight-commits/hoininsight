
"""
Phase 35: Self-Evolution Engine (Logic Gap Detector)
This module analyzes narrative content to detect MISSING data axes or anomaly logic
in the Master Documentation, enabling the system to propose its own evolution.
"""

import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any

# Dynamic Knowledge Base Import
try:
    from src.utils.knowledge_base import KnowledgeBase
except ImportError:
    # Fallback for direct script execution
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.utils.knowledge_base import KnowledgeBase

class GapDetector:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.kb = KnowledgeBase(base_dir / "docs")
        self.kb.load()
        
    def analyze_transcript(self, transcript_text: str) -> List[Dict[str, Any]]:
        """
        Analyze text to find high-frequency nouns that are NOT in the Knowledge Base.
        Returns a list of 'Gap Candidates'.
        """
        # 1. Load Current Knowledge
        known_concepts = set()
        for d in self.kb.get_data_definitions():
            # Add name, category to known set
            known_concepts.add(d['name'].split('(')[0].strip())
            known_concepts.add(d['category'])
            
        # 2. Extract Nouns (Simple Heuristic for Prototype)
        # In production, use NLP libraries (konlpy, etc) if available.
        # Here we use regex to find 2+ character Korean words.
        words = re.findall(r'[가-힣]{2,}', transcript_text)
        
        # Filter common stopwords (expand this list over time)
        stopwords = {
            "영상", "오늘", "지금", "때문에", "해서", "있습니다", "합니다", "그냥", "진짜", "너무",
            "다시", "보고", "생각", "사람", "우리", "이제", "사실", "경우", "정도", "부분",
            "계속", "일단", "저희", "여러분", "내용", "말씀", "가장", "제가", "그거", "많이",
            "정말", "바로", "관련", "대해", "통해", "대한", "위해", "까지", "부터", "면서"
        }
        
        counts = Counter([w for w in words if w not in stopwords])
        
        candidates = []
        for word, count in counts.most_common(20):
            # Threshold: Must appear at least 3 times to be a candidate
            if count < 3: continue
            
            # Check if likely already known (substring match)
            is_known = False
            for k in known_concepts:
                if word in k or k in word:
                    is_known = True
                    break
            
            if not is_known:
                candidates.append({
                    "term": word,
                    "frequency": count,
                    "type": "DATA_MISSING_CANDIDATE"
                })
        
        return candidates

def main():
    """Testing Entry Point"""
    base_dir = Path(__file__).parent.parent.parent
    detector = GapDetector(base_dir)
    
    print("[Phase 35] Starting Gap Detection...")
    
    # Test with a sample transcript if available
    t_dir = base_dir / "data/narratives/transcripts"
    transcripts = list(t_dir.rglob("*.txt"))
    
    if transcripts:
        target = transcripts[0]
        print(f"Analyzing: {target.name}")
        gaps = detector.analyze_transcript(target.read_text(encoding='utf-8'))
        
        print(f"\nFound {len(gaps)} potential gaps:")
        for gap in gaps:
            print(f"- [NEW?] {gap['term']} (Freq: {gap['frequency']})")
            
        # Here we would normally save these as 'Evolution Proposals'
    else:
        print("No transcripts found.")

if __name__ == "__main__":
    main()
