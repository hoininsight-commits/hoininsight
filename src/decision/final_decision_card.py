#!/usr/bin/env python3
"""
Phase 38: Final Decision Card Generator
Aggregates Regime, Revival, and Ops context into a single structured card for human decision making.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import re

# Human-readable Title Mapping
ID_TO_TITLE = {
    "struct_dart_disposal": "기업 자산 매각(Disposal) 급증",
    "struct_dart_cb_bw": "전환사채(CB/BW) 발행 폭증",
    "risk_vix_fred": "공포지수(VIX) 이상 급등",
    "metal_gold_paxg_coingecko": "골드(Gold) 가격 이상 변동",
    "rates_us10y_fred": "미국 10년물 국채금리 급변",
    "index_kospi_stooq": "코스피(KOSPI) 지수 충격",
    "fx_usdkrw_ecos": "원달러 환율(USDKRW) 급변",
    "credit_hy_spread_fred": "하이일드 스프레드(Credit Risk) 확대",
    "inflation_kor_cpi_ecos": "한국 소비자물가(CPI) 쇼크",
    "inflation_cpi_fred": "미국 소비자물가(CPI) 충격",
    "inflation_pce_fred": "미국 개인소비지출(PCE) 물가 이상",
    "rates_fed_funds_fred": "연준 기준금리(Fed Funds) 변동",
    "comm_wti_fred": "국제유가(WTI) 급등락",
    "liquidity_m2_fred": "시장 유동성(M2) 위축 감지",
    "derived_yield_curve_10y_2y": "장단기 금리차(Yield Curve) 역전/해소"
}

ID_TO_SUBJECT = {
    "struct_dart_disposal": ("기업 자산 매각 공시", "건"),
    "struct_dart_cb_bw": ("전환사채(CB/BW) 발행", "건"),
    "risk_vix_fred": ("공포지수(VIX)", "배"),
    "metal_gold_paxg_coingecko": ("골드 가격", "배"),
    "rates_us10y_fred": ("미국 10년물 국채금리", "배"),
    "index_kospi_stooq": ("코스피 지수", "배"),
    "fx_usdkrw_ecos": ("원달러 환율", "배"),
    "credit_hy_spread_fred": ("크레딧 스프레드", "배"),
    "inflation_kor_cpi_ecos": ("한국 소비자물가", "배"),
    "inflation_cpi_fred": ("미국 소비자물가", "배"),
    "rates_fed_funds_fred": "연준 기준금리",
    "comm_wti_fred": ("국제유가", "배"),
    "liquidity_m2_fred": ("시장 유동성", "배"),
    "derived_yield_curve_10y_2y": ("장단기 금리차", "배")
}

# Logic Blocks for Oracle Reasoning
LOGIC_BLOCKS = [
    {
        "name": "Risk-Off Wave",
        "requirements": ["RISK_METRICS", "PRECIOUS_METALS", "GLOBAL_INDEX"],
        "min_matches": 2
    },
    {
        "name": "Monetary Tightening",
        "requirements": ["RATES_YIELD", "INFLATION", "FX_RATES"],
        "min_matches": 2
    },
    {
        "name": "Capital Flight (Korea)",
        "requirements": ["FX_RATES", "STRUCTURAL", "KOSPI"],
        "min_matches": 2
    }
]

# Representative Stock Mapping
THEME_STOCKS = {
    "Risk-Off Wave": ["KODEX 200선물인버스2X(곱버스)", "SQQQ", "VIXY"],
    "Monetary Tightening": ["KB금융", "신한지주", "JP모건(JPM)", "골드만삭스(GS)"],
    "Capital Flight (Korea)": ["SK하이닉스", "삼성전자", "현대차"],
    "PRECIOUS_METALS": ["엘컴텍", "KODEX 골드선물", "Newmont(NEM)", "Barrick Gold(GOLD)"],
    "REAL_ESTATE": ["HDC현대산업개발", "GS건설", "D.R. Horton(DHI)"],
    "INFLATION": ["포스코홀딩스", "ExxonMobil(XOM)", "건강기능식품주"]
}

def get_leader_stocks(category: str, logic_block: str = None) -> List[str]:
    stocks = []
    if logic_block and logic_block in THEME_STOCKS:
        stocks.extend(THEME_STOCKS[logic_block])
    if category in THEME_STOCKS:
        stocks.extend(THEME_STOCKS[category])
    
    # Return unique stocks, limit 4
    seen = set()
    unique_stocks = []
    for s in stocks:
        if s not in seen:
            unique_stocks.append(s)
            seen.add(s)
    return unique_stocks[:4]

def humanize_rationale(ds_id: str, text: str, cand: Dict = None) -> str:
    """Generates a natural language explanation based on dataset and anomaly stats."""
    if not text: return "특이사항 없음"
    
    subject_info = ID_TO_SUBJECT.get(ds_id, ("지표", "배"))
    if isinstance(subject_info, tuple):
        subject, unit = subject_info
    else:
        subject, unit = subject_info, "배"

    # Z-Score based Adjectives (v1.12 Statistical Normalization)
    z_match = re.search(r"Z-Score\s+([\d\.]+)", text)
    z_val_float = float(z_match.group(1)) if z_match else 0.0
    
    if z_val_float >= 3.5:
        adj = "폭발적인 충격"
    elif z_val_float >= 2.5:
        adj = "급격한 이상 변동"
    elif z_val_float >= 1.5:
        adj = "유의미한 변화"
    else:
        adj = "우호적/부진한 흐름"

    # Pattern 1: Count (Events)
    count_match = re.search(r"Count=(\d+)", text)
    if count_match:
        cnt = count_match.group(1)
        base_msg = f"{subject}가 오늘 하루 {cnt}{unit} 발생하며 평소보다 {adj} 양상을 보였습니다."
    else:
        # Pattern 2: Z-Score (Volatility)
        if z_match:
            base_msg = f"{subject}가 평소 변동폭 대비 {z_val_float}배(표준편차) 이상 {adj}을(를) 보였습니다."
        else:
            # Fallback
            clean_text = re.sub(r"\[.*?\]", "", text)
            clean_text = re.sub(r"\(Regime.*?\)", "", clean_text)
            clean_text = clean_text.replace("New Event Detected", "신규 이상징후 포착").strip()
            base_msg = f"{subject}에서 {clean_text}."

    # Multi-axis addition
    if cand and cand.get("supporting_evidence"):
        evidence = cand["supporting_evidence"]
        intra = evidence.get("intra_category", [])
        inter = evidence.get("inter_category_axes", [])
        
        # v1.13: Explicitly mention the cluster context
        if cand.get("logic_block_match"):
            logic_name = cand["logic_block_match"]
            base_msg = f"현재 시장은 [{logic_name}] 국면에 진입한 것으로 분석됩니다. " + base_msg
        
        if intra:
            base_msg += f" 특히 동일 섹터인 [{intra[0]}] 등에서도 동시다발적으로 이상 신호가 감지되어 해당 테마의 신뢰도가 매우 높습니다."
        elif inter:
            base_msg += f" 글로벌 시장의 [{inter[0]}] 축과 연동된 움직임으로 해석되며, 이는 시장 전반의 체계적 리스크를 시사합니다."

    # v1.12 Temporal Caution: Avoid 'announcement' unless verified
    if "CPI" in subject or "PCE" in subject:
         base_msg += " (※ 해당 지표 발표 일정에 따른 실질 반응 여부는 추가 검증이 필요합니다.)"

    return base_msg

def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return None

def validate_proof(ds_id: str, cand_meta: Dict) -> Dict[str, Any]:
    """
    v1.13 Proof-First Validation Rule
    Checks if a topic has supporting 'Proof Data' (Sector RS, Budget, etc.)
    """
    evidence = cand_meta.get("supporting_evidence", {})
    intra = evidence.get("intra_category", [])
    inter = evidence.get("inter_category_axes", [])
    
    proof_status = "VALIDATED"
    missing_sensors = []
    
    # Heuristic: Macro themes require at least one intra-category OR inter-category cross-axis match
    # Real v1.13 would check specific datasets like 'rates_us10y_rs'
    if not intra and not inter:
        proof_status = "PROOF_REQUIRED"
        
        # Determine what's missing based on category
        cat = cand_meta.get("category", "OTHER")
        if cat == "RISK_METRICS":
            missing_sensors.append("Sector ETF Relative Strength (RS)")
        elif cat == "INFLATION" or cat == "RATES_YIELD":
            missing_sensors.append("Policy-to-CAPEX Execution Speed (ΔΔ)")
        elif cat == "PRECIOUS_METALS":
            missing_sensors.append("Capital Route Lock-in Index")
            
    return {
        "status": proof_status,
        "missing_sensors": missing_sensors
    }

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    now_utc = datetime.now(timezone.utc)
    ymd_path = now_utc.strftime("%Y/%m/%d")
    ymd_dash = now_utc.strftime("%Y-%m-%d")
    
    # 1. Load Data Sources
    # Regime
    regime_path = base_dir / f"data/regimes/regime_{ymd_dash}.json"
    regime_data = load_json(regime_path) or {}
    
    meta_path = base_dir / "data/meta_topics" / ymd_path / "meta_topics.json"
    meta_topics = load_json(meta_path) or []
    
    # Revival
    rev_base = base_dir / "data/narratives/revival" / ymd_path
    revival_proposals = load_json(rev_base / "revival_proposals.json") or {}
    revival_evidence = load_json(rev_base / "revival_evidence.json") or {}
    revival_loops = load_json(rev_base / "revival_loop_flags.json") or {}
    
    # Ops
    fresh_path = base_dir / "data/ops/freshness" / ymd_path / "freshness_summary.json"
    fresh_data = load_json(fresh_path) or {}
    
    score_path = base_dir / "data/ops/scoreboard" / ymd_path / "ops_scoreboard.json"
    ops_scoreboard = load_json(score_path) or {}

    # Candidates (Phase 39 Output)
    cand_path = base_dir / "data/topics/candidates" / ymd_path / "topic_candidates.json"
    candidates_data = load_json(cand_path)
    candidates = candidates_data.get("candidates", []) if candidates_data else []

    # 2. Build Blocks
    
    # Regime Block
    regime_block = {
        "current_regime": regime_data.get("regime", "Unknown"),
        "confidence": regime_data.get("confidence", 0.0),
        "has_meta_topics": len(meta_topics) > 0,
        "meta_topic_count": len(meta_topics),
        "basis_type": regime_data.get("basis_type", "NONE")
    }

    # Revival Block
    rev_items = revival_proposals.get("items", [])
    revival_block = {
        "proposal_count": len(rev_items),
        "has_revival": len(rev_items) > 0,
        "loop_warning_count": len(revival_loops.get("loop_detected_vids", [])),
        "primary_revival_reason": revival_proposals.get("condition_met", "N/A") if rev_items else "N/A"
    }

    # Ops Block
    ops_block = {
        "system_freshness": fresh_data.get("overall_system_freshness_pct", 0),
        "sla_breach_count": fresh_data.get("sla_breach_count", 0),
        "has_stale_warning": fresh_data.get("sla_breach_count", 0) > 0,
        "7d_success_rate": f"{ops_scoreboard.get('success_count', 0)}/7" if ops_scoreboard else "N/A"
    }

    # 3. Topic Selection Logic (Daily Top 5)
    selected_topic_title = None
    selected_rationale = None
    # [Phase 50] distinct variables
    structural_topic_title = None
    structural_rationale = None
    anchor_topic_title = None
    anchor_rationale = None
    
    key_data = {}
    top_topics = []

    # [Phase 50] Check for Anchor Result first (Economy Hunter Logic)
    anchor_path = base_dir / "data/topics/anchor" / ymd_path / "anchor_result.json"
    if anchor_path.exists():
        try:
            anchor_data = load_json(anchor_path)
            if anchor_data:
                # Convert Anchor format to Card format
                # AnchorResult(anomaly_logic, why_now_type, level, level_proof, gap_detection...)
                logic = anchor_data.get("anomaly_logic", "Unknown")
                why = anchor_data.get("why_now_type", "Unknown")
                proof = anchor_data.get("level_proof", "")
                gap = anchor_data.get("gap_detection", "")
                
                selected_topic_title = f"[{logic}] {why}"
                selected_rationale = f"Anchor Logic: {proof} (Gap Status: {gap})"
                
                # [Phase 50] Capture separate Anchor vars
                anchor_topic_title = selected_topic_title
                anchor_rationale = selected_rationale
                
                # Add strict 6-step details to card
                key_data["ANCHOR"] = {
                    "step1_axis": anchor_data.get("data_axis"),
                    "step6_gap": gap,
                    "request": anchor_data.get("missing_data_request"),
                    "pre_structural": anchor_data.get("pre_structural_context")
                }
                print(f"[Decision] Anchor Result loaded: {selected_topic_title}")
        except Exception as e:
            print(f"[Decision] Failed to load Anchor Result: {e}")

    if candidates:
        scored_candidates = []
        
        for cand in candidates:
            ds_id = cand["dataset_id"]
            topic_file = base_dir / "data/topics" / ymd_path / f"{ds_id}.json"
            t_data_raw = load_json(topic_file)
            
            if t_data_raw:
                # Handle List structure
                t_obj = t_data_raw[0] if isinstance(t_data_raw, list) and len(t_data_raw) > 0 else t_data_raw
                if not isinstance(t_obj, dict): continue

                # Determine level value
                lvl = t_obj.get("anomaly_level")
                if not lvl and "evidence" in t_obj:
                    lvl = t_obj["evidence"].get("level")
                lvl = lvl or "L1"
                
                # Multi-Axis Scoring
                lvl_val = {"L4": 80, "L3": 60, "L2": 40, "L1": 20}.get(lvl, 10)
                
                # Find matching candidate from Gate output
                cand_meta = next((c for c in candidates if c["dataset_id"] == ds_id), {})
                evidence = cand_meta.get("supporting_evidence", {})
                intra_count = len(evidence.get("intra_category", []))
                inter_cats = evidence.get("inter_category_axes", [])
                
                final_score = lvl_val + (intra_count * 15)
                
                # Check Logic Blocks
                my_cat = cand_meta.get("category", "OTHER")
                active_categories = set([my_cat] + inter_cats)
                
                matched_block = None
                for block in LOGIC_BLOCKS:
                    matches = [req for req in block["requirements"] if req in active_categories]
                    if len(matches) >= block["min_matches"]:
                        final_score += 30
                        matched_block = block["name"]
                        break
                
                # Extract Title/Rationale for display
                raw_title = t_obj.get("key_conception") or t_obj.get("topic") or t_obj.get("title") or ""
                
                # Humanize Title and rationale with multi-axis context
                human_title = ID_TO_TITLE.get(ds_id)
                if not human_title:
                   if "/" in raw_title or "\\" in raw_title:
                       fname = Path(raw_title).name.replace(".json", "")
                       human_title = ID_TO_TITLE.get(fname, f"감지된 토픽: {fname}")
                   else:
                       human_title = raw_title if raw_title else "알 수 없는 토픽"

                t_title = human_title
                cand_meta["logic_block_match"] = matched_block
                
                # v1.13: Cluster-First Title Refinement
                if matched_block:
                    # Collect all supporting sensors for the title
                    all_sensors = [ds_id] + evidence.get("intra_category", []) + inter_cats
                    sensor_names = []
                    for s_id in all_sensors[:3]: # Max 3 in title
                        s_name = ID_TO_TITLE.get(s_id, s_id)
                        if isinstance(s_name, tuple): s_name = s_name[0]
                        sensor_names.append(s_name)
                    
                    t_title = f"[{matched_block}] {human_title} 중심의 시장 발작 ({', '.join(sensor_names[1:])} 동반)"
                
                raw_rationale = t_obj.get("why_now") or t_obj.get("rationale") or ""
                t_rationale = humanize_rationale(ds_id, raw_rationale, cand_meta)
                
                # Get relevant stocks
                related_stocks = get_leader_stocks(my_cat, matched_block)
                
                # Calculate Confidence Score (v1.12/13)
                confidence = lvl_val
                if matched_block: confidence += 25  # Increased weight for clusters
                if intra_count > 0: confidence += 15
                # Schedule match placeholder
                confidence = min(100, confidence)

                # v1.13: Proof-First Validation
                proof_result = validate_proof(ds_id, cand_meta)
                p_status = proof_result["status"]
                
                if p_status == "PROOF_REQUIRED":
                    t_title = f"[PROOF_REQUIRED] " + t_title
                    confidence -= 20 # Penalize lack of proof
                
                scored_candidates.append({
                    "dataset_id": ds_id,
                    "level": lvl,
                    "score": final_score,
                    "confidence": max(0, confidence),
                    "proof_status": p_status,
                    "missing_sensors": proof_result["missing_sensors"],
                    "title": t_title,
                    "rationale": t_rationale,
                    "raw_data": t_obj,
                    "logic_block": matched_block,
                    "leader_stocks": related_stocks
                })
        
        # Sort by Score Descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Select Top 5
        top_topics = scored_candidates[:5]
        
        # Set Main Topic
        if top_topics:
            best = top_topics[0]
            selected_topic_title = best["title"]
            selected_rationale = best["rationale"]
            # [Phase 50] Capture for Dual Display
            structural_topic_title = best["title"]
            structural_rationale = best["rationale"]
            
            key_data[best["dataset_id"]] = "Primary"
            
            # Add secondary badges
            for other in top_topics[1:]:
                key_data[other["dataset_id"]] = "Secondary"

    # Fallback if no candidates but maybe Revival exists? 
    # (Existing logic didn't handle this, but adding minimal fallback)
    if not selected_topic_title and revival_block["has_revival"]:
        selected_topic_title = "Narrative Revival"
        selected_rationale = "Past narratives have resurfaced based on recent signals."

    # [Phase 40] Load Narrative Topics
    narrative_dir = base_dir / "data/topics/narrative" / ymd_path
    narrative_path = narrative_dir / "narrative_topics.json"
    narrative_topics = []
    if narrative_path.exists():
        try:
             ndata = json.loads(narrative_path.read_text(encoding="utf-8"))
             narrative_topics = ndata.get("topics", [])
        except: pass

    # Refined Topic Logic: Structural > Narrative > None
    # If no structural topic is selected, but narrative topics exist, we explicitly state that.
    
    if not selected_topic_title and narrative_topics:
        # We DO NOT promote Narrative to 'topic' field (Structural).
        # We leave 'topic' as None or explicit "Waiting for Structural Confirmation"
        # But we can update the rationale.
        selected_topic_title = None # Explicitly None for Structural
        selected_rationale = f"구조적(Structural) 토픽은 발견되지 않았으나, {len(narrative_topics)}개의 내러티브(Narrative) 후보가 감지되었습니다."

    # 4. Construct Final Card
    # 4. Construct Final Card
    card = {
        "card_version": "phase66_editorial_v1",
        "generated_at": now_utc.isoformat() + "Z",
        "date": ymd_dash,
        "blocks": {
            "regime": regime_block,
            "revival": revival_block,
            "ops": ops_block
        },
        "topic": structural_topic_title or anchor_topic_title,  # Legacy fallback
        "structural_topic": structural_topic_title,  # [New] Engine 1
        "anchor_topic": anchor_topic_title,          # [New] Engine 2
        "structural_rationale": structural_rationale,
        "anchor_rationale": anchor_rationale,
        "narrative_topics": narrative_topics,        
        "decision_rationale": structural_rationale,  # Legacy rationale
        "key_data": key_data,
        "top_topics": top_topics,                    # Full Top 5 List
        "human_prompt": "현재 Regime 및 데이터 상태를 고려할 때, 이 주제를 오늘 다룰 가치가 있다고 판단하십니까?"
    }

    # 4. Save
    output_dir = base_dir / "data/decision" / ymd_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. [NEW] Auto-generate Evolution Proposals for missing sensors (v1.13)
    evo_dir = base_dir / "data/evolution/proposals"
    evo_dir.mkdir(parents=True, exist_ok=True)
    
    for top in top_topics:
        if top.get("proof_status") == "PROOF_REQUIRED":
            for sensor in top.get("missing_sensors", []):
                p_id = f"EVO-PROOF-{top['dataset_id']}-{abs(hash(sensor)) % 1000:03d}"
                p_file = evo_dir / f"{p_id}.json"
                if not p_file.exists():
                    p_data = {
                        "id": p_id,
                        "generated_at": now_utc.isoformat(),
                        "category": "DATA_ADD",
                        "status": "PROPOSED",
                        "content": {
                            "condition": sensor,
                            "meaning": f"v1.13 Requirement: Topic [{top['title']}] provides inference but lacks direct proof sensor."
                        }
                    }
                    with open(p_file, "w", encoding="utf-8") as f:
                        json.dump(p_data, f, indent=2, ensure_ascii=False)
                    print(f"  [Evolution] Generated proof-requested extension: {sensor}")

    output_file = output_dir / "final_decision_card.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    print(f"✓ Final Decision Card generated: {output_file}")
    print(f"  - Topic: {selected_topic_title}")
    print(f"  - Rationale: {selected_rationale}")
    print(f"  - Regime: {regime_block['current_regime']} (Conf: {regime_block['confidence']})")
    print(f"  - Revival: {revival_block['proposal_count']} props")
    print(f"  - Ops: {ops_block['system_freshness']}% freshness")

if __name__ == "__main__":
    main()
