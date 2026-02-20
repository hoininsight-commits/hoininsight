"""
IS-98-3 Script Finalizer
Converts Hero Topic into Final Shorts/Long Scripts using YAML Templates.
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

class ScriptFinalizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.decision_dir = self.base_dir / "data" / "decision"
        self.registry_dir = self.base_dir / "registry" / "templates"
        self.export_dir = self.base_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def load_data(self):
        hero_data = {}
        mentionables = []
        templates = {}

        try:
            hero_raw = json.loads((self.decision_dir / "hero_topic_lock.json").read_text())
            if hero_raw.get("status") == "LOCKED":
                hero_data = hero_raw.get("hero_topic", {})
        except: pass

        try:
            mentionables = json.loads((self.decision_dir / "mentionables_ranked.json").read_text()).get("top", [])
        except: pass
        
        try:
            templates = yaml.safe_load((self.registry_dir / "script_templates_v1.yml").read_text())
        except: pass

        return hero_data, mentionables, templates

    def format_text(self, text_block, context):
        """Replaces placeholders in text with context values."""
        for key, value in context.items():
            text_block = text_block.replace(f"{{{key}}}", str(value))
        return text_block

    def generate_scripts(self):
        hero, mentionables, tpl = self.load_data()
        
        if not hero:
            print("[SCRIPT] No Hero Topic Locked. Skipping.")
            return

        # Prepare Context
        wnb = hero.get("why_now_bundle", {})
        eyes = hero.get("eyes_used", [])
        
        # Pickaxe Context (Safe access)
        p1 = mentionables[0] if len(mentionables) > 0 else {}
        p2 = mentionables[1] if len(mentionables) > 1 else {}
        
        context = {
            "HOOK_TEXT": wnb.get("why_now_3", "구조적 변화가 감지되었습니다."), # Simplify mapping
            "CLAIM_TEXT": f"{hero.get('sector')} 섹터의 패러다임이 바뀝니다.",
            "SECTOR_NAME": hero.get("sector"),
            "EYE_1_TEXT": wnb.get("why_now_1", "-"),
            "EYE_2_TEXT": wnb.get("why_now_2", "-"),
            "EYE_3_TEXT": wnb.get("why_now_3", "-"),
            "EYE_1_TITLE": hero.get("dominant_eye", "Main"),
            "EYE_2_TITLE": "Policy", 
            "EYE_3_TITLE": "Structure",
            "YEARS_BACK": "3", # Placeholder or logic
            "PICK_1_NAME": p1.get("name", "Top Pick"),
            "PICK_1_REASON": p1.get("why_must", "Bottleneck"),
            "PICK_1_TICKER": p1.get("ticker", "Code"),
            "PICK_1_ROLE": p1.get("role", "Leader"),
            "PICK_2_NAME": p2.get("name", "2nd Pick"),
            "PICK_2_REASON": p2.get("why_must", "Supply Chain"),
            "PICK_2_TICKER": p2.get("ticker", "Code"),
            "PICK_2_ROLE": p2.get("role", "Follower"),
            "TOPIC_TYPE_KR": "구조적 성장", # Map EN enum to KR
            "RISK_FACTOR_1": "매크로 변동성",
            "DOMINANT_EYE_DESC": f"{hero.get('dominant_eye')} 관점에서 확실한 신호가 잡혔습니다.",
            "DISCLAIMER_TEXT": "본 분석은 투자 권유가 아닙니다."
        }
        
        # Hypothesis Jump Handling
        if hero.get("topic_type") == "HYPOTHESIS_JUMP":
             context["DISCLAIMER_TEXT"] = "⚠️ 주의: 이 분석은 확정이 아닌 '가설'에 기반합니다. 투자에 유의하세요."

        # Generate Shorts
        shorts_content = ""
        for section in tpl.get("shorts_structure", []):
            shorts_content += self.format_text(section["content"], context) + "\n"
            
        (self.export_dir / "final_script_shorts.txt").write_text(shorts_content)
        print("[SCRIPT] Generated Shorts Script")

        # Generate Long
        long_content = ""
        for section in tpl.get("long_structure", []):
            long_content += self.format_text(section["content"], context) + "\n"
            
        (self.export_dir / "final_script_long.txt").write_text(long_content)
        print("[SCRIPT] Generated Long Script")

if __name__ == "__main__":
    finalizer = ScriptFinalizer()
    finalizer.generate_scripts()
