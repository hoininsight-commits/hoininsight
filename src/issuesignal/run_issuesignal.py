from pathlib import Path
import sys
from datetime import datetime
import dataclasses
import json
import logging

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.issue_pool import IssuePool
from src.issuesignal.content_pack import ContentPack
from src.issuesignal.dashboard.models import DecisionCard
from src.issuesignal.dashboard.build_dashboard import DashboardBuilder
from src.collectors.fact_evidence_harvester import FactEvidenceHarvester
from src.issuesignal.capital_rotation.engine import CapitalRotationEngine
from src.collectors.capital_flow_connector import collect_capital_flows
from src.collectors.macro_fact_connector import collect_macro_facts
from src.collectors.official_fact_connector import collect_official_facts
from src.collectors.corporate_action_connector import collect_corporate_facts
from src.issuesignal.bottleneck_ranker import BottleneckRanker
from src.issuesignal.why_now_synthesizer import WhyNowSynthesizer
from src.issuesignal.script_lock_engine import ScriptLockEngine

def run_dashboard_build(base_dir, decision_card_model=None, pack_data=None):
    # Final: Dashboard Build
    try:
        # Inject Content Package
        if decision_card_model and pack_data:
            pack_content = {
                "long_form": pack_data.get("long_form", "-"),
                "shorts_ready": pack_data.get("shorts_ready", []),
                "text_card": pack_data.get("one_liner", "-")
            }
            decision_card_model.blocks["content_package"] = pack_content

        db_builder = DashboardBuilder(base_dir)
        db_builder.build()
        
        # Generator Index
        from src.issuesignal.index_generator import IssueSignalIndexGenerator
        index_gen = IssueSignalIndexGenerator(base_dir)
        
        cards_for_index = []
        if decision_card_model:
            cards_for_index.append(dataclasses.asdict(decision_card_model))
        
        index_gen.generate(cards_for_index)
        
        # [IS-63] Ensure today.json is overwritten
        if decision_card_model:
            today_json_path = base_dir / "data" / "dashboard" / "today.json"
            today_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(today_json_path, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(decision_card_model), f, ensure_ascii=False, indent=2)
                
    except Exception as e:
        print(f"CRITICAL: Dashboard Build Failed: {e}")
        # sys.exit(1) # Don't exit here, allows main to cleanup if needed, but logging critical

def get_ticker_from_details(details):
    # [IS-62] Minimal Ticker Extraction
    # In real world, logic would map CIK/Company Name to Ticker
    # Here we mock extraction or check for pre-existing ticker field
    return details.get("ticker", None)

def main():
    base_dir = Path(".")
    print(f"[{datetime.now()}] Starting IssueSignal Run (IS-62 Loop Lock)...")
    
    # Init Models to None for safety
    decision_card_model = None
    pack_data = None
    
    try:
        # 1. Harvest Context (Used for filtering and WhyNow)
        ymd = datetime.now().strftime("%Y-%m-%d")
        
        flow_evidence = collect_capital_flows(base_dir, ymd)
        macro_facts = collect_macro_facts(base_dir, ymd)
        official_facts = collect_official_facts(base_dir, ymd)
        corporate_facts = collect_corporate_facts(base_dir, ymd)
        
        all_context = flow_evidence + macro_facts + official_facts
        
        # 2. Rotation Verdict
        rotation_engine = CapitalRotationEngine(base_dir)
        rotation_verdict = rotation_engine.get_rotation_verdict(ymd)
        
        # 3. Candidate Selection (IS-62 Strict Selection)
        # Priority: Protagonists (Score >= 75) > Rotation Trigger > Others
        
        # 3. Candidate Selection (IS-66 Editorial Mode)
        # Rank Top 3
        bottleneck_result = BottleneckRanker.rank_protagonists(corporate_facts)
        ranked_protagonists = bottleneck_result.get('protagonists', [])
        
        # Merge types for consideration (Protagonists + High Grade Corp Facts)
        # For simplicity, we prioritize Protagonists. If < 3, fill with Corp Facts.
        candidates_pool = ranked_protagonists[:]
        for cf in corporate_facts:
             # Avoid duplicates if Corp Fact is already in Protagonist source
             if not any(p['fact_text'] == cf['fact_text'] for p in candidates_pool):
                 candidates_pool.append(cf)
        
        # Take Top 3
        top_candidates = candidates_pool[:3]
        
        editorial_candidates_data = [] # List to store processed candidates
        
        # Process Top Candidates
        processed_candidates = []
        for idx, cand in enumerate(top_candidates):
            # Generate WhyNow if missing
            if not cand.get('why_now'):
                cand['why_now'] = WhyNowSynthesizer.synthesize(
                    cand, 
                    all_context, 
                    rotation_verdict['triggered'], 
                    rotation_verdict.get('target_sector', '-')
                )
            
            # Determine Status
            # Base logic: Protagonist -> High Score. Corp Fact -> Medium.
            is_proto = (cand in ranked_protagonists)
            
            # Score
            score = 50
            if is_proto: score += 40
            if rotation_verdict["triggered"]: score += 20
            if cand.get('details', {}).get('ticker'): score += 10
            
            # Status Decision
            # TRUST_LOCKED: Rank #1 AND Score >= 80 AND Ticker AND WhyNow
            # EDITORIAL_CANDIDATE: HardFact (Implicit in collection) AND WhyNow AND (Proto OR Corp OR Capital)
            
            status = "HOLD"
            if idx == 0 and score >= 80 and cand.get('details', {}).get('ticker') and cand.get('why_now'):
                status = "TRUST_LOCKED"
            elif cand.get('why_now') and (is_proto or len(corporate_facts) > 0 or rotation_verdict["triggered"]):
                # [IS-66] Editorial Candidate Condition
                status = "EDITORIAL_CANDIDATE"
            
            # Generate Script if Eligible
            script_data = None
            if status in ["TRUST_LOCKED", "EDITORIAL_CANDIDATE"]:
                try:
                    script_data = ScriptLockEngine.generate(
                        cand, 
                        cand.get('why_now', '시점 정보 부족'), 
                        rotation_verdict.get('target_sector', '관련 섹터')
                    )
                    cand['generated_script'] = script_data
                except Exception as e:
                    print(f"[Warn] Script Gen Failed for {idx}: {e}")
            
            cand['final_status'] = status
            cand['final_score'] = score
            processed_candidates.append(cand)
            
            # Add to Editorial List for Dashboard
            editorial_candidates_data.append({
                "index": idx,
                "title": cand.get('fact_text', '')[:30],
                "full_text": cand.get('fact_text', ''),
                "status": status,
                "why_now": cand.get('why_now', '-'),
                "script": script_data,
                "score": score
            })

        # Select Primary for DecisionCard (Rank 0)
        selected_candidate = processed_candidates[0] if processed_candidates else None
        
        # 4. Silence Condition (Update logic)
        # If no candidates at all -> Silence
        # If candidates exist, we always make a card, but status might be HOLD.
        
        if not selected_candidate:
             print("[Loop] No valid candidates found. Generating SILENCE.")
             decision_card_model = DecisionCard(
                topic_id=f"SILENCE-{datetime.now().strftime('%Y%m%d')}",
                title="오늘의 확정 토픽 없음",
                status="SILENT",
                one_liner="수집된 데이터가 없거나 기준에 미달합니다.",
                trigger_type="NO_DATA",
                actor="-",
                must_item="-",
                tickers=[],
                kill_switch="-",
                signature="silence_sig",
                authority_sentence="수집된 데이터 없음.",
                decision_rationale="유의미한 시장 신호가 감지되지 않았습니다."
            )
             # Even in silence, add empty editorial list
             decision_card_model.blocks["editorial_candidates"] = []
             
        else:
            # 5. Build Active Card (Based on Rank 0)
            fact_text = selected_candidate.get('fact_text', 'No Text')
            source = selected_candidate.get('source', 'Unknown')
            details = selected_candidate.get('details', {})
            ticker = get_ticker_from_details(details)
            tickers_list = [ticker] if ticker else []
            
            status_verdict = selected_candidate['final_status']
            score_val = selected_candidate['final_score']
            
            # Prepare Script for Rank 0
            long_form = "스크립트 생성 대기중"
            one_liner = "대기"
            shorts_ready = []
            
            if selected_candidate.get('generated_script'):
                s_data = selected_candidate['generated_script']
                long_form = s_data['long_form']
                one_liner = s_data['one_liner']
                shorts_ready = s_data['shorts_ready']
            else:
                # Fallback for HOLD
                long_form = f"## 분석 대기\n{fact_text}"
                one_liner = f"[대기] {fact_text}"

            desc_rationale = f"Rank #1 Selected. Score: {score_val}, Status: {status_verdict}"

            # Pack Data
            pack_data = {
                "id": f"ISSUE-{datetime.now().strftime('%Y%m%d')}-001",
                "one_liner": one_liner,
                "actor": details.get('company', 'Market'),
                "must_item": "Topic",
                "time_window": "24h",
                "long_form": long_form,
                "shorts_ready": shorts_ready,
                "tickers": tickers_list,
                "confidence": score_val
            }
            
            # Save Pack [IS-63]
            generator = ContentPack(base_dir)
            generator.generate(pack_data)
            
            # Build Decision Card
            decision_card_model = DecisionCard(
                topic_id=pack_data['id'],
                title=fact_text[:50],
                status=status_verdict,
                one_liner=one_liner,
                trigger_type="CAPITAL_ROTATION" if rotation_verdict["triggered"] else "DATA",
                actor=details.get('company', 'Market'),
                must_item="Issue",
                tickers=tickers_list,
                kill_switch="즉시 중단 가능",
                signature=f"sig_{datetime.now().strftime('%H%M%S')}",
                authority_sentence=one_liner,
                decision_rationale=desc_rationale,
                observed_metrics=[f"Source: {source}"],
                leader_stocks=[rotation_verdict.get('target_sector', '-')],
                risk_factors=["시장 변동성 확인 필요"],
                blocks={
                     "capital_rotation": rotation_verdict,
                     "flow_evidence": flow_evidence + macro_facts + official_facts,
                     "corporate_facts": corporate_facts, 
                     "all_evidence": all_context + corporate_facts,
                     "bottleneck_analysis": bottleneck_result,
                     "editorial_candidates": editorial_candidates_data # [IS-66] List Injection
                }
            )
            
        # Save Canonical [IS-63] (Moved out of else to handle Silence)
        if decision_card_model:
            today_ymd = datetime.now().strftime("%Y-%m-%d")
            y, m, d = today_ymd.split('-')
            canonical_dir = base_dir / "data" / "decision" / y / m / d
            canonical_dir.mkdir(parents=True, exist_ok=True)
            canonical_card_path = canonical_dir / "final_decision_card.json"
            
            with open(canonical_card_path, "w", encoding="utf-8") as cf:
                 card_dict = dataclasses.asdict(decision_card_model)
                 card_dict["card_version"] = "phase66_editorial_v1"
                 card_dict["_date"] = today_ymd
                 card_dict["_timestamp_kst"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 json.dump(card_dict, cf, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"CRITICAL: IssueSignal Loop Error: {e}")
        # In lock mode, maybe generate SILENCE card here too if nothing exist?
        sys.exit(1)
        
    finally:
        # ALWAYS Run Dashboard Build
        print("[IS-62] Loop Finish - Triggering Dashboard Build")
        run_dashboard_build(base_dir, decision_card_model, pack_data)

if __name__ == "__main__":
    main()
