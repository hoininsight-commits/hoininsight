
import os

path = "src/dashboard/dashboard_generator.py"
with open(path, 'r') as f:
    lines = f.readlines()

# Find the line with the loop "for h in ops_scoreboard.get('history', [])[:7]:"
loop_start = -1
for i, line in enumerate(lines):
    if "for h in ops_scoreboard.get('history', [])[:7]:" in line:
        loop_start = i
        break

if loop_start == -1:
    print("Could not find loop start")
    exit(1)

# Find where the loop logic ends. It ends with a `html += f"""` block usually.
# In the BROKEN file, it creates a table row inside the loop.
# We want to keep the loop and the `html +=` inside it.
# We want to find the line AFTER the loop finishes.
# The loop block ends when indentation goes back.

# Let's just find the generated HTML for the table end.
# In the original code, after the loop, we append the closing tags.
# We can just cut off the file right after the loop logic.

# Scan down from loop_start to find `html += f"""` that closes the row
truncate_at = -1
for i in range(loop_start, len(lines)):
    if "html += f" in lines[i] and "</tbody>" in lines[i+1]: # looking for the closing block
        # This approach is risky if the file is truly broken.
        pass
    
    # Simpler: Find the line `                        </tbody>` which is part of the broken string?
    pass

# Hard Reset Strategy:
# Keep everything up to the loop start + a few lines.
# The loop is:
#     for h in ops_scoreboard.get('history', [])[:7]:
#         st_color = ...
#         html += f"""
#             <tr>...</tr>
#         """
# 
# We want to keep this.
# Then we want to append the closing table tags.

# Find the end of the loop block
# It usually ends with `        """` (indent 8 spaces) inside the loop?
# Or `    """` (indent 4 spaces)?

# Let's truncate exactly where the last `"""` inside the loop occurs.
last_triple_quote = -1
for i in range(loop_start, loop_start + 20):
    if i < len(lines) and '"""' in lines[i]:
        last_triple_quote = i

# We assume the file is valid up to `last_triple_quote`.
# But wait, the loop runs multiple times. The `html +=` is inside the loop?
# Yes.
# So after the loop, we need to close the table.

# Let's just find `</tbody>`? No, that's inside the string.

# Safer Strategy: 
# Truncate BEFORE `html += f"""` that contains `</tbody>`. 
# Or just reconstruct the whole table tail.

cutoff = -1
for i, line in enumerate(lines):
    if "<!-- Ops History Table -->" in line:
        # We are safe here.
        cutoff = i
        break

valid_head = lines[:cutoff]

# Rebuild the Ops Table Block entirely to be safe
ops_table_block = r'''                <!-- Ops History Table -->
                <div style="margin-top: 30px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; background: white;">
                        <thead style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                            <tr>
                                <th style="padding: 10px 15px; text-align: left; color: #64748b;">Date</th>
                                <th style="padding: 10px 15px; text-align: left; color: #64748b;">Status</th>
                                <th style="padding: 10px 15px; text-align: right; color: #64748b;">Duration</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for h in ops_scoreboard.get('history', [])[:7]:
        st_color = 'background:#dcfce7; color:#166534;' if h.get('status') == 'SUCCESS' else 'background:#fee2e2; color:#991b1b;'
        html += f"""
                            <tr style="border-bottom: 1px solid #f1f5f9;">
                                <td style="padding: 10px 15px; color: #1e293b;">{h.get('date')}</td>
                                <td style="padding: 10px 15px;">
                                    <span style="padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; {st_color}">
                                        {h.get('status')}
                                    </span>
                                </td>
                                <td style="padding: 10px 15px; text-align: right; color: #64748b;">{h.get('duration_minutes')}m</td>
                            </tr>
        """

    html += """
                        </tbody>
                    </table>
                </div>
    """

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

if __name__ == "__main__":
    import os
    os.makedirs("data/dashboard", exist_ok=True)
    os.makedirs("dashboard", exist_ok=True)
    
    html = generate_dashboard()
    
    with open("dashboard/index.html", "w") as f:
        f.write(html)
    
    print("[Dashboard] Generated dashboard/index.html")
'''

full_content = "".join(valid_head) + ops_table_block

with open(path, 'w') as f:
    f.write(full_content)

print("[Fixer] Successfully rewrote dashboard_generator.py")
