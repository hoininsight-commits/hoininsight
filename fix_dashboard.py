
import os
import sys

# Read the original file
path = "/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight/src/dashboard/dashboard_generator.py"
with open(path, 'r') as f:
    lines = f.readlines()

# Find the split point (around line 1980, inside the generate_dashboard function)
# We look for the closing of the ops table
split_index = 0
for i, line in enumerate(lines):
    if "<!-- Ops History Table -->" in line:
        # Move down to find where the table logic ends
        # Looking for the end of the previous `html +=` block
        pass
    if "<!-- Insight Script Section -->" in line:
        split_index = i
        break

# If we couldn't find the exact marker, fallback to a known safe area or hard index
if split_index == 0:
    # Fallback: Find the end of `ops_scoreboard` logic
    for i, line in enumerate(lines):
        if "ops_scoreboard.get('history'" in line:
             split_index = i + 20 # rough jump
             break

# Let's try to match the exact content from previous `view_file`
# Line 1980 was `                </div>`
# Line 1981 was `    """`
# We will truncate AFTER line 1981

valid_lines = lines[:1981] # This should check out based on previous view

# New Tail Content (Correctly Indented Python)
new_tail = r'''    """
    
    html += f"""
        <!-- Insight Script Section -->
        <div id="insight-script" style="background: white; border-top: 2px solid #e2e8f0; padding: 40px; margin-top: 0;">
            <div style="max-width: 1100px; margin: 0 auto;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin: 0;">📝 인사이트 스크립트 (V1)</h2>
                    <button onclick="copyScript()" style="padding:5px 10px; background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; border-radius:4px; cursor:pointer; font-size:12px; font-weight:bold;">Copy Text</button>
                </div>
                <p style="font-size: 14px; color: #64748b; margin-bottom: 25px;">최종 생성된 분석 원고(v1.0)입니다.</p>
                
                <div style="background:#f8fafc; padding:20px; border-radius:8px; border:1px solid #e2e8f0; font-family:'Inter',sans-serif; white-space:pre-wrap; font-size:13px; line-height:1.6; color:#334155;">
{script_body if script_body else "스크립트가 아직 생성되지 않았습니다."}
                </div>
            </div>
        </div>
    """

    html += """
        <div style="height: 50px;"></div>
        </div> <!-- End sections-wrapper -->
    </div> <!-- End Main Panel -->

    <!-- Right Sidebar -->
    <div class="sidebar">
        <div class="section-header" style="border:none; margin-bottom:10px;">
            <div style="font-size:14px; font-weight:800; color:#475569; text-transform:uppercase;">Data Status</div>
        </div>
        
        <div id="sidebar-content">
            <!-- Dynamic Content injected here -->
        </div>
    </div>

</div>

<!-- MODAL -->
<div id="scriptModal" class="modal">
    <div class="modal-box">
         <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
             <h2 style="margin:0;">Insight Script</h2>
             <button onclick="closeModal()" style="border:none; background:none; font-size:20px; cursor:pointer;">✕</button>
         </div>
         <p id="script-modal-content">Script content here...</p>
    </div>
</div>

<script>
    function closeModal() {
        document.getElementById('scriptModal').classList.remove('modal-active');
    }
    function copyScript() {
        const text = document.querySelector('#insight-script pre') ? document.querySelector('#insight-script pre').innerText : document.querySelector('#insight-script div').innerText;
        navigator.clipboard.writeText(text).then(() => alert('Copied!'));
    }
</script>

</body>
</html>
"""
    return html

def main():
    # ... (existing main logic placeholder if needed) ...
    pass
'''

# We need to preserve the `if __name__ == "__main__":` block at the very end of the original file
# But based on file size, it might be further down.
# Actually, the file ends with `if __name__ == "__main__":` usually. 
# Let's just append the standard runner for this script.

runner_code = """

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/dashboard", exist_ok=True)
    os.makedirs("dashboard", exist_ok=True)
    
    html = generate_dashboard()
    
    with open("dashboard/index.html", "w") as f:
        f.write(html)
    
    print("[Dashboard] Generated dashboard/index.html")
"""

# Reconstruct
full_content = "".join(valid_lines) + new_tail + runner_code

with open(path, 'w') as f:
    f.write(full_content)

print("Fixed dashboard_generator.py")
