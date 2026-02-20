#!/usr/bin/env python3
"""
IS-73 Opening Sentence Rendering Verification (Editorial View)
Verifies that opening_sentence from today.json is rendered in the Editorial View
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_opening_sentence_in_editorial_view():
    """Test that opening_sentence is rendered in Editorial View HTML"""
    print("=" * 70)
    print("IS-73 Opening Sentence Editorial View Verification")
    print("=" * 70)
    
    # Step 1: Load today.json
    today_json_path = project_root / "data" / "dashboard" / "today.json"
    print(f"\n📁 Loading: {today_json_path}")
    
    if not today_json_path.exists():
        print("❌ today.json not found!")
        return False
    
    with open(today_json_path, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    
    opening_sentence = today_data.get("opening_sentence", "")
    print(f"📝 opening_sentence from JSON: {opening_sentence[:80]}..." if len(opening_sentence) > 80 else f"📝 opening_sentence from JSON: {opening_sentence}")
    
    if not opening_sentence or opening_sentence == "-":
        print("⚠️  opening_sentence is empty or '-', skipping HTML check")
        return True  # Not an error, just no content to render
    
    # Step 2: Check HTML output
    html_path = project_root / "docs" / "index.html"
    print(f"\n📄 Checking HTML: {html_path}")
    
    if not html_path.exists():
        print("❌ docs/index.html not found!")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Step 3: Verify rendering
    print("\n" + "=" * 70)
    print("VERIFICATION CHECKS")
    print("=" * 70)
    
    checks_passed = 0
    total_checks = 2
    
    # Check 1: "📌 오늘의 핵심 한 문장:" exists
    marker = "📌 오늘의 핵심 한 문장:"
    if marker in html_content:
        print(f"✅ CHECK 1: '{marker}' found in HTML")
        checks_passed += 1
    else:
        print(f"❌ CHECK 1: '{marker}' NOT found in HTML!")
    
    # Check 2: Actual opening_sentence content exists
    # Extract first 30 chars for partial match (to handle HTML encoding)
    opening_snippet = opening_sentence[:30]
    if opening_snippet in html_content:
        print(f"✅ CHECK 2: opening_sentence content found in HTML")
        print(f"   Snippet: '{opening_snippet}...'")
        checks_passed += 1
    else:
        print(f"❌ CHECK 2: opening_sentence content NOT found in HTML!")
        print(f"   Expected snippet: '{opening_snippet}...'")
    
    # Show context if found
    if marker in html_content:
        idx = html_content.find(marker)
        context = html_content[max(0, idx-50):idx+200]
        print(f"\n📋 HTML Context:")
        print(context)
    
    print("\n" + "=" * 70)
    print(f"RESULT: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    
    return checks_passed == total_checks


if __name__ == "__main__":
    success = test_opening_sentence_in_editorial_view()
    sys.exit(0 if success else 1)
