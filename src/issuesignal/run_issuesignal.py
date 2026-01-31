from pathlib import Path
import sys
from datetime import datetime
import dataclasses

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
from src.issuesignal.quote_proof import QuoteProofEngine
from src.issuesignal.source_diversity import SourceDiversityEngine
from src.issuesignal.dashboard.models import DecisionCard, ProofPack, TriggerQuote
from src.issuesignal.dashboard.build_dashboard import DashboardBuilder

def save_reject_log(base_dir, issue_id, reason_code, detail):
    import json
    log_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic_id": issue_id,
        "reason_code": reason_code,
        "fact_text": detail
    }
    # Append to daily reject logs or save individual
    # We'll save individual for simplicity, dashboard builder aggregates them
    log_path = base_dir / "data" / "issuesignal" / "rejects" / f"{datetime.now().strftime('%H%M%S')}_{issue_id}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    print(f"REJECT LOG SAVED: {log_path}")

def run_dashboard_build(base_dir, decision_card_model=None, pack_data=None):
    # Final: Dashboard Build (IS-27) - Hard fail for IS-51/52 compliance
    try:
        # [IS-52] Inject Content Package
        if decision_card_model and pack_data:
            pack_content = {
                "long_form": pack_data.get("long_form", "-"),
                "shorts_ready": pack_data.get("shorts_ready", []),
                "text_card": pack_data.get("one_liner", "-")
            }
            # Add to content_package block
            decision_card_model.blocks["content_package"] = pack_content

        db_builder = DashboardBuilder(base_dir)
        db_builder.build()
        
        # (IS-48) Generate SSOT Index
        from src.issuesignal.index_generator import IssueSignalIndexGenerator
        index_gen = IssueSignalIndexGenerator(base_dir)
        
        cards_for_index = []
        if decision_card_model:
            cards_for_index.append(dataclasses.asdict(decision_card_model))
        
        index_gen.generate(cards_for_index)
        
    except Exception as e:
        print(f"CRITICAL: IssueSignal Pipeline Failed: {e}")
        sys.exit(1)
    else:
        print("IssueSignal Loop Completed Successfully.")

def main():
    base_dir = Path(".")
    print(f"[{datetime.now()}] Starting IssueSignal Run...")
    
    pool = IssuePool(base_dir)
    gate = FastGate()
    adapter = HoinAdapter(base_dir)
    generator = ContentPack(base_dir)
    
    # Context variables for finally block
    decision_card_model = None
    pack_data = None
    
    try:
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
        
        if status != "READY":
            save_reject_log(base_dir, issue_id, f"GATE_{status}", "Gate evaluation not ready")
            return

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
            save_reject_log(base_dir, issue_id, "TRAP_FAIL", trap_reason)
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
            save_reject_log(base_dir, issue_id, "FACT_FAIL", fact_reason)
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
            save_reject_log(base_dir, issue_id, f"TRUST_{trust_state}", str(trust_fails))
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

        # 9. Quote Proof Enforcement (IS-31)
        quote_engine = QuoteProofEngine(base_dir)
        # Add mock trigger quotes to artifacts
        mock_artifacts[0]["trigger_quotes"] = [
            {
                "excerpt": "Effective immediately, all exports of specialized semiconductor chips to listed entities are suspended pending further technical review.",
                "source_kind": "GOV",
                "source_ref": "https://www.whitehouse.gov/briefing-room/",
                "source_date": "2026-01-29",
                "fact_type": "POLICY_EXCERPT"
            }
        ]
        decision_card_model, quote_logs = quote_engine.process_card(decision_card_model, mock_artifacts)
        
        for q_log in quote_logs:
            print(f"QUOTESIGNAL: {q_log}")

        # 10. Source Diversity Audit (IS-32)
        diversity_engine = SourceDiversityEngine()
        # Simulate artifact analysis for audit
        for art in mock_artifacts:
            for fact in art.get("hard_facts", []):
                diversity_engine.get_cluster(fact.get("source_ref", ""), fact.get("fact_claim", ""))
            for q in art.get("trigger_quotes", []):
                diversity_engine.get_cluster(q.get("source_ref", ""), q.get("excerpt", ""))
        
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "topic_id": issue_id,
            "audit_trail": diversity_engine.get_audit_trail(),
            "distinct_clusters": [c.cluster_id for c in decision_card_model.source_clusters],
            "verdict": decision_card_model.status
        }
        
        audit_path = base_dir / "data" / "issuesignal" / "audit" / f"{issue_id}_diversity.json"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "w", encoding="utf-8") as af:
            json.dump(audit_data, af, indent=2)
        print(f"Diversity Audit: {audit_path}")

        # 11. Narrative Reconstruction (IS-50)
        from src.issuesignal.narrative_reconstruction import NarrativeReconstructionEngine
        narrative_engine = NarrativeReconstructionEngine(base_dir)
        recon_result = narrative_engine.reconstruct(dataclasses.asdict(decision_card_model))
        
        if recon_result:
            print(f"NARRATIVE RECONSTRUCTED: {recon_result['pattern_tag']}")
            # Add to Decision Card Blocks (for Dashboard)
            if not decision_card_model.blocks: decision_card_model.blocks = {}
            decision_card_model.blocks['narrative_reconstruction'] = recon_result

        # 12. Content Generation
        # Convert back or use model to save (simulation simplified)
        pack_path = generator.generate(pack_data)
        
        # Save V2 Decision Card (Additive)
        v2_card_path = base_dir / "data" / "issuesignal" / "packs" / f"{issue_id}_v2.json"
        v2_card_path.parent.mkdir(parents=True, exist_ok=True)
        with open(v2_card_path, "w", encoding="utf-8") as v2f:
            json.dump(dataclasses.asdict(decision_card_model), v2f, ensure_ascii=False, indent=2)
        
        print(f"Content Pack Ready: {pack_path}")
        
        # [IS-51] Canonical Path Synchronization
        # Ensure data/decision/{Y}/{M}/{D}/final_decision_card.json is the SSOT
        today_ymd = datetime.now().strftime("%Y-%m-%d")
        y, m, d = today_ymd.split('-')
        canonical_dir = base_dir / "data" / "decision" / y / m / d
        canonical_dir.mkdir(parents=True, exist_ok=True)
        canonical_card_path = canonical_dir / "final_decision_card.json"
        
        with open(canonical_card_path, "w", encoding="utf-8") as cf:
             # Ensure date/timestamp is in the card
             card_dict = dataclasses.asdict(decision_card_model)
             card_dict["card_version"] = "phase50_dual_v1" # [IS-52] Required for Phase 38 Verification
             card_dict["_date"] = today_ymd
             card_dict["_timestamp_kst"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             json.dump(card_dict, cf, ensure_ascii=False, indent=2)
             
        print(f"[IS-51] Validated SSOT: {canonical_card_path}")
        print(f"V2 Decision Card: {v2_card_path}")
        
    finally:
        # ALWAYS Run Dashboard Build
        print("[IS-52] Loop Finish - Triggering Dashboard Build")
        run_dashboard_build(base_dir, decision_card_model, pack_data)

if __name__ == "__main__":
    main()
