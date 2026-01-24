"""
Phase 35: Logic Evolver (Pattern-based Logic Discovery)
Analyzes narrative content to discover CAUSAL LINKS and ANOMALY LOGIC patterns.
Goes beyond simple keyword gap detection to find structural logic.
Output: Generates Logic Proposal JSONs for Dashboard Approval.
"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
try:
    from src.utils.knowledge_base import KnowledgeBase
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.utils.knowledge_base import KnowledgeBase

class LogicEvolver:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.kb = KnowledgeBase(base_dir / "docs")
        self.kb.load()
        self.proposal_dir = base_dir / "data" / "evolution" / "proposals"
        self.proposal_dir.mkdir(parents=True, exist_ok=True)
        
    def discover_logic_patterns(self, transcript_text: str, source_id: str) -> List[Dict[str, str]]:
        """
        Extract logical assertions from text using structural pattern matching.
        """
        sentences = re.split(r'[.!?]\n+', transcript_text)
        if len(sentences) < 2:
             sentences = re.split(r'[.!?]\s+', transcript_text)
        
        discovered_patterns = []
        
        # Enhanced Regex Patterns for Logic Extraction (Korean)
        patterns = [
            # If-Then Strong: "만약 A라면 B입니다"
            (r'(?:만약|If)\s+(.+?)(?:면|다면|라면),\s+(.+?)(?:입니다|합니다|것입니다)', "LOGIC_IF_THEN"),
            
            # Meaning/Signal: "A는 B의 신호입니다"
            (r'(.+?)(?:은|는)\s+(.+?)(?:의 신호|의 징조|의 전조|를 의미|라고 볼 수)입니다', "LOGIC_SIGNAL"),
            
            # Tendency: "A하면 B하는 경향이 있습니다"
            (r'(.+?)(?:면|하면)\s+(.+?)(?:하는 경향|하는 패턴|하는 습성)이 있습니다', "LOGIC_TENDENCY"),
            
            # Priority/Add: "따라서 A를 추가해야 합니다" (Actionable)
            (r'따라서\s+(.+?)(?:를|을)\s+(?:추가해야|봐야|확인해야)\s+(?:합니다|됩니다)', "ACTION_ADD_DATA")
        ]
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 10: continue
            
            for pattern, p_type in patterns:
                match = re.search(pattern, sent)
                if match:
                    # For ACTION_ADD_DATA, only 1 group
                    if p_type == "ACTION_ADD_DATA":
                        cond = "USER_NEED"
                        impl = match.group(1).strip()
                    else:
                        cond = match.group(1).strip()
                        impl = match.group(2).strip()
                    
                    if len(cond) < 2 or len(impl) < 2: continue
                    
                    # Deduplicate in current run
                    if not any(d['original_sentence'] == sent for d in discovered_patterns):
                        discovered_patterns.append({
                            "type": p_type,
                            "condition": cond,
                            "implication": impl,
                            "original_sentence": sent,
                            "source_id": source_id,
                            "confidence": "HIGH" # Pattern-based match is usually explicit
                        })
                        
        return discovered_patterns

    def generate_proposals(self, patterns: List[Dict[str, str]]):
        """Save discovered patterns as JSON proposals."""
        ymd = datetime.utcnow().strftime("%Y%m%d")
        
        for p in patterns:
            # Create unique ID for the proposal
            pid = hashlib.md5(p['original_sentence'].encode()).hexdigest()[:8]
            
            proposal = {
                "id": f"EVO-{ymd}-{pid}",
                "generated_at": datetime.utcnow().isoformat(),
                "category": "LOGIC_UPDATE" if "LOGIC" in p['type'] else "DATA_UPDATE",
                "status": "PROPOSED", # Waiting for approval
                "content": {
                    "condition": p['condition'],
                    "meaning": p['implication'],
                    "type": p['type']
                },
                "evidence": {
                    "quote": p['original_sentence'],
                    "source": p['source_id']
                },
                "action_required": "REVIEW_AND_MERGE"
            }
            
            # Save
            path = self.proposal_dir / f"{proposal['id']}.json"
            path.write_text(json.dumps(proposal, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"[Evolution] Generated Proposal: {path.name}")

def main():
    base_dir = Path(__file__).parent.parent.parent
    evolver = LogicEvolver(base_dir)
    
    # Test file
    test_file = base_dir / "data/narratives/transcripts/test/logic_sample.txt"
    if test_file.exists():
        print(f"[Phase 35] Analyzing Mock Script: {test_file.name}")
        text = test_file.read_text(encoding='utf-8')
        
        patterns = evolver.discover_logic_patterns(text, "MOCK_VIDEO_001")
        
        print(f"\n[Result] Discovered {len(patterns)} Logical Rules:")
        for p in patterns:
            print(f"✨ Rule: [{p['condition']}] -> [{p['implication']}]")
            print(f"   (Type: {p['type']})")
        
        if patterns:
            print("\nGenerating Evolution Proposals...")
            evolver.generate_proposals(patterns)
    else:
        print("Test file not found.")

if __name__ == "__main__":
    main()
