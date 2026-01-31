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
            
            # [IS-57] Capital Rotation Trigger Layer
            rotation_engine = CapitalRotationEngine(base_dir)
            ymd = datetime.now().strftime("%Y-%m-%d")
            rotation_verdict = rotation_engine.get_rotation_verdict(ymd)
            
            fact_text = candidate_fact['fact_text']
            source = candidate_fact['source']
            
            # Default One Liner
            one_liner = f"[자동 감지] {fact_text}"
            desc_rationale = "실시간 RSS/Official 데이터에서 감지된 최우선 토픽입니다."
            status_verdict = "TRUST_LOCKED"
            
            # [IS-57] Override logic if Rotation Triggered
            if rotation_verdict["triggered"]:
                print(f"[IS-57] Capital Rotation Triggered: {rotation_verdict['rule_id']}")
                one_liner = f"[자본 이동] {rotation_verdict['logic_ko']}"
                desc_rationale = f"구조적 신호({rotation_verdict['rule_id']})에 의해 자본 이동이 강제됩니다.\n타겟 섹터: {rotation_verdict['target_sector']}"
                status_verdict = "TRUST_LOCKED" # Force Speak
            
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
                "confidence": 80 if rotation_verdict["triggered"] else 70
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
                blocks={"capital_rotation": rotation_verdict} # Store full verdict for Dashboard
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
