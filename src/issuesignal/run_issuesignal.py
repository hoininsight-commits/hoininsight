from pathlib import Path
import sys
from datetime import datetime, timezone, timedelta
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
from src.issuesignal.actor_bridge import ActorBridgeEngine
from src.issuesignal.ticker_path_extractor import TickerPathExtractor
from src.issuesignal.editorial_light_engine import EditorialLightEngine
from src.issuesignal.structural_bridge import StructuralBridge
from src.issuesignal.decision_tree import DecisionTree
from src.issuesignal.opening_one_liner import synthesize_opening_one_liner

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

        # [IS-63] Ensure today.json is overwritten BEFORE build
        if decision_card_model:
            today_json_path = base_dir / "data" / "dashboard" / "today.json"
            today_json_path.parent.mkdir(parents=True, exist_ok=True)
            
            card_dict = dataclasses.asdict(decision_card_model)
            
            with open(today_json_path, "w", encoding="utf-8") as f:
                json.dump(card_dict, f, ensure_ascii=False, indent=2)
            
            # [IS-73] Also save to packs directory for DashboardLoader
            packs_dir = base_dir / "data" / "issuesignal" / "packs"
            packs_dir.mkdir(parents=True, exist_ok=True)
            pack_json_path = packs_dir / f"{decision_card_model.topic_id}.json"
            with open(pack_json_path, "w", encoding="utf-8") as f:
                json.dump(card_dict, f, ensure_ascii=False, indent=2)

        db_builder = DashboardBuilder(base_dir)
        db_builder.build()
        
        # Generator Index
        from src.issuesignal.index_generator import IssueSignalIndexGenerator
        index_gen = IssueSignalIndexGenerator(base_dir)
        
        cards_for_index = []
        if decision_card_model:
            cards_for_index.append(dataclasses.asdict(decision_card_model))
        
        index_gen.generate(cards_for_index)
                
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
    now_kst = datetime.now()
    print(f"[{now_kst}] Starting IssueSignal Run (IS-62 Loop Lock - KST Focus)...")
    
    # Init Models to None for safety
    decision_card_model = None
    pack_data = None
    
    try:
        # 1. Harvest Context (Used for filtering and WhyNow)
        # 1. Harvest Context (Used for filtering and WhyNow)
        ymd = now_kst.strftime("%Y-%m-%d")
        
        flow_evidence = collect_capital_flows(base_dir, ymd)
        macro_facts = collect_macro_facts(base_dir, ymd)
        official_facts = collect_official_facts(base_dir, ymd)
        corporate_facts = collect_corporate_facts(base_dir, ymd)
        
        all_context = flow_evidence + macro_facts + official_facts
        
        # 2. Rotation Verdict
        rotation_engine = CapitalRotationEngine(base_dir)
        rotation_verdict = rotation_engine.get_rotation_verdict(ymd)
        
        # [IS-71] Structural Bridge Engine
        bridge_engine = StructuralBridge(base_dir)
        
        # 3. Candidate Selection (IS-62 Strict Selection)
        # Priority: Protagonists (Score >= 75) > Rotation Trigger > Others
        
        # 3. Candidate Selection (IS-66 Editorial Mode)
        # Rank Top 3
        bottleneck_result = BottleneckRanker.rank_protagonists(corporate_facts)
        ranked_protagonists = bottleneck_result.get('protagonists', [])
        
        # Merge types for consideration (Protagonists + High Grade Corp Facts)
        # For simplicity, we prioritize Protagonists. If < 3, fill with Corp Facts.
        candidates_pool = ranked_protagonists[:]
        
        # 3-B. Macro → Actor Bridge (New IS-68 Step)
        macro_candidates = ActorBridgeEngine.bridge(macro_facts)
        candidates_pool.extend(macro_candidates)
        
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
            # IS-72: Initialize Decision Tree Path
            dt_results = {"DA": True} # Data Ingest is PASS if in loop
            
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
            
            # Status Decision (Updated for IS-68 Actor Bridge)
            # TRUST_LOCKED: Rank #1 AND Score >= 80 AND Ticker AND WhyNow
            # EDITORIAL_CANDIDATE: HardFact (Implicit in collection) AND WhyNow AND Actor Confidence >= 70
            
            # Actor details
            actor_type = cand.get('details', {}).get('actor_type', '없음')
            actor_conf = cand.get('details', {}).get('actor_confidence', 0)
            has_ticker = bool(cand.get('details', {}).get('ticker'))

            status = "HOLD"
            # Priority 1: High confidence Structural/Macro with Actor
            if idx == 0 and score >= 80 and (has_ticker or actor_type != '없음') and cand.get('why_now'):
                if actor_type == '없음' or actor_conf >= 70:
                    status = "TRUST_LOCKED"
            
            # Priority 2: Editorial Candidate if it meets quality floor + Actor
            if status == "HOLD":
                if cand.get('why_now') and (is_proto or len(corporate_facts) > 0 or rotation_verdict["triggered"] or cand.get('is_macro_promotion')):
                    # IS-68 Rule: Must have actor with confidence >= 70 for promotion
                    if actor_type != '없음' and actor_conf >= 70:
                        status = "EDITORIAL_CANDIDATE"
                    elif is_proto and not cand.get('is_macro_promotion'):
                        # Keep existing proto promotion for now
                        status = "EDITORIAL_CANDIDATE"
            
            # IS-69: Ticker Path Extraction
            actor_info = {
                "actor_type": actor_type,
                "actor_name_ko": cand.get('details', {}).get('actor_name_ko', '-'),
                "actor_tag": cand.get('details', {}).get('actor_tag', '-')
            }
            ticker_path_result = TickerPathExtractor.extract(actor_info, corporate_facts)
            cand['details']['ticker_path'] = ticker_path_result
            cand['details']['bottleneck_link'] = ticker_path_result.get('global_bottleneck_ko', '-')
            
            # IS-71: Find Structural Bridge
            bridge_info = bridge_engine.find_bridge({
                "actor": cand.get('details', {}).get('actor_name_ko', ''),
                "sector": rotation_verdict.get('target_sector', ''),
                "fact_text": cand.get('fact_text', '')
            })
            cand['details']['bridge_info'] = bridge_info
            
            # Generate Script if Eligible (IS-67 Quality Floor)
            script_data = None
            
            # Floor Check: HARD_FACT >= 1, WHY_NOW exists
            # We count official_facts and corporate_facts as hard facts
            has_hard_fact = len(corporate_facts) > 0 or len(official_facts) > 0
            has_why_now = bool(cand.get('why_now'))
            
            # IS-72: Fill decision results for tree
            dt_results["HF"] = has_hard_fact
            dt_results["WN"] = has_why_now
            dt_results["AM"] = (actor_type != '없음')
            dt_results["QF"] = False # Initial

            if status in ["TRUST_LOCKED", "EDITORIAL_CANDIDATE"]:
                if has_hard_fact and has_why_now:
                    try:
                        script_data = ScriptLockEngine.generate(
                            cand, 
                            cand.get('why_now', '시점 정보 부족'), 
                            rotation_verdict.get('target_sector', '관련 섹터'),
                            all_context + corporate_facts, # Evidence Pool
                            bridge_info=cand['details'].get('bridge_info')
                        )
                        cand['generated_script'] = script_data
                        dt_results["QF"] = True
                    except Exception as e:
                        print(f"[Warn] Script Gen Failed for {idx}: {e}")
                else:
                    status = "HOLD" # Downgrade if floor not met
                    print(f"[Floor] Candidate {idx} rejected: hard_fact={has_hard_fact}, why_now={has_why_now}")
            
            if status in ["TRUST_LOCKED", "EDITORIAL_CANDIDATE"] and not script_data:
                status = "HOLD" # Catch-all for failed script generation
                dt_results["QF"] = False
                print(f"[Floor] Candidate {idx} rejected: Script generation failed or blocked by validation.")
            
            # IS-72: Finalize Tree Data
            cand['decision_tree_data'] = DecisionTree.create_path(dt_results)
            
            if status in ["TRUST_LOCKED", "EDITORIAL_CANDIDATE"]:
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
            else:
                # Add to a bottom 'Reference' pool for reference (HOLD/SILENT)
                # This meets requirement 4 (Silence/Hold candidates in 'Reference' area)
                pass

        # Select Primary for DecisionCard (Rank 0)
        selected_candidate = processed_candidates[0] if processed_candidates else None
        
        # 4. Editorial Rhythm & Light Layer (IS-70)
        rhythm_path = base_dir / "data" / "ops" / "editorial_rhythm.json"
        rhythm_path.parent.mkdir(parents=True, exist_ok=True)
        rhythm_data = {"consecutive_hold_days": 0, "last_editorial_date": ymd}
        if rhythm_path.exists():
            try: rhythm_data = json.loads(rhythm_path.read_text())
            except: pass

        # Check if we have an editorial for today
        has_editorial = len(processed_candidates) > 0
        
        if not has_editorial:
            rhythm_data["consecutive_hold_days"] += 1
        else:
            rhythm_data["consecutive_hold_days"] = 0
            rhythm_data["last_editorial_date"] = ymd

        rhythm_path.write_text(json.dumps(rhythm_data, indent=2))
        
        if not editorial_candidates_data:
             # Check for LIGHT Trigger (3 days HOLD & Non-Neutral Macro)
             is_macro_active = len(macro_facts) > 0 
             if rhythm_data["consecutive_hold_days"] >= 3 and is_macro_active:
                 print(f"[IS-70] Consecutive HOLD ({rhythm_data['consecutive_hold_days']}d) & Macro Active. Triggering LIGHT.")
                 # Use macro_candidates from IS-68 step if available, else generic
                 best_macro = macro_candidates[0]['details'] if macro_candidates else {"actor_name_ko": "시장 구조", "actor_tag": "관찰"}
                 light_data = EditorialLightEngine.generate(best_macro, "Neut")
                 
                 decision_card_model = DecisionCard(
                    topic_id=f"LIGHT-{datetime.now().strftime('%Y%m%d')}",
                    title=light_data["title"],
                    status="EDITORIAL_LIGHT",
                    one_liner=light_data["one_liner"],
                    actor=light_data["actor"],
                    actor_type=light_data["actor_type"],
                    actor_tag=light_data["actor_tag"],
                    authority_sentence=light_data["one_liner"],
                    decision_rationale=light_data["decision_rationale"],
                    blocks={
                        "content_package": {
                            "long_form": light_data["long_form"],
                            "shorts_ready": [],
                            "text_card": light_data["one_liner"]
                        },
                        "ticker_path": light_data["ticker_path"]
                    }
                 )
                 # IS-71: Record the new structure
                 bridge_engine.record_structure({
                     "structure_id": light_data["structure_id"],
                     "summary": light_data["summary"],
                     "actor": light_data["actor"],
                     "sector": rotation_verdict.get('target_sector', ''),
                     "keywords": light_data["keywords"]
                 })
             else:
                 print("[IS-67] No valid candidates passed quality floor. Generating SILENCE.")
                 decision_card_model = DecisionCard(
                    topic_id=f"SILENCE-{datetime.now().strftime('%Y%m%d')}",
                    title="❌ 오늘 발화할 토픽 없음",
                    status="SILENT",
                    one_liner="수집된 데이터가 없거나 운영 품질 하한선(Quality Floor)을 만족하지 못합니다.",
                    trigger_type="NO_DATA",
                    actor="-",
                    must_item="-",
                    tickers=[],
                    kill_switch="-",
                    signature="silence_sig",
                     authority_sentence="수집된 유의미한 데이터 신호 없음.",
                     decision_rationale="사유: 시점(WHY-NOW) 요건 미충족 또는 시장 가격 반영 완료로 인한 발화 실익 부재 (상태: 침묵)"
                 )
             decision_card_model.blocks["editorial_candidates"] = []
             # Reference Area (Hold/Silent candidates)
             decision_card_model.blocks["reference_candidates"] = [c for c in top_candidates if c not in processed_candidates]
             
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
            text_card = "-"
            shorts_15s = "-"
            shorts_30s = "-"
            shorts_45s = "-"

            if selected_candidate.get('generated_script'):
                s_data = selected_candidate['generated_script']
                long_form = s_data['long_form']
                one_liner = s_data['one_liner']
                text_card = s_data.get('text_card', '-')
                shorts_15s = s_data.get('shorts_15s', '-')
                shorts_30s = s_data.get('shorts_30s', '-')
                shorts_45s = s_data.get('shorts_45s', '-')
                shorts_ready = [shorts_15s, shorts_30s, shorts_45s]
            else:
                # Fallback for HOLD
                long_form = f"## 분석 대기\n{fact_text}"
                one_liner = f"[대기] {fact_text}"

            status_map = {"TRUST_LOCKED": "확정", "EDITORIAL_CANDIDATE": "후보", "HOLD": "보류", "SILENT": "침묵"}
            desc_rationale = f"1순위 선정. 점수: {score_val}, 최종 상태: {status_map.get(status_verdict, status_verdict)}"

            # [IS-73] Opening One-Liner
            opening_sentence = synthesize_opening_one_liner(selected_candidate, details.get('decision_tree_data', []))

            # Pack Data
            pack_data = {
                "id": f"ISSUE-{datetime.now().strftime('%Y%m%d')}-001",
                "one_liner": one_liner,
                "opening_sentence": opening_sentence,
                "actor": details.get('actor_name_ko') or details.get('company') or '시장 자본',
                "actor_type": details.get('actor_type', '없음'),
                "actor_tag": details.get('actor_tag', '-'),
                "bottleneck_link": details.get('bottleneck_link', '-'),
                "ticker_path": details.get('ticker_path', {}),
                "bridge_info": details.get('bridge_info'),
                "decision_tree_data": details.get('decision_tree_data', []),
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
                opening_sentence=opening_sentence,
                trigger_type="CAPITAL_ROTATION" if rotation_verdict["triggered"] else "DATA",
                actor=pack_data.get('actor', '-'),
                actor_type=pack_data.get('actor_type', '없음'),
                actor_tag=pack_data.get('actor_tag', '-'),
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
                     "actor_bridge": {
                        "actor_evidence": selected_candidate.get('details', {}).get('actor_evidence', [])
                     },
                     "bottleneck_analysis": bottleneck_result,
                     "editorial_candidates": editorial_candidates_data, # [IS-66] List Injection
                     "content_package": {
                        "long_form": long_form,
                        "shorts_ready": shorts_ready,
                        "shorts_15s": shorts_15s,
                        "shorts_30s": shorts_30s,
                        "shorts_45s": shorts_45s,
                        "one_liner": one_liner,
                        "text_card": text_card
                     }
                }
            )
            
        # Save Canonical [IS-63] (Moved out of else to handle Silence)
        if decision_card_model:
            today_ymd = now_kst.strftime("%Y-%m-%d")
            y, m, d = today_ymd.split('-')
            canonical_dir = base_dir / "data" / "decision" / y / m / d
            canonical_dir.mkdir(parents=True, exist_ok=True)
            canonical_card_path = canonical_dir / "final_decision_card.json"
            
            with open(canonical_card_path, "w", encoding="utf-8") as cf:
                 card_dict = dataclasses.asdict(decision_card_model)
                 card_dict["card_version"] = "phase66_editorial_v1"
                 card_dict["_date"] = today_ymd
                 card_dict["_timestamp_kst"] = now_kst.strftime("%Y-%m-%d %H:%M:%S")
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
