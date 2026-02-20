import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

class EvidenceCitationLayer:
    """
    IS-98-1: Evidence Citation Layer
    Matches claims to official sources and adjusts script tone for unverified evidence.
    """

    def __init__(self, registry_path: str = "registry/sources/source_registry_v1.yml"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Source registry not found at {self.registry_path}")
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def run(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        units = bundle.get("interpretation_units", [])
        scripts = bundle.get("script_realization", [])
        
        citations_output = []
        guarded_scripts = []

        # 1. Process Citations
        for unit in units:
            topic_id = unit["interpretation_id"]
            topic_citations = self._find_citations(unit)
            
            citations_output.append({
                "topic_id": topic_id,
                "version": "is98_1_v1",
                "citations": topic_citations,
                "governance": {
                    "deterministic": True,
                    "no_llm": True,
                    "add_only_integrity": True
                }
            })

            # 2. Process Script Guard
            # Find the script realization for this topic
            script = next((s for s in scripts if s["topic_id"] == topic_id), None)
            if script:
                guarded_script = self._apply_tone_guard(script, topic_citations)
                guarded_scripts.append(guarded_script)

        return {
            "evidence_citations": citations_output,
            "script_with_citation_guard": guarded_scripts
        }

    def _find_citations(self, unit: Dict[str, Any]) -> List[Dict[str, Any]]:
        tags = unit.get("evidence_tags", [])
        key_text = unit.get("interpretation_key", "").lower()
        
        topic_citations = []
        
        # We look at each evidence tag and try to match it in the registry
        for tag in tags:
            found_sources = []
            for rule in self.registry.get("rules", []):
                match_cfg = rule["match"]
                if match_cfg["evidence_tag"] == tag:
                    # Check for keyword match
                    if any(kw.lower() in key_text for kw in match_cfg.get("contains_any", [])):
                        found_sources.extend(rule["sources"])
            
            status = "VERIFIED" if found_sources else "UNVERIFIED"
            
            topic_citations.append({
                "evidence_tag": tag,
                "status": status,
                "sources": found_sources
            })
            
        return topic_citations

    def _apply_tone_guard(self, script_data: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        # If any citation is UNVERIFIED, downgrade the tone
        has_unverified = any(c["status"] == "UNVERIFIED" for c in citations)
        
        guarded_script = script_data.copy()
        if has_unverified:
            # Downgrade strings in the script
            # Example mapping based on IS-98-1 rules
            def downgrade(text: str) -> str:
                # Basic deterministic replacements
                new_map = {
                    "다.": "다. (관찰 중)",
                    "야.": "야. (해석 필요)",
                    "게.": "게. (관찰 구간)",
                    "이다.": "로 해석된다."
                }
                # Sort by length descending to match longest pattern first (e.g., '이다.' vs '다.')
                for old in sorted(new_map.keys(), key=len, reverse=True):
                    if text.endswith(old):
                        return text[:-len(old)] + new_map[old]
                return text + " (데이터 확인 필요)"

            s = guarded_script.get("script", {})
            guarded_script["script"] = {
                "hook": downgrade(s.get("hook", "")),
                "claim": downgrade(s.get("claim", "")),
                "evidence_3": [downgrade(e) for e in s.get("evidence_3", [])],
                "checklist_3": s.get("checklist_3", []), # Checklist remains same
                "risk_note": s.get("risk_note", ""),
                "closing": downgrade(s.get("closing", ""))
            }
            guarded_script["tone"] = "CAUTIONARY"
            
        return guarded_script

    def save(self, output: Dict[str, Any], output_dir: str = "data/decision"):
        base = Path(output_dir)
        base.mkdir(parents=True, exist_ok=True)
        
        with open(base / "evidence_citations.json", "w", encoding="utf-8") as f:
            json.dump(output["evidence_citations"], f, ensure_ascii=False, indent=2)
            
        with open(base / "script_with_citation_guard.json", "w", encoding="utf-8") as f:
            json.dump(output["script_with_citation_guard"], f, ensure_ascii=False, indent=2)
            
        print(f"[OK] Saved citations and guarded scripts to {base}")

def run_citation_layer(data_dir: str = "data/decision"):
    base = Path(data_dir)
    bundle = {}
    files = ["interpretation_units.json", "script_realization.json"]
    for f in files:
        p = base / f
        if p.exists():
            bundle[f.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
        else:
            bundle[f.replace(".json", "")] = []

    layer = EvidenceCitationLayer()
    output = layer.run(bundle)
    layer.save(output)
    return output
