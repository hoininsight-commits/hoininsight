import json
from pathlib import Path
from typing import Dict, Any, Optional

class NarrativeEntryHookGenerator:
    """
    IS-101-2: Narrative Entry Hook Layer
    Generates a single, assertive Korean sentence to immediately capture operator attention.
    """

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.decision_dir = self.base_dir / "data" / "decision"
        self.ui_dir = self.base_dir / "data" / "ui"
        self.ui_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except:
                return {}
        return {}

    def run(self):
        hero_summary = self.load_json(self.ui_dir / "hero_summary.json")
        hero_lock = self.load_json(self.decision_dir / "hero_topic_lock.json")
        why_now_trigger = self.load_json(self.decision_dir / "why_now_trigger.json")

        # 1. Classification & Hook Logic
        status = hero_summary.get("status", "HOLD")
        why_now = hero_summary.get("why_now", [])
        core_logic = hero_summary.get("core_logic", [])
        
        hook_type = "STRUCTURAL"
        entry_sentence = "지금 보이는 움직임은 결과가 아니라, 구조 전환의 시작이다."
        confidence_level = "LOW"

        # Classification Logic
        is_structural = (status == "READY" and len(core_logic) >= 2)
        
        schedule_keywords = ["날짜", "일정", "발표", "시점", "D-", "예정"]
        is_schedule = any(any(kw in wn for kw in schedule_keywords) for wn in why_now)
        
        flow_keywords = ["자금", "수급", "이동", "유입", "capital", "rotation"]
        is_flow = any(any(kw in wn for kw in flow_keywords) for wn in why_now)

        is_warning = (status in ["HOLD", "HYPOTHESIS"])

        if is_warning:
            hook_type = "WARNING"
            entry_sentence = "지금은 낙관이 아니라, 전제가 무너지는 구간이다."
            confidence_level = "LOW"
        elif is_structural:
            hook_type = "STRUCTURAL"
            entry_sentence = "이건 단기 이슈가 아니라, 산업 구조가 갈라지는 시점이다."
            confidence_level = "HIGH"
        elif is_schedule:
            hook_type = "SCHEDULE"
            entry_sentence = "이 이슈는 이미 날짜가 정해진 구조적 이벤트다."
            confidence_level = "MEDIUM"
        elif is_flow:
            hook_type = "FLOW"
            entry_sentence = "돈은 사라진 게 아니라, 방향을 바꾸고 있다."
            confidence_level = "MEDIUM"

        # Contract Enforcement (No numbers, no special chars, max 2 commas)
        # Entry sentences above are already pre-vetted.

        output = {
            "hook_type": hook_type,
            "entry_sentence": entry_sentence,
            "confidence_level": confidence_level
        }

        out_path = self.ui_dir / "narrative_entry_hook.json"
        out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"[HOOK] Generated {hook_type} hook (Level: {confidence_level})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=".", help="Base directory")
    args = parser.parse_args()
    
    gen = NarrativeEntryHookGenerator(Path(args.base))
    gen.run()
