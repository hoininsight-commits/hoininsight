import json
import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

def verify_is48_no_topic_reasons():
    print("Testing IS-48: No Topic Reasons...")
    base_dir = Path(".")
    
    # Mock index with 0 topics
    from src.issuesignal.index_generator import IssueSignalIndexGenerator
    gen = IssueSignalIndexGenerator(base_dir)
    gen.generate([
        {"topic_id": "REF_001", "status": "HOLD", "reason_code": "QUOTE_MISSING"},
        {"topic_id": "REF_002", "status": "HOLD", "reason_code": "TRUST_LOCKED_FAIL"}
    ])
    
    # Run renderer (simulated)
    from src.issuesignal.dashboard.loader import DashboardLoader
    from src.issuesignal.dashboard.renderer import DashboardRenderer
    
    loader = DashboardLoader(base_dir)
    summary = loader.load_today_summary("2026-01-30")
    
    renderer = DashboardRenderer()
    html = renderer.render(summary)
    
    if "오늘 확정된 발화 토픽이 없습니다" in html and "QUOTE_MISSING" in html:
        print("✅ Zero-topic alert found in IssueSignal dashboard")
    else:
        print("❌ Zero-topic alert NOT found in IssueSignal dashboard")
        return False
        
    print("✅ No Topic Reasons Logic Passed")
    return True

if __name__ == "__main__":
    import sys
    if verify_is48_no_topic_reasons():
        sys.exit(0)
    else:
        sys.exit(1)
