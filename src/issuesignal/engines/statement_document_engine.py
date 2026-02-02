import re
from typing import List, Dict, Any
from pathlib import Path

class StatementDocumentEngine:
    """
    [IS-93] Narrative Supply Engine (Statement / Person / Document Layer)
    Extracts high-quality issue candidates from raw text (statements, IR documents, etc.)
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        # Extraction Rules (Keywords/Regex)
        self.rules = {
            "TIME": [r"\bnow\b", r"\bthis year\b", r"\bfrom 2026\b", r"\bimmediately\b", r"\bupcoming\b"],
            "INTENT": [r"\bdecided\b", r"\bprioritize\b", r"\bcore strategy\b", r"\bwe will\b", r"\bfocused on\b"],
            "SCALE": [r"\btrillion\b", r"\bbillion\b", r"\brecord\b", r"\bmaximum\b", r"\bsignificant\b"],
            "STRUCTURE": [r"\bsupply constraint\b", r"\bcapacity\b", r"\binfrastructure\b", r"\bplatform\b", r"\bbottleneck\b"],
            "COMPETITION": [r"\bcompetitor\b", r"\bequivalent to\b", r"\bunbeatable\b", r"\bmarket share\b"]
        }

    def extract_candidates(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = []
        for item in raw_data:
            text = item.get("content", "").lower()
            detected = []
            
            for category, patterns in self.rules.items():
                if any(re.search(p, text) for p in patterns):
                    detected.append(category)
            
            if detected:
                # Promotion to Candidate
                candidates.append({
                    "id": f"STMT-{hash(text) % 1000000}",
                    "type": "STATEMENT",
                    "source": item.get("source_type", "Person"),
                    "entity": item.get("entity", "Unknown"),
                    "organization": item.get("organization", "N/A"),
                    "content": item.get("content", ""), # Original text
                    "detected_signals": detected,
                    "why_it_matters_hint": self._generate_hint(detected, item.get("entity", "")),
                    "linked_assets": item.get("linked_assets", []),
                    "confidence": "CANDIDATE"
                })
        
        return candidates

    def _generate_hint(self, signals: List[str], entity: str) -> str:
        hints = []
        if "TIME" in signals or "INTENT" in signals:
            hints.append("실행 시점 및 강력한 의도 포착")
        if "STRUCTURE" in signals:
            hints.append("공급망 및 인프라 구조적 변화 암시")
        if "SCALE" in signals:
            hints.append("압도적 규모의 물리적 성과 언급")
        if "COMPETITION" in signals:
            hints.append("시장 점유율 및 경쟁 구도 재편 가능성")
            
        return " / ".join(hints) if hints else f"{entity}의 핵심 발언 포착"
