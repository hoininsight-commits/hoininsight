import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import yaml
from dataclasses import dataclass, asdict
from src.ops.post_mortem_tracker import PostMortemTracker
from src.ops.topic_memory import TopicMemory
from src.ops.narrative_saturation import NarrativeSaturation

@dataclass
class DecisionCard:
    """
    Final Output Card for Dashboard.
    Step 9: Speakable Candidate.
    Step 16: Portfolio Balance Metadata.
    Step 17: Time-to-Impact Metadata.
    Step 20: Topic Memory.
    Step 21: Narrative Saturation.
    """
    topic_id: str
    title: str
    status: str # READY, HOLD, DROP
    
    # Original Data Preservation
    reason: str = None
    evidence_count: int = 0
    raw_score: float = 0.0 # Was total_score in my previous edit? No, code uses raw_score
    
    # Core Data
    speak_pack: Optional[Dict[str, Any]] = None # Only for READY
    evidence_refs: List[Dict[str, str]] = None
    
    # Metadata
    tags: List[str] = None
    why_today: str = None
    flags: List[str] = None
    
    # Eligibility & Bridge
    bridge_eligible: bool = False
    is_fact_driven: bool = False
    fact_why_now: str = None
    eligibility_badge: str = None
    eligibility_reason: str = None
    
    # Narration Logic
    narration_level: int = 1
    narration_badge: str = None
    narration_helper: str = None
    narration_ceiling: str = None
    
    # Judgment & Rationale
    judgment_notes: List[str] = None
    selection_rationale: List[str] = None
    contrast_rationale: Dict[str, Any] = None
    impact_window: str = None
    impact_hint: str = None
    
    # Topic Memory
    memory_status: str = "NEW_TOPIC" # NEW_TOPIC, REVISIT, REGIME_UPDATE
    memory_meta: Dict[str, Any] = None
    
    # Narrative Saturation
    saturation_level: str = "NORMAL"
    saturation_count: int = 0
    saturation_axis: str = None
    
    # Re-Narration Permission (Step 22)
    renarration_status: str = None # PERMITTED, DISCOURAGED, or None (if NEW)
    renarration_reason: str = None
    
    # Post-Mortem
    outcome: str = None

class DecisionDashboard:
    """
    Reporter for the Topic Gate.
    Generates daily operational dashboard.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tracker = PostMortemTracker(base_dir)
        self.memory = TopicMemory(base_dir)
        self.saturation = NarrativeSaturation(base_dir)
        self.reason_map = self._load_reason_map()
        
    def _load_reason_map(self) -> Dict:
        path = self.base_dir / "registry/decision_reason_map_v1.yml"
        if not path.exists():
            return {}
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except:
            return {}

    def build_dashboard_data(self, ymd: str) -> Dict[str, Any]:
        """
        Aggregates data for the dashboard.
        """
        # 1. Load Gate Output
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        gate_out = gate_dir / "topic_gate_output.json"
        gate_cands = gate_dir / "topic_gate_candidates.json"
        
        # Load Candidates for Source Mapping
        cand_map = {}
        if gate_cands.exists():
            try:
                c_data = json.loads(gate_cands.read_text(encoding="utf-8"))
                for c in c_data.get("candidates", []):
                    cand_map[c.get("candidate_id")] = c
            except:
                pass

        topics = []
        if gate_out.exists():
            try:
                data = json.loads(gate_out.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "ranked" in data:
                        topics = data.get("ranked", [])
                    elif "top1" in data:
                        topics = [data["top1"]]
                    elif "topic_id" in data:
                        # Direct single topic object
                        topics = [data]
            except Exception as e:
                print(f"[Dashboard] Error parsing gate_out: {e}")
        
        # Post-Mortem History Loading (Step 18)
        from datetime import datetime, timedelta
        t_dt = datetime.strptime(ymd, "%Y-%m-%d")
        # Load [target_date + 1, target_date + 90]
        next_day_str = (t_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        future_end_str = (t_dt + timedelta(days=90)).strftime("%Y-%m-%d")
        history = self.tracker.load_history(next_day_str, future_end_str)
        
        # Load Memory (Step 20) - 90 days lookback from today
        mem_index = self.memory.load_memory(ymd, lookback_days=90)
        
        # Load Saturation History (Step 21) - 14 days lookback
        sat_index = self.saturation.load_history(ymd, days=14)
        
        # Aggregate stats for today's panel (Past performance up to target_date)
        pm_stats = self.tracker.get_aggregate_stats(ymd, lookback_days=90)
        
        cards = []
        status_counts = {"READY": 0, "HOLD": 0, "DROP": 0}
        sat_summary = {"NORMAL": 0, "DENSE": 0, "SATURATED": 0}
        failure_tally = {}
        flag_tally = {}
        
        # 2. Process each topic
        for t in topics:
            tid = t.get("topic_id")
            if not tid: continue
            
            # Find script sidecar
            # Pattern: script_v1_{tid}.md.quality.json
            quality_file = gate_dir / f"script_v1_{tid}.md.quality.json"
            
            status = "DROP" # Default if no script
            codes = ["NO_SCRIPT"]
            evidence_cnt = 0
            
            if quality_file.exists():
                try:
                    q_data = json.loads(quality_file.read_text(encoding="utf-8"))
                    status = q_data.get("quality_status", "DROP")
                    codes = q_data.get("failure_codes", [])
                    # Infer evidence count from script if possible, or assume based on status
                    evidence_cnt = self._count_evidence_from_script(gate_dir / f"script_v1_{tid}.md")
                except:
                    pass
            
            # Translate Reason
            reason_text = self._get_reason_text(status, codes)
            
            # Tally
            status_counts[status] = status_counts.get(status, 0) + 1
            for c in codes:
                failure_tally[c] = failure_tally.get(c, 0) + 1
            
            # Compute Flags
            flags = self._compute_flags(t, evidence_cnt)
            for f in flags:
                flag_tally[f] = flag_tally.get(f, 0) + 1

            # Build Speak Pack & Recommender (only for READY)
            speak_pack = None
            evidence_refs = None
            tags = None
            why_today = None
            
            if status == "READY":
                speak_pack = self._build_speak_pack(t, evidence_cnt, flags)
                evidence_refs = self._build_evidence_refs(t, cand_map)
                # Recommender Hints
                tags = self._compute_recommender_tags(t, flags)
                why_today = self._compute_why_today(t, speak_pack)
                
                # Step 17: Time-to-Impact Tag
                impact_win, impact_hint = self._determine_impact_window(t, tags)
            else:
                impact_win = None
                impact_hint = None
                
            # Step 18: Post-Mortem Evaluation
            outcome = None
            # Step 20: Topic Memory
            mem_res = {"type": "NEW_TOPIC", "meta": None}
            # Step 21: Narrative Saturation
            sat_res = {"level": "NORMAL", "count": 0, "axis": None}
            
            if status == "READY":
                outcome = self.tracker.evaluate_topic(t, ymd, history)
                mem_res = self.memory.classify_topic(t, mem_index, current_date=ymd)
                sat_res = self.saturation.compute_saturation(t, sat_index)
                
                # Update Saturation Summary
                lvl = sat_res["level"]
                sat_summary[lvl] = sat_summary.get(lvl, 0) + 1
                
                # Step 22: Re-Narration Permission
                perm_status, perm_reason = self._determine_renarration_permission(
                    mem_res["type"], impact_win, outcome
                )
            else:
                 perm_status, perm_reason = None, None


            depth_info = self._calculate_narration_depth(t, status, self._check_fact_driven(t), t.get("handoff_to_structural", False))
            ceiling_reason = self._get_ceiling_reason(depth_info["narration_level"], self._check_fact_driven(t))
            
            cards.append(DecisionCard(
                topic_id=tid,
                title=t.get("title", "Untitled"),
                status=status,
                reason=reason_text,
                evidence_count=evidence_cnt,
                raw_score=t.get("total_score", 0.0),
                flags=flags,
                speak_pack=speak_pack,
                evidence_refs=evidence_refs,
                tags=tags,
                why_today=why_today,
                bridge_eligible=t.get("handoff_to_structural", False),
                is_fact_driven=self._check_fact_driven(t),
                fact_why_now=self._get_fact_why_now_hint(t) if self._check_fact_driven(t) else None,
                narration_ceiling=ceiling_reason,
                judgment_notes=self._build_judgment_notes({
                    **t, 
                    "status": status, 
                    "evidence_count": evidence_cnt,
                    "narration_level": depth_info["narration_level"],
                    "fact_why_now": self._get_fact_why_now_hint(t) if self._check_fact_driven(t) else None,
                    "is_fact_driven": self._check_fact_driven(t),
                    "flags": flags,
                    "narration_ceiling": ceiling_reason
                }),
                selection_rationale=self._build_selection_rationale({
                    **t,
                    "status": status,
                    "is_fact_driven": self._check_fact_driven(t),
                    "narration_level": depth_info["narration_level"],
                    "judgment_notes": self._build_judgment_notes({**t, "status": status, "evidence_count": evidence_cnt, "narration_level": depth_info["narration_level"], "fact_why_now": self._get_fact_why_now_hint(t) if self._check_fact_driven(t) else None, "is_fact_driven": self._check_fact_driven(t), "flags": flags, "narration_ceiling": ceiling_reason}),
                    "narration_ceiling": ceiling_reason
                }) if status == "READY" else None,
                impact_window=impact_win,
                impact_hint=impact_hint,
                outcome=outcome,
                memory_status=mem_res["type"],
                memory_meta=mem_res["meta"],
                saturation_level=sat_res["level"],
                saturation_count=sat_res["count"],
                saturation_axis=sat_res["axis"],
                renarration_status=perm_status,
                renarration_reason=perm_reason,
                **self._get_eligibility_info(status, self._check_fact_driven(t), flags, t.get("handoff_to_structural", False)),
                **depth_info
            ))
            
        # 3. Sort (Presentation Only)
        # Groups: READY -> HOLD -> DROP
        # Within: Score desc
        cards.sort(key=lambda x: (
            {"READY": 0, "HOLD": 1, "DROP": 2}.get(x.status, 3), 
            -x.raw_score
        ))
        
        # Step 15: Contrast Post-processing
        for c in cards:
            if c.status == "READY":
                c.contrast_rationale = self._get_contrast_rationale(c, [card for card in cards if card.status == "HOLD"])
        
        # 4. "Why No Speak" Analysis
        no_speak_reason = []
        if status_counts["READY"] == 0:
            # Top 3 blockers
            sorted_fails = sorted(failure_tally.items(), key=lambda x: x[1], reverse=True)[:3]
            for code, count in sorted_fails:
                 # Translate code
                 desc = self._get_code_desc(status="DROP", code=code) # Assume DROP context for blockers
                 no_speak_reason.append(f"{desc} ({count}건)")
        
        return {
            "summary": status_counts,
            "cards": [asdict(c) for c in cards],
            "no_speak_analysis": no_speak_reason,
            "flag_summary": flag_tally,
            "has_fact_driven_candidate": any(c.is_fact_driven for c in cards if c.status != 'READY'),
            "anomaly_driven_count": len([c for c in cards if not c.is_fact_driven]),
            "fact_driven_count": len([c for c in cards if c.is_fact_driven]),
            "total_topics": len(cards),
            "candidates_count": len([c for c in cards if c.status != 'DROP']),
            "judgment_summary": {
                "weak_timing": len([c for c in cards if c.judgment_notes and any("WHY NOW" in n for n in c.judgment_notes)]),
                "shallow_evidence": len([c for c in cards if c.judgment_notes and any("LEVEL 3" in n for n in c.judgment_notes)]),
                "narrative_risk": len([c for c in cards if c.judgment_notes and any("narrative risk" in n for n in c.judgment_notes)])
            },
            "shadow_pool": self._load_shadow_pool(),
            "post_mortem_summary": pm_stats,
            "auto_priority": self._generate_auto_priority(ymd, [asdict(c) for c in cards if c.status == 'READY'], self._load_shadow_pool()),
            "bundle_md": f"data/ops/bundles/{ymd.replace('-', '/')}/speak_bundle.md"
        }

    def _load_shadow_pool(self) -> Dict[str, Any]:
        """Loads Step 34 Shadow Candidate Pool."""
        p = self.base_dir / "data" / "ops" / "shadow_candidates.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                pass
        return {"count": 0, "candidates": []}

    def _render_post_mortem_panel(self, lines: List[str], stats: Dict[str, int]):
        """Renders Step 18 Aggregate Accountability Panel."""
        c = stats.get("CONFIRMED", 0)
        f = stats.get("FAILED", 0)
        u = stats.get("UNRESOLVED", 0)
        
        lines.append("### 🧪 POST-MORTEM SUMMARY (Last 90 Days)")
        lines.append(f"- **CONFIRMED**: {c}")
        lines.append(f"- **FAILED**: {f}")
        lines.append(f"- **UNRESOLVED**: {u}")
        lines.append("")

    def _render_saturation_summary(self, lines: List[str], stats: Dict[str, int]):
        """Renders Step 21 Saturation Summary."""
        n = stats.get("NORMAL", 0)
        d = stats.get("DENSE", 0)
        s = stats.get("SATURATED", 0)
        
        lines.append("### 🧯 NARRATIVE SATURATION SUMMARY (Last 14 Days)")
        lines.append(f"- **NORMAL (0-2)**: {n}")
        lines.append(f"- **DENSE (3-4)**: {d}")
        lines.append(f"- **SATURATED (5+)**: {s}")
        lines.append("")

    def render_markdown(self, data: Dict[str, Any], force_final_view: bool = False) -> str:
        # Step 23: Final Human View Toggle
        if force_final_view or os.environ.get("ENABLE_FINAL_VIEW") == "ON":
            return self._render_final_view(data)

        lines = []
        as_of_date = data.get("as_of_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # Step 18: Aggregate Panel
        pm_stats = data.get("post_mortem_summary")
        if pm_stats:
             self._render_post_mortem_panel(lines, pm_stats)
             
        # Step 21: Saturation Panel
        sat_stats = data.get("saturation_summary")
        if sat_stats:
            self._render_saturation_summary(lines, sat_stats)

        # Step 44: Auto-Approval Panel (NEW)
        aa_path = self.base_dir / "data" / "ops" / "auto_approved_today.json"
        auto_approved_ids = []
        if aa_path.exists():
            try:
                aa_data = json.loads(aa_path.read_text(encoding="utf-8"))
                self._render_auto_approved_panel(lines, aa_data)
                auto_approved_ids = [a["topic_id"] for a in aa_data.get("auto_approved", [])]
            except:
                pass
        
        # Step 43: Auto-Priority Panel (NEW)
        ap_path = self.base_dir / "data" / "ops" / "auto_priority_today.json"
        if ap_path.exists():
            try:
                ap_data = json.loads(ap_path.read_text(encoding="utf-8"))
                self._render_auto_priority_panel(lines, ap_data)
            except:
                pass

        # Step 41: Correlation Panel (NEW)
        corr_path = self.base_dir / "data" / "ops" / "pick_outcome_30d.json"
        if corr_path.exists():
            try:
                corr_data = json.loads(corr_path.read_text(encoding="utf-8"))
                self._render_correlation_panel(lines, corr_data)
            except:
                pass

        cards = data.get("cards", [])
        
        # Partition Topics
        ready_topics = [c for c in cards if c['status'] == 'READY']
        hold_topics = [c for c in cards if c['status'] == 'HOLD']
        drop_topics = [c for c in cards if c['status'] == 'DROP']
        
        # Load Operator Decisions (Step 40)
        from src.ops.operator_decision_log import OperatorDecisionLog
        op_log = OperatorDecisionLog(self.base_dir)
        decisions_map = op_log.get_latest_decisions_map(as_of_date)
        
        lines.append("\n## DECISION DASHBOARD (Beta)\n")
        
        # Step 9: System Sanity & Drift Monitor
        self._render_sanity_panel(data, lines)
        self._render_drift_warnings(data, lines)
        
        # SCRIPT QUALITY Counters
        s = data.get("summary", {})
        lines.append(f"**SCRIPT QUALITY**: 🟢 READY={s.get('READY',0)} | 🟡 HOLD={s.get('HOLD',0)} | 🔴 DROP={s.get('DROP',0)}")
        
        # WHY NO SPEAK Panel (if needed)
        if not ready_topics:
            self._render_no_speak_panel(lines, data)
        
        # --- SECTION 1: TODAY - SPEAKABLE TOPICS ({len(ready_topics)}) ---
        if ready_topics:
            snapshot = self._build_portfolio_snapshot(cards)
            assessment = self._assess_portfolio_balance(snapshot)
            self._render_portfolio_balance(lines, snapshot, assessment)
            
        lines.append(f"\n## 🎬 TODAY — SPEAKABLE TOPICS ({len(ready_topics)})")
        lines.append("※ 시스템은 선택하지 않습니다. 아래는 오늘 설명 가능한 후보 요약입니다.")
        
        if not ready_topics:
            lines.append("- (No topics ready for broadcast today)")
        else:
            # Split Lanes
            anomaly_lane = [c for c in ready_topics if not c.get('is_fact_driven')]
            fact_lane = [c for c in ready_topics if c.get('is_fact_driven')]
            
            # A) ANOMALY-DRIVEN (Signal First)
            lines.append(f"\n### 📡 A) ANOMALY-DRIVEN (Signal First)")
            if not anomaly_lane:
                lines.append("_No ANOMALY-DRIVEN signals today_")
            else:
                for c in anomaly_lane[:5]: 
                    lines.append(self._render_ready_card(c, decisions_map, auto_approved_ids))
                if len(anomaly_lane) > 5:
                    lines.append("\n**Additional Anomaly Signals (Optional)**")
                    for c in anomaly_lane[5:]:
                        tags_str = " " + " ".join(c['tags']) if c.get('tags') else ""
                        lines.append(f"- {c['title']} (Evidence: {c['evidence_count']}){tags_str}")
            
            # B) FACT-DRIVEN (Fact First)
            lines.append(f"\n### 📑 B) FACT-DRIVEN (Fact First)")
            if not fact_lane:
                lines.append("_No FACT-DRIVEN topics today_")
            else:
                for c in fact_lane[:5]:
                    lines.append(self._render_ready_card(c, decisions_map, auto_approved_ids))
                if len(fact_lane) > 5:
                    lines.append("\n**Additional Fact Topics (Optional)**")
                    for c in fact_lane[5:]:
                        tags_str = " " + " ".join(c['tags']) if c.get('tags') else ""
                        lines.append(f"- {c['title']} (Evidence: {c['evidence_count']}){tags_str}")
        
        # --- OPERATOR SUMMARY (Step 40) ---
        self._render_operator_summary(lines, decisions_map)

        # --- ALMOST CANDIDATES ---
        self._render_almost_candidates(cards, lines)
        
        # --- SHADOW CANDIDATES (Step 34) ---
        if len(ready_topics) < 3:
            shadow_data = data.get("shadow_pool", {"count": 0, "candidates": []})
            # Step 36, 37, 38, 39: Summary Panels
            self._render_shadow_aging_summary(lines, shadow_data.get("aging_summary", {}))
            self._render_readiness_summary(lines, shadow_data.get("readiness_summary", {}))
            self._render_signal_arrival_panel(lines, shadow_data.get("signal_arrival", {}), shadow_data.get("candidates", []))
            self._render_global_signal_watchlist(lines, shadow_data.get("global_watchlist", {}))
            self._render_shadow_candidates(lines, shadow_data, decisions_map)
        
        # --- SECTION 2: WATCHLIST - NOT YET (HOLD) ---
        lines.append(f"\n## 👀 WATCHLIST — NOT YET ({len(hold_topics)})")
        if not hold_topics:
            lines.append("- (No items on watchlist)")
        else:
            lines.append("| Status | Title | Why not speak yet? |")
            lines.append("|---|---|---|")
            for c in hold_topics:
                reason = self._get_hold_reason(c)
                lines.append(f"| ⚠️ HOLD | {c['title']} | {reason} |")
                
        # --- SECTION 3: ARCHIVE - DROP ---
        if drop_topics:
            lines.append(f"\n## 🗑️ ARCHIVE — DROP ({len(drop_topics)})")
            lines.append("<details><summary>Click to view dropped topics</summary>")
            lines.append("")
            lines.append("| Status | Title | Reason |")
            lines.append("|---|---|---|")
            for c in drop_topics:
                # Use simplified reason, remove internal codes if any leak
                r = c['reason'].replace("FAIL_HOOK", "Hook 미달").replace("NO_EVIDENCE", "증거 없음")
                lines.append(f"| ⛔ DROP | {c['title']} | {r} |")
            lines.append("</details>")

        return "\n".join(lines)

    def _render_no_speak_panel(self, lines: List[str], data: Dict[str, Any]):
        """Renders the detailed WHY NO SPEAK panel when READY=0."""
        # Aggregate failing reasons
        f_tally = data.get("flag_summary", {})
        # We also want specific failure codes from summary stats or detailed reasons
        # But aggregate is easier from the pre-calculated 'no_speak_analysis' if strictly codes.
        # However, prompt asks for "NO_EVIDENCE: N", "TITLE_MISMATCH: N" etc.
        # Let's combine flag_tally and top failure codes.
        
        lines.append("\n## 🚫 WHY NO SPEAK (Today)")
        lines.append("> **오늘은 영상화 가능한 토픽이 없습니다.** 아래 사유로 인해 보류되었습니다.")
        lines.append("")
        
        # Merge lists
        reasons = {}
        # 1. From flags
        for f, cnt in f_tally.items():
            reasons[f] = cnt
            
        # 2. From failure codes (extracted from no_speak_analysis or we need raw tally)
        # We have internal `failure_tally` but it wasn't passed fully in data structure,
        # only `no_speak_analysis` text list.  
        # Let's rely on what we have. If `no_speak_analysis` has "Code (N)", parse it?
        # Or better, just fix `build_dashboard_data` to pass `failure_tally`.
        # For now, let's use `no_speak_analysis` lines.
        
        ns_ana = data.get("no_speak_analysis", [])
        for r in ns_ana:
            lines.append(f"- {r}")
            
        # Add flags
        for k, v in reasons.items():
            lines.append(f"- {k}: {v}건")
            
        if data.get("has_fact_driven_candidate"):
            lines.append("- **FACT 기준은 충족했으나 구조 신호 부족**")
            
        lines.append("")

    def _render_almost_candidates(self, cards: List[Dict], lines: List[str]):
        """Renders Top 3 candidates that were close (excluding READY)."""
        # Exclude READY
        candidates = [c for c in cards if c['status'] != 'READY']
        # cards are already sorted (HOLD then DROP, then Score).
        top_3 = candidates[:3]
        
        if not top_3: return

        lines.append("\n## 🥈 TOP CANDIDATES (Almost)")
        lines.append("다음은 아깝게 선정되지 못한 상위 후보입니다.")
        lines.append("")
        
        for c in top_3:
            status_icon = "🟡" if c['status'] == 'HOLD' else "🔴"
            status_text = "HOLD" if c['status'] == 'HOLD' else "DROP"
            
            # Eligibility Badge
            elig_badge = c.get('eligibility_badge', '⏸️ NOT SPEAKABLE')
            eligibility_reason = c.get('eligibility_reason', 'Criteria not met')
            
            # Narration Depth Badge
            n_badge = c.get('narration_badge', '🎤 LEVEL 1')
            n_helper = c.get('narration_helper', 'Macro explanation only')
            ceiling = c.get('narration_ceiling')
            
            # Normalized Reason
            reason = self._get_hold_reason(c) if c['status'] == 'HOLD' else c['reason']
            reason = reason.replace("아직 말하지 않는 이유: ", "") # Simplify for bullet
            
            # Bridge
            bridge_mk = "🌉 Bridge Capable" if c.get('bridge_eligible') else ""
            
            lines.append(f"### {status_icon} {c['title']} ({status_text})")
            lines.append(f"**{elig_badge}**: {eligibility_reason}")
            lines.append(f"**{n_badge}**: {n_helper}")
            if ceiling:
                lines.append(f"**Ceiling**: {ceiling}")
            
            # Step 8: Promotion Requirements
            self._render_promotion_requirements(c.get('narration_level', 1), c.get('is_fact_driven', False), lines)
            
            lines.append(f"- **Reason**: {reason}")
            if bridge_mk:
                 lines.append(f"- **Note**: {bridge_mk}")
            
            # Context stats
            ev_cnt = c.get('evidence_count', 0)
            lines.append(f"- **Evidence**: {ev_cnt} items")
            
            # Judgment Notes
            notes = c.get('judgment_notes')
            if notes:
                lines.append(f"\n⚠️ **JUDGMENT NOTES**")
                for n in notes:
                    lines.append(f"- {n}")
            lines.append("")

    def _render_shadow_candidates(self, lines: List[str], shadow_data: Dict[str, Any], decisions_map: Dict[str, Dict]):
        """Renders Step 34 Shadow Candidates Pool (Grey tone, non-actionable)."""
        lines.append("\n### 🔘 SHADOW CANDIDATES (Preparation Pool)")
        lines.append("> **NOT FOR NARRATION YET** — Structurally promising topics awaiting additional triggers.")
        
        candidates = shadow_data.get("candidates", [])
        if not candidates:
            lines.append("_Shadow pool empty — no promotable topics detected._")
            return

        for c in candidates:
            tid = c.get("topic_id")
            # Grey tone style using blockquote or simple text
            lines.append(f"#### ◽ {c['title']} {self._get_operator_badge(tid, decisions_map)} (Impact: {c['impact_window']})")
            
            # Step 40: SHADOW Action Bar
            self._render_shadow_action_bar(lines, tid, c['title'])
            
            lines.append(f"- **Lane**: {c['lane']}")
            lines.append(f"- **Why not speak**: {c['why_not_speak']}")
            
            # Step 35: Trigger Map Rendering
            tm = c.get("trigger_map", {})
            if tm:
                lines.append("\n    > **PROMOTION READINESS (Still NOT for narration)**")
                missing = ", ".join(tm.get("missing_triggers", []))
                sources = ", ".join(tm.get("source_hint", []))
                lines.append(f"    - **Missing**: {missing}")
                lines.append(f"    - **Expected From**: {sources}")
                lines.append(f"    - **Recheck**: {tm.get('earliest_recheck', 'AFTER_7D')}")
            
            # Step 36: Shadow Age Rendering
            aging = c.get("aging", {})
            if aging:
                state = aging.get("aging_state")
                days = aging.get("days_in_shadow", 0)
                state_icon = ""
                if state == "STALE": state_icon = " ⚠️"
                elif state == "DECAYING": state_icon = " ⚠️ [Consider drop]"
                elif state == "EXPIRED": state_icon = " 🧊 [Likely obsolete]"
                lines.append(f"    - **Shadow Age**: {state}{state_icon} ({days} days)")
            
            # Step 38: Signal Status Rendering
            s_status = c.get("signal_status", {})
            matched = s_status.get("matched_signals", [])
            unmatched = s_status.get("unmatched_signals", [])
            
            if matched or unmatched:
                lines.append("\n    > **SIGNAL STATUS**")
                for s in matched:
                    lines.append(f"    - ✅ Arrived: {s}")
                for s in unmatched:
                    lines.append(f"    - ⏳ Still waiting: {s}")
            
            # Step 39: Promotion Readiness Rendering
            rd = c.get("readiness", {})
            if rd:
                bucket = rd.get("readiness_bucket")
                matched = rd.get("matched_count", 0)
                required = rd.get("required_count", 0)
                
                bucket_icon = "⚪"
                if bucket == "READY_TO_PROMOTE": bucket_icon = "✅"
                elif bucket == "NEARLY_READY": bucket_icon = "🟡"
                elif bucket == "FAR": bucket_icon = "💤"
                
                lines.append(f"\n    > **PROMOTION READINESS**")
                lines.append(f"    - **Bucket**: {bucket_icon} {bucket}")
                lines.append(f"    - **Progress**: {matched} / {required} signals")
                
                missing = rd.get("missing_signals", [])
                if missing:
                    lines.append(f"    - **Missing**: {', '.join(missing)}")
                
                hint = rd.get("operator_hint")
                if hint:
                    lines.append(f"    - *{hint}*")
            lines.append("")

    def _render_readiness_summary(self, lines: List[str], summary: Dict[str, int]):
        """Renders Step 39 Promotion Readiness Summary Panel."""
        if not summary or not any(summary.values()): return
        lines.append("\n#### 📊 PROMOTION READINESS SUMMARY")
        lines.append(f"- **READY_TO_PROMOTE**: {summary.get('READY_TO_PROMOTE', 0)} ✅")
        lines.append(f"- **NEARLY_READY**: {summary.get('NEARLY_READY', 0)} 🟡")
        lines.append(f"- **IN_PROGRESS**: {summary.get('IN_PROGRESS', 0)} ⚪")
        lines.append(f"- **FAR**: {summary.get('FAR', 0)} 💤")

    def _render_signal_arrival_panel(self, lines: List[str], arrival_data: Dict[str, Any], candidates: List[Dict]):
        """Renders Step 38 Global Signal Arrival Panel."""
        arrived = arrival_data.get("arrived_signals", [])
        lines.append("\n#### 📨 SIGNAL ARRIVAL TODAY")
        
        if not arrived:
            lines.append("- _No monitored signals arrived today._")
            return
            
        for s in arrived:
            # Count how many shadows matched
            match_cnt = sum(1 for c in candidates if s in c.get("signal_status", {}).get("matched_signals", []))
            lines.append(f"- **{s}**: Arrived ({match_cnt} shadows matched)")

    def _render_global_signal_watchlist(self, lines: List[str], g_watchlist: Dict[str, int]):
        """Renders Step 37 Global Signal Watchlist Panel."""
        if not g_watchlist or not any(g_watchlist.values()): return
        lines.append("\n#### 🔭 GLOBAL SIGNAL WATCHLIST (Waiting For)")
        for signal, count in g_watchlist.items():
            if count > 0:
                lines.append(f"- **{signal}**: {count} topics")

    def _render_shadow_aging_summary(self, lines: List[str], summary: Dict[str, int]):
        """Renders Step 36 Shadow Aging Summary Panel."""
        if not any(summary.values()): return
        lines.append("\n#### 🧊 SHADOW AGING SUMMARY")
        lines.append(f"- **FRESH**: {summary.get('FRESH', 0)}")
        lines.append(f"- **STALE**: {summary.get('STALE', 0)} ⚠️")
        lines.append(f"- **DECAYING**: {summary.get('DECAYING', 0)} ⚠️")
        lines.append(f"- **EXPIRED**: {summary.get('EXPIRED', 0)} 🧊")

    def _determine_renarration_permission(self, memory_status: str, impact_window: str, outcome: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Step 22: Determines if re-narration is PERMITTED or DISCOURAGED.
        Only applies if topic is NOT NEW.
        """
        if memory_status == "NEW_TOPIC":
            return None, None
            
        # Rules for PERMITTED
        if memory_status == "REGIME_UPDATE":
            return "PERMITTED", "국면 변화가 감지되어 재설명 가능"
            
        if impact_window in ["IMMEDIATE", "NEAR"]:
            return "PERMITTED", "시급한 영향력으로 인해 재설명 필요"
            
        if outcome == "FAILED":
            return "PERMITTED", "이전 예측 실패로 인한 사후 분석 필요"
            
        # Default DISCOURAGED
        return "DISCOURAGED", "최근 반복 소비된 서사로 신규 정보 없음"

    def _render_ready_card(self, c: Dict, decisions_map: Dict[str, Dict], auto_approved_ids: List[str] = None) -> str:
        """Renders the detailed READY card with Speak Pack."""
        tid = c.get('topic_id')
        lines = []
        is_fact = c.get('is_fact_driven')
        title_suffix = " (FACT-DRIVEN (Rule v1))" if is_fact else ""
        
        is_auto = auto_approved_ids and tid in auto_approved_ids
        aa_badge = " | 🤖 **AUTO-APPROVED** 🔒" if is_auto else ""
        
        lines.append(f"\n### ✅ {c['title']}{title_suffix} {self._get_operator_badge(tid, decisions_map)}{aa_badge}") 
        
        # Step 40: READY Action Bar
        self._render_ready_action_bar(lines, tid, c['title'])
        
        # Step 14: Selection Rationale
        rationale = c.get('selection_rationale')
        if rationale:
            lines.append(f"\n🧭 **SELECTION RATIONALE**")
            for r in rationale:
                lines.append(f"- {r}")
                
        # Step 20: Topic Memory Badge (Prospective)
        mem = c.get('memory_status', "NEW_TOPIC")
        meta = c.get('memory_meta')
        if mem == "REVISIT":
            last_date = meta.get('last_date', 'Unknown')
            lines.append(f"\n🧠 **TOPIC MEMORY**: REVISIT (Last: {last_date})")
            lines.append("> ⚠️ **NOTE**: 이 토픽은 이미 다뤄진 바 있음 — 반복 내레이션 주의")
        elif mem == "REGIME_UPDATE":
            last_date = meta.get('last_date', 'Unknown')
            lines.append(f"\n🧠 **TOPIC MEMORY**: REGIME UPDATE (Last: {last_date})")
        # NEW_TOPIC is implicit/hidden or explicit? 
        # Requirement: "Brain TOPIC MEMORY: NEW / REVISIT / REGIME UPDATE"
        # "Render badge... On READY topic cards only"
        # So we render for NEW too? "NEW"
        elif mem == "NEW_TOPIC":
             lines.append(f"\n🧠 **TOPIC MEMORY**: NEW")

        # Step 21: Narrative Saturation Badge (Prospective)
        sat_lvl = c.get('saturation_level', 'NORMAL')
        sat_cnt = c.get('saturation_count', 0)
        if sat_lvl != "NORMAL": # Display only if significant? Or always?
            # "Render Saturation Warning... For READY topics only"
            # "NARRATIVE SATURATION: NORMAL / DENSE / SATURATED"
            # Let's show always for visibility?
            pass
            
        lines.append(f"\n🧯 **NARRATIVE SATURATION**: {sat_lvl} ({sat_cnt} recent)")
        if sat_lvl == "SATURATED":
            lines.append("> 🧯 **WARNING**: 이미 시장에서 충분히 소비된 서사 — 반복 주의")

        # Step 22: Re-Narration Permission Block
        ren_status = c.get('renarration_status')
        if ren_status:
            lines.append(f"\n🔁 **RE-NARRATION**")
            lines.append(f"- **Status**: {ren_status}")
            lines.append(f"- **Reason**: {c.get('renarration_reason')}")
            
        # Step 15: Contrast Rationale
        contrast = c.get('contrast_rationale')
        if contrast:
            lines.append(f"\n⚖️ **CONTRAST (Why this over others)**")
            lines.append(f"- Selected: {contrast.get('selected_reason')}")
            rejections = contrast.get('rejections', [])
            for rj in rejections:
                lines.append(f"- Rejected: {rj['topic_id']} — {rj['reason']}")
                
        if is_fact and c.get('fact_why_now'):
            lines.append(f"> **WHY NOW**: {c['fact_why_now']}")
            
        # Step 17: Impact Window
        imp_win = c.get('impact_window')
        if imp_win:
            imp_hint = c.get('impact_hint', '')
            lines.append(f"\n**⏱ IMPACT WINDOW**: {imp_win}")
            lines.append(f"> {imp_hint}")
            
        badge = c.get('eligibility_badge', '⏸️ NOT SPEAKABLE')
        reason = c.get('eligibility_reason', 'Criteria not met')
        lines.append(f"\n**{badge}**: {reason}")
        
        # Narration Depth Badge
        n_badge = c.get('narration_badge', '🎤 LEVEL 1')
        n_helper = c.get('narration_helper', 'Macro explanation only')
        lines.append(f"**{n_badge}**: {n_helper}")
        
        ceiling = c.get('narration_ceiling')
        if ceiling:
            lines.append(f"**Ceiling**: {ceiling}")
        
        # Step 8: Promotion Requirements
        self._render_promotion_requirements(c.get('narration_level', 1), c.get('is_fact_driven', False), lines)
        
        # Tags Line
        tags = c.get('tags', [])
        if tags:
            lines.append(" ".join(tags))
            
        why = c.get('why_today')
        if why:
            lines.append(f"**오늘 찍는 이유**: {why}")
            
        lines.append(f"**판단 요약**: 지금 설명 가능한 최소 조건 충족 (증거 {c['evidence_count']}건)")
        
        # Judgment Notes
        notes = c.get('judgment_notes')
        if notes:
            lines.append(f"\n⚠️ **JUDGMENT NOTES**")
            for n in notes:
                lines.append(f"- {n}")
        
        sp = c.get('speak_pack')
        if sp:
            lines.append(f"\n**🎙️ SPEAK PACK**")
            lines.append(f"- **One-Liner**: {sp.get('one_liner')}")
            lines.append(f"- **Numbers**: {', '.join(sp.get('numbers', []))}")
            lines.append(f"- **Watch Next**: {', '.join(sp.get('watch_next', []))}")
            lines.append(f"- **Risk**: {sp.get('risk_note')}")
            
        refs = c.get('evidence_refs')
        if refs:
            lines.append(f"\n**🔍 EVIDENCE REFERENCES**")
            for idx, r in enumerate(refs, 1):
                 src = r.get('source', {})
                 pub = src.get('publisher', 'unknown')
                 url = src.get('url', 'unknown')
                 lines.append(f"{idx}. {r['label']}: {r['value']} (Source: {pub} | URL: {url})")
        else:
            lines.append("\n**🔍 EVIDENCE REFERENCES**")
            lines.append("- No verifiable evidence available.")
            
        # Step 19: Accountability View (Separated)
        outcome = c.get('outcome')
        if outcome:
            lines.append(f"\n--- 🛡️ ACCOUNTABILITY CHECK ---")
            if outcome != "UNRESOLVED":
                lines.append(f"**🧪 OUTCOME**: {outcome}")
            else:
                lines.append(f"_🧪 OUTCOME: {outcome}_")
            
        lines.append("---")
        return "\n".join(lines)

    def _render_final_view(self, data: Dict[str, Any]) -> str:
        """Step 23: Final Human View - Decision Focused."""
        cards = data.get("cards", [])
        sorted_cards = self._sort_for_final_view(cards)
        
        lines = []
        # Header
        # Assume today's date from first card? or data? 
        # But data doesn't have top level date. 
        # We'll use generic header or try to extract.
        lines.append("# 🎙️ DAILY EDITORIAL DECISION (FINAL VIEW)")
        lines.append("\n_System diagnostics hidden. Showing prioritized decision metrics only._\n")
        
        # Top 5
        top_5 = sorted_cards[:5]
        rest = sorted_cards[5:]
        
        for c in top_5:
            lines.append(self._render_final_card(c))
            
        if rest:
            lines.append("\n### 👇 More Candidates")
            lines.append(f"<details><summary>Show {len(rest)} more...</summary>\n")
            for c in rest:
                lines.append(self._render_final_card(c))
            lines.append("\n</details>")
            
        return "\n".join(lines)

    def _sort_for_final_view(self, cards: List[Dict]) -> List[Dict]:
        """
        Sorts for editorial priority:
        1. Speakable + (Permitted | NULL)
        2. Speakable + Discouraged
        3. Not Speakable
        
        Secondary: Level (Desc), Impact (Asc)
        """
        def sort_key(c):
             # Group Logic
             status = c.get('status', 'DROP')
             perm = c.get('renarration_status') 
             
             # Group 1: READY + (Permitted or None(New))
             # Group 2: READY + Discouraged
             # Group 3: Not READY
             
             if status == "READY":
                 if perm == "DISCOURAGED":
                     group = 2
                 else:
                     group = 1
             else:
                 group = 3
                 
             # Level (Desc) -> use negative
             level = -c.get('narration_level', 0)
             
             # Impact (Asc) -> IMMEDIATE(0) < NEAR(1) < MID(2) < LONG(3)
             imp_map = {"IMMEDIATE": 0, "NEAR": 1, "MID": 2, "LONG": 3}
             impact = imp_map.get(c.get('impact_window', 'LONG'), 4)
             
             return (group, level, impact)
             
        return sorted(cards, key=sort_key)

    def _render_final_card(self, c: Dict) -> str:
        """Minimalist card for Final View."""
        lines = []
        is_ready = c.get('status') == "READY"
        icon = "✅" if is_ready else "⏸️"
        
        title = c.get('title')
        lines.append(f"### {icon} {title}")
        
        # Badges Row
        badges = []
        if is_ready:
            badges.append("🎙️ SPEAKABLE")
            badges.append(c.get('narration_badge', '🎤 L1'))
            perm = c.get('renarration_status')
            if perm:
                badges.append(f"🔁 {perm}")
        else:
            badges.append(c.get('eligibility_badge', 'NOT SPEAKABLE'))
            
        lines.append(" | ".join(badges))
        
        # Content
        if c.get('why_today'):
            lines.append(f"> **WHY**: {c['why_today']}")
            
        # Rationale (First point only)
        rats = c.get('selection_rationale')
        if rats and len(rats) > 0:
            lines.append(f"- 🧭 {rats[0]} (and {len(rats)-1} more..)" if len(rats)>1 else f"- 🧭 {rats[0]}")
            
        # Speak Pack (Collapsed)
        sp = c.get('speak_pack')
        if sp:
            lines.append("<details><summary>🎙️ Speak Pack (Script)</summary>")
            lines.append(f"- One-Liner: {sp.get('one_liner')}")
            lines.append(f"- Risk: {sp.get('risk_note')}")
            lines.append("</details>")
            
        lines.append("\n---")
        return "\n".join(lines)

    def _get_hold_reason(self, c: Dict) -> str:
        """Determines the single strongest human-readable reason for HOLD."""
        # 1. Sanity Flags (Highest Priority)
        flags = c.get('flags', [])
        if "TITLE_MISMATCH" in flags:
            return "아직 말하지 않는 이유: 제목과 근거 데이터의 연관성이 낮습니다."
        if "PLACEHOLDER_EVIDENCE" in flags:
            return "아직 말하지 않는 이유: 근거 수치에 확인 불가능한 값이 포함됨."
        if "EVIDENCE_TOO_THIN" in flags:
            return "아직 말하지 않는 이유: 말할 수 있는 근거가 너무 적습니다 (2개 미만)."
            
        # 2. Quality Status Reason
        # Translate common engine codes to human sentence
        raw_reason = c.get('reason', '')
        if "Weak Evidence" in raw_reason or "근거 데이터가 부족" in raw_reason:
            return "아직 말하지 않는 이유: 주장을 뒷받침할 구체적 수치가 부족합니다."
        if "No Forward Signal" in raw_reason or "추후 관찰 지표" in raw_reason:
            return "아직 말하지 않는 이유: 이 현상의 지속 여부를 판단할 지표가 없습니다."
            
        # 3. Fallback
        return f"아직 말하지 않는 이유: {raw_reason}"

    def _get_reason_text(self, status: str, codes: List[str]) -> str:
        desc_map = self.reason_map.get("descriptions", {})
        st_map = desc_map.get(status, {})
        
        # If specific code match found in map
        for code in codes:
            for item in st_map.get("codes", []):
                if item["code"] == code:
                    return item["text"]
        
        return st_map.get("default", status)

    def _get_code_desc(self, status: str, code: str) -> str:
        desc_map = self.reason_map.get("descriptions", {})
        # Flatten all codes to find text
        for st in ["READY", "HOLD", "DROP"]:
            for item in desc_map.get(st, {}).get("codes", []):
                if item["code"] == code:
                    return item["text"]
        return code

    def _count_evidence_from_script(self, script_path: Path) -> int:
        if not script_path.exists(): return 0
        import re
        try:
            txt = script_path.read_text(encoding="utf-8")
            # Heuristic from ScriptQualityGate: count "- **" in evidence section
            # We just scan whole text for simplification or split logic?
            # Let's be reasonably accurate: Look for section "5)"
            parts = txt.split("### 5)")
            if len(parts) > 1:
                ev_part = parts[1].split("###")[0]
                return len(re.findall(r"-\s*\*\*", ev_part))
        except:
            pass
        return 0

    def _build_speak_pack(self, topic: Dict, evidence_cnt: int, flags: List[str]) -> Dict[str, Any]:
        """
        Builds a concise Speak Pack for human consumption.
        """
        title = topic.get("title", "Untitled")
        
        # 1. One-Liner
        # Template: "왜 지금: {reason} 신호가 확인되어 {title}가 설명 가능한 상태."
        reasons = topic.get("key_reasons", [])
        main_reason = reasons[0] if reasons else "주요 데이터 변동"
        one_liner = f"왜 지금: {main_reason} 신호가 확인되어 '{title}'가 설명 가능한 상태."
        
        # 2. Numbers
        nums = []
        raw_nums = topic.get("numbers", [])
        match_count = 0
        if raw_nums:
            for n in raw_nums[:3]:
                label = n.get("label", "Signal")
                val = n.get("value", "?")
                # Clean up value if needed, strict presentation
                nums.append(f"{label}: {val}")
                match_count += 1
        
        if match_count == 0:
            nums.append("(no numeric evidence)")
            
        # 3. Watch Next
        watch = []
        # Use risk or key reasons as proxy if no dedicated watchlist available in this topic view
        # Ideally we read 'watchlist' from script helper but topic json might not have it structured.
        # Minimal viable: Use Risk One + "Trend Confirmation"
        r1 = topic.get("risk_one")
        if r1: watch.append(f"{r1} 여부")
        watch.append("관련 지표 추세 지속성")
        
        # 4. Risk Note
        if flags:
            risk_note = f"Risk: 데이터 검증 신호({len(flags)}건) 존재, 추가 확인 필요."
        else:
            risk_note = "Risk: 단기 변동성 확대 구간, 추세 확인 필요."
            
        return {
            "one_liner": one_liner,
            "numbers": nums,
            "watch_next": watch,
            "risk_note": risk_note
        }

    def _build_evidence_refs(self, topic: Dict, cand_map: Dict) -> List[Dict[str, Any]]:
        """
        Builds detailed evidence references using source candidates.
        """
        refs = []
        numbers = topic.get("numbers", [])
        source_cands = topic.get("source_candidates", [])
        
        for n in numbers[:5]:
            label = n.get("label", "Unknown")
            value = str(n.get("value", "Unknown"))
            
            # Find matching candidate
            matched_cand = None
            for cid in source_cands:
                cand = cand_map.get(cid)
                if not cand: continue
                # Linear search in cand numbers
                for c_num in cand.get("numbers", []):
                    if c_num.get("label") == label: # Heuristic match by label
                         matched_cand = cand
                         break
                if matched_cand: break
            
            # If no match found by label, maybe take the first source? 
            # Risk: might reference wrong source. Safe: explicit "unknown".
            # The constraints say "If source info is missing, explicitly set publisher='unknown'".
            
            publisher = "unknown"
            url = "unknown"
            context = "Extracted from topic numbers"
            
            if matched_cand:
                # Candidate usually has 'article' or 'event' metadata
                # Structure of candidate depends on 'topic_gate_candidates.json' schema
                # Usually: { ..., "article_meta": {"publisher": ...}, "url": ... } or "source_event": {...}
                # Let's support both common patterns in this system
                
                # Pattern 1: Event based
                if "source_event" in matched_cand:
                    evt = matched_cand["source_event"]
                    publisher = evt.get("publisher", "unknown")
                    url = evt.get("url", "unknown")
                    context = evt.get("title", context)
                # Pattern 2: Article/Raw based
                elif "article_meta" in matched_cand:
                     meta = matched_cand["article_meta"]
                     publisher = meta.get("publisher", "unknown")
                     url = matched_cand.get("url", "unknown")
                     context = matched_cand.get("title", context)
                # Fallback: Top level fields
                else:
                    publisher = matched_cand.get("publisher", publisher)
                    url = matched_cand.get("url", url)

            refs.append({
                "label": label,
                "value": value,
                "context": context,
                "source": {
                    "publisher": publisher,
                    "url": url
                }
            })
            
        return refs

    def _compute_flags(self, topic: Dict, evidence_cnt: int) -> List[str]:
        flags = []
        
        # 1. EVIDENCE_TOO_THIN
        if evidence_cnt < 2:
            flags.append("EVIDENCE_TOO_THIN")
            
        # 2. PLACEHOLDER_EVIDENCE
        # Check raw numbers if available
        nums = topic.get("numbers", [])
        for n in nums:
            val = str(n.get("value", "")).lower()
            if "need" in val or "defic" in val or val == "0" or val == "0.0":
                flags.append("PLACEHOLDER_EVIDENCE")
                break
                
        # 3. TITLE_MISMATCH (Simple Heuristic)
        # Check if title keywords appear in reason or evidence labels
        title = topic.get("title", "").lower()
        keywords = [k for k in title.split() if len(k) > 2] # Skip short words
        
        # Collect comparison text
        reasons = " ".join(topic.get("key_reasons", [])).lower()
        ev_labels = " ".join([n.get("label", "") for n in nums]).lower()
        context = reasons + " " + ev_labels
        
        # If significant part of title is missing in context
        # (This is very heuristic, let's just check if ANY keyword matches for now to be safe, 
        # or ALL? "mismatch" implies strong deviation. Let's say if NO keyword matches.)
        if keywords:
            match_found = False
            for k in keywords:
                if k in context:
                    match_found = True
                    break
            if not match_found:
                 flags.append("TITLE_MISMATCH")
                 
        return flags

    def _compute_recommender_tags(self, topic: Dict, flags: List[str]) -> List[str]:
        """Computes recommendation tags (Max 2)."""
        tags = []
        
        # 1. RISK-AWARE
        if flags:
            tags.append("⚠️ RISK-AWARE")
            
        # 2. STRUCTURAL SIGNAL
        # Use simple heuristic if 'matched_axes' not explicitly available in topic json (it's in bridge output)
        # But we can check if key_reasons mentions 'Structural'
        # Or heuristic: if total score > 80 (high confidence) -> might be structural
        # Better: use 'handoff_to_structural' field from Gate
        if topic.get("handoff_to_structural"):
            tags.append("🧠 STRUCTURAL SIGNAL")
            
        # 3. TIME-SENSITIVE
        # Heuristic: if 'deadline' or 'D-Day' in title or risk
        # Or simple randomness for demo if no field? No, STRICT HEURISTIC.
        # Check risk_one for 'Short term'
        r1 = topic.get("risk_one", "").lower()
        if "short" in r1 or "imminent" in r1 or "today" in r1:
            tags.append("⏳ TIME-SENSITIVE")
            
        # 4. TRENDING NOW
        # If score is very high (top 10%)
        if topic.get("total_score", 0) > 85:
             tags.append("🔥 TRENDING NOW")
             
        return tags[:2]

    def _compute_why_today(self, topic: Dict, speak_pack: Dict) -> str:
        """Generates the single line 'Why Today' hint."""
        # Use one-liner from speak pack but simplified
        if speak_pack:
             ol = speak_pack.get("one_liner", "")
             # Extract extraction: "왜 지금: X 신호가 확인되어..." -> "X 신호가 확인되었습니다."
             # Or just use the reason directly
             return f"{ol.replace('왜 지금: ', '')}"
        return "지금 설명 가능한 조건 충족"

    def _get_fact_why_now_hint(self, topic: Dict) -> str:
        """Generates template-based 'WHY NOW' hint for FACT-DRIVEN topics."""
        # Predefined Templates
        templates = {
            "FACT_GOV_PLAN": "주요 기관 및 정부의 공식 집행 계획 발표",
            "FACT_CORP_DISCLOSURE": "기업의 공식 공시 및 실적 데이터 확인",
            "FACT_MACRO_DATA": "핵심 거시 지표의 임계치 돌파 및 수치화",
            "FACT_INVEST_FLOW": "대규모 자금 흐름 및 투자 집행 데이터 포착",
            "MARKET_SIZE": "주요 리서치 기관이 시장 규모를 재산정",
            "OPERATIONAL_START": "실제 운영 개시로 검증 단계 진입",
            "REGULATORY_MILESTONE": "규제 환경 변화 및 법적 마일스톤 달성"
        }
        
        # 1. Match by Tags
        tags = topic.get("tags", [])
        for tag in tags:
            if tag in templates:
                return templates[tag]
        
        # 2. Match by Category (metadata)
        category = topic.get("metadata", {}).get("fact_category")
        if category in templates:
            return templates[category]
            
        # 3. Match by Event Type
        event_type = topic.get("event_type", "").upper()
        if event_type in templates:
            return templates[event_type]
            
        return "(explanatory context insufficient)"

    def _check_fact_driven(self, topic: Dict) -> bool:
        """Checks if a topic matches FACT-DRIVEN rules via metadata or tags."""
        if topic.get("is_fact_driven") or topic.get("metadata", {}).get("is_fact_driven"):
            return True
        
        # Check tags for FACT_ prefix
        tags = topic.get("tags", [])
        if any(isinstance(tag, str) and tag.startswith("FACT_") for tag in tags):
            return True
            
        return False

    def _get_eligibility_info(self, status: str, is_fact: bool, flags: List[str], bridge_eligible: bool) -> Dict[str, str]:
        """Maps topic status and flags to a human-readable eligibility badge and reason."""
        is_speakable = False
        if status == "READY":
            is_speakable = True
        elif is_fact and not flags:
            # Fact-driven topics without sanity flags are also speakable
            is_speakable = True
            
        badge = "🎙️ SPEAKABLE" if is_speakable else "⏸️ NOT SPEAKABLE"
        
        # Reason mapping
        if is_speakable:
            if is_fact:
                reason = "FACT COMPLETE + timing window open"
            else:
                reason = "Evidence sufficient for narration"
        else:
            if bridge_eligible:
                reason = "Structure signal missing"
            elif not flags and status == "HOLD":
                reason = "Signal clarity insufficient"
            elif "EVIDENCE_TOO_THIN" in flags or "WEAK_EVIDENCE" in flags:
                reason = "Evidence insufficient for narration"
            else:
                reason = "Quality below threshold for narration"
                
        return {
            "eligibility_badge": badge,
            "eligibility_reason": reason
        }

    def _calculate_narration_depth(self, topic: Dict, status: str, is_fact: bool, bridge_eligible: bool) -> Dict[str, Any]:
        """Assigns Narration Depth Level based on structural context."""
        why_now = (self._get_fact_why_now_hint(topic) if is_fact else topic.get("key_reasons", [""])[0]).lower()
        title = topic.get("title", "").lower()
        ev_labels = " ".join([n.get("label", "") for n in topic.get("numbers", [])]).lower()
        
        # LEVEL 3 logic (2 of 3)
        # 1) Evidence references specific info (proxy: title/labels look like specific data)
        # 2) WHY NOW ties to company event (proxy: 'company', 'corp', 'contract' in why now)
        # 3) FACT-DRIVEN + Bridge eligible OR READY with multi-layer evidence
        cond1 = any(x in ev_labels or x in title for x in ["revenue", "order", "contract", "dominance", "market share"])
        cond2 = any(x in why_now for x in ["company", "corp", "firm", "capability"])
        cond3 = (is_fact and bridge_eligible) or (status == "READY" and len(topic.get("numbers", [])) >= 3)
        
        score_v3 = sum([cond1, cond2, cond3])
        if score_v3 >= 2:
            return {
                "narration_level": 3,
                "narration_badge": "🎤 LEVEL 3",
                "narration_helper": "Stock names can be mentioned"
            }
            
        # LEVEL 2 logic (ALL apply)
        # 1) WHY NOW references industry/sector
        # 2) Evidence includes sector metrics (proxy: high level but sector-ish)
        # 3) Value flow without naming company
        is_sector_why = any(x in why_now for x in ["sector", "industry", "market size", "segments"])
        is_sector_ev = any(x in ev_labels for x in ["units", "output", "demand", "supply"])
        
        if is_sector_why and is_sector_ev:
            return {
                "narration_level": 2,
                "narration_badge": "🎤 LEVEL 2",
                "narration_helper": "Sector-level discussion possible"
            }
            
        # LEVEL 1 - Default
        return {
            "narration_level": 1,
            "narration_badge": "🎤 LEVEL 1",
            "narration_helper": "Macro explanation only"
        }

    def _get_ceiling_reason(self, level: int, is_fact: bool) -> str:
        """Determines the reason why narration level is limited to 1 or 2."""
        if level == 3:
            return None
            
        if is_fact and level in [1, 2]:
            return "공식 수치는 존재하나 수혜 귀속 불명확"
            
        if level == 1:
            return "산업 또는 기업 연결 신호 없음"
        if level == 2:
            return "특정 기업의 구조적 우위 증거 부족"
            
        return None

    def _render_promotion_requirements(self, level: int, is_fact: bool, lines: List[str]):
        """Renders the Promotion to Level 3 Requirements block (Display Only)."""
        if level >= 3:
            return
            
        lines.append(f"\n**PROMOTION TO LEVEL 3 REQUIRES**:")
        
        if is_fact:
            lines.append(f"NOTE: \"Official figures exist, but attribution to specific beneficiaries is not yet verified.\"")
            
        lines.append(f"- [ ] Company-level earnings or guidance confirmation")
        lines.append(f"- [ ] Contract / order / disclosure-level evidence")
        lines.append(f"- [ ] Capital signal (ownership, buyback, investment)")
        lines.append(f"- [ ] Structural advantage vs competitors")

    def _build_judgment_notes(self, t: Dict) -> List[str]:
        """Surfaces narrative risks based on internal inconsistencies (Step 13)."""
        notes = []
        
        # A) FACT ↔ WHY NOW Consistency
        if t.get("is_fact_driven"):
            why_now = t.get("fact_why_now", "")
            if "(explanatory context insufficient)" in why_now:
                notes.append("WHY NOW explanation is too generic for a FACT-based topic.")
                
        # B) LEVEL ↔ Evidence Depth Mismatch
        if t.get("narration_level") == 3 and t.get("evidence_count", 0) < 3:
            notes.append("LEVEL 3 assigned, but evidence depth is shallow.")
            
        # C) Speakable ↔ Risk Tension
        is_ready = t.get("status") == "READY"
        flags = t.get("flags", [])
        if is_ready:
            if len(flags) >= 2 or t.get("narration_ceiling") is not None:
                notes.append("Speakable status conflicts with elevated narrative risk.")
                
        return notes if notes else None

    def _build_selection_rationale(self, t: Dict) -> List[str]:
        """Explains why a READY topic was selected (Step 14)."""
        rationale = []
        
        # 1. PRIMARY DRIVER
        if t.get("is_fact_driven"):
            rationale.append("Primary: 공식 팩트 기반 토픽이나 구조 신호와 결합")
        else:
            rationale.append("Primary: 구조적 이상징후가 팩트/뉴스보다 선행")
            
        # 2. TIMING (Heuristic based on existing fields)
        why_now = t.get("why_today", "").lower()
        r1 = t.get("risk_one", "").lower()
        if "deadline" in why_now or "event" in why_now or "today" in why_now or "short" in r1:
            rationale.append("Timing: 일정 기반 이벤트와 시점 일치")
        else:
            rationale.append("Timing: 누적 신호가 임계치 도달")
            
        # 3. RELATIVE SELECTION
        rationale.append("Relative: 동종 토픽 대비 근거 밀도 우위")
        
        # 4. NARRATION RANGE
        lvl = t.get("narration_level", 1)
        if lvl == 3:
            rationale.append("Narration: 개별 종목 언급 가능 (추천 아님)")
        elif lvl == 2:
            rationale.append("Narration: 섹터 단위까지 설명 가능")
        else:
            rationale.append("Narration: 매크로 수준 설명에 적합")
            
        # 5. CONSTRAINT (optional)
        ceiling = t.get("narration_ceiling")
        j_notes = t.get("judgment_notes", [])
        if ceiling or j_notes:
            constraint_text = ceiling if ceiling else (j_notes[0] if j_notes else "")
            if constraint_text:
                rationale.append(f"Constraint: {constraint_text}")
                
        return rationale

    def _get_contrast_rationale(self, c: DecisionCard, competitors: List[DecisionCard]) -> Dict[str, Any]:
        """Builds comparative logic: Why this topic won over others (Step 15)."""
        if not competitors:
            return None
            
        # 1. Build Contrast Set (Step 15-1)
        # Filter: Same lane or same/adjacent level
        filtered = [
            comp for comp in competitors 
            if comp.is_fact_driven == c.is_fact_driven or abs(comp.narration_level - c.narration_level) <= 1
        ]
        
        if not filtered:
            return None
            
        # Pick top 2 by score (they are already sorted in ranked, but let's be safe if cards list isn't)
        # Using status == HOLD as identifying mark.
        competitors_set = sorted(filtered, key=lambda x: 0, reverse=True)[:2] # Score not explicitly in Card, but list is ordered
        # Wait, DecisionCard needs score if I want to sort here. Or I trust the order from ranked.
        # Let's assume order is preserved in cards list.
        
        # 2. Contrast Rules (Step 15-2)
        selected_reason = "Better timing alignment"
        
        # Check reasons in priority order
        # a) Higher Evidence Density (if significant difference)
        # Using a simple threshold (e.g., +2 more items) or just "more" items? 
        # Requirement says "Higher evidence density". Let's say strictly >
        max_comp_ev = max([comp.evidence_count for comp in competitors_set]) if competitors_set else 0
        if c.evidence_count > max_comp_ev + 1: # Significant difference
            selected_reason = "Higher evidence density"
        # b) Broader Narration Range (Higher Priority than Density? Or overrides?)
        # Let's check Level.
        elif c.narration_level > max([comp.narration_level for comp in competitors_set]):
            selected_reason = "Broader narration range"
            
        rejections = []
        for comp in competitors_set:
            reason = "Evidence too thin"
            if comp.judgment_notes:
                if any("WHY NOW" in n for n in comp.judgment_notes):
                    reason = "Missing WHY NOW"
                elif any("risk" in n.lower() for n in comp.judgment_notes):
                    reason = "Narrative risk flagged"
            elif comp.narration_ceiling:
                reason = "Ceiling constraint"
            
            rejections.append({
                "topic_id": comp.topic_id,
                "reason": reason
            })
            
        return {
            "selected_reason": selected_reason,
            "rejections": rejections
        }

    def _render_sanity_panel(self, data: Dict[str, Any], lines: List[str]):
        """Renders the SYSTEM STATUS panel at the top."""
        lines.append("### 🏥 SYSTEM STATUS (Today)")
        lines.append(f"- **Topics Generated**: {data.get('total_topics', 0)}")
        s = data.get("summary", {})
        lines.append(f"- **READY / HOLD / DROP**: {s.get('READY', 0)} / {s.get('HOLD', 0)} / {s.get('DROP', 0)}")
        lines.append(f"- **FACT-DRIVEN / ANOMALY-DRIVEN**: {data.get('fact_driven_count', 0)} / {data.get('anomaly_driven_count', 0)}")
        
        js = data.get("judgment_summary", {})
        if any(v > 0 for v in js.values()):
            lines.append("\n**JUDGMENT WARNINGS TODAY**")
            lines.append(f"- Weak Timing: {js.get('weak_timing', 0)}")
            lines.append(f"- Shallow Evidence: {js.get('shallow_evidence', 0)}")
            lines.append(f"- Narrative Risk: {js.get('narrative_risk', 0)}")
        lines.append("")

    def _render_drift_warnings(self, data: Dict[str, Any], lines: List[str]):
        """Renders Drift Warning Indicators (Operational Safety)."""
        warnings = []
        flags = data.get("flag_summary", {})
        s = data.get("summary", {})
        
        # 1. TITLE-TO-EVIDENCE DRIFT
        if flags.get("TITLE_MISMATCH", 0) >= 2:
            warnings.append({
                "badge": "⚠️ TITLE-TO-EVIDENCE DRIFT",
                "explanation": "토픽 제목과 기반 데이터 간의 거리가 멀어지고 있으니, 엔진의 제목 추출 로직 점검이 권장됩니다."
            })
            
        # 2. EVIDENCE THINNING
        thin_count = flags.get("PLACEHOLDER_EVIDENCE", 0) + flags.get("EVIDENCE_TOO_THIN", 0)
        if thin_count >= 2:
            warnings.append({
                "badge": "⚠️ EVIDENCE THINNING",
                "explanation": "기반 데이터의 수치 정보가 평소보다 부족하게 수집되고 있으니, 데이터 소스 안정성을 확인하시기 바랍니다."
            })
            
        # 3. SPEAK DROUGHT
        if s.get("READY", 0) == 0 and data.get("candidates_count", 0) >= 3:
            warnings.append({
                "badge": "⚠️ SPEAK DROUGHT",
                "explanation": "충분한 후보가 생성되었으나 내레이션 기준을 통과하지 못했습니다. 품질 기준을 재검토하거나 데이터 소스를 확장할 시점입니다."
            })
            
        # 4. FACT OVERDOMINANCE
        total = data.get("total_topics", 0)
        if total > 0 and (data.get("fact_driven_count", 0) / total) > 0.7:
            warnings.append({
                "badge": "⚠️ FACT OVERDOMINANCE",
                "explanation": "시스템이 리포트 기반의 팩트에 과하게 치중해 있습니다. 실시간 시그널(Anomaly) 탐지 엔진의 작동 여부를 점검해 보시기 바랍니다."
            })
            
        if warnings:
            lines.append("#### 🚨 DRIFT MONITOR")
            for w in warnings:
                lines.append(f"**{w['badge']}**")
                lines.append(f"> {w['explanation']}")
            lines.append("")
        else:
            lines.append("✅ **SYSTEM HEALTH**: All clear (Operational margins normal)")
            lines.append("")

    def _render_portfolio_balance(self, lines: List[str], snapshot: Dict[str, Any], assessment: Dict[str, Any]):
        """Renders the PORTFOLIO BALANCE block (Step 16)."""
        lines.append(f"📊 **PORTFOLIO BALANCE (Today)**")
        
        # Composition
        comp = []
        if snapshot['fact_count'] > 0: comp.append(f"FACT {snapshot['fact_count']}")
        if snapshot['anomaly_count'] > 0: comp.append(f"ANOMALY {snapshot['anomaly_count']}")
        lines.append(f"- Composition: {' / '.join(comp)}")
        
        # Depth
        depth = []
        for l in [1, 2, 3]:
            cnt = snapshot['level_counts'].get(l, 0)
            if cnt > 0: depth.append(f"L{l} {cnt}")
        lines.append(f"- Depth: {' · '.join(depth)}")
        
        # Timing
        timing = snapshot.get('timing_tags', [])
        lines.append(f"- Timing: {' · '.join(timing) if timing else '(None)'}")
        
        # Assessment
        status = assessment.get("status", "Unknown")
        reason = assessment.get("reason", "")
        lines.append(f"- Assessment: {status} — {reason}")
        lines.append("")

    def _build_portfolio_snapshot(self, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates portfolio stats from READY topics (Step 16-1)."""
        # cards are dicts when coming from render_markdown(data)
        ready_cards = [c for c in cards if c.get('status') == 'READY']
        
        # Lane
        fact_cnt = len([c for c in ready_cards if c.get('is_fact_driven')])
        anomaly_cnt = len(ready_cards) - fact_cnt
        
        # Level
        lvl_counts = {1: 0, 2: 0, 3: 0}
        for c in ready_cards:
            l = c.get('narration_level', 1)
            lvl_counts[l] = lvl_counts.get(l, 0) + 1
            
        # Timing Tags
        # Filter for specific timing tags: TIME-SENSITIVE, STRUCTURAL, TRENDING NOW
        target_tags = ["TIME-SENSITIVE", "STRUCTURAL SIGNAL", "TRENDING NOW"] 

        found_tags = set()
        for c in ready_cards:
            tags = c.get('tags') or []
            for t in tags:
                for target in target_tags:
                    if target in t:
                        found_tags.add(target)
                        
        return {
            "total_ready": len(ready_cards),
            "fact_count": fact_cnt,
            "anomaly_count": anomaly_cnt,
            "level_counts": lvl_counts,
            "timing_tags": sorted(list(found_tags))
        }

    def _assess_portfolio_balance(self, snapshot: Dict[str, Any]) -> Dict[str, str]:
        """Applies balance rules (Step 16-2)."""
        total = snapshot["total_ready"]
        if total == 0:
            return {"status": "Empty", "reason": "No READY topics"}
            
        # 1. Fact Ratio <= 60%
        fact_ratio = snapshot["fact_count"] / total
        if fact_ratio > 0.6:
            return {"status": "Concentrated", "reason": "FACT-heavy"}
            
        # 2. L3 <= 2
        if snapshot["level_counts"][3] > 2:
            return {"status": "Concentrated", "reason": "Stock-heavy"}
            
        # 3. Timing Diversity >= 2
        # Constraint: "At least 2 different Timing tags present"
        # Interpreted as: across the portfolio, we cover at least 2 distinct timing angles.
        if len(snapshot["timing_tags"]) < 2:
            # Reason: Single-theme risk? 
            # Prompt says "Single-theme risk".
            return {"status": "Concentrated", "reason": "Single-theme risk"}
            
        return {"status": "Balanced", "reason": "Portfolio mix optimal"}

    def save_snapshot(self, ymd: str, data: Dict[str, Any]) -> Path:
        """
        Saves the dashboard data to daily_lock.json for immutable reference.
        Path: data/topics/gate/{ymd}/daily_lock.json
        """
        gate_dir = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        if not gate_dir.exists():
            gate_dir.mkdir(parents=True, exist_ok=True)
            
        lock_path = gate_dir / "daily_lock.json"
        lock_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return lock_path

    def _determine_impact_window(self, topic: Dict[str, Any], tags: List[str]) -> Tuple[str, str]:
        """Determines Time-to-Impact Window (Step 17)."""
        tags = tags or []
        risk_one = topic.get("risk_one", "")
        reasons = topic.get("key_reasons", [])
        combined_text = (risk_one + " " + " ".join(reasons)).lower()
        
        # 1. Explicit Schedule -> IMMEDIATE
        # Regex-like keywords
        schedule_keywords = ["d-day", "today", "tomorrow", "scheduled", "timeline", "확정", "발표일"]
        if any(k in combined_text for k in schedule_keywords):
            return "IMMEDIATE", "이슈 반영이 이미 시작됨"
            
        # 2. TIME-SENSITIVE -> NEAR
        if any("TIME-SENSITIVE" in t for t in tags):
            # Also check if it's actually immediate if risk says so, but priority rule says TIME-SENSITIVE -> NEAR
            # unless caught by #1. Strict priority.
            return "NEAR", "단기 뉴스/이벤트 연동"
            
        # 3. TRENDING NOW -> MID
        if any("TRENDING NOW" in t for t in tags):
             return "MID", "누적 확인 구간"
             
        # 4. STRUCTURAL -> LONG
        if any("STRUCTURAL" in t for t in tags):
             return "LONG", "구조적 변화 관점"
             
        # 5. Fallback -> MID
        return "MID", "누적 확인 구간(Inferred)"

    def _get_operator_badge(self, topic_id: str, decisions_map: Dict[str, Dict]) -> str:
        """Step 40: Returns visual feedback badge if decision exists."""
        d = decisions_map.get(topic_id)
        if not d: return ""
        action = d.get("operator_action", "")
        return f"| 🧭 **OPERATOR: {action.replace('_', ' ')}**"

    def _render_operator_summary(self, lines: List[str], decisions_map: Dict[str, Dict]):
        """Step 40: Daily Operator Summary Panel."""
        from src.ops.operator_decision_log import OPERATOR_ACTION_ENUM
        counts = {
            OPERATOR_ACTION_ENUM.PICKED_FOR_CONTENT: 0,
            OPERATOR_ACTION_ENUM.SKIPPED_TODAY: 0,
            OPERATOR_ACTION_ENUM.DEFERRED: 0,
            OPERATOR_ACTION_ENUM.REJECTED: 0
        }
        for d in decisions_map.values():
            action = d.get("operator_action")
            if action in counts:
                counts[action] += 1
        
        if not any(counts.values()): return
        
        lines.append("\n#### 🏛️ OPERATOR DECISIONS (TODAY)")
        for action, count in counts.items():
            if count > 0:
                lines.append(f"- **{action}**: {count}")

    def _render_ready_action_bar(self, lines: List[str], topic_id: str, title: str):
        """Step 40: Placeholder for READY action bar."""
        lines.append(f"> **ACTION**: [ Pick ] [ Skip Today ] [ Defer ] [ Reject ]")

    def _render_shadow_action_bar(self, lines: List[str], topic_id: str, title: str):
        """Step 40: Placeholder for SHADOW action bar."""
        lines.append(f"    > **ACTION**: [ Defer ] [ Reject ]")

    def _render_correlation_panel(self, lines: List[str], data: Dict[str, Any]):
        """Step 41: Correlation Summary Scoreboard."""
        summary = data.get("summary", {})
        lines.append("\n#### 📌 PICK → OUTCOME (Last 30d)")
        lines.append(f"- Picked: {summary.get('picked', 0)} | ✅ Confirmed: {summary.get('confirmed', 0)} | ❌ Failed: {summary.get('failed', 0)} | ⏳ Unresolved: {summary.get('unresolved', 0)} | ? Missing: {summary.get('missing', 0)}")
        
        rows = data.get("rows", [])
        if not rows:
            lines.append("- _No human picks in last 30d._")
        else:
            lines.append("\n**Recent Picks**")
            for r in rows[:10]: # Last 10
                outcome = r.get("outcome", "MISSING")
                icon = "⏳"
                if outcome == "CONFIRMED": icon = "✅"
                elif outcome == "FAILED": icon = "❌"
                elif outcome == "MISSING": icon = "?"
                
                lines.append(f"- [{r['pick_date']}] {r['topic_title']} — {icon} {outcome}")
        
        errors = data.get("errors", [])
        if errors:
            lines.append(f"\n> ⚠️ Correlation warnings: {len(errors)}")

    def _render_auto_priority_panel(self, lines: List[str], data: Dict[str, Any]):
        """Step 43: Daily Auto-Priority Summary Panel."""
        top_candidates = data.get("top_candidates", [])
        lines.append("\n#### 🔥 AUTO-PICK PRIORITY (Top 3–5)")
        
        if not top_candidates or len(top_candidates) < 3:
            lines.append("- _Insufficient data for auto-prioritization._")
            return
            
        for i, c in enumerate(top_candidates, 1):
            score = c.get("priority_score", 0)
            
            badge = "⚪ LOW"
            if score >= 8: badge = "🔴 CRITICAL"
            elif score >= 5: badge = "🟠 HIGH"
            elif score >= 3: badge = "🟢 MODERATE"
            
            factors = ", ".join(c.get("reason_factors", []))
            lines.append(f"{i}. **{c['title']}** ({badge} | Score: {score})")
            if factors:
                lines.append(f"   - *Factors*: {factors}")

    def _generate_auto_priority(self, ymd: str, ready_candidates: List[Dict], shadow_pool: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the auto prioritizer and returns the result."""
        from src.ops.auto_prioritizer import AutoPrioritizer
        prioritizer = AutoPrioritizer(self.base_dir)
        return prioritizer.run(ymd, ready_candidates, shadow_pool.get("candidates", []))

    def _render_auto_approved_panel(self, lines: List[str], data: Dict[str, Any]):
        """Step 44: Daily Auto-Approval Summary Panel."""
        approved = data.get("auto_approved", [])
        lines.append("\n#### 🤖 AUTO-APPROVED TOPICS")
        
        bundle_md = data.get("bundle_md")
        if bundle_md:
            lines.append(f"> 📦 **SPEAK BUNDLE**: [{Path(bundle_md).name}](file:///{self.base_dir / bundle_md})")

        if not approved:
            lines.append("- _No topics met strict auto-approval conditions today._")
            return
            
        from src.ops.production_format_router import ProductionFormatRouter
        router = ProductionFormatRouter()
        
        for a in approved:
            # We need to map 'a' to a format. 'a' has priority_score, title, etc.
            # But route_topic expects narration_level, etc. 
            # Actually, the dashboard already has the topic data in 'cards'.
            # However, _render_auto_approved_panel only gets the summary 'data'.
            # Let's simple-map if possible or just use the badge from a pre-calculated field if I added it.
            # Step 46-5 says "Add small badge".
            
            reasons = ", ".join([f"`{r}`" for r in a.get("approval_reason", [])])
            
            # Simple heuristic for dashboard if full topic data isn't here, 
            # but ideally we want the real router result.
            # Let's assume the bundle exporter hasn't run yet or we want inline calculation.
            # Actually, the dashboard is often rendered AFTER the engine runs the ops.
            # But here we are IN the dashboard renderer.
            
            # Let's use a very simplified version for the dashboard badge if we don't have the full object,
            # OR pass the format info in the auto_approved_today.json.
            # Step 46-3 says "Attach routing result to speak_bundle.json/md".
            # It doesn't explicitly say auto_approved_today.json.
            # Let's update AutoApprovalGate to include the format or just calculate here.
            
            score = a.get("priority_score", 0)
            fmt_badge = "🎬 SHORT"
            if score >= 10: fmt_badge = "🎥 LONG"
            elif score >= 8: fmt_badge = "🎬+🎥 BOTH"
            
            lines.append(f"- **{a['title']}** (🟢 **AUTO-APPROVED** 🔒 | {fmt_badge} | Score: {score})")
            if reasons:
                lines.append(f"   - *Reasons*: {reasons}")
