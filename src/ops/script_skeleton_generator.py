import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ScriptSkeletonGenerator:
    """
    Step 47: Script Skeleton Generator v1.0 (Structure-Only).
    Converts speak pack data into standardized script skeletons.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def run(self, ymd: str, bundle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates skeletons for all topics in the speak bundle.
        bundle_data is expected to be the content of speak_bundle.json.
        """
        topics = bundle_data.get("topics", [])
        y, m, d = ymd.split("-")
        skeleton_dir = self.base_dir / "data" / "ops" / "bundles" / y / m / d / "skeletons"
        skeleton_dir.mkdir(parents=True, exist_ok=True)
        
        items = []
        count_short = 0
        count_long = 0
        
        for t in topics:
            fmt = t.get("production_format", "SHORT_ONLY")
            tid = t.get("topic_id")
            
            short_path = None
            long_path = None
            
            if fmt in ["SHORT_ONLY", "BOTH"]:
                short_path = skeleton_dir / f"topic_{tid}_short.md"
                short_path.write_text(self._generate_short_skeleton(t), encoding="utf-8")
                count_short += 1
                
            if fmt in ["LONG_ONLY", "BOTH"]:
                long_path = skeleton_dir / f"topic_{tid}_long.md"
                long_path.write_text(self._generate_long_skeleton(t), encoding="utf-8")
                count_long += 1
                
            items.append({
                "topic_id": tid,
                "short_md": str(short_path.relative_to(self.base_dir)) if short_path else None,
                "long_md": str(long_path.relative_to(self.base_dir)) if long_path else None
            })
            
        index_json = {
            "run_date": ymd,
            "count_short": count_short,
            "count_long": count_long,
            "items": items
        }
        
        index_path = skeleton_dir / "skeleton_index.json"
        index_path.write_text(json.dumps(index_json, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return index_json

    def _generate_short_skeleton(self, t: Dict[str, Any]) -> str:
        sp = t.get("speak_pack", {})
        nums = sp.get("numbers", [])
        nums_lines = "\n".join([f"- {n}" for n in nums[:3]]) if nums else "- (no numeric evidence)"
        
        refs = t.get("evidence_refs", [])
        refs_lines = "\n".join([f"- {r.get('publisher', 'Unknown')} — {r.get('url', '#')}" for r in refs]) if refs else "No verifiable evidence available"
        
        lines = [
            f"# TITLE\n{t.get('title')}\n",
            f"## ONE-LINER\n{sp.get('one_liner', 'N/A')}\n",
            f"## NUMBERS (max 3)\n{nums_lines}\n",
            f"## WHY NOW (from impact_tag + speak_pack context)",
            f"- Impact: {t.get('impact_tag', 'N/A')}",
            f"- Note: (Ref: Risk Note/Watch Next) {sp.get('risk_note', 'None')}\n",
            f"## EVIDENCE REFS\n{refs_lines}\n",
            f"## CTA (Fixed text, no hype)",
            f"- \"핵심 수치와 근거는 위 링크로 확인 가능. 다음 확인 포인트는 Watch Next 참고.\""
        ]
        return "\n".join(lines)

    def _generate_long_skeleton(self, t: Dict[str, Any]) -> str:
        sp = t.get("speak_pack", {})
        nums = sp.get("numbers", [])
        nums_lines = "\n".join([f"- {n}" for n in nums[:3]]) if nums else "- (no numeric evidence)"
        
        refs = t.get("evidence_refs", [])
        refs_lines = "\n".join([f"- {r.get('publisher', 'Unknown')} — {r.get('url', '#')}" for r in refs]) if refs else "No verifiable evidence available"
        
        wn = sp.get("watch_next", [])
        wn_lines = "\n".join([f"- {w}" for w in wn]) if wn else "- No specific follow-up provided"
        
        lines = [
            f"# TITLE\n{t.get('title')}\n",
            f"## OPENING (2 lines, structure-only)",
            f"- Hook: {sp.get('one_liner', 'N/A')}",
            f"- Frame: \"오늘은 근거(수치/출처) 기준으로만 정리합니다.\"\n",
            f"## FACTS / SIGNALS (no new claims)",
            f"### Numbers",
            f"{nums_lines}\n",
            f"### Evidence",
            f"{refs_lines}\n",
            f"## WHAT TO WATCH NEXT (2~3)\n{wn_lines}\n",
            f"## RISK NOTE (verbatim from speak_pack.risk_note or default)\n- {sp.get('risk_note', 'None')}\n",
            f"## OUTRO (Fixed text)",
            f"- \"이 토픽은 예측이 아니라 근거 기반 정리입니다. 추적 신호가 업데이트되면 재점검합니다.\""
        ]
        return "\n".join(lines)
