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
from src.issuesignal.trust_lock import TrustLockEngine
from src.issuesignal.proof_pack import ProofPackEngine
from src.issuesignal.dashboard.models import DecisionCard, ProofPack
from src.issuesignal.dashboard.build_dashboard import DashboardBuilder

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
            "long_form": "The official signing of export controls marks an irreversible shift... 자본은 지금 당장 이동해야 한다.",
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

        # 7. Trust Lock (IS-26)
        # Prepare final card for validation
        final_card = {
            "what": pack_data["one_liner"],
            "why": pack_data["long_form"],
            "who": pack_data["actor"],
            "where": pack_data["must_item"],
            "kill_switch": "Any structural change to export control decree."
        }
        
        trust_engine = TrustLockEngine(base_dir)
        # Mock novelty check (is_fact_passed is already from IS-25, mock has_duplicate)
        trust_state, trust_fails, signature = trust_engine.evaluate(final_card, is_fact_passed, has_duplicate=False)
        
        if trust_state != "TRUST_LOCKED":
            print(f"TRUST LOCK BLOCKED: {trust_state}")
            print(f"FAIL CODES: {trust_fails}")
            return

        print(f"TRUST_LOCKED (Signature: {signature})")

        # 8. Proof Pack Enforcement (IS-30)
        # Convert dict to model first for the engine
        decision_card_model = DecisionCard(
            topic_id=issue_id,
            title="Export Control Impact",
            status=trust_state,
            one_liner=pack_data["one_liner"],
            trigger_type="GOV_ACTION",
            actor=pack_data["actor"],
            must_item=pack_data["must_item"],
            tickers=pack_data["tickers"],
            kill_switch=final_card["kill_switch"],
            signature=signature,
            authority_sentence=pack_data.get("one_liner", "-")
        )
        
        # Simulated artifacts for proof
        mock_artifacts = [
            {
                "tickers": ["ASML"],
                "hard_facts": [
                    {
                        "fact_type": "CONTRACT",
                        "fact_claim": "Signed delivery agreement with Intel.",
                        "source_kind": "OFFICIAL_PRESS",
                        "source_ref": "press_asml_001.pdf",
                        "independence_key": "asml_intel_deal"
                    },
                    {
                        "fact_type": "CAPEX",
                        "fact_claim": "Samsung 2026 Capex allocated to EUV.",
                        "source_kind": "EARNINGS_CALL",
                        "source_ref": "samsung_q4_call.json",
                        "independence_key": "samsung_earnings"
                    }
                ]
            }
        ]
        
        proof_engine = ProofPackEngine(base_dir)
        decision_card_model, proof_logs = proof_engine.process_card(decision_card_model, mock_artifacts)
        
        for p_log in proof_logs:
            print(f"PROOFSIGNAL: {p_log}")

        # 9. Content Generation
        # Convert back or use model to save (simulation simplified)
        pack_path = generator.generate(pack_data)
        
        # Save V2 Decision Card (Additive)
        v2_card_path = base_dir / "data" / "issuesignal" / "packs" / f"{issue_id}_v2.json"
        v2_card_path.parent.mkdir(parents=True, exist_ok=True)
        with open(v2_card_path, "w", encoding="utf-8") as v2f:
            import dataclasses
            json.dump(dataclasses.asdict(decision_card_model), v2f, ensure_ascii=False, indent=2)
        
        print(f"Content Pack Ready: {pack_path}")
        print(f"V2 Decision Card: {v2_card_path}")

    # Final: Dashboard Build (IS-27) - Soft fail
    try:
        db_builder = DashboardBuilder(base_dir)
        db_builder.build()
    except Exception as e:
        print(f"WARNING: Dashboard build failed: {e}")
    else:
        print("Signal held or rejected.")

if __name__ == "__main__":
    main()
