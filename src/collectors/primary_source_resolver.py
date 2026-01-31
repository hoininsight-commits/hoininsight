from urllib.parse import urlparse
from typing import Dict, Any

# Trusted Official Domains (STRONG Evidence)
TRUSTED_DOMAINS = [
    "bok.or.kr",       # Bank of Korea
    "federalreserve.gov", # US Fed
    "moef.go.kr",      # Ministry of Economy and Finance (KR)
    "whitehouse.gov",  # US White House
    "fsc.go.kr",       # Financial Services Commission (KR)
    "kdi.re.kr",       # KDI
    "imf.org",         # IMF
    "worldbank.org",   # World Bank
    "krx.co.kr"        # Korea Exchange
]

# Tier 1 News (MEDIUM Evidence) - Reliable but Secondary
TIER1_NEWS_DOMAINS = [
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "yonhapnews.co.kr",
    "yna.co.kr"
]

def resolve_primary_source(url: str, title: str) -> Dict[str, Any]:
    """
    Analyzes the URL to determine if it's a Primary Source (Official).
    Returns a dictionary with grade and metadata.
    """
    if not url:
        return {
            "evidence_grade": "TEXT_HINT",
            "grade_reason_ko": "URL 부재 (단순 텍스트 감지)",
            "primary_url": None,
            "publisher_domain": None
        }

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        
        # 1. Check Trusted (STRONG)
        for trusted in TRUSTED_DOMAINS:
            if trusted in domain:
                return {
                    "evidence_grade": "HARD_FACT", # Synonymous with STRONG in previous context, using HARD_FACT for consistency
                    "grade_reason_ko": f"공식 도메인 확인됨 ({trusted})",
                    "primary_url": url,
                    "publisher_domain": domain,
                    "doc_type": "PDF" if url.lower().endswith(".pdf") else "HTML"
                }
                
        # 2. Check Tier 1 News (MEDIUM)
        for news in TIER1_NEWS_DOMAINS:
            if news in domain:
                return {
                    "evidence_grade": "MEDIUM",
                    "grade_reason_ko": f"신뢰할 수 있는 언론사 ({news}), 그러나 원문 아님",
                    "primary_url": url,
                    "publisher_domain": domain,
                    "doc_type": "NEWS"
                }
                
        # 3. Default (HINT)
        return {
            "evidence_grade": "TEXT_HINT",
            "grade_reason_ko": "일반 뉴스/블로그 또는 재인용 출처",
            "primary_url": url,
            "publisher_domain": domain,
            "doc_type": "WEB"
        }
        
    except Exception as e:
        return {
            "evidence_grade": "TEXT_HINT",
            "grade_reason_ko": f"URL 파싱 오류: {e}",
            "primary_url": url,
            "publisher_domain": None
        }
