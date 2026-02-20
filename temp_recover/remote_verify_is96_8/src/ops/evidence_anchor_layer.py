from typing import List, Dict, Any, Optional
from pathlib import Path

class EvidenceAnchorLayer:
    """
    STEP 54 — EVIDENCE ANCHOR MAPPING
    Maps data sources to reasoning steps.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        
    def map_anchors(self, topic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract anchors from topic metadata.
        """
        anchors = []
        
        # 1. Macro/Market Anchors from 'evidence' field
        evidence = topic.get("evidence", [])
        for ev in evidence:
            source = ev.get("source", "UNKNOWN")
            type_tag = "MARKET"
            if source in ["FRED", "ECOS", "BOK"]:
                type_tag = "MACRO"
            elif source in ["DART", "SEC"]:
                type_tag = "POLICY"
                
            anchors.append({
                "type": type_tag,
                "source": source,
                "ref_id": ev.get("ref_id", "N/A"),
                "key_value": str(ev.get("value", "Data Point")),
                "rationale": ev.get("context", "추론을 뒷받침하는 핵심 팩트 지표.")
            })
            
        # 2. Source Refs
        source_refs = topic.get("source_refs", [])
        for ref in source_refs:
            if any(a["ref_id"] == ref for a in anchors):
                continue
            anchors.append({
                "type": "REFERENCE",
                "source": ref.split(":")[0] if ":" in ref else "EXTERNAL",
                "ref_id": ref,
                "key_value": "LINKED",
                "rationale": "데이터 정합성 및 교차 검증을 위한 외부 참조."
            })
            
        return anchors[:5] # Limit to top 5
