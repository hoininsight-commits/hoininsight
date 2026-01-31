from pathlib import Path
import sys
from datetime import datetime
import dataclasses
import json

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.issue_pool import IssuePool
from src.issuesignal.content_pack import ContentPack
from src.issuesignal.dashboard.models import DecisionCard
from src.issuesignal.dashboard.build_dashboard import DashboardBuilder
from src.collectors.fact_evidence_harvester import FactEvidenceHarvester

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
        
    except Exception as e:
        print(f"CRITICAL: IssueSignal Pipeline Failed: {e}")
        sys.exit(1)
    else:
        print("IssueSignal Loop Completed Successfully.")

def main():
    base_dir = Path(".")
    print(f"[{datetime.now()}] Starting IssueSignal Run (Strict Real Mode)...")
    
    # 1. Real Data Harvest
    harvester = FactEvidenceHarvester(base_dir)
    facts = harvester.harvest() # Returns list of facts
    
    decision_card_model = None
    pack_data = None
    
    try:
        if not facts:
            print("No new facts harvested. Generating SILENCE card.")
            # Create SILENT Card
            decision_card_model = DecisionCard(
                topic_id=f"SILENCE-{datetime.now().strftime('%Y%m%d')}",
                title="오늘의 확정 토픽 없음",
                status="SILENT",   # or HOLD/SILENT
                one_liner="수집된 데이터가 없거나 기준에 미달합니다.",
                trigger_type="NO_DATA",
                actor="-",
                must_item="-",
                tickers=[],
                kill_switch="-",
                signature="silence_sig",
                authority_sentence="수집된 데이터 없음.",
                decision_rationale="가용한 외부 데이터 소스(RSS/Official)에서 유의미한 신호가 포착되지 않았습니다."
            )
        else:
            # Pick Top Candidate (Simplest Logic for MVP)
            # Sort by length or keywords if needed, but taking first is fine for 'Real Data' ingestion proof
            candidate_fact = facts[0]
            print(f"Selected Candidate Fact: {candidate_fact['fact_text'][:50]}...")
            
            issue_id = f"ISSUE-{datetime.now().strftime('%Y%m%d')}-001"
            
            # 2. Content Generation (Korean Template)
            from src.issuesignal.capital_rotation.engine import CapitalRotationEngine
            from src.collectors.capital_flow_connector import collect_capital_flows
            from src.collectors.macro_fact_connector import collect_macro_facts
            from src.collectors.official_fact_connector import collect_official_facts
            from src.collectors.corporate_action_connector import collect_corporate_facts
            from src.issuesignal.bottleneck_ranker import BottleneckRanker
            
            # [IS-59] Harvest All Evidence Sources (Expanded)
            ymd = datetime.now().strftime("%Y-%m-%d")
            
            # 1. Flow Hints (RSS)
            flow_evidence = collect_capital_flows(base_dir, ymd)
            # 2. Macro Hard Facts (Yahoo/FRED)
            macro_facts = collect_macro_facts(base_dir, ymd)
            # 3. Official Hard Facts (Gov/Bank RSS Filter)
            official_facts = collect_official_facts(base_dir, ymd)
            # 4. Corporate Hard Facts (SEC 8-K)
            corporate_facts = collect_corporate_facts(base_dir, ymd)
            
            # Combine for Dashboard
            all_evidence = flow_evidence + macro_facts + official_facts + corporate_facts
            
            # [IS-57] Capital Rotation Trigger Layer
            rotation_engine = CapitalRotationEngine(base_dir)
            rotation_verdict = rotation_engine.get_rotation_verdict(ymd)
            
            fact_text = candidate_fact['fact_text']
            source = candidate_fact['source']
            
            # Default One Liner
            one_liner = f"[자동 감지] {fact_text}"
            desc_rationale = "실시간 RSS/Official 데이터에서 감지된 최우선 토픽입니다."
            
            # [IS-59] Trust Integrity Logic (Combinatorial)
            # Base Score
            trust_score = 50
            status_verdict = "HOLD"
            
            # Scoring Components & Checks
            has_hint = len(flow_evidence) > 0
            has_macro = len(macro_facts) > 0
            has_official = len(official_facts) > 0
            has_corporate = len(corporate_facts) > 0
            
            # 1. Rotation (+30)
            if rotation_verdict["triggered"]:
                trust_score += 30
                one_liner = f"[자본 이동] {rotation_verdict['logic_ko']}"
                desc_rationale = f"구조적 신호({rotation_verdict['rule_id']})에 의해 자본 이동이 강제됩니다.\n타겟 섹터: {rotation_verdict['target_sector']}"
            
            # 2. Evidence Scoring
            if has_hint:
                trust_score += 20
                desc_rationale += f"\n\n[증거:FlowHint] 자금 흐름 단서 {len(flow_evidence)}건 포착."

            if has_macro:
                trust_score += 40
                desc_rationale += f"\n\n[증거:Macro] 거시경제 지표 변동 {len(macro_facts)}건 확인."
                
            if has_official:
                trust_score += 40
                desc_rationale += f"\n\n[증거:Official] 공식 기관 발표 {len(official_facts)}건 확인."
                
            if has_corporate:
                trust_score += 45 # Slightly higher than Macro/Official
                desc_rationale += f"\n\n[증거:Corporate] 기업 중요 공시/계약 {len(corporate_facts)}건 확인."

            # Final Gate (IS-59 Upgrade)
            status_verdict = "HOLD"
            
            # Condition 1: High Score (80+) -> Requires at least one Hard Fact
            if trust_score >= 80:
                if has_macro or has_official or has_corporate:
                    status_verdict = "TRUST_LOCKED"
                else:
                    status_verdict = "SPEAKABLE_CANDIDATE" # Backoff if only Rotation+Hint
                    
            elif trust_score >= 60:
                status_verdict = "SPEAKABLE_CANDIDATE"

            # Condition 2: IS-59 Combinatorial Trigger (Corporate + Macro/Official)
            # "CorporateAction STRONG 1 + Macro/Policy STRONG 1 -> TRUST_CHAIN Pass"
            if has_corporate and (has_macro or has_official):
                 status_verdict = "TRUST_LOCKED"
                 desc_rationale += "\n(트리거 발동: 기업 행동 + 거시/정책 교차 검증 완료)"

            # Condition 3: Strict Constitution Backup
            if status_verdict == "TRUST_LOCKED" and not (has_macro or has_official or has_corporate):
                 # Should be caught by Condition 1 logic, but redundancy is safe.
                 status_verdict = "SPEAKABLE_CANDIDATE"

            # Operational Fallback (IS-56)
            # If Candidate + ANY Hard Fact -> Lock (Operational Continuity with legit data)
            if status_verdict == "SPEAKABLE_CANDIDATE" and (has_macro or has_official or has_corporate):
                 status_verdict = "TRUST_LOCKED" 

            long_form = (
                f"# 감지된 신호 분석\n\n"
                f"## 1. 핵심 내용\n"
                f"{fact_text}\n\n"
                f"## 2. 자본 이동 판단 (Rotation)\n"
                f"{desc_rationale}\n\n"
                f"## 3. 대응 코멘트\n"
                f"시장 데이터를 기반으로 분석된 결과입니다. {rotation_verdict.get('target_sector', '-')} 섹터에 대한 비중 확대를 검토하십시오."
            )
            
            pack_data = {
                "id": issue_id,
                "one_liner": one_liner,
                "actor": "Market",
                "must_item": "Topic",
                "time_window": "24h",
                "long_form": long_form,
                "shorts_ready": [f"속보: {fact_text}", "지금 바로 확인하세요.", f"자본이동: {rotation_verdict.get('target_sector', '-')}"],
                "tickers": [],
                "confidence": trust_score
            }
            
            # Content Pack Save
            generator = ContentPack(base_dir)
            generator.generate(pack_data)
            
            # 3. Create Decision Card
            decision_card_model = DecisionCard(
                topic_id=issue_id,
                title=fact_text[:30] + ("..." if len(fact_text)>30 else ""),
                status=status_verdict,
                one_liner=one_liner,
                trigger_type="CAPITAL_ROTATION" if rotation_verdict["triggered"] else "DATA_INGRESS",
                actor="Market",
                must_item="Data",
                tickers=[],
                kill_switch="시장 반응이 예상과 다를 경우 즉시 중단.",
                signature=f"sig_{datetime.now().strftime('%H%M%S')}",
                authority_sentence=one_liner,
                decision_rationale=desc_rationale,
                observed_metrics=[f"Source: {source}", f"Rotation: {rotation_verdict['triggered']}"],
                leader_stocks=[rotation_verdict.get('target_sector', "TBD")],
                risk_factors=["초기 데이터 불확실성"],
                blocks={
                    "capital_rotation": rotation_verdict,
                    "flow_evidence": all_evidence, # [IS-59] Pass ALL Evidence (Flow + Macro + Official + Corporate) to general pool if needed, OR separate.
                    # User requested distinct panel. Let's pass separate lists AND a combined one if useful.
                    # Actually, if I pass 'all_evidence' to 'flow_evidence' key, the existing panel shows them all.
                    # But verifying IS-59-4: "Separate Panel".
                    # So I will pass 'corporate_facts' separately.
                    # And 'flow_evidence' will contain (Flow + Macro + Official).
                    "flow_evidence": flow_evidence + macro_facts + official_facts,
                    "corporate_facts": corporate_facts,
                    # [IS-60] Structural Bottleneck Analysis
                    "bottleneck_analysis": BottleneckRanker.rank_protagonists(corporate_facts)
                } 
            )
            
            # [Fix] Inject Content Package BEFORE saving
            if pack_data:
                decision_card_model.blocks["content_package"] = {
                    "long_form": pack_data.get("long_form", "-"),
                    "shorts_ready": pack_data.get("shorts_ready", []),
                    "text_card": pack_data.get("one_liner", "-")
                }
            
            # Canonical Save
            today_ymd = datetime.now().strftime("%Y-%m-%d")
            y, m, d = today_ymd.split('-')
            canonical_dir = base_dir / "data" / "decision" / y / m / d
            canonical_dir.mkdir(parents=True, exist_ok=True)
            canonical_card_path = canonical_dir / "final_decision_card.json"
            
            with open(canonical_card_path, "w", encoding="utf-8") as cf:
                 card_dict = dataclasses.asdict(decision_card_model)
                 card_dict["card_version"] = "phase50_real_v1"
                 card_dict["_date"] = today_ymd
                 card_dict["_timestamp_kst"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 json.dump(card_dict, cf, ensure_ascii=False, indent=2)

    finally:
        # ALWAYS Run Dashboard Build
        print("[IS-52] Loop Finish - Triggering Dashboard Build")
        run_dashboard_build(base_dir, decision_card_model, pack_data)

if __name__ == "__main__":
    main()
