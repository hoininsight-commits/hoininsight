from pathlib import Path
import sys
from datetime import datetime

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.issue_pool import IssuePool
from src.issuesignal.fast_gate import FastGate
from src.issuesignal.hoin_adapter import HoinAdapter
from src.issuesignal.content_pack import ContentPack

def main():
    base_dir = Path(".")
    print(f"[{datetime.now()}] Starting IssueSignal Run...")
    
    pool = IssuePool(base_dir)
    gate = FastGate()
    adapter = HoinAdapter(base_dir)
    generator = ContentPack(base_dir)
    
    # 1. Simulate Issue Capture
    test_signal = {
        "source": "NEWS_API",
        "content": "Official confirmation of new export controls on semiconductor equipment.",
        "metadata": {"market": "GLOBAL"}
    }
    issue_id = pool.add_issue(test_signal)
    print(f"Captured: {issue_id}")
    
    # 2. Gate Evaluation
    with open(base_dir / "data" / "issuesignal" / "pool" / f"{issue_id}.json", "r") as f:
        import json
        issue = json.load(f)
        
    status = gate.evaluate(issue)
    print(f"Gate Status: {status}")
    
    if status == "READY":
        # 3. Adapter Call (Mocking keyword match)
        evidence = adapter.get_structural_evidence("semiconductor")
        
        # 4. Content Generation
        pack_data = {
            "id": issue_id,
            "one_liner": "Export controls freeze chip supply chain.",
            "long_form": "The official signing of export controls marks an irreversible shift in the semiconductor landscape...",
            "shorts_ready": ["New export controls signed.", "Structural bottleneck confirmed.", "Capital forced to move."],
            "tickers": [{"ticker": "ASML", "role": "OWNER", "revenue_focus": 0.95}],
            "confidence": 90
        }
        pack_path = generator.generate(pack_data)
        print(f"Content Pack Ready: {pack_path}")
    else:
        print("Signal held or rejected.")

if __name__ == "__main__":
    main()
