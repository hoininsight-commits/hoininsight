import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

class MentionablesLayer:
    """
    IS-97-4: Mentionables Layer
    Links topics to specific stocks based on strict data-backed evidence.
    """

    def __init__(self, registry_path: str = "registry/mappings/mentionables_map_v1.yml"):
        self.registry_path = Path(registry_path)
        self.mapping = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return {"groups": []}
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def run(self, decision_bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        units = decision_bundle.get("interpretation_units", [])
        realizations = decision_bundle.get("script_realization", [])
        
        # Mapping by topic_id
        realization_map = {r["topic_id"]: r for r in realizations}
        mentionables_output = []

        for unit in units:
            topic_id = unit["interpretation_id"]
            realization = realization_map.get(topic_id)
            if not realization:
                continue

            # Candidate selection based on triggers
            candidates = self._get_candidates(unit)
            
            # Filtering and justification
            validated_mentionables = []
            for candidate in candidates:
                mentionable = self._validate_and_justify(candidate, unit)
                if mentionable:
                    validated_mentionables.append(mentionable)

            # Build output per topic
            mentionables_output.append({
                "topic_id": topic_id,
                "version": "is97_4_v1",
                "speakability": realization.get("speakability", "DROP"),
                "mentionables": validated_mentionables,
                "governance": {
                    "deterministic": True,
                    "no_llm": True,
                    "add_only_integrity": True,
                    "no_unbacked_stock_calls": True
                }
            })

        return mentionables_output

    def _get_candidates(self, unit: Dict[str, Any]) -> List[Dict[str, Any]]:
        tags = unit.get("evidence_tags", [])
        raw_text = unit.get("interpretation_key", "").lower()
        candidates = []
        seen_codes = set()

        for group in self.mapping.get("groups", []):
            match_found = False
            for trigger in group.get("triggers", []):
                if trigger["tag"] in tags:
                    for keyword in trigger.get("contains", []):
                        if keyword.lower() in raw_text:
                            match_found = True
                            break
                if match_found:
                    break
            
            if match_found:
                for cand in group.get("candidates", []):
                    code = cand["code"]
                    if code not in seen_codes:
                        candidates.append(cand.copy())
                        seen_codes.add(code)
        
        return candidates

    def _validate_and_justify(self, candidate: Dict[str, Any], unit: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        tags = unit.get("evidence_tags", [])
        metrics = unit.get("derived_metrics_snapshot", {})
        
        # Rules for Why-Must (Minimum 2 points)
        # Primary: KR_POLICY, GLOBAL_INDEX, EARNINGS_VERIFY
        # Secondary: FLOW_ROTATION, PRETEXT_VALIDATION, ANOMALY_DETECTION
        
        primary_tags = [t for t in tags if t in ["KR_POLICY", "GLOBAL_INDEX", "EARNINGS_VERIFY"]]
        secondary_tags = [t for t in tags if t in ["FLOW_ROTATION", "PRETEXT_VALIDATION", "ANOMALY_DETECTION"]]
        
        why_must_say = []
        name = candidate["name"]
        sector = unit.get("target_sector", "관련")

        # Justification Assembly
        if "KR_POLICY" in tags:
            why_must_say.append({
                "claim": f"정책/제도 집행이 {sector} 수요를 직접 만든다 → {name}는 그 수혜 포지션이다.",
                "evidence_tag": "KR_POLICY",
                "evidence_key": "POLICY_EXECUTION"
            })
        if "GLOBAL_INDEX" in tags:
            why_must_say.append({
                "claim": f"지수/패시브 이벤트는 수급을 강제한다 → {name}는 수급 유입 구간에서 수혜다.",
                "evidence_tag": "GLOBAL_INDEX",
                "evidence_key": "INDEX_EVENT"
            })
        if "EARNINGS_VERIFY" in tags:
            why_must_say.append({
                "claim": f"실적/현금흐름이 먼저 찍히는 쪽이 보상받는다 → {name}의 실적 지표가 확인 구간이다.",
                "evidence_tag": "EARNINGS_VERIFY",
                "evidence_key": "EARNINGS_METRIC"
            })
        if "FLOW_ROTATION" in tags:
            why_must_say.append({
                "claim": f"순환매는 '덜 오른 + 명분 있는' 쪽으로 이동한다 → {name}는 수급 대기 구간에 있다.",
                "evidence_tag": "FLOW_ROTATION",
                "evidence_key": "ROTATION_SLOT"
            })
        if "PRETEXT_VALIDATION" in tags:
             why_must_say.append({
                "claim": f"명분의 강도가 유효하다 → {name}는 테마의 본질적 가치에 부합한다.",
                "evidence_tag": "PRETEXT_VALIDATION",
                "evidence_key": "PRETEXT_STRENGTH"
            })

        # Final Conviction Check
        has_primary = len(primary_tags) > 0
        has_secondary = len(secondary_tags) > 0
        is_safe = has_primary and has_secondary and len(why_must_say) >= 2
        
        if not is_safe:
            # We don't return unbacked stocks in mentionables list
            return None

        return {
            "ticker_or_code": candidate["code"],
            "name": name,
            "market": candidate["market"],
            "role": candidate["role"],
            "why_must_say": why_must_say,
            "safety": {
                "is_inferred": False,
                "confidence": "HIGH" if len(why_must_say) >= 3 else "MED",
                "block_reason": ""
            }
        }

    def save(self, data: List[Dict[str, Any]], output_path: str = "data/decision/mentionables.json"):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved Mentionables to {output_path}")

def run_mentionables_layer(data_dir: str = "data/decision"):
    base = Path(data_dir)
    files = [
        "interpretation_units.json",
        "script_realization.json"
    ]
    bundle = {}
    for f in files:
        p = base / f
        if p.exists():
            bundle[f.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
        else:
            bundle[f.replace(".json", "")] = []

    layer = MentionablesLayer()
    results = layer.run(bundle)
    layer.save(results)
    return results
