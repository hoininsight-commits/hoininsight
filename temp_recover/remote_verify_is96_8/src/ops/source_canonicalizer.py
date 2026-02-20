import hashlib
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List, Dict, Any, Optional

class SourceCanonicalizer:
    """
    IS-32: SOURCE_CANONICALIZER
    Normalizes URLs and generates stable canonical identifiers for sources.
    """

    def __init__(self):
        # Patterns for official document IDs
        self.OFFICIAL_ID_PATTERNS = [
            r"sec\.gov/Archives/edgar/data/\d+/(\d+)", # SEC Accession
            r"federalregister\.gov/d/(\d{4}-\d+)",      # Federal Register
            r"whitehouse\.gov/briefing-room/.*?/(\d{4}/\d{2}/\d{2}/.*?)", # WH Briefing
            r"federalreserve\.gov/newsevents/pressreleases/(.*?)\.htm", # Fed PR
        ]

    def canonicalize(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: Source dict with 'url', 'publisher', 'source_type', etc.
        Output: source dict with 'canonical_source_id' and 'canonical_fingerprint'.
        """
        url = source.get("url")
        source_type = source.get("source_type", "UNKNOWN").upper()
        publisher = source.get("publisher", "UNKNOWN").upper()
        
        # 1. URL Normalization
        norm_url = self.normalize_url(url) if url else None
        
        # 2. Extract Document ID (if official or contains known ID)
        doc_id = None
        if url:
             for pattern in self.OFFICIAL_ID_PATTERNS:
                 match = re.search(pattern, url)
                 if match:
                     doc_id = match.group(1)
                     break
             
             # Fallback: if URL contains something that looks like an accession number 
             # (18 digits with dashes or similar)
             if not doc_id:
                 accession_match = re.search(r"(\d{10}-\d{2}-\d{6})|(\d{18})", url)
                 if accession_match:
                     doc_id = accession_match.group(0)

        # 3. Generate Canonical ID
        # (source_type + issuing_body + doc_id/event_id + date + headline_key)
        date_str = source.get("date") or "NO_DATE"
        headline = (source.get("title") or "").strip().lower()
        headline_key = hashlib.md5(headline.encode()).hexdigest()[:8] if headline else "NO_HEADLINE"
        
        cid_parts = [source_type, publisher, doc_id or "NO_DOC", date_str, headline_key]
        canonical_source_id = ":".join(cid_parts)
        
        # 4. Generate Fingerprint
        # Collapses mirrors. If doc_id exists, that's the fingerprint. 
        # Otherwise, normalized URL.
        fingerprint_content = doc_id if doc_id else (norm_url or canonical_source_id)
        canonical_fingerprint = hashlib.sha256(fingerprint_content.encode()).hexdigest()
        
        source["canonical_source_id"] = canonical_source_id
        source["canonical_fingerprint"] = canonical_fingerprint
        source["normalized_url"] = norm_url
        
        return source

    def normalize_url(self, url: str) -> str:
        """Strips query params, UTM, and normalizes components."""
        try:
            parsed = urlparse(url)
            # 1. Normalize scheme and host
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            
            # 2. Path normalization
            path = parsed.path
            if path.endswith("/"):
                path = path[:-1]
                
            # 3. Strip tracking/query params
            # Keep none for strict canonicalization unless specified
            query = "" 
            
            # 4. Reconstruct
            return urlunparse((scheme, netloc, path, "", "", ""))
        except:
            return url
