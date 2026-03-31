import re
from typing import Dict, Any, List, Tuple
from .dashboard.models import SourceCluster

class SourceDiversityEngine:
    """
    (IS-32) Canonicalizes sources and detects wire chains to ensure independence.
    """
    
    # Predefined cluster mappings (simplified for simulation)
    CLUSTERS = {
        "reuters": ("REUTERS_WIRE", "MAJOR_MEDIA", "Reuters"),
        "bloomberg": ("BLOOMBERG_WIRE", "MAJOR_MEDIA", "Bloomberg"),
        "wsj": ("DOW_JONES_GROUP", "MAJOR_MEDIA", "WSJ / Dow Jones"),
        "dow jones": ("DOW_JONES_GROUP", "MAJOR_MEDIA", "WSJ / Dow Jones"),
        "federalreserve": ("FED_OFFICIAL", "OFFICIAL", "Federal Reserve"),
        "treasury.gov": ("US_TREASURY", "OFFICIAL", "US Treasury"),
        "whitehouse.gov": ("WH_OFFICIAL", "OFFICIAL", "White House"),
        "sec.gov": ("SEC_OFFICIAL", "OFFICIAL", "SEC"),
        "fred.stlouisfed": ("FRED_DATA", "MARKET_DATA", "FRED"),
    }

    def __init__(self):
        self.audit_log = []

    def get_cluster(self, source_ref: str, text: str = "", source_kind: str = "UNKNOWN") -> SourceCluster:
        """
        Assigns a SourceCluster based on the reference, optional text analysis, and source_kind.
        """
        source_ref_lower = source_ref.lower()
        text_lower = text.lower()
        source_kind = source_kind.upper()
        
        # 1. Prioritize source_kind for OFFICIAL
        if any(k in source_kind for k in ["GOV", "REGULATOR", "COURT", "FILING", "OFFICIAL"]):
             cluster = SourceCluster(cluster_id=f"{source_kind}_OFFICIAL_{source_ref_lower[:10]}", 
                                    cluster_type="OFFICIAL", 
                                    origin_name=f"{source_kind} Source", 
                                    reason="Source kind identified as OFFICIAL.")
             return cluster

        # 2. Detect Wire Chains / Citations in text
        chain_origin = self._detect_wire_chain(text_lower)
        if chain_origin:
            cid, ctype, name = self.CLUSTERS[chain_origin]
            cluster = SourceCluster(cluster_id=cid, cluster_type=ctype, origin_name=name, reason=f"Chain detected: {chain_origin}")
            self.audit_log.append({"ref": source_ref, "found": chain_origin, "cluster": cid})
            return cluster

        # 2. Match Domain/Ref
        for key, (cid, ctype, name) in self.CLUSTERS.items():
            if key in source_ref_lower:
                cluster = SourceCluster(cluster_id=cid, cluster_type=ctype, origin_name=name, reason="Domain match.")
                self.audit_log.append({"ref": source_ref, "found": key, "cluster": cid})
                return cluster

        # 3. Handle mirrored PDFs or generic origins
        if ".pdf" in source_ref_lower:
            # If same PDF name appears elsewhere, it would normally be clustered by filename
            # For this simulation, we'll use the basename as a cluster hint
            pdf_name = source_ref.split("/")[-1]
            cluster = SourceCluster(cluster_id=f"FILE_{pdf_name}", cluster_type="GENERAL_NEWS", origin_name=pdf_name, reason="Filename match.")
            return cluster

        # Default
        return SourceCluster(cluster_id=f"GENERIC_{source_ref_lower[:10]}", cluster_type="GENERAL_NEWS", origin_name="Generic Source")

    def _detect_wire_chain(self, text: str) -> str:
        """
        Search for phrases like 'Reuters reports', 'according to Bloomberg', etc.
        """
        for key in self.CLUSTERS.keys():
            patterns = [
                rf"{key}\s+reports",
                rf"according\s+to\s+{key}",
                rf"citing\s+{key}",
                rf"source:\s*{key}",
                rf"reprinted\s+from\s+{key}"
            ]
            for p in patterns:
                if re.search(p, text):
                    return key
        return ""

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.audit_log
