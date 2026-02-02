from pathlib import Path
import sys
from datetime import datetime
import yaml

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.issue_pool import IssuePool
from src.issuesignal.fast_gate import FastGate
from src.issuesignal.hoin_adapter import HoinAdapter
from src.issuesignal.content_pack import ContentPack
from src.issuesignal.content_compiler import ContentCompiler
from src.issuesignal.watchlist.strategic_watchlist_engine import StrategicWatchlistEngine
from src.issuesignal.editorial.watchlist_promotion_engine import WatchlistPromotionEngine
from src.issuesignal.editorial.editorial_tone_selector import EditorialToneSelector
from src.issuesignal.editorial.script_writer_v2 import ScriptWriterV2
from src.issuesignal.narrative.narrative_framing_engine import NarrativeFramingEngine
from src.issuesignal.narrative.urgency_amplifier import UrgencyAmplifierEngine
from src.issuesignal.trap_engine import TrapEngine
from src.issuesignal.fact_verifier import FactVerifier
from src.issuesignal.trust_lock import TrustLockEngine
from src.issuesignal.proof_pack import ProofPackEngine
from src.issuesignal.quote_proof import QuoteProofEngine
from src.issuesignal.source_diversity import SourceDiversityEngine
from src.issuesignal.dashboard.models import DecisionCard, ProofPack, TriggerQuote
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

        # 11. Content Generation
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

        # 12. Create Dashboard-Ready ISSUE-*.json (IS-73)
        # Use ContentCompiler to generate EH-style content
        compiler = ContentCompiler(base_dir)
        eh_path = compiler.compile(pack_data, evidence)
        
        # Load the YAML content generated by ContentCompiler
        with open(eh_path, "r", encoding="utf-8") as f:
            eh_content = yaml.safe_load(f)
        
        # Map fields to Dashboard Schema
        issue_json = {
            "issue_id": issue_id,
            "opening_sentence": eh_content["content"]["headline"], # Map headline to opening_sentence
            "title": eh_content["header"]["title"],
            "status": decision_card_model.status,
            "content_type": "STRUCTURE", # Default for now
            "visual_badges": {
                "fact": "FACT",
                "structure": "STRUCTURE", 
                "preview": "PREVIEW"
            },
            "content_package": {
                "long_form": eh_content["scripts"]["long_form"],
                "shorts": eh_content["scripts"]["shorts"],
                "surface_view": eh_content["content"]["surface_view"],
                "true_why_now": eh_content["content"]["true_why_now"],
                "incompleteness": eh_content["content"]["incompleteness"], 
                "forced_flow": eh_content["content"]["forced_flow"],
                "tickers": eh_content["content"]["bottleneck_tickers"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # [IS-84 Extension] Narrative Framing
        # Must run BEFORE script writer and AFTER opening sentence
        framing_engine = NarrativeFramingEngine(base_dir)
        # Mock main candidate data for framing
        main_candidate_for_framing = {
             "why_now": issue_json["content_package"]["true_why_now"],
             "content_type": "STRUCTURE", # Default for Main Issue
             "status": "TRUST_LOCKED"
        }
        issue_json["narrative_framing"] = framing_engine.generate(main_candidate_for_framing)

        # [IS-85] Urgency Amplifier (Main)
        urgency_engine = UrgencyAmplifierEngine(base_dir)
        issue_json["urgency_sentence"] = urgency_engine.generate(main_candidate_for_framing, tone="WARNING")

        # [IS-84] Script Writer V2 (Main Issue)
        # Determine main tone first (Defaulting for now if Selector not run on Main)
        main_candidate_mock = {
            "tone_type": "STRUCTURAL", "script_mode": "EXPLANATION",
            "title": issue_json["title"],
            "opening_sentence": issue_json["opening_sentence"],
            "reason": issue_json["content_package"]["true_why_now"],
            "category": "MAIN_ISSUE"
        }
        v2_writer = ScriptWriterV2(base_dir)
        v2_package = v2_writer.generate_package(main_candidate_mock)
        issue_json["content_package_v2"] = v2_package
        
        # Save as ISSUE-{id}.json
        issue_path = base_dir / "data" / "issuesignal" / "packs" / f"ISSUE-{issue_id}.json"
        with open(issue_path, "w", encoding="utf-8") as jf:
            json.dump(issue_json, jf, indent=2, ensure_ascii=False)
            
        print(f"Dashboard Issue Pack: {issue_path}")

    # [IS-81] Strategic Watchlist Generation
    try:
        watchlist_engine = StrategicWatchlistEngine(base_dir)
        watchlist_path = watchlist_engine.generate()
        print(f"Strategic Watchlist Ready: {watchlist_path}")
        
        # [IS-82] Watchlist Promotion
        promotion_engine = WatchlistPromotionEngine(base_dir)
        promoted_path = promotion_engine.process(datetime.utcnow().strftime("%Y-%m-%d"))
        print(f"Promoted Candidates Ready: {promoted_path}")

        # [IS-83] Editorial Tone Selection
        if promoted_path:
            # [IS-84 Extension] Narrative Framing for Promoted
            # Load, inject, save
            try:
                import json
                p_data = json.loads(promoted_path.read_text(encoding="utf-8"))
                updates = []
                f_engine = NarrativeFramingEngine(base_dir)
                u_engine = UrgencyAmplifierEngine(base_dir)
                for c in p_data.get("candidates", []):
                    c["narrative_framing"] = f_engine.generate(c)
                    c["urgency_sentence"] = u_engine.generate(c, tone=c.get("tone", "WARNING"))
                    updates.append(c)
                p_data["candidates"] = updates
                with open(promoted_path, "w", encoding="utf-8") as f:
                     json.dump(p_data, f, indent=2, ensure_ascii=False)
                print("Narrative Framing Applied to Candidates.")
            except Exception as e:
                print(f"Narrative Framing Failed: {e}")

            tone_selector = EditorialToneSelector(base_dir)
            tone_selector.process(promoted_path)
            tone_selector.process(promoted_path)
            print(f"Editorial Tone Applied to Candidates.")

            # [IS-84] Script Writer V2 (Promoted Candidates)
            # Reload, generate scripts, save back
            try:
                import json
                p_data = json.loads(promoted_path.read_text(encoding="utf-8"))
                updates = []
                for c in p_data.get("candidates", []):
                    # Only generate if Tone is set (IS-83 should have set it)
                    if "tone_type" in c:
                        # Use same writer instance
                        writer = ScriptWriterV2(base_dir) 
                        script_pkg = writer.generate_package(c)
                        c["content_package_v2"] = script_pkg
                    updates.append(c)
                p_data["candidates"] = updates
                with open(promoted_path, "w", encoding="utf-8") as f:
                    json.dump(p_data, f, indent=2, ensure_ascii=False)
                print(f"Scripts V2 generated for Promoted Candidates.")
            except Exception as e:
                print(f"Failed to generate V2 scripts for candidates: {e}")

    except Exception as e:
        print(f"WARNING: Watchlist/Promotion generation failed: {e}")

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
