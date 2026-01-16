
import os
import json
from datetime import datetime
from pathlib import Path

path = "src/dashboard/dashboard_generator.py"
with open(path, 'r') as f:
    lines = f.readlines()

# Find the insertion point before `html = f"""`
insert_idx = -1
for i, line in enumerate(lines):
    if 'html = f"""' in line and '[Layout Fix]' in lines[i-1]:
        insert_idx = i
        break

if insert_idx == -1:
    # Fallback search
    for i, line in enumerate(lines):
        if 'html = f"""' in line:
            insert_idx = i
            break

if insert_idx == -1:
    print("Could not find insertion point")
    exit(1)

# Logic to restore missing variables
restored_logic = r'''
    # [Restored Logic] Calculate missing variables for Dashboard
    
    # 1. Change Effectiveness
    effectiveness_html = """
    <div style="padding:40px; text-align:center; color:#94a3b8; background:white; border:1px solid #e2e8f0; border-radius:8px;">
        <h3>데이터 누적 중...</h3>
        <p style="font-size:12px;">변경 효과 분석을 위한 데이터가 충분하지 않습니다.</p>
    </div>
    """
    try:
        eff_path = base_dir / "data/ops/effectiveness" / ymd.replace("-","/") / "effectiveness_report.json"
        if eff_path.exists():
            eff_data = json.loads(eff_path.read_text(encoding='utf-8'))
            # Simple render
            effectiveness_html = '<div style="background:white; padding:20px; border-radius:8px; border:1px solid #e2e8f0;">'
            effectiveness_html += f"<div><strong>Score:</strong> {eff_data.get('score', 0)}</div>"
            effectiveness_html += f"<div style='margin-top:10px; font-size:12px; white-space:pre-wrap;'>{eff_data.get('analysis','')}</div>"
            effectiveness_html += "</div>"
    except: pass

    # 2. Topic Candidates & Script Output
    topics_count = 0
    try:
        tc_path = base_dir / "data/topics/candidates" / ymd.replace("-","/") / "topic_candidates.json"
        if tc_path.exists():
            tc_data = json.loads(tc_path.read_text(encoding='utf-8'))
            topics_count = len(tc_data.get("candidates", []))
    except: pass
    
    # Candidate HTML (Simple List)
    candidate_html = ""
    if topics_count > 0:
        candidate_html += f'<div style="background:white; padding:20px; border-radius:8px; border:1px solid #e2e8f0;">Found {topics_count} candidates.</div>'
    else:
        candidate_html += '<div style="padding:20px; text-align:center; color:#94a3b8;">No candidates found.</div>'

    # Script Output
    topic_title = "주제 선정 대기중"
    script_exists = False
    script_body = ""
    try:
        out_path = base_dir / "data/output" / ymd.replace("-","/") / "insight_script.md"
        if out_path.exists():
            script_exists = True
            script_body = out_path.read_text(encoding='utf-8')
            # Extract title
            for line in script_body.splitlines():
                if line.startswith("# "):
                    topic_title = line[2:].strip()
                    break
            if not topic_title: topic_title = "스크립트 생성 완료"
    except: pass

    # 3. Archive HTML
    archive_html = ""
    try:
        # List last 7 days of output
        archive_html += '<div class="archive-list" style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">'
        from datetime import timedelta
        for i in range(1, 8):
            past_date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y/%m/%d")
            p_script = base_dir / "data/output" / past_date / "insight_script.md"
            if p_script.exists():
                archive_html += f'<div style="padding:15px; border-bottom:1px solid #f1f5f9; display:flex; justify-content:space-between;">'
                archive_html += f'<span style="font-weight:bold; color:#334155;">{past_date} Report</span>'
                archive_html += f'<a href="#" style="color:#3b82f6; text-decoration:none; font-size:12px;">View</a>'
                archive_html += '</div>'
        
        if archive_html == '<div class="archive-list" style="background:white; border-radius:8px; border:1px solid #e2e8f0; overflow:hidden;">':
             archive_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No archives found.</div>'
        else:
             archive_html += '</div>'
    except: 
        archive_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">Archive error.</div>'
    
    # 4. Revival HTML
    revival_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No revival data.</div>'
    
    # 5. Ledger HTML
    ledger_html = '<div style="padding:20px; text-align:center; color:#94a3b8;">No ledger data.</div>'
    
    # 6. Final Card (Ensure variable exists)
    if 'final_card' not in locals():
        final_card = {}

'''

# Insert logic
new_lines = lines[:insert_idx] + [restored_logic] + lines[insert_idx:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print("[Restore] Restored missing logic variables.")
