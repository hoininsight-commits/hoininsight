from typing import List, Dict, Any, Optional, Set
from src.ops.source_canonicalizer import SourceCanonicalizer
from src.ops.dependency_chain_detector import DependencyChainDetector

class DiversityEnforcer:
    """
    IS-32: DIVERSITY_ENFORCER
    Ensures final evidence set contains at least 2 independent clusters 
    and 2 different source families.
    """

    FAMILY_MAP = {
        "OFFICIAL_RELEASE": "OFFICIAL",
        "OFFICIAL_TRANSCRIPT": "OFFICIAL",
        "OFFICIAL_SCHEDULE": "OFFICIAL",
        "REGULATORY_DOCKET": "REGULATORY",
        "FILING": "FILINGS",
        "EARNINGS_CALL_TRANSCRIPT": "TRANSCRIPT",
        "MARKET_DATA": "MARKET_DATA",
        "REUTERS": "MAJOR_MEDIA",
        "BLOOMBERG": "MAJOR_MEDIA",
        "WSJ": "MAJOR_MEDIA",
        "AP": "MAJOR_MEDIA",
        "FT": "MAJOR_MEDIA",
        "CNBC": "MAJOR_MEDIA"
    }

    def __init__(self):
        self.canonicalizer = SourceCanonicalizer()
        self.chain_detector = DependencyChainDetector()

    def enforce(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Input: List of raw source dicts.
        Output: Dict with 'verdict', 'reason_code', and 'enriched_sources'.
        """
        if not sources:
            return {"verdict": "REJECT", "reason_code": "NO_EVIDENCE", "enriched_sources": []}

        # 1. Enrich Sources
        enriched = []
        for s in sources:
            s = self.canonicalizer.canonicalize(s.copy())
            s = self.chain_detector.detect(s)
            enriched.append(s)

        # 2. Cluster Sources
        clusters = {} # origin_cluster_id -> [sources]
        for s in enriched:
            cid = s["origin_cluster_id"]
            if cid not in clusters:
                clusters[cid] = []
            clusters[cid].append(s)

        # 3. Identify Independent Clusters
        # Collapse Original + Derived into the same cluster if they relate to the same wire
        refined_clusters = {}
        for s in enriched:
            pub = s.get("publisher", "").upper()
            derived_from = s.get("derived_from", "").upper()
            
            # Cluster key strategy:
            # If it's a wire or derived from a wire, use the wire name as cluster key
            wire_names = ["REUTERS", "BLOOMBERG", "AP", "AFP", "YONHAP", "YONHAPNEWS", "NEWSIS"]
            
            final_cid = s["origin_cluster_id"]
            if pub in wire_names:
                final_cid = f"WIRE_{pub}"
            elif s["dependency_label"] == "DERIVED" and derived_from:
                # derived_from might be "Reuters" or "로이터" - DependencyChainDetector handles normalization mostly
                final_cid = f"WIRE_{derived_from}"
            
            if final_cid not in refined_clusters:
                refined_clusters[final_cid] = []
            refined_clusters[final_cid].append(s)
            s["final_cluster_id"] = final_cid

        unique_clusters = list(refined_clusters.keys())
        
        # 4. Identify Source Families
        found_families = set()
        for s in enriched:
            # Map publisher or source_type to family
            pub = s.get("publisher", "").upper()
            stype = s.get("source_type", "").upper()
            
            family = self.FAMILY_MAP.get(pub) or self.FAMILY_MAP.get(stype) or "OTHER"
            if family != "OTHER":
                found_families.add(family)
            s["family"] = family

        # 5. Apply Rules
        # Min 2 clusters AND Min 2 families
        verdict = "PASS"
        reason_code = "DIVERSITY_OK"

        if len(unique_clusters) < 2:
            verdict = "HOLD"
            if "WIRE_" in unique_clusters[0]:
                reason_code = "WIRE_CHAIN_DUPLICATION"
            else:
                reason_code = "LACK_SOURCE_DIVERSITY"
        elif len(found_families) < 2:
            verdict = "HOLD"
            reason_code = "LACK_SOURCE_FAMILIES"

        return {
            "verdict": verdict,
            "reason_code": reason_code,
            "clusters_count": len(unique_clusters),
            "families_count": len(found_families),
            "families_list": list(found_families),
            "enriched_sources": enriched
        }
