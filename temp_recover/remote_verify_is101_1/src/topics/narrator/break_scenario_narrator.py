import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

class BreakScenarioNarrator:
    """
    IS-98-5: Break Scenario Narrator
    Generates deterministic scripts when RELATIONSHIP_BREAK_RISK is detected.
    """

    RELATIONSHIP_IMPACT_MAP = {
        "capital_loop": "자본 투입 및 구매력 감소(Capex slowdown) 리스크",
        "supplier_dependency": "물량 재배정 및 공급망 전환(Procurement shift)",
        "strategic_partner": "우선적 플랫폼 이점 상실(Advantage erosion)",
        "distribution_dependency": "판매 채널 붕괴 및 유통 병목(Distribution shock)"
    }

    SECOND_ORDER_MAP = {
        "capital_loop": "신규 증설 지연 및 인프라 대기 수요 폭발",
        "supplier_dependency": "공급사 간 경쟁 심화로 인한 대체재 가격 하락",
        "strategic_partner": "오픈 생태계 확대로 인한 기술 표준 재정립",
        "distribution_dependency": "물류비 상승 및 리드타임 불확실성 증대"
    }

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.decision_dir = self.base_dir / "data" / "decision"
        self.registry_dir = self.base_dir / "registry" / "templates"
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def load_inputs(self):
        ctx = {}
        try:
            ctx["units"] = json.loads((self.decision_dir / "interpretation_units.json").read_text(encoding="utf-8"))
        except: ctx["units"] = []
        
        try:
            hero_raw = json.loads((self.decision_dir / "hero_topic_lock.json").read_text(encoding="utf-8"))
            ctx["hero"] = hero_raw.get("hero_topic") if hero_raw.get("status") == "LOCKED" else None
        except: ctx["hero"] = None
        
        try:
            ctx["hold_queue"] = json.loads((self.decision_dir / "hold_queue.json").read_text(encoding="utf-8"))
        except: ctx["hold_queue"] = []
        
        try:
            data = json.loads((self.decision_dir / "mentionables_ranked.json").read_text(encoding="utf-8"))
            ctx["mentionables"] = data.get("top", [])
        except: ctx["mentionables"] = []
        
        try:
            ctx["templates"] = yaml.safe_load((self.registry_dir / "script_templates_v1.yml").read_text(encoding="utf-8"))
        except: ctx["templates"] = {}
        
        return ctx

    def _get_break_unit(self, ctx):
        # 1. Check Hero Topic for RELATIONSHIP_BREAK_RISK
        # In MultiEyeTopicSynthesizer, REL_BREAK might be in source_units
        if ctx["hero"]:
            source_ids = ctx["hero"].get("source_units", [])
            for u in ctx["units"]:
                if u.get("interpretation_id") in source_ids and u.get("interpretation_key") == "RELATIONSHIP_BREAK_RISK":
                    return u
        
        # 2. Check Hold Queue (Priority 1-5)
        for h in ctx["hold_queue"]:
            source_ids = h.get("source_units", [])
            for u in ctx["units"]:
                if u.get("interpretation_id") in source_ids and u.get("interpretation_key") == "RELATIONSHIP_BREAK_RISK":
                    return u
        
        # 3. Direct check in units if not synthesized (as fallback)
        for u in ctx["units"]:
            if u.get("interpretation_key") == "RELATIONSHIP_BREAK_RISK":
                return u
        
        return None

    def run(self):
        ctx = self.load_inputs()
        unit = self._get_break_unit(ctx)
        
        if not unit:
            print("[BREAK_NARRATOR] No RELATIONSHIP_BREAK_RISK signal found. Skipping.")
            return

        # Deterministic Mapping
        dm = unit.get("derived_metrics_snapshot", {})
        rel_type = dm.get("signals", {}) # This is slightly different from my interpreter, let's look at interpretation_units.json
        # Wait, in relationship_break_interpreter.py:
        # "derived_metrics_snapshot": { "stress_score": ..., "signals": rel["signals"], "break_risk": ..., "reliability": ... }
        # signals is a dict: {"capital_loop": {"present": True, ...}, ...}
        
        present_signals = [k for k, v in dm.get("signals", {}).items() if v.get("present")]
        primary_signal = present_signals[0] if present_signals else "strategic_partner"
        
        what_breaks = self.RELATIONSHIP_IMPACT_MAP.get(primary_signal, "구조적 협력 체계의 약화")
        second_order = self.SECOND_ORDER_MAP.get(primary_signal, "시장 전반의 공급망 재편 및 불확실성 증대")
        
        # Confidence logic
        status = unit.get("hypothesis_jump", {}).get("status", "HOLD")
        reliability = dm.get("reliability", 0.0)
        source_count = unit.get("hypothesis_jump", {}).get("independent_sources_count", 1)
        
        hold_text = ""
        if status == "HOLD":
            triggers = []
            if source_count < 2: triggers.append("교차 검증된 제2의 소스")
            if reliability < 0.7: triggers.append("공식 공문 또는 실적 공시")
            trigger_str = " 및 ".join(triggers) if triggers else "신뢰할 수 있는 데이터"
            hold_text = f"📍 아직 확정이 아닙니다. {trigger_str}가 확인될 때까지 트리거를 기다리겠습니다."

        # Mentionables (Top 3)
        picks = ctx["mentionables"][:3]
        winners_list = []
        winners_detail_text = ""
        for p in picks:
            winner_entry = {
                "category": p.get("role", "UNKNOWN"),
                "why_must": p.get("why_must", "Bottleneck necessity"),
                "evidence_ids": p.get("citations", [])
            }
            winners_list.append(winner_entry)
            winners_detail_text += f"- {p.get('name')}: {p.get('why_must')} (출처: {', '.join(p.get('citations', []))})\n"

        # Structured JSON
        # Need to find entities A and B from narrative or unit
        # In interpreter, structural_narrative = f"{rel['entity_a']}와 {rel['entity_b']} 사이의..."
        narrative = unit.get("structural_narrative", "")
        relationship = "UNKNOWN"
        if "와" in narrative and " 사이" in narrative:
            relationship = narrative.split(" 사이")[0].replace(" ", "-") # Rough extraction

        scenario_json = {
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "topic_id": unit.get("interpretation_id"),
            "relationship": relationship,
            "scenario": {
                "premise": unit.get("structural_narrative"),
                "what_breaks_first": [what_breaks],
                "second_order_effects": [second_order],
                "winners_pickaxe": winners_list,
                "guardrails": {
                    "confidence": status,
                    "disclaimer": "본 시나리오는 데이터 기반 가설이며 실제와 다를 수 있습니다."
                }
            }
        }
        
        # Save JSON
        (self.decision_dir / "break_scenario.json").write_text(json.dumps(scenario_json, indent=2, ensure_ascii=False))
        print("[BREAK_NARRATOR] Saved break_scenario.json")

        # Generate Scripts
        context = {
            "PREMISE_TEXT": unit.get("structural_narrative"),
            "RELATIONSHIP": relationship,
            "HOLD_TEXT": hold_text,
            "WHAT_BREAKS_FIRST": what_breaks,
            "SECOND_ORDER_EFFECTS": second_order,
            "WINNERS_TEXT": winners_detail_text,
            "PICKAXE_DETAILS": winners_detail_text,
            "DISCLAIMER_TEXT": "본 분석은 투자 권유가 아닙니다."
        }
        
        tpl = ctx["templates"]
        
        # Shorts
        shorts_content = ""
        for section in tpl.get("break_scenario_shorts", []):
            text = section["content"]
            for key, val in context.items():
                text = text.replace(f"{{{key}}}", str(val))
            shorts_content += text + "\n"
        
        (self.export_dir / "final_script_break_scenario_shorts.txt").write_text(shorts_content)
        print("[BREAK_NARRATOR] Generated break_scenario_shorts.txt")

        # Long
        long_content = ""
        for section in tpl.get("break_scenario_long", []):
            text = section["content"]
            for key, val in context.items():
                text = text.replace(f"{{{key}}}", str(val))
            long_content += text + "\n"
        
        (self.export_dir / "final_script_break_scenario_long.txt").write_text(long_content)
        print("[BREAK_NARRATOR] Generated break_scenario_long.txt")

if __name__ == "__main__":
    narrator = BreakScenarioNarrator()
    narrator.run()
