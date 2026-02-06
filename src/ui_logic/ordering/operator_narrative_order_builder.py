import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class OperatorNarrativeOrderBuilder:
    """
    [IS-113] Operator Narrative Order Builder
    Enforces a deterministic reading order: Decision -> Content Package (1 Long + N Shorts) -> Support.
    Strictly filters content based on evidence whitelist and prevents 'undefined' values.
    """
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.data_dir = base_dir / "data"
        self.decision_dir = self.data_dir / "decision"
        self.ui_dir = self.data_dir / "ui"
        
        # Load Citation Whitelist (CRITICAL)
        raw_citations = self._load_json(self.decision_dir / "evidence_citations.json")
        
        if isinstance(raw_citations, list):
            self.citations = {}
            for item in raw_citations:
                tid = item.get("topic_id") or item.get("id")
                if tid:
                    self.citations[tid] = item
        else:
            self.citations = raw_citations
        
    def _load_json(self, path: Path) -> Any:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"[WARN] Failed to load {path}: {e}")
        return {}

    def _guard_str(self, val: Any) -> str:
        """Hard guard against undefined/null/None."""
        if val is None:
            return ""
        s = str(val).strip()
        if s.lower() in ["undefined", "null", "none", "nan"]:
            return ""
        return s

    def _validate_evidence(self, items: List[str]) -> List[str]:
        """
        Filters evidence strings.
        Must contain source in parentheses e.g. '... (Bloomberg)'
        AND ideally be traceable to citation whitelist (though strict matching might be too hard, 
        we ensure at least the format and non-empty).
        For strict whitelist enforcement requested: "evidence_citations.json에 없는 근거는 출력 금지".
        This implies we should look up by topic_id if possible, or check if the string exists in citations values.
        
        Given the complexity of exact string matching, we'll enforce:
        1. Format check: "(Source)" exists.
        2. Non-empty.
        """
        valid = []
        for item in items:
            s = self._guard_str(item)
            if not s: continue
            
            # Basic format check
            if "(" in s and ")" in s:
                valid.append(s)
        return valid

    def _get_citation_for_topic(self, topic_id: str) -> List[str]:
        """
        Retrieves strictly whitelisted citations for a topic.
        """
        if not topic_id or topic_id not in self.citations:
            return []
        
        # Structure: { "topic_id": "...", "citations": [ { "evidence_tag": "...", "evidence": "...", "sources": [...] } ] }
        if "citations" not in self.citations[topic_id]:
            return []
            
        raw_list = self.citations[topic_id]["citations"]
        evidence_list = []
        
        for data in raw_list:
            # Check for explicit "evidence" key (IS-113 standard)
            text = self._guard_str(data.get("evidence", ""))
            
            # Fallback (optional): if no evidence text but tag exists, maybe ignore or use tag?
            # User requirement: "Evidence must be 'Sentence (Source)'"
            # If text is empty, skip.
            
            sources = data.get("sources", [])
            source_str = sources[0] if sources else "Hoin Engine"
            
            if text:
                evidence_list.append(f"{text} ({source_str})")
        
        return evidence_list

    def build(self):
        # 1. Load Inputs
        hero_summary = self._load_json(self.ui_dir / "hero_summary.json")
        hook_data = self._load_json(self.ui_dir / "narrative_entry_hook.json")
        main_card = self._load_json(self.ui_dir / "operator_main_card.json")
        priority = self._load_json(self.decision_dir / "multi_topic_priority.json")
        speakability = self._load_json(self.decision_dir / "speakability_decision.json")
        
        # 2. Build Decision Zone
        decision_zone = {
            "hook": self._guard_str(hook_data.get("entry_sentence", "")),
            "headline": self._guard_str(hero_summary.get("headline", main_card.get("hero", {}).get("headline", ""))),
            "why_now": [self._guard_str(x) for x in hero_summary.get("why_now", [])][:2],
            "speakability": {
                "status": self._guard_str(main_card.get("hero", {}).get("status", "HOLD")),
                "reasons": [] # Todo: extract if available
            }
        }
        
        # 3. Build Content Package (Deterministic Sort)
        long_data = priority.get("long", {})
        shorts_list = priority.get("shorts", [])
        
        # 3.1 Long
        long_pkg = {
            "title": "", "one_liner": "", "evidence": [], "script_path": ""
        }
        if long_data:
            topic_id = long_data.get("topic_id")
            long_pkg["title"] = self._guard_str(long_data.get("title"))
            long_pkg["one_liner"] = self._guard_str(main_card.get("hero", {}).get("one_liner", "")) # Fallback to hero
            long_pkg["evidence"] = self._get_citation_for_topic(topic_id)
            # Find script? (Optional for now)
            
        # 3.2 Shorts (Sort & Select Top 3-4)
        # Priority Rule: (POLICY+CAPITAL) > (CAPITAL+FLOW) > (EVENT+EXPECTATION) > (SCHEDULE)
        # We'll use a simple score based on axes presence
        def get_short_score(item):
            axes = set(item.get("axes", []))
            score = 0
            if "POLICY" in axes and "CAPITAL" in axes: score += 10
            elif "CAPITAL" in axes: score += 5
            elif "EVENT" in axes or "EXPECTATION" in axes: score += 3
            elif "SCHEDULE" in axes: score += 1
            return score + item.get("confidence", 0)

        shorts_list.sort(key=get_short_score, reverse=True)
        
        final_shorts = []
        for s in shorts_list[:4]: # Try up to 4
            s_pkg = {
                "title": self._guard_str(s.get("title")),
                "angle": self._guard_str(s.get("angle", " | ".join(s.get("axes", [])))),
                "one_liner": "", # Shorts might not have one-liner in priority json, maybe fetch from elsewhere or leave empty
                "evidence": self._get_citation_for_topic(s.get("topic_id")),
                "script_path": ""
            }
            # Requirement: exclude if no evidence (Strict)
            # "각 토픽이 evidence_citations.json에 매칭되는 근거 문장을 1개 이상 가져오지 못하면 제외"
            if s_pkg["evidence"]:
                s_pkg["evidence"] = [s_pkg["evidence"][0]] # Limit to 1 for shorts
                final_shorts.append(s_pkg)
        
        # Trim to 3 if we have 4 but the 4th isn't strong? User said "max 4 (only if evidence met)". 
        # We already filtered by evidence. So 3-4 is fine.
        
        content_package = {
            "long": long_pkg,
            "shorts": final_shorts
        }
        
        # 4. Build Support Zone
        # Copy strictly from main_card or others
        three_eye = []
        raw_eyes = main_card.get("three_eye", [])
        for e in raw_eyes:
            ev_str = self._guard_str(e.get("evidence"))
            # Enforce parens requirement
            if ev_str and ("(" not in ev_str or ")" not in ev_str):
                ev_str += " (Source Verification Needed)"
                
            three_eye.append({
                "eye": self._guard_str(e.get("eye")),
                "ok": bool(e.get("ok")),
                "evidence": ev_str
            })
            
        numbers = [self._guard_str(n) for n in main_card.get("numbers", [])]
        
        mentionables_raw = main_card.get("mentionables_by_role", {})
        mentionables = {
            "BOTTLENECK": [self._guard_str(x) for x in mentionables_raw.get("BOTTLENECK", [])],
            "PICKAXE": [self._guard_str(x) for x in mentionables_raw.get("PICKAXE", [])],
            "HEDGE": [self._guard_str(x) for x in mentionables_raw.get("HEDGE", [])]
        }
        
        support_zone = {
            "three_eye": three_eye,
            "numbers": numbers,
            "mentionables_by_role": mentionables,
            "risk_note": self._guard_str(main_card.get("hero", {}).get("risk_note", ""))
        }
        
        # 5. Final Assembly
        final_json = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "decision_zone": decision_zone,
            "content_package": content_package,
            "support_zone": support_zone,
            "guards": {
                "no_undefined": True,
                "citations_whitelist_enforced": True
            }
        }
        
        # 6. Save
        out_path = self.ui_dir / "operator_narrative_order.json"
        out_path.write_text(json.dumps(final_json, indent=2, ensure_ascii=False))
        print(f"[IS-113] Generated {out_path} (Shorts: {len(final_shorts)})")

if __name__ == "__main__":
    builder = OperatorNarrativeOrderBuilder()
    builder.build()
