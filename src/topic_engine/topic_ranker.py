from typing import List, Dict

class TopicRanker:
    """[TASK #101.6] 최종 점수 계산 및 토픽 랭킹 (Production v1.0)"""

    def __init__(self):
        pass

    def rank(self, candidates: List[Dict], evaluations: List[Dict], market_axis: Dict = None) -> Dict:
        # 1. Create lookup for evaluations
        eval_map = {e["candidate_id"]: e for e in evaluations}
        
        primary_axis = market_axis.get("primary_axis") if market_axis else None
        secondary_axis = market_axis.get("secondary_axis") if market_axis else None
        
        scored_candidates = []
        
        # [v12.3 Agnostic Persistence] Load historical topics from committed index
        prev_topics = []
        try:
            index_path = Path("docs/topics/index.json")
            if index_path.exists():
                index_data = json.loads(index_path.read_text(encoding="utf-8"))
                # 최근 3일간의 토픽 제목들을 가져옴
                prev_topics = [item.get("topic", "") for item in index_data[:5]]
        except: pass

        for cand in candidates:
            c_id = cand["candidate_id"]
            ev = eval_map.get(c_id)
            if not ev:
                continue
                
            # Map selection semantics from evaluation
            cand["structure_axis"] = ev.get("structure_axis", cand.get("structure_axis", "unknown"))
            cand["why_now_gate"] = ev.get("why_now_gate", {"passed": False})
            cand["explainability_score"] = ev.get("explainability_score", 0)
            cand["selection_reason"] = ev.get("selection_reason", "")
            cand["tier_decision_reason"] = ev.get("tier_decision_reason", "")
            
            # Formula from TASK #101 Section 6
            det_score = (cand.get("recency_score", 0) + cand.get("evidence_score", 0)) / 2.0
            qual_score = (ev.get("topic_fit_score", 0) + ev.get("market_impact_score", 0)) / 2.0
            
            # [NEW] Hunter's Eye Bonus (Mismatch 가중치)
            mismatch_bonus = 0.3 if cand.get("is_mismatch") else 0.0
            
            # [NEW] Social / Prediction Market Bonus (v11.0)
            social_bonus = 0.0
            if cand.get("candidate_type") in ["SOCIAL", "PRED_MARKET"]:
                social_bonus = 0.4  # 강력한 소셜 우선 가중치 (지표를 압도할 수 있도록)
            
            # [v12.3] Agnostic Fatigue Check (Similarity-based)
            selection_title = cand.get("event", "")
            continuity_penalty = 0.0
            
            for pt in prev_topics:
                # 제목이 50% 이상 겹치거나 포함관계일 경우 페널티 (Agnostic Diversity 강화)
                if pt and (pt in selection_title or selection_title in pt or len(set(pt.split()) & set(selection_title.split())) >= 2):
                    continuity_penalty = 5.0  # 강력한 배제 (v12.5)
                    print(f"  📢 Fatigue Alert: Aggressive continuity penalty (5.0) applied to '{selection_title}'")
                    break
            
            # [v11.0] Balanced Final Score
            final_score = (det_score * 0.4) + (qual_score / 10.0 * 0.4) + mismatch_bonus + social_bonus - continuity_penalty
            
            cand["final_score"] = round(final_score, 4)
            cand["evaluation"] = ev
            scored_candidates.append(cand)
            
        # 2. Sort by score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # 3. Axis Winners (Ensure only 1 MAIN per axis)
        axis_winners = {}
        for cand in scored_candidates:
            axis = cand["structure_axis"]
            if axis not in axis_winners:
                axis_winners[axis] = cand

        # 4. Tier Decision Logic (v3.1 Calibration)
        main_candidate = None
        secondary_candidates = []
        early_candidates = []
        
        # [NEW] Track primary axis candidates for fallback
        primary_axis_candidates = []

        for cand in scored_candidates:
            axis = cand["structure_axis"]
            ev = cand.get("evaluation", {})
            is_mismatch = cand.get("is_mismatch", False)
            
            is_axis_winner = axis_winners.get(axis) == cand
            passed_why_now = cand.get("why_now_gate", {}).get("passed", False)
            
            # [3-1] explainability threshold 완화 (7.0 -> 5.5, Mismatch면 더 완화)
            threshold = 4.5 if is_mismatch else 5.5
            high_explainability = cand.get("explainability_score", 0) >= threshold
            
            # [HUNTER RULE] Market 엔티티 허용 (거시경제 테마 포착용)
            has_specific_entity = cand.get("entity") and cand.get("entity") != ["Market"]
            if is_mismatch or (axis == primary_axis):
                # 모순 상황이거나 주력 축이면 Market 엔티티도 MAIN 자격 부여
                has_specific_entity = True
                
            if not has_specific_entity and ev.get("sector_hints"):
                has_specific_entity = True # Sector level entity fallback
                
            has_market_data = len(cand.get("core_facts", [])) > 0
            
            # [v3.1] 'emerging' 축도 이제 조건만 만족하면 MAIN/SECONDARY 진입 가능
            if axis == "emerging" and not high_explainability:
                if len(early_candidates) < 3:
                    early_candidates.append(cand)
                    cand["tier"] = "EARLY/TIER_3"
                continue

            if axis == primary_axis:
                primary_axis_candidates.append(cand)

            # [RULE] MAIN / TIER_1 (모순이거나 모든 조건을 만족할 때)
            if not main_candidate and axis == primary_axis and is_axis_winner and (passed_why_now or is_mismatch) and high_explainability and has_specific_entity and has_market_data:
                main_candidate = cand
                cand["tier"] = "MAIN/TIER_1"
                if is_mismatch:
                    cand["tier_reason"] = "hunter_mismatch_priority"
                continue
            
            # [RULE] SECONDARY / TIER_2
            is_secondary_axis = (axis == secondary_axis)
            is_weak_primary = (axis == primary_axis and not high_explainability)
            
            if len(secondary_candidates) < 2 and (is_secondary_axis or is_weak_primary or is_mismatch):
                secondary_candidates.append(cand)
                cand["tier"] = "SECONDARY/TIER_2"
                continue
                
            # [RULE] EARLY / TIER_3
            if len(early_candidates) < 3:
                early_candidates.append(cand)
                cand["tier"] = "EARLY/TIER_3"

        # [3-3] MAIN fallback 규칙 추가
        if not main_candidate and primary_axis_candidates:
            # Primary axis 내 최고 점수 1개를 MAIN 강제 승격
            fallback_cand = primary_axis_candidates[0]
            
            # 다른 티어 리스트에서 제거 (중복 방지)
            if fallback_cand in secondary_candidates:
                secondary_candidates.remove(fallback_cand)
            if fallback_cand in early_candidates:
                early_candidates.remove(fallback_cand)
                
            main_candidate = fallback_cand
            main_candidate["tier"] = "MAIN/TIER_1"
            main_candidate["tier_reason"] = "fallback_main"
            print(f"  ⚠️ [Fallback] MAIN forced promotion for: {main_candidate['event']}")

        return {
            "MAIN": main_candidate,
            "SECONDARY": secondary_candidates,
            "EARLY": early_candidates
        }
