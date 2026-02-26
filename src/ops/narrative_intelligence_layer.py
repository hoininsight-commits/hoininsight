import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class NarrativeIntelligenceLayer:
    """
    PHASE 12.7: Conflict & Tension Layer v1.0
    Detects structural conflict, expectation gaps, and tension signals.
    Extends TopicV2 to TopicV3.
    """
    
    TIER_1_ACTORS = [
        "FEDERAL RESERVE", "FED", "연준", "IMF", "BIS", "ECB", "BOJ", "PBOC", "중앙은행", "CENTRAL BANK", 
        "G7", "G20", "정부", "TREASURY", "WHITE HOUSE", "백악관", "국가안보회의", "NSC"
    ]
    TIER_2_ACTORS = [
        "BIG TECH", "빅테크", "APPLE", "MICROSOFT", "GOOGLE", "AMAZON", "META", "NVIDIA", "TSMC", "ASML", 
        "INTEL", "SAMSUNG", "삼성전자", "SK HYNIX", "SK하이닉스", "JPMORGAN", "GS", "GOLDMAN SACHS", 
        "HSBC", "BOFA", "CITI", "BLACKROCK", "VANGUARD", "SOVEREIGN WEALTH FUND", "국민연금", "NPS", 
        "SOFTBANK", "ARM", "OPENAI"
    ]
    TIER_3_ACTORS = [
        "MINISTRY", "기획재정부", "기재부", "금융위원회", "금융위", "금융감독원", "금감원", "한국은행", "BOK",
        "산업통상자원부", "국토교통부", "HYUNDAI", "현대차", "SK", "LG", "POSCO", "포스코", "TOYOTA", 
        "BERKSHIRE", "TESLA", "테슬라"
    ]
    TIER_4_ACTORS = [
        "CORPORATION", "COMPANY", "기업", "업체", "STARTUP", "벤처", "공장", "FACTORY", "MARKET"
    ]

    AXES_KEYWORDS = {
        "Policy": ["POLICY", "정책", "규제", "DECREE", "GOV", "MANDATE", "STANDARD", "FED FUNDS", "RATE"],
        "Capital Flow": ["FLOW", "자본", "수급", "유입", "CAPITAL", "LIQUIDITY", "ROTATION", "INFLOW", "OUTFLOW"],
        "Supply Chain": ["CHAIN", "SUPPLY", "공급망", "물류", "SEMICONDUCTOR", "CHIP", "PRODUCTION"],
        "Structural Capital": ["STRUCTURAL", "구조적", "ASSET", "CAPITAL", "EQUITY", "BALANCE SHEET"],
        "Liquidity": ["LIQUIDITY", "유동성", "M2", "MONEY", "CASH", "CREDIT"],
        "Geopolitical": ["GEOPOLITICAL", "지정학", "WAR", "군사", "TENSION", "CONFLICT", "SANCTION"]
    }

    # Conflict Pattern Keywords
    CONFLICT_KEYWORDS = {
        "Tightening": ["TIGHTENING", "HAWKISH", "RATE HIKE", "금리 인상", "긴축", "FED FUNDS", "RATES"],
        "Easing": ["EASING", "DOVISH", "RATE CUT", "금리 인하", "완화"],
        "Inflow": ["INFLOW", "유입", "매수", "BUY", "SURGE", "INFLOWS"],
        "Drain": ["DRAIN", "OUTFLOW", "유출", "매도", "SELL", "DROP", "DISPOSAL"],
        "SupplyExp": ["SUPPLY EXPANSION", "생산 확대", "증설", "CAPEX", "CHAIN"],
        "DemandWeak": ["DEMAND WEAKNESS", "수요 둔화", "부진", "WEAK"],
        "StrongEarnings": ["EARNINGS SURPRISE", "어닝 서프라이즈", "실적 호조", "PROFIT"],
        "PriceDecline": ["PRICE DECLINE", "하락", "폭락", "CRASH", "BEAR", "DISPOSAL"],
        "RegPressure": ["REGULATION", "규제", "압박", "제재", "BAN", "MANDATE", "FORCING", "COMPLY", "STANDARD"],
        "InvSurge": ["INVESTMENT", "투자", "유치", "유입", "FUNDING"],
        "GeoRisk": ["WAR", "CONFLICT", "전쟁", "분쟁", "RISK", "TENSION", "VIX"],
        "AssetRally": ["RALLY", "상승", "급등", "BULL", "SURGE", "RECOVERY"],
        "MacroEvent": ["FOMC", "PPI", "CPI", "GDP", "EMPLOYMENT", "지표", "발표", "지수", "INDEX", "DATA", "MEETING", "MINUTES", "FRED", "ECOS", "DART", "STOOQ"]
    }

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger("NarrativeIntelligenceLayer")
        self.ymd = datetime.now().strftime("%Y-%m-%d")
        self.diagnostics = []
        self.context_pack_enabled = True

    def _inject_context_pack(self, card: Dict, all_cards: List[Dict]) -> str:
        """
        [Phase 16A] Narrative Density Injection v1.0
        Enriches rationale_natural with Observed/Expectation/Deviation blocks 
        to trigger conflict detection without formula changes.
        """
        title = self._normalize_text(card.get("title", ""))
        rationale = self._normalize_text(card.get("rationale_natural", ""))
        full_text = title + " " + rationale
        
        # 1. Identify Primary Observed Signal
        obs = "N/A"
        target_axis = "Unknown"
        for axis, kws in self.AXES_KEYWORDS.items():
            if any(kw in full_text for kw in kws):
                obs = axis
                target_axis = axis
                break
        
        # 2. Define Deterministic Expectation (Market Norms)
        # Mapping: If X happens, Y is normally expected.
        expectations = {
            "Policy": ("Capital Flow", "INFLOW"),      # Rate hike -> Inflow
            "Capital Flow": ("Liquidity", "CASH"),     # Inflow -> Liquidity update
            "Geopolitical": ("Structural Capital", "ASSET RALLY"), # Geo stability -> Rally (or Tension -> Safe Haven)
            "Supply Chain": ("Structural Capital", "PRODUCTION"),
            "Liquidity": ("Capital Flow", "ROTATION"),
            "Structural Capital": ("Policy", "GOV")
        }
        
        exp_axis, exp_keyword = expectations.get(target_axis, ("N/A", "N/A"))
        
        # 3. Find Deviation via Pattern-Mirroring (Phase 16A refinement)
        dev = "N/A (insufficient evidence)"
        
        # Define patterns that the detector looks for
        mirror_logic = [
            (["Tightening"], ["Inflow", "AssetRally"]), # Tightening vs Rally
            (["Easing"], ["Drain", "PriceDecline"]),   # Easing vs Price Drop
            (["SupplyExp"], ["DemandWeak", "PriceDecline"]),
            (["StrongEarnings"], ["PriceDecline"]),
            (["RegPressure"], ["InvSurge", "AssetRally"]),
            (["GeoRisk"], ["AssetRally"]),
            (["MacroEvent"], ["PriceDecline", "AssetRally", "Drain"])
        ]
        
        # Helper to check if a card matches ANY keyword in a list of sets
        def matches_sets(t_norm, sets):
            return any(any(kw in t_norm for kw in self.CONFLICT_KEYWORDS[s]) for s in sets)

        for my_sets, mirror_sets in mirror_logic:
            if matches_sets(full_text, my_sets):
                # Search ALL cards (including current one for self-contained conflict, 
                # but focus on others for "density injection")
                for other in all_cards:
                    if other.get("topic_id") == card.get("topic_id"): continue
                    otext = self._normalize_text(other.get("title", "") + " " + other.get("rationale_natural", ""))
                    
                    if matches_sets(otext, mirror_sets):
                        # Find the specific keyword for the report
                        found_kw = "SIGNAL"
                        for s in mirror_sets:
                            for kw in self.CONFLICT_KEYWORDS[s]:
                                if kw in otext: 
                                    found_kw = kw
                                    break
                            if found_kw != "SIGNAL": break
                        
                        dev = f"Friction detected: related signal shows divergent {found_kw} on {mirror_sets} axes."
                        break
                if dev != "N/A (insufficient evidence)": break

        context_block = (
            "\n\n[CONTEXT PACK v1.0]\n"
            f"A) Observed: Primary signal detected in {target_axis} axis.\n"
            f"B) Expectation: Based on {target_axis}, monitoring for divergent {exp_keyword} signals.\n"
            f"C) Deviation: {dev}"
        )
        return context_block

    def _normalize_text(self, text: str) -> str:
        """
        [Phase 15] Universal Text Normalization for Detection
        - Hand-Eng mixed normalization
        - Strip special characters
        - Normalize case
        """
        if not text: return ""
        import re
        # Remove special characters except common separators
        text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text.upper()

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to load {path}: {e}")
            return None

    def _save_json(self, path: Path, data: Any):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def _get_actor_tier_score(self, card: Dict) -> float:
        text = str(card.get("title", "")) + " " + str(card.get("rationale_natural", "")) + " " + str(card.get("why_now_summary", ""))
        text_norm = self._normalize_text(text)
        
        matches = []
        score = 0.0
        
        tier_map = [
            (self.TIER_1_ACTORS, 1.00, "TIER_1"),
            (self.TIER_2_ACTORS, 0.90, "TIER_2"),
            (self.TIER_3_ACTORS, 0.75, "TIER_3"),
            (self.TIER_4_ACTORS, 0.55, "TIER_4")
        ]
        
        for actor_list, tier_score, tier_label in tier_map:
            for actor in actor_list:
                if actor in text_norm:
                    matches.append(f"{tier_label}:{actor}")
                    score = max(score, tier_score)
                    # Don't break, find all for diagnostics
        
        card["_diag_actor_matches"] = matches
        return score

    def _get_cross_axis_metrics(self, card: Dict) -> Tuple[int, float]:
        text = str(card.get("title", "")) + " " + str(card.get("rationale_natural", ""))
        text_norm = self._normalize_text(text)
        
        count = 0
        matches = []
        for axis, keywords in self.AXES_KEYWORDS.items():
            matched_kws = [kw for kw in keywords if kw in text_norm]
            if matched_kws:
                count += 1
                matches.append(f"{axis}:{matched_kws[0]}")
        
        multiplier = 1.0
        if count >= 3:
            multiplier = 1.15
        elif count >= 2:
            multiplier = 1.08
            
        card["_diag_axis_matches"] = matches
        return count, multiplier

    def _get_history(self, dataset_id: str) -> List[Dict]:
        history_path = self.base_dir / "data/ops/ps_history.json"
        if not history_path.exists():
            return []
        try:
            history = json.loads(history_path.read_text(encoding='utf-8'))
            matches = [h for h in history if h.get("dataset_id") == dataset_id]
            matches.sort(key=lambda x: x.get("ts_utc", ""), reverse=True)
            return matches
        except:
            return []

    def _check_escalation(self, card: Dict, matches: List[Dict]) -> bool:
        intensity = float(card.get("intensity", 0))
        if not matches:
            return False
            
        # Rule 1: intensity increase for 2 consecutive days
        if len(matches) >= 2:
            recent_intensities = [float(matches[0].get("intensity", 0)), float(matches[1].get("intensity", 0))]
            if intensity > recent_intensities[0] > recent_intensities[1]:
                return True
        
        # Rule 2: persistence >= 3 days
        if len(matches) >= 3:
            return True
            
        # Rule 3: intensity delta >= +10 from prior occurrence
        if len(matches) >= 1:
            if intensity >= (float(matches[0].get("intensity", 0)) + 10):
                return True
                    
        return False

    def _detect_conflict(self, card: Dict, matches: List[Dict], is_escalated: bool) -> bool:
        text = str(card.get("title", "")) + " " + str(card.get("rationale_natural", ""))
        text_norm = self._normalize_text(text)
        intensity = float(card.get("intensity", 50))
        
        def has(keys): return any(k in text_norm for k in self.CONFLICT_KEYWORDS[keys])

        patterns = {
            "Tightening_Inflow": has("Tightening") and has("Inflow"),
            "Easing_Drain": has("Easing") and has("Drain"),
            "Supply_Demand_Gap": has("SupplyExp") and has("DemandWeak"),
            "Earnings_Price_Conflict": has("StrongEarnings") and has("PriceDecline"),
            "Policy_Inv_Tension": has("RegPressure") and has("InvSurge"),
            "GeoRisk_Rally": has("GeoRisk") and has("AssetRally"),
            "Macro_Price_Divergence": has("MacroEvent") and (has("PriceDecline") or has("AssetRally"))
        }
        
        # 8. High Persistence (count >= 3) + Sudden Intensity Drop (delta <= -15)
        if len(matches) >= 3:
            last_intensity = float(matches[0].get("intensity", 0))
            if intensity <= (last_intensity - 15):
                patterns["Persistence_Drop"] = True
                
        # 9. Low Intensity + Escalation Flag True
        if intensity < 50 and is_escalated:
            patterns["Escalation_Low_Intensity"] = True
            
        matched_patterns = [k for k, v in patterns.items() if v]
        card["_diag_conflict_patterns"] = matched_patterns
        return any(patterns.values())

    def _get_expectation_gap(self, card: Dict, matches: List[Dict], n_score_jump: float) -> Tuple[int, str]:
        intensity = float(card.get("intensity", 50))
        
        # Calculate scores
        gap_score = 0
        
        if matches:
            # delta from 7-day avg (if history long enough)
            recent_i = [float(m.get("intensity", 0)) for m in matches[:7]]
            avg_i = sum(recent_i) / len(recent_i)
            if abs(intensity - avg_i) >= 15: gap_score += 2
            
            # jump >= +12
            if intensity >= (float(matches[0].get("intensity", 0)) + 12): gap_score += 2
            
            # persistence >= 3 with sudden shift (delta >= 10 in either direction)
            if len(matches) >= 3 and abs(intensity - float(matches[0].get("intensity", 0))) >= 10:
                gap_score += 2
                
        # n_score_jump >= +10
        if n_score_jump >= 10: gap_score += 1
        
        level = "none"
        if gap_score >= 6: level = "strong"
        elif gap_score >= 3: level = "moderate"
        
        return gap_score, level

    def process_topics(self):
        self.logger.info(f"Running Narrative Intelligence Phase 15 for {self.ymd}...")
        
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        if not data or not data.get("cards"):
            self.logger.warning("No IssueSignal cards found.")
            return

        v3_topics = []
        
        # [Phase 17] authoritative intensity sync
        decision_path = self.base_dir / f"data/decision/{self.ymd.replace('-', '/')}/final_decision_card.json"
        decision_data = self._load_json(decision_path)
        score_map = {}
        if decision_data and "top_topics" in decision_data:
            for t in decision_data["top_topics"]:
                ds_id = t.get("dataset_id")
                if ds_id:
                    score_map[ds_id] = float(t.get("score", 0))

        for card in data["cards"]:
            ds_id = card.get("dataset_id", "")
            intensity = float(card.get("intensity", 50))
            
            # [Phase 17] Link to final engine score (100/85) for calculation parity
            if ds_id in score_map:
                intensity = score_map[ds_id]

            matches = self._get_history(ds_id)
            
            # --- PHASE 16A: Narrative Density Injection ---
            if self.context_pack_enabled:
                context_block = self._inject_context_pack(card, data["cards"])
                card["rationale_natural"] = card.get("rationale_natural", "") + context_block

            # --- Base Metrics (PHASE 12.5) ---
            actor_tier_score = self._get_actor_tier_score(card)
            axis_count, axis_multiplier = self._get_cross_axis_metrics(card)
            is_escalated = self._check_escalation(card, matches)
            escalation_bonus = 5.0 if is_escalated else 0.0
            
            # Derived factors
            actor_weight_score = actor_tier_score * 100.0
            # Use normalized text for these checks too
            text_norm = self._normalize_text(str(card.get("title", "")) + " " + str(card.get("rationale_natural", "")))
            flow_score = 100.0 if any(kw in text_norm for kw in ["FLOW", "자본", "수급", "유입", "CAPITAL", "LIQUIDITY", "ROTATION"]) else 0.0
            policy_score = 100.0 if any(kw in text_norm for kw in ["POLICY", "정책", "규제", "금리", "RATE", "SHIFT", "DECREE"]) else 0.0
            persistence_score = 100.0 if is_escalated else 0.0
            
            base_weighted_sum = (
                0.28 * intensity +
                0.22 * actor_weight_score +
                0.18 * flow_score +
                0.17 * policy_score +
                0.15 * persistence_score
            )
            
            last_n_score = float(matches[0].get("narrative_score", 0)) if matches else 0.0
            pre_multiplier_score = (base_weighted_sum * axis_multiplier) + escalation_bonus
            n_score_jump = pre_multiplier_score - last_n_score if matches else 0.0

            # --- PHASE 12.7 Scopes ---
            conflict_flag = self._detect_conflict(card, matches, is_escalated)
            gap_score, gap_level = self._get_expectation_gap(card, matches, n_score_jump)
            
            tension_mult = 1.12 if conflict_flag else 1.0
            final_n_score = pre_multiplier_score * tension_mult
            if gap_level == "strong":
                final_n_score += 4.0
            
            final_n_score = round(min(100.0, max(0.0, final_n_score)), 2)

            video_ready = (
                (final_n_score >= 80 and actor_tier_score >= 0.75) or
                (conflict_flag == True and final_n_score >= 75) or
                (is_escalated == True and gap_level != "none")
            )

            # --- Output Construction (v3.0) ---
            v3_topic = card.copy()
            v3_topic.update({
                "narrative_score": pre_multiplier_score,
                "final_narrative_score": final_n_score,
                "video_ready": video_ready,
                "actor_tier_score": actor_tier_score,
                "structural_actor_score": actor_weight_score, # For baseline reporting
                "capital_flow_score": flow_score,
                "policy_score": policy_score,
                "cross_axis_count": axis_count,
                "cross_axis_multiplier": axis_multiplier,
                "escalation_flag": is_escalated,
                "conflict_flag": conflict_flag,
                "expectation_gap_score": gap_score,
                "expectation_gap_level": gap_level,
                "tension_multiplier_applied": tension_mult > 1.0 or gap_level == "strong",
                "causal_chain": {
                    "cause": card.get("why_now_summary", None),
                    "structural_shift": card.get("structure_type", None),
                    "market_consequence": "Derived from final_n_score" if final_n_score > 70 else "Monitoring friction",
                    "affected_sector": card.get("title", None),
                    "time_pressure": "high" if intensity >= 80 else "medium" if intensity >= 60 else "low"
                },
                "summary_3_line": self._generate_3_line_summary(v3_topic),
                "schema_version": "v3.0"
            })
            v3_topics.append(v3_topic)
            self._capture_diagnostics(v3_topic)

        # Save Results
        out_data = {
            "date": self.ymd,
            "total_topics": len(v3_topics),
            "video_ready_count": len([t for t in v3_topics if t["video_ready"]]),
            "topics": v3_topics
        }
        
        v3_topics_path = self.base_dir / "data/ops/narrative_intelligence_v2.json"
        self._save_json(v3_topics_path, out_data)
        
        # Phase 15: Video Candidate Pool
        video_candidates = [
            t for t in v3_topics 
            if t.get("final_narrative_score", 0) >= 60 
            and t.get("actor_tier_score", 0) > 0 
            and t.get("cross_axis_multiplier", 1.0) > 1.0
        ]
        video_pool_path = self.base_dir / "data_outputs/ops/video_candidate_pool.json"
        self._save_json(video_pool_path, {
            "date": self.ymd,
            "count": len(video_candidates),
            "candidates": video_candidates
        })
        
        self.save_diagnostics()
        self.logger.info(f"Narrative Intelligence Phase 15 completed. {out_data['video_ready_count']} Video Ready, {len(video_candidates)} Video Candidates.")

    def _generate_3_line_summary(self, topic: Dict) -> str:
        """[Phase 15] 3-line summary enforcement"""
        struct = topic.get("structure_type", "N/A")
        axes = ", ".join(topic.get("_diag_axis_matches", ["N/A"]))
        actors = ", ".join(topic.get("_diag_actor_matches", ["N/A"]))
        
        line1 = f"구조적 원인: {struct} 감지 ({axes})"
        line2 = f"자본 흐름 영향: {actors} 중심의 시장 반응 및 지표 변동"
        line3 = f"리스크 포인트: {topic.get('evidence_refs', {}).get('risk_factor', '데이터 기반 모니터링 필요')}"
        
        return f"{line1}\n{line2}\n{line3}"

    def _capture_diagnostics(self, topic: Dict):
        self.diagnostics.append({
            "title": topic.get("title"),
            "actor_matches": topic.get("_diag_actor_matches"),
            "axis_matches": topic.get("_diag_axis_matches"),
            "conflict_patterns": topic.get("_diag_conflict_patterns"),
            "n_score": topic.get("final_narrative_score")
        })

    def save_diagnostics(self):
        diag_path = self.base_dir / "data_outputs/ops/phase15_detection_diagnostics.md"
        content = "# Phase 15 Detection Diagnostics\n\n"
        for d in self.diagnostics:
            content += f"## Topic: {d['title']}\n"
            content += f"- **Actors**: {', '.join(d['actor_matches']) if d['actor_matches'] else 'None'}\n"
            content += f"- **Axes**: {', '.join(d['axis_matches']) if d['axis_matches'] else 'None'}\n"
            content += f"- **Conflict**: {', '.join(d['conflict_patterns']) if d['conflict_patterns'] else 'None'}\n"
            content += f"- **Final Score**: {d['n_score']}\n\n"
        
        diag_path.parent.mkdir(parents=True, exist_ok=True)
        diag_path.write_text(content, encoding='utf-8')

    def run_conflict_trace(self, count=10):
        """[Phase 15] 3️⃣ Conflict / Escalation 상세 추적 및 로그 생성"""
        issues_path = self.base_dir / "data/ops/issuesignal_today.json"
        data = self._load_json(issues_path)
        if not data or not data.get("cards"): return
        
        trace_path = self.base_dir / "data_outputs/ops/phase15_conflict_trace.md"
        content = "# Phase 15 Conflict Trace Report\n\n"
        
        samples = data["cards"][:count]
        for i, card in enumerate(samples):
            matches = self._get_history(card.get("dataset_id", ""))
            is_escalated = self._check_escalation(card, matches)
            
            text_norm = self._normalize_text(str(card.get("title", "")) + " " + str(card.get("rationale_natural", "")))
            
            content += f"### Sample {i+1}: {card.get('title')}\n"
            content += f"- **Raw Input (Norm)**: {text_norm[:200]}...\n"
            content += f"- **Escalated**: {is_escalated}\n"
            
            intensity = float(card.get("intensity", 50))
            def has(keys): return any(k in text_norm for k in self.CONFLICT_KEYWORDS[keys])
            patterns = {
                "Tightening_Inflow": has("Tightening") and has("Inflow"),
                "Easing_Drain": has("Easing") and has("Drain"),
                "Supply_Demand_Gap": has("SupplyExp") and has("DemandWeak"),
                "Earnings_Price_Conflict": has("StrongEarnings") and has("PriceDecline"),
                "Policy_Inv_Tension": has("RegPressure") and has("InvSurge"),
                "GeoRisk_Rally": has("GeoRisk") and has("AssetRally"),
                "Macro_Price_Divergence": has("MacroEvent") and (has("PriceDecline") or has("AssetRally"))
            }
            
            matched = [k for k, v in patterns.items() if v]
            content += f"- **Matched Patterns**: {matched if matched else 'NONE'}\n"
            content += f"- **Reason for Result**: "
            if any(patterns.values()):
                content += f"Conflict triggered by patterns: {matched}\n\n"
            else:
                content += "No conflict patterns matched semantic conditions.\n\n"
                
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    base = Path(__file__).resolve().parent.parent.parent
    ni = NarrativeIntelligenceLayer(base)
    ni.process_topics()
    ni.run_conflict_trace()
