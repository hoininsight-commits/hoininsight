import json
from pathlib import Path
from typing import Dict, List, Any
import yaml
from dataclasses import dataclass, asdict

@dataclass
class DecisionCard:
    topic_id: str
    title: str
    status: str
    reason: str
    evidence_count: int
    raw_score: float
    flags: List[str]
    speak_pack: Dict[str, Any] = None
    evidence_refs: List[Dict[str, Any]] = None
    tags: List[str] = None
    why_today: str = None
    bridge_eligible: bool = False
    is_fact_driven: bool = False

class DecisionDashboard:
    """
    Renders human-readable Decision Dashboard from read-only outputs.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
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
        
        cards = []
        status_counts = {"READY": 0, "HOLD": 0, "DROP": 0}
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
                is_fact_driven=self._check_fact_driven(t)
            ))
            
        # 3. Sort (Presentation Only)
        # Groups: READY -> HOLD -> DROP
        # Within: Score desc
        cards.sort(key=lambda x: (
            {"READY": 0, "HOLD": 1, "DROP": 2}.get(x.status, 3), 
            -x.raw_score
        ))
        
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
            "has_fact_driven_candidate": any(c.is_fact_driven for c in cards if c.status != 'READY')
        }

    def render_markdown(self, data: Dict[str, Any]) -> str:
        lines = []
        cards = data.get("cards", [])
        
        # Partition Topics
        ready_topics = [c for c in cards if c['status'] == 'READY']
        hold_topics = [c for c in cards if c['status'] == 'HOLD']
        drop_topics = [c for c in cards if c['status'] == 'DROP']
        
        lines.append("\n## DECISION DASHBOARD (Beta)\n")
        
        # SCRIPT QUALITY Counters
        s = data.get("summary", {})
        lines.append(f"**SCRIPT QUALITY**: 🟢 READY={s.get('READY',0)} | 🟡 HOLD={s.get('HOLD',0)} | 🔴 DROP={s.get('DROP',0)}")
        
        # WHY NO SPEAK Panel (if needed)
        if not ready_topics:
            self._render_no_speak_panel(lines, data)
        
        # --- SECTION 1: TODAY - SPEAKABLE (READY) ---
        lines.append(f"\n## 🎬 TODAY — SPEAKABLE TOPICS ({len(ready_topics)})")
        lines.append("※ 시스템은 선택하지 않습니다. 아래는 오늘 설명 가능한 후보 요약입니다.")
        
        if not ready_topics:
            lines.append("- (No topics ready for broadcast today)")
        else:
            # Top 3-5 Rule
            # High Priority: Top 5
            primary = ready_topics[:5]
            secondary = ready_topics[5:]
            
            lines.append("**🎯 RECOMMENDED FOR TODAY**")
            for c in primary:
                lines.append(self._render_ready_card(c))
                
            if secondary:
                lines.append("\n**Additional READY (Optional)**")
                for c in secondary:
                    # Minimal render for secondary
                    tags_str = ""
                    if c.get('tags'):
                        tags_str = " " + " ".join(c['tags'])
                    lines.append(f"- {c['title']} (Evidence: {c['evidence_count']}){tags_str}")
        
        # --- ALMOST CANDIDATES ---
        self._render_almost_candidates(cards, lines)
        
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
            badge = "🟡" if c['status'] == 'HOLD' else "🔴"
            status_text = "HOLD" if c['status'] == 'HOLD' else "DROP"
            
            # Normalized Reason
            reason = self._get_hold_reason(c) if c['status'] == 'HOLD' else c['reason']
            reason = reason.replace("아직 말하지 않는 이유: ", "") # Simplify for bullet
            
            # Bridge
            bridge_mk = "🌉 Bridge Capable" if c.get('bridge_eligible') else ""
            
            lines.append(f"### {badge} {c['title']} ({status_text})")
            lines.append(f"- **Reason**: {reason}")
            if bridge_mk:
                 lines.append(f"- **Note**: {bridge_mk}")
            
            # Context stats
            ev_cnt = c.get('evidence_count', 0)
            lines.append(f"- **Evidence**: {ev_cnt} items")
            lines.append("")

    def _render_ready_card(self, c: Dict) -> str:
        """Renders the detailed READY card with Speak Pack."""
        lines = []
        title_suffix = " (FACT-DRIVEN (Rule v1))" if c.get('is_fact_driven') else ""
        lines.append(f"\n### ✅ {c['title']}{title_suffix}") 
        
        # Tags Line
        tags = c.get('tags', [])
        if tags:
            lines.append(" ".join(tags))
            
        why = c.get('why_today')
        if why:
            lines.append(f"**오늘 찍는 이유**: {why}")
            
        lines.append(f"**판단 요약**: 지금 설명 가능한 최소 조건 충족 (증거 {c['evidence_count']}건)")
        
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
            
        lines.append("---")
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

    def _check_fact_driven(self, topic: Dict) -> bool:
        """Checks if a topic matches FACT-DRIVEN rules via metadata or tags."""
        if topic.get("is_fact_driven") or topic.get("metadata", {}).get("is_fact_driven"):
            return True
        
        # Check tags for FACT_ prefix
        tags = topic.get("tags", [])
        if any(isinstance(tag, str) and tag.startswith("FACT_") for tag in tags):
            return True
            
        return False

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
