from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
from .source_diversity import SourceDiversityEngine

class SourceType(Enum):
    GOV_DOC = "GOV_DOC"
    REGULATORY = "REGULATORY"
    COMPANY_FILINGS = "COMPANY_FILINGS"
    CONTRACT_DATA = "CONTRACT_DATA"
    FLOW_DATA = "FLOW_DATA"
    PHYSICAL_DATA = "PHYSICAL_DATA"
    EARNINGS_CALL = "EARNINGS_CALL"
    MAJOR_MEDIA = "MAJOR_MEDIA"
    ANALYST_REPORT = "ANALYST_REPORT"

class FactVerifier:
    """
    (IS-25) Enforces cross-source verification for all triggers.
    Ensures at least two independent source types support a hard fact.
    """
    STRONG_SOURCES = {
        SourceType.GOV_DOC, 
        SourceType.REGULATORY, 
        SourceType.COMPANY_FILINGS, 
        SourceType.CONTRACT_DATA
    }
    
    MEDIUM_SOURCES = {
        SourceType.FLOW_DATA, 
        SourceType.PHYSICAL_DATA, 
        SourceType.EARNINGS_CALL, 
        SourceType.MAJOR_MEDIA
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def verify(self, signal: Dict[str, Any], evidence_pack: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Verifies if the facts in the signal are supported by cross-sources.
        Returns: (is_passed, reason_code, debug_info)
        """
        debug = {}
        
        # 1. Identify facts and their supporting sources
        # Input evidence_pack expects: {"evidence": [{"text": "...", "source_type": "...", "is_original": bool}]}
        evidence = evidence_pack.get("evidence", [])
        if not evidence:
            return False, "NO_EVIDENCE_PROVIDED", {}

        # group sources by fact (simplified: assume one main fact per trigger in this version)
        source_types_found: Set[SourceType] = set()
        verified_facts = []
        
        for ev in evidence:
            s_type_str = ev.get("source_type", "").upper()
            try:
                s_type = SourceType(s_type_str)
            except ValueError:
                continue

            # IS-32: Check Clusters
            diversity_engine = SourceDiversityEngine()
            source_ref = ev.get("source_ref", "")
            text = ev.get("text", "")
            cluster = diversity_engine.get_cluster(source_ref, text, s_type_str)
            ev["cluster_id"] = cluster.cluster_id
            ev["cluster_type"] = cluster.cluster_type

            source_types_found.add(s_type)
            verified_facts.append(ev)

        debug["source_types"] = [s.value for s in source_types_found]
        debug["fact_count"] = len(verified_facts)

        # 2. Apply PASS Logic
        # Condition 1: 2+ different types AND different clusters
        unique_clusters = {ev.get("cluster_id") for ev in verified_facts if ev.get("cluster_id")}
        debug["unique_clusters"] = list(unique_clusters)
        
        if len(source_types_found) >= 2 and len(unique_clusters) >= 2:
            return True, None, debug
        
        if len(unique_clusters) < 2 and len(source_types_found) >= 2:
            return False, "WIRE_CHAIN_DUPLICATION", debug
            
        # Condition 2: 1 Strong + 1 Medium (but we checked len >= 2 above)
        # Re-check logic: If only 1 type, it's a fail.
        # If 2 types, check types. Actually, any 2 different types is a PASS in current spec
        # UNLESS one is MAJOR_MEDIA and we want to be stricter.
        # Given "Strong 1 + Medium 1", any 2 types from {Strong, Medium} passed together or individually.
        
        if len(source_types_found) < 2:
            return False, "SINGLE_SOURCE_RISK", debug

        return False, "UNKNOWN_VALIDATION_FAILURE", debug

    def _get_category(self, s_type: SourceType) -> str:
        if s_type in self.STRONG_SOURCES:
            return "STRONG"
        if s_type in self.MEDIUM_SOURCES:
            return "MEDIUM"
        return "WEAK"
