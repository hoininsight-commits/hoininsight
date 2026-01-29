from pathlib import Path
import sys
from datetime import datetime

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.issue_pool import IssuePool
from src.issuesignal.fast_gate import FastGate
from src.issuesignal.hoin_adapter import HoinAdapter
from src.issuesignal.content_pack import ContentPack
from src.issuesignal.trap_engine import TrapEngine
from src.issuesignal.fact_verifier import FactVerifier

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
        # 3. Adapter Call
        evidence = adapter.get_structural_evidence("semiconductor")
        # Mock evidence if empty for simulation
        if not evidence:
            evidence = {
                "evidence": [
                    {"type": "STRONG", "desc": "Confirmed factory expansion orders."}
                ]
            }
        
        # 4. Content Prep
        pack_data = {
            "id": issue_id,
            "one_liner": "Export controls freeze chip supply chain.",
            "actor": "GOV",
            "must_item": "EUV_STEPPER",
            "time_window": "2w",
            "entry_latency": 1,
            "exit_shock": 2,
            "long_form": "The official signing of export controls marks an irreversible shift...",
            "shorts_ready": ["New export controls signed."],
            "tickers": [{"ticker": "ASML", "role": "OWNER", "revenue_focus": 0.95}],
            "confidence": 90
        }

        # 5. Trap Detection (IS-24)
        trap_engine = TrapEngine(base_dir)
        is_trap_passed, trap_reason, trap_debug = trap_engine.evaluate(pack_data, evidence)
        
        if not is_trap_passed:
            print(f"REJECTED BY TRAP ENGINE: {trap_reason}")
            print(f"DEBUG: {trap_debug}")
            return

        # 6. Fact Verification (IS-25)
        # Enhance evidence with source types for verification
        evidence_pack = {
            "evidence": [
                {"text": "Confirmed factory expansion orders.", "source_type": "COMPANY_FILINGS", "is_original": True},
                {"text": "Government subsidy audit report.", "source_type": "GOV_DOC", "is_original": True}
            ]
        }
        
        fact_verifier = FactVerifier(base_dir)
        is_fact_passed, fact_reason, fact_debug = fact_verifier.verify(pack_data, evidence_pack)
        
        if not is_fact_passed:
            print(f"REJECTED BY FACT VERIFIER: {fact_reason}")
            print(f"DEBUG: {fact_debug}")
            return

        # 7. Content Generation
        pack_path = generator.generate(pack_data)
        print(f"Content Pack Ready: {pack_path}")
    else:
        print("Signal held or rejected.")

if __name__ == "__main__":
    main()
