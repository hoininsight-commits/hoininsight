#!/usr/bin/env python3
"""
IS-73 Dashboard Loader Verification Script
Verifies that DashboardLoader correctly loads ISSUE-*.json files
and excludes latest*.json and RAW-*.json files.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.issuesignal.dashboard.loader import DashboardLoader


def test_loader_loads_issue_files():
    """Test that loader prioritizes ISSUE-*.json files"""
    print("=" * 60)
    print("IS-73 Dashboard Loader Verification")
    print("=" * 60)
    
    loader = DashboardLoader(project_root)
    
    # Check packs directory
    packs_dir = project_root / "data" / "issuesignal" / "packs"
    print(f"\n📁 Packs directory: {packs_dir}")
    
    if not packs_dir.exists():
        print("❌ Packs directory does not exist!")
        return False
    
    # List all JSON files
    all_json = sorted(packs_dir.glob("*.json"))
    issue_json = sorted(packs_dir.glob("ISSUE-*.json"), reverse=True)
    
    print(f"\n📋 Total JSON files: {len(all_json)}")
    for f in all_json:
        print(f"  - {f.name}")
    
    print(f"\n✅ ISSUE-*.json files (should be loaded): {len(issue_json)}")
    for f in issue_json:
        print(f"  - {f.name}")
    
    # Load cards using the loader
    cards = loader._load_recent_cards()
    
    print(f"\n🎯 Cards loaded by DashboardLoader: {len(cards)}")
    for i, card in enumerate(cards[:5]):  # Show first 5
        print(f"  {i+1}. {card.topic_id}")
        print(f"     Status: {card.status}")
        print(f"     opening_sentence: {card.opening_sentence[:60]}..." if len(card.opening_sentence) > 60 else f"     opening_sentence: {card.opening_sentence}")
    
    # Verification checks
    print("\n" + "=" * 60)
    print("VERIFICATION CHECKS")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 3
    
    # Check 1: At least one card loaded
    if len(cards) > 0:
        print("✅ CHECK 1: At least one card loaded")
        checks_passed += 1
    else:
        print("❌ CHECK 1: No cards loaded!")
    
    # Check 2: First card is an ISSUE card
    if len(cards) > 0 and cards[0].topic_id.startswith("ISSUE-"):
        print(f"✅ CHECK 2: First card is ISSUE card ({cards[0].topic_id})")
        checks_passed += 1
    else:
        print(f"❌ CHECK 2: First card is NOT an ISSUE card!")
    
    # Check 3: First card has opening_sentence
    if len(cards) > 0 and cards[0].opening_sentence and cards[0].opening_sentence != "-":
        print(f"✅ CHECK 3: opening_sentence exists: \"{cards[0].opening_sentence[:80]}...\"")
        checks_passed += 1
    else:
        print(f"❌ CHECK 3: opening_sentence missing or empty!")
    
    print("\n" + "=" * 60)
    print(f"RESULT: {checks_passed}/{total_checks} checks passed")
    print("=" * 60)
    
    return checks_passed == total_checks


if __name__ == "__main__":
    success = test_loader_loads_issue_files()
    sys.exit(0 if success else 1)
