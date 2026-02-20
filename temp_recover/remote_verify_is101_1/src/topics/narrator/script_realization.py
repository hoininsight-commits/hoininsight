import json
from pathlib import Path
from typing import Any, Dict, List, Optional

class ScriptRealizationBuilder:
    """
    IS-97-3: Script Realization Layer
    Assembles actual script sentences using deterministic templates and input data.
    """

    def build(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        units = inputs.get("interpretation_units", [])
        decisions = inputs.get("speakability_decision", {})
        skeletons = inputs.get("narrative_skeleton", {})
        speak_maps = inputs.get("content_speak_map", [])
        tone_locks = inputs.get("tone_persona_lock", [])

        # Create lookups
        unit_map = {u["interpretation_id"]: u for u in units}
        cm_map = {cm["topic_id"]: cm for cm in speak_maps}
        lock_map = {tl["topic_id"]: tl for tl in tone_locks}

        realized_scripts = []

        for unit_id, unit in unit_map.items():
            decision = decisions.get(unit_id, {})
            skeleton = skeletons.get(unit_id, {})
            cmap = cm_map.get(unit_id, {})
            lock = lock_map.get(unit_id, {})

            flag = decision.get("speakability_flag", "DROP")
            if flag == "DROP":
                continue

            # Core Assembly Logic
            script_data = {
                "topic_id": unit_id,
                "version": "is97_3_v1",
                "persona": lock.get("persona", "MARKET_OBSERVER"),
                "tone": lock.get("tone", "OBSERVATIONAL"),
                "speakability": flag,
                "script": self._assemble_script(flag, unit, skeleton, cmap, lock),
                "citations": self._generate_citations(unit),
                "governance": {
                    "deterministic": True,
                    "no_llm": True,
                    "add_only_integrity": True
                }
            }
            realized_scripts.append(script_data)

        return realized_scripts

    def _assemble_script(self, flag: str, unit: Dict, skeleton: Dict, cmap: Dict, lock: Dict) -> Dict[str, Any]:
        title = unit.get("target_sector", "SECTOR")
        root_cause = unit.get("interpretation_key", "UNKNOWN_CAUSE")
        content_mode = cmap.get("content_mode", "HOLD")
        
        # 1. Hook
        hook = ""
        if flag == "HOLD" or content_mode == "MONITORING":
            hook = f"지금은 {title}이 확정 구간이 아니라 '조건 대기' 구간이야. 트리거만 확인하면 된다."
        elif content_mode == "SHORT":
            hook = f"님들, 지금 {title} 이슈에서 시장이 진짜 무서워하는 건 {root_cause}야."
        elif content_mode == "LONG":
            hook = f"오늘은 {title}을 '왜 지금인가' 관점에서 데이터로만 정리할게. 핵심은 {root_cause}다."

        # 2. Claim
        claim = ""
        stance = lock.get("stance", "STRUCTURAL")
        if flag == "HOLD":
            claim = f"이슈는 진행 중이지만 조건이 완성되려면 {skeleton.get('hold_trigger', '데이터')}가 필요하다."
        elif stance == "DATA_VALIDATED":
            claim = f"숫자가 확인됐다. {unit.get('derived_metrics_snapshot', {}).get('pretext_score', '지표')}가 핵심 증거다."
        else: # STRUCTURAL
            claim = f"이건 단기 뉴스가 아니라 구조 변화다. {unit.get('interpretation_key', '패턴')} 조합이 근거다."

        # 3. Evidence 3
        evidence = skeleton.get("evidence_3", [])
        if not evidence:
            tags = unit.get("evidence_tags", [])
            evidence = [f"{t} 기반 추세 포착" for t in tags[:3]]

        # 4. Checklist 3
        checklist = []
        tags = unit.get("evidence_tags", [])
        for i, tag in enumerate(tags[:3]):
            checklist.append(f"지표 {tag}: {tag} 데이터 확인 — 임계치 도달 여부")
        
        # 5. Risk Note
        risk_mode = lock.get("risk_disclaimer_mode", "EXPLICIT")
        if risk_mode == "EXPLICIT":
            risk_note = f"단, {skeleton.get('hold_trigger', '추가 지표')} 변동 시 시나리오 폐기가 필요함."
        else:
            risk_note = "데이터 기반 관찰 지속이 필요함."

        # 6. Closing
        if flag == "READY":
            closing = f"정리하면, 지금은 {title} 섹터가 보상받는 구간이다. 체크리스트만 보고 따라가면 된다."
        else:
            closing = f"정리하면, 지금은 {skeleton.get('hold_trigger', '트리거')}만 기다리면 된다. 조건이 오면 행동하고, 아니면 관찰이다."

        return {
            "hook": hook,
            "claim": claim,
            "evidence_3": evidence,
            "checklist_3": checklist,
            "risk_note": risk_note,
            "closing": closing
        }

    def _generate_citations(self, unit: Dict) -> List[Dict[str, str]]:
        tags = unit.get("evidence_tags", [])
        return [{"key": tag, "source": "INTERNAL_ENGINE"} for tag in tags]

    def save(self, data: List[Dict[str, Any]], output_path: str = "data/decision/script_realization.json"):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved Script Realization to {output_path}")

def run_script_realization(data_dir: str = "data/decision"):
    base = Path(data_dir)
    files = [
        "narrative_skeleton.json",
        "interpretation_units.json",
        "speakability_decision.json",
        "content_speak_map.json",
        "tone_persona_lock.json"
    ]
    inputs = {}
    for f in files:
        p = base / f
        if p.exists():
            inputs[f.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
        else:
            inputs[f.replace(".json", "")] = {}

    builder = ScriptRealizationBuilder()
    results = builder.build(inputs)
    builder.save(results)
    return results
