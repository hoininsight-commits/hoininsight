
import os
import json
import re
from pathlib import Path

# Placeholder for LLM interaction logic. 
# In a real scenario, this would call OpenAI/Gemini API.
# Here we simulate the logic extraction for demonstration.

class LogicExtractor:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """Loads critical asset names from DATA_COLLECTION_MASTER to check against."""
        kb = []
        master_path = self.base_dir / "docs/DATA_COLLECTION_MASTER.md"
        if master_path.exists():
            content = master_path.read_text(encoding='utf-8')
            # Extract basic keywords (simple heuristic)
            # Find lines starting with `|` and capture first word
            matches = re.findall(r"\|\s*([A-Za-z0-9_]+)\s*\|", content)
            kb = [m.lower() for m in matches if "id" not in m.lower()]
        return set(kb)

    def analyze_transcript(self, transcript_path):
        """
        Reads transcript and extracts key logic claims.
        Returns a structured report.
        """
        path = Path(transcript_path)
        if not path.exists():
            return None
            
        text = path.read_text(encoding='utf-8')
        
        # --- SIMULATED LLM ANALYSIS ---
        # In reality, we would send `text` to an LLM with a prompt:
        # "Extract key economic indicators and causal logic (if X then Y) from this text."
        
        extracted_concepts = []
        
        # Simple Keyword Matching for prototype
        keywords = {
            "구리": "copper",
            "재고": "inventory",
            "환율": "exchange_rate",
            "엔화": "jpy",
            "금리": "interest_rate",
            "유가": "oil_price",
            "반도체": "semiconductor"
        }
        
        found_keywords = []
        for word, key in keywords.items():
            if word in text:
                found_keywords.append(key)
                
        # Logic Construction
        logic_report = {
            "video_id": path.parent.name,
            "found_terms": found_keywords,
            "claims": [],
            "missing_in_db": []
        }
        
        # Identify Gaps
        for term in found_keywords:
            # Check if this term exists in our Knowledge Base (DATA_COLLECTION_MASTER)
            # This is a fuzzy check.
            known = False
            for db_term in self.knowledge_base:
                if term in db_term or db_term in term:
                    known = True
                    break
            
            if not known:
                logic_report['missing_in_db'].append(term)
                
        # Mocking a specific logic for the known video (Reverse Engineering Demo)
        if "구리" in text and "재고" in text:
            logic_report['claims'].append({
                "logic": "구리 재고 감소 -> 구리 가격 상승 -> 경기 선행 지표 호전",
                "drivers": ["copper_inventory", "copper_price"],
                "gap": True if "copper_inventory" not in self.knowledge_base else False
            })
            if "copper_inventory" not in self.knowledge_base:
                 logic_report['missing_in_db'].append("copper_inventory")

        return logic_report

    def create_proposal(self, logic_report):
        """
        Creates a markdown proposal file if gaps are found.
        """
        if not logic_report['missing_in_db']:
            print(f"[Extractor] No missing data found for {logic_report['video_id']}")
            return None
            
        vid = logic_report['video_id']
        missing = ", ".join(logic_report['missing_in_db'])
        
        proposal_content = f"""
# 🚀 [AUTO-PROPOSAL] Logic Gap Detected from Video {vid}

## 1. Source Analysis
*   **Source Video**: {vid}
*   **Detected Logic**: {logic_report['claims'][0]['logic'] if logic_report['claims'] else 'N/A'}

## 2. Gap Identification
*   The video emphasizes **{missing}** as a key indicator.
*   Current `DATA_COLLECTION_MASTER` **DOES NOT** explicitly track this metric.

## 3. Proposal
*   **Action**: Add `{missing}` to Data Collection.
*   **Target File**: `docs/DATA_COLLECTION_MASTER.md`, `registry/datasets.yml`
*   **Rationale**: Competitor analysis suggests this indicator is currently driving market narrative.

## 4. Expected Impact
*   Improvement in prediction accuracy for Commodity/Industrial cycles.

"""
        # Save Proposal
        ymd = "2026/01/17" # Using today for demo
        save_dir = self.base_dir / f"data/narratives/proposals/{ymd}"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / f"proposal_gap_{vid}.md"
        file_path.write_text(proposal_content, encoding='utf-8')
        
        print(f"[Extractor] Proposal created: {file_path}")
        return str(file_path)

if __name__ == "__main__":
    base = Path(__file__).parent.parent.parent
    extractor = LogicExtractor(base)
    # Test
    # logic = extractor.analyze_transcript("data/raw/youtube/VIDEO_ID/transcript.txt")
    # extractor.create_proposal(logic)
