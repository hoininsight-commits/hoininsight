from typing import List, Dict, Any, Optional

class QuoteSourceVerifier:
    """
    IS-31: QUOTE_SOURCE_VERIFIER
    Implements strict cross-source validation and context rules for quotes.
    """
    
    SOURCE_TRUST_LEVELS = {
        "OFFICIAL_TRANSCRIPT": "STRONG",
        "OFFICIAL_RELEASE": "STRONG",
        "OFFICIAL_SCHEDULE": "STRONG",
        "REGULATORY_DOCKET": "STRONG",
        "EARNINGS_CALL_TRANSCRIPT": "STRONG",
        "REUTERS": "STRONG",
        "BLOOMBERG": "STRONG",
        "WSJ": "STRONG",
        "AP": "STRONG",
        "CNBC": "MEDIUM",
        "FT": "MEDIUM",
        "YAHOO_FINANCE": "MEDIUM"
    }

    def __init__(self):
        pass

    def verify_quote(self, quote_pack: Dict[str, Any], all_sources: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Input: 
          - quote_pack: The QuoteEvidencePack to verify.
          - all_sources: List of all source objects citing this quote.
        Output:
          - verdict: PASS | HOLD | REJECT
          - reason_code: string
        """
        # 1. Official Source Rule
        if quote_pack["source_type"].startswith("OFFICIAL_"):
            # Check if all context is present in the same pack
            if all([quote_pack.get("speaker"), quote_pack.get("event_time_utc"), quote_pack.get("event_name")]):
                return {"verdict": "PASS", "reason_code": "OFFICIAL_SOURCE_VERIFIED"}
            return {"verdict": "HOLD", "reason_code": "NO_CONTEXT"}

        # 2. Cross-Source Rule (Strong + Strong) OR (Strong + Medium)
        trust_scores = []
        unique_publishers = set()
        
        for src in all_sources:
            pub = src.get("publisher", "unknown").upper()
            if pub == "UNKNOWN" or pub in unique_publishers:
                continue
            
            level = self.SOURCE_TRUST_LEVELS.get(pub, "LOW")
            trust_scores.append(level)
            unique_publishers.add(pub)

        # Count levels
        strong_count = trust_scores.count("STRONG")
        medium_count = trust_scores.count("MEDIUM")

        if strong_count >= 2:
            return {"verdict": "PASS", "reason_code": "CROSS_SOURCE_STRONG"}
        if strong_count >= 1 and medium_count >= 1:
            return {"verdict": "PASS", "reason_code": "CROSS_SOURCE_MIXED"}

        # 3. Rejection Rules
        if len(unique_publishers) <= 1:
            return {"verdict": "HOLD", "reason_code": "SINGLE_SOURCE"}
        
        if len(quote_pack["quote_text"]) > 240:
            return {"verdict": "REJECT", "reason_code": "QUOTE_TOO_LONG"}
        
        # Non-independent check (Simplified: if publishers are obviously related, e.g., Wire Chain)
        # This part of IS-32 logic is hinted but IS-31 requires independence.
        # For IS-31 basic: just check if they are the same.
        
        return {"verdict": "HOLD", "reason_code": "NO_STRONG_SOURCE"}
