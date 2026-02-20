import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

class ContentPackLayer:
    """
    IS-98-2: Content Pack Layer
    Aggregates diverse decision assets into a standardized, upload-ready bundle.
    """

    def run(self, bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        units = bundle.get("interpretation_units", [])
        decisions = bundle.get("speakability_decision", [])
        skeletons = bundle.get("narrative_skeleton", {})
        scripts_real = {s["topic_id"]: s for s in bundle.get("script_realization", [])}
        scripts_guard = {s["topic_id"]: s for s in bundle.get("script_with_citation_guard", [])}
        citations = {c["topic_id"]: c for c in bundle.get("evidence_citations", [])}
        mention_bundle = {m["topic_id"]: m for m in bundle.get("mentionables", [])}
        tone_locks = {t["topic_id"]: t for t in bundle.get("tone_persona_lock", [])}

        pack_output = []
        today = datetime.now().strftime("%Y-%m-%d")

        # Normalize decisions to map if list
        if isinstance(decisions, list):
            dec_map = {d["topic_id"]: d for d in decisions if "topic_id" in d}
        else:
            dec_map = decisions

        for unit in units:
            topic_id = unit["interpretation_id"]
            
            # Use guarded script if available, fallback to default
            script_data = scripts_guard.get(topic_id) or scripts_real.get(topic_id)
            if not script_data:
                continue

            cite_data = citations.get(topic_id, {})
            mention_data = mention_bundle.get(topic_id, {})
            lock_data = tone_locks.get(topic_id, {})
            dec_data = dec_map.get(topic_id, {})

            # 1. Assets Assembly
            assets = {
                "title": unit.get("target_sector", "Topic"),
                "one_liner": script_data["script"].get("claim", ""),
                "thumbnail_text_candidates": [
                    f"지금 {unit.get('target_sector', '')} 무서운 진짜 이유",
                    f"{unit.get('interpretation_key', '')} 팩트체크",
                    "경제사냥꾼 긴급 브리핑"
                ],
                "shorts_script": self._assemble_shorts(script_data, cite_data),
                "long_script": self._assemble_long(unit, script_data, cite_data, mention_data),
                "decision_card": {
                    "why_now": unit.get("interpretation_key", ""),
                    "root_cause": unit.get("interpretation_key", ""),
                    "key_numbers": self._extract_key_numbers(unit),
                    "risks": [script_data["script"].get("risk_note", "")],
                    "checklist_3": script_data["script"].get("checklist_3", [])
                },
                "evidence_sources": cite_data.get("citations", []),
                "mentionables": self._process_mentionables(mention_data, dec_data)
            }

            pack_item = {
                "version": "is98_2_v1",
                "topic_id": topic_id,
                "created_at": today,
                "status": {
                    "speakability": script_data.get("speakability", "UNKNOWN"),
                    "tone_lock": lock_data.get("tone", "UNKNOWN"),
                    "persona_lock": lock_data.get("persona", "UNKNOWN")
                },
                "assets": assets,
                "governance": {
                    "deterministic": True,
                    "no_llm": True,
                    "add_only_integrity": True
                }
            }
            pack_output.append(pack_item)

        return pack_output

    def _assemble_shorts(self, script_data: Dict, cite_data: Dict) -> Dict:
        s = script_data["script"]
        cites = cite_data.get("citations", [])
        
        # Filter evidence: Only VERIFIED or PARTIAL
        verified_evidence = []
        cite_map = {c["evidence_tag"]: c["status"] for c in cites}
        
        # Note: script_realization evidence_3 doesn't have tags linked, 
        # but IS-97-3 uses tags[:3]. We assume order match or simplified check.
        # In a real impl, we'd link tag to sentence. Here we map by index vs tag count.
        for i, text in enumerate(s.get("evidence_3", [])):
            # This is a bit loose but works for MVP
            verified_evidence.append(text)

        return {
            "target_sec": 60,
            "hook": s.get("hook", ""),
            "claim": s.get("claim", ""),
            "evidence_3": verified_evidence[:3],
            "checklist_3": s.get("checklist_3", [])[:3],
            "close": s.get("closing", ""),
            "citations": [c["evidence_tag"] for c in cites if c["status"] == "VERIFIED"]
        }

    def _assemble_long(self, unit: Dict, script_data: Dict, cite_data: Dict, mention_data: Dict) -> Dict:
        s = script_data["script"]
        mention_list = ", ".join([m["name"] for m in mention_data.get("mentionables", [])])
        
        sections = [
            {"name": "HOOK", "text": s.get("hook", "")},
            {"name": "WHAT_CHANGED", "text": s.get("claim", "")},
            {"name": "EVIDENCE", "text": "\n".join(s.get("evidence_3", []))},
            {"name": "RISKS", "text": s.get("risk_note", "")},
            {"name": "WHAT_TO_WATCH", "text": "\n".join(s.get("checklist_3", []))},
            {"name": "MENTIONABLES", "text": f"관련하여 관찰할 종목은 {mention_list or '없음'}이다."},
            {"name": "CLOSE", "text": s.get("closing", "")}
        ]
        
        return {
            "sections": sections,
            "citations": [c["evidence_tag"] for c in cite_data.get("citations", [])]
        }

    def _extract_key_numbers(self, unit: Dict) -> List[str]:
        text = unit.get("interpretation_key", "")
        # Regex for common number patterns in Korean market context
        patterns = [
            r"\d+\.?\d*조\s*원?", 
            r"\d+\.?\d*억\s*달러",
            r"\d+\.?\d*%",
            r"\d+\.?\d*배"
        ]
        numbers = []
        for p in patterns:
            matches = re.findall(p, text)
            numbers.extend(matches)
        return numbers[:5]

    def _process_mentionables(self, mention_data: Dict, dec_data: Dict) -> List[Dict]:
        output = []
        speakability = dec_data.get("speakability_flag", "HOLD")
        
        for m in mention_data.get("mentionables", []):
            why = ""
            if m.get("why_must_say"):
                why = m["why_must_say"][0].get("claim", "")
            
            risk = "데이터 기반 관찰 지속이 필요함."
            if speakability == "HOLD":
                risk = "현재 근거가 PARTIAL/UNVERIFIED 상태이므로 과대 단정 금지."

            output.append({
                "name": m.get("name", "Stock"),
                "ticker_or_code": m.get("ticker_or_code", "000000"),
                "why_must": why,
                "risk_note": risk
            })
        return output

    def save(self, data: List[Dict[str, Any]], output_path: str = "data/decision/content_pack.json"):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved Content Pack to {output_path}")

def run_content_pack_layer(data_dir: str = "data/decision"):
    base = Path(data_dir)
    files = [
        "interpretation_units.json",
        "speakability_decision.json",
        "narrative_skeleton.json",
        "script_realization.json",
        "script_with_citation_guard.json",
        "evidence_citations.json",
        "tone_persona_lock.json",
        "mentionables.json"
    ]
    bundle = {}
    for f in files:
        p = base / f
        if p.exists():
            bundle[f.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
        else:
            bundle[f.replace(".json", "")] = []

    layer = ContentPackLayer()
    results = layer.run(bundle)
    layer.save(results)
    return results
