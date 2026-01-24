
"""
Knowledge Base Module
Reads markdown documentation files to provide dynamic logic for the engine.
"""

from pathlib import Path
from typing import List, Dict, Any

class KnowledgeBase:
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.dm_path = docs_dir / "DATA_COLLECTION_MASTER.md"
        self.al_path = docs_dir / "ANOMALY_DETECTION_LOGIC.md"
        
        # Cache
        self._data_defs = []
        self._anomaly_logic = []
        
    def load(self):
        """Force reload of knowledge base."""
        self._data_defs = self._parse_data_master()
        self._anomaly_logic = self._parse_anomaly_logic()
        
    def get_data_definitions(self) -> List[Dict[str, str]]:
        if not self._data_defs:
            self.load()
        return self._data_defs

    def get_anomaly_logic(self) -> List[Dict[str, str]]:
        if not self._anomaly_logic:
            self.load()
        return self._anomaly_logic

    def get_keywords_for_extraction(self) -> List[str]:
        """Generate a list of keywords to look for in transcripts based on Data Master."""
        defs = self.get_data_definitions()
        keywords = set()
        
        # Extract keywords from 'name' (e.g., "미국 기준금리" -> "기준금리", "미국")
        # And 'category'
        for d in defs:
            name = d['name']
            
            # Simple tokenization by space
            tokens = name.split()
            keywords.update(tokens)
            
            # Clean up parenthesis
            cleaned_name = name.split('(')[0].strip()
            keywords.add(cleaned_name)
            
            # Add category words
            cat = d['category'].replace('·', ' ').replace('/', ' ')
            keywords.update(cat.split())
            
        # Add basic manually mandated keywords that might not be in titles but are essential
        essentials = ["인플레이션", "물가", "실업", "고용", "경기", "침체", "호황", "폭락", "급등"]
        keywords.update(essentials)
        
        # Filter short words
        return sorted([k for k in keywords if len(k) >= 2])

    def _parse_data_master(self) -> List[Dict[str, str]]:
        if not self.dm_path.exists():
            return []
            
        content = self.dm_path.read_text(encoding='utf-8')
        defs = []
        
        for line in content.splitlines():
            line = line.strip()
            # Valid table row: starts with | and not a separator
            if line.startswith('|') and '---|' not in line and '카테고리' not in line:
                # | Category | Name | Source | Method | Free | Status | Why | ...
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 7:
                    defs.append({
                        "category": parts[0],
                        "name": parts[1],
                        "why": parts[6]
                    })
        return defs

    def _parse_anomaly_logic(self) -> List[Dict[str, str]]:
        if not self.al_path.exists():
            return []
            
        content = self.al_path.read_text(encoding='utf-8')
        logic_entries = []
        current_section = ""
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('### '):
                current_section = line.replace('###', '').strip()
            
            # Pattern: **(A) Title**
            if line.startswith('**(') and ') ' in line:
                title = line.replace('**', '').strip()
                condition = ""
                meaning = ""
                
                # Check next few lines for Condition/Meaning
                for j in range(i+1, min(i+6, len(lines))):
                    subline = lines[j].strip()
                    if subline.startswith('- 조건:'):
                        condition = subline.replace('- 조건:', '').strip()
                    elif subline.startswith('- 의미:'):
                        meaning = subline.replace('- 의미:', '').strip()
                
                if condition:
                    logic_entries.append({
                        "section": current_section,
                        "title": title,
                        "condition": condition,
                        "meaning": meaning
                    })
        return logic_entries
