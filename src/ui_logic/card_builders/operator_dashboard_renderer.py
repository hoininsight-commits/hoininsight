"""
IS-97-7 Operator UI Renderer
Transforms engine outputs into a human-operable HTML dashboard.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

class OperatorDashboardRenderer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.decision_dir = self.base_dir / "data" / "decision"
        self.export_dir = self.base_dir / "exports"
        self.template_path = self.base_dir / "templates" / "operator_dashboard.html"
        self.export_dir.mkdir(exist_ok=True)
        
    def render(self):
        # Load Data
        hero_data = {}
        hold_queue = []
        mentionables = []
        
        try:
            hero_raw = json.loads((self.decision_dir / "hero_topic_lock.json").read_text())
            hero_data = hero_raw.get("hero_topic", {})
            hero_status = hero_raw.get("status", "UNKNOWN")
        except:
            hero_status = "NO_DATA"

        try:
            hold_queue = json.loads((self.decision_dir / "hold_queue.json").read_text())
        except: pass

        try:
            mentionables = json.loads((self.decision_dir / "mentionables_ranked.json").read_text()).get("top", [])
        except: pass

        # Load Template
        if not self.template_path.exists():
            print("[UI] Template not found.")
            return
            
        tpl = self.template_path.read_text()
        
        # Prepare Replacements
        today = datetime.now().strftime("%Y-%m-%d")
        
        if hero_status != "LOCKED" or not hero_data:
            # NO HERO STATE
            html = tpl.replace("{HERO_TITLE}", "NO HERO TODAY")
            html = html.replace("{HERO_TYPE}", "STANDBY")
            html = html.replace("{HERO_DECLARATION}", "No structural theme met the 3-Eye criteria.")
            html = html.replace("{HERO_EYES}", "-")
            html = html.replace("{HERO_SCORE}", "N/A")
            html = html.replace("{TODAY_DATE}", today)
            
            # Empty blocks
            html = html.replace("{EYE_1_TITLE}", "-")
            html = html.replace("{EYE_1_DESC}", "Waiting for signals...")
            html = html.replace("{EYE_2_TITLE}", "-")
            html = html.replace("{EYE_2_DESC}", "-")
            html = html.replace("{EYE_3_DESC}", "-")
            html = html.replace("{MENTIONABLES_BLOCK}", "<div class='card'>No active picks.</div>")
        else:
            # HERO STATE
            eyes = hero_data.get("eyes_used", [])
            dominant_eye = hero_data.get("dominant_eye", "UNKNOWN")
            wnb = hero_data.get("why_now_bundle", {})
            score = hero_data.get("priority_score", {}).get("total", 0.0)
            
            html = tpl.replace("{HERO_TITLE}", hero_data.get("sector", "TOPIC"))
            html = html.replace("{HERO_TYPE}", hero_data.get("topic_type", "TYPE"))
            html = html.replace("{HERO_DECLARATION}", f"오늘의 구조적 진실: {hero_data.get('sector')} 주도권 이동 (Rigidity Confirmed)")
            html = html.replace("{HERO_EYES}", ", ".join(eyes))
            html = html.replace("{HERO_SCORE}", str(score))
            html = html.replace("{TODAY_DATE}", today)
            
            html = html.replace("{EYE_1_TITLE}", dominant_eye)
            html = html.replace("{EYE_1_DESC}", wnb.get("why_now_1", "-"))
            html = html.replace("{EYE_2_TITLE}", "Policy/Context")
            html = html.replace("{EYE_2_DESC}", wnb.get("why_now_2", "-"))
            html = html.replace("{EYE_3_DESC}", wnb.get("why_now_3", "-"))
            
            # Mentionables Logic
            m_html = ""
            for m in mentionables[:3]:
                m_html += f"""
                <div class="mention-item">
                    <div class="mention-role">{m.get('role', 'PLAYER')}</div>
                    <div>{m.get('name', 'Name')} ({m.get('ticker','-')})</div>
                    <div style="font-size:0.9rem; color:#aaa;">{m.get('why_must','Bottleneck confirmed')}</div>
                </div>
                """
            html = html.replace("{MENTIONABLES_BLOCK}", m_html if m_html else "<div>No picks available</div>")

        # Hold Queue Logic
        h_html = ""
        for h in hold_queue:
            h_html += f"""
            <div class="hold-item">
                <div style="font-weight:bold; color:#aaa;">{h.get('sector', 'Unknown')}</div>
                <div style="color:#666;">{h.get('topic_type','-')} (Score: {h.get('priority_score',{}).get('total',0.0)})</div>
            </div>
            """
        html = html.replace("{HOLD_QUEUE_BLOCK}", h_html if h_html else "<div style='color:#666;'>Queue empty</div>")

        # Write Output
        out_path = self.export_dir / "operator_dashboard.html"
        out_path.write_text(html)
        print(f"[UI] Generated dashboard at {out_path}")

if __name__ == "__main__":
    renderer = OperatorDashboardRenderer()
    renderer.render()
