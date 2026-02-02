import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.roster.statement_roster_manager import StatementRosterManager
from src.collectors.statement_primary_anchor_resolver import StatementPrimaryAnchorResolver
from src.issuesignal.engines.statement_dedup_engine import StatementDedupEngine
from src.issuesignal.dashboard.renderer import DashboardRenderer
from src.issuesignal.dashboard.models import DashboardSummary, DecisionCard, TriggerQuote

def verify_is94a():
    base_dir = Path(__file__).parent.parent
    print("=== IS-94A Verification Started ===")

    # 1. Verify Roster Manager
    roster_path = base_dir / "src" / "issuesignal" / "config" / "statement_roster.json"
    manager = StatementRosterManager(roster_path)
    active = manager.get_active_roster()
    print(f"Active roster items: {len(active)}")
    assert len(active) > 0, "Active roster should not be empty"
    
    sources = manager.get_sources_for_collection()
    print(f"Total collection sources: {len(sources)}")
    assert len(sources) >= len(active), "Sources should be at least as many as roster items"
    print("✅ StatementRosterManager verified.")

    # 2. Verify Anchor Resolver
    resolver = StatementPrimaryAnchorResolver()
    item = {
        "person_or_org": "Elon Musk",
        "source_url": "https://www.tesla.com/blog/2026/ai-musk",
        "content": "AI is the future.",
        "trust_level": "MEDIUM"
    }
    allowlist = ["tesla.com", "spacex.com"]
    resolved = resolver.resolve(item, allowlist)
    print(f"Resolved Trust: {resolved['trust_level']}, Confidence: {resolved['anchor_confidence']}")
    assert resolved['trust_level'] == "HARD_FACT", "Should be HARD_FACT for allowlisted domain"
    assert resolved['anchor_confidence'] == 1.0, "Confidence should be 1.0 for allowlisted domain"
    print("✅ StatementPrimaryAnchorResolver verified.")

    # 3. Verify Dedup Engine
    dedup_engine = StatementDedupEngine()
    items = [
        {
            "person_or_org": "Jensen Huang",
            "content": "Blackwell is ramping up.",
            "primary_url": "https://nvidianews.nvidia.com/1",
            "anchor_confidence": 1.0,
            "trust_level": "HARD_FACT",
            "published_at": "2026-02-02T10:00:00"
        },
        {
            "person_or_org": "Jensen Huang",
            "content": "Blackwell is ramping up fast.",
            "primary_url": "https://nvidianews.nvidia.com/1", # Same URL
            "anchor_confidence": 0.8,
            "trust_level": "HARD_FACT",
            "published_at": "2026-02-02T11:00:00"
        }
    ]
    deduped = dedup_engine.dedup(items)
    print(f"Deduped: {len(items)} -> {len(deduped)}, Merged Count: {deduped[0]['merged_count']}")
    assert len(deduped) == 1, "Should merge items with same primary_url"
    assert deduped[0]['merged_count'] == 2, "Merged count should be 2"
    print("✅ StatementDedupEngine verified.")

    # 4. Verify Dashboard Rendering
    renderer = DashboardRenderer()
    quote = TriggerQuote(
        excerpt="The Blackwell GPU is in full production.",
        source_kind="OFFICIAL_STATEMENT",
        source_ref="https://nvidia.com/news/123",
        source_date="2026-02-02",
        anchor_confidence=1.0,
        primary_url="https://nvidia.com/news/123",
        merged_count=3,
        all_sources=["https://nvidia.com/news/123", "https://reuters.com/news/456", "https://bloomberg.com/789"]
    )
    card = DecisionCard(
        topic_id="ISSUE-NVDA-1",
        title="NVIDIA Blackwell Production Ramp",
        status="TRIGGER",
        trigger_quote=quote
    )
    
    html = renderer._render_evidence_summary(card)
    print("Rendered HTML check...")
    assert "[ORIGINAL]" in html, "ORIGINAL badge missing"
    assert "[MERGED x3]" in html, "MERGED badge missing"
    assert "원문 앵커:" in html, "Primary anchor section missing"
    assert "https://nvidia.com/news/123" in html, "Primary URL missing"
    assert "기타 출처 (2개) 보기" in html, "Additional sources toggle missing"
    print("✅ Dashboard rendering verified.")

    print("\n=== IS-94A Verification COMPLETE: SUCCESS ===")

if __name__ == "__main__":
    try:
        verify_is94a()
    except Exception as e:
        print(f"❌ Verification FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
