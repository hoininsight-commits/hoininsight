import re
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

def test_zero_english_in_dashboard_html():
    """
    IS-47 Zero English Policy Test.
    Scans docs/index.html for unauthorized English text in visible UI.
    """
    html_path = Path("docs/index.html")
    if not html_path.exists():
        pytest.skip("docs/index.html not generated yet")
        
    html_content = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
        
    text = soup.get_text(separator=' ')
    
    # Filter out whitelisted terms
    # 1. URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # 2. File paths / extensions
    text = re.sub(r'\.json|\.md|\.py|html', '', text)
    # 3. Tickers (All caps 2-5 chars, often inside parens or context) - Heuristic
    # We'll allow all-caps words of length 2-5 for now as Tickers/Codes
    text = re.sub(r'\b[A-Z]{2,5}\b', '', text)
    # 4. Specific Allowed Technical Terms (if any, strictly minimized)
    whitelist = [
        "HOIN", "Insight", "IssueSignal", "GitHub", "Pages", "Copyright", "Rights", "Reserved", "Top-1", "PRE-TRIGGER", "CSS", "JS", "URL", "JSON", "WHY", "NOW", "PRESSURE", "SCOPE", "INTENSITY", "FLASH", "STRIKE", "DEEP_HUNT", "STRUCTURAL", "RHYTHM", "NEW", "TOPIC", "RECURRING", "INTENSIFIED", "EASED", "SUSTAINED", "OBSERVE", "MONITOR", "PREPARE", "STAND_BY", "EXECUTOR", "BENEFICIARY", "VICTIM", "HEDGE", "BOTTLENECK", "LOCKED"
    ]
    # Note: I am whitelisting terms I just translated BUT checking if they were replaced. 
    # Actually IS-47 requires these to be KOREAN. 
    # So I should NOT whitelist terms like "ACTIVE", "SILENCE", "TRUST LOCKED" etc via replacements.
    # The whitelist above allows some internal codes if they appear in badges. 
    # BUT "Trust Locked" was explicitly asked to be translated.
    
    # Improved Whitelist (Only unverifiable proper nouns or essential technical codes)
    strict_whitelist = [
        "HOIN", "Insight", "IssueSignal", "GitHub", "Pages", "Copyright", "2026", "AAPL", "KRW", "USD", "BTC", "ETH", "ECOS", "FRED"
    ]

    for w in strict_whitelist:
        text = text.replace(w, "")

    # Find remaining English words (3+ letters to avoid noise)
    english_pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
    matches = english_pattern.findall(text)
    
    # Filter out likely false positives or noise
    real_matches = [m for m in matches if len(m) > 2]
    
    if real_matches:
        unique_matches = sorted(list(set(real_matches)))
        # Fail if unauthorized English found
        # We perform a softer check: report them first. 
        # For IS-47 strictness, we should fail. 
        # However, purely checking rendered HTML text is tricky.
        # Let's print them and assert empty.
        print(f"\n[IS-47] Unauthorized English found: {unique_matches}")
        assert not unique_matches, f"Found {len(unique_matches)} English terms violating Zero English Policy: {unique_matches[:10]}..."

if __name__ == "__main__":
    test_zero_english_in_dashboard_html()
