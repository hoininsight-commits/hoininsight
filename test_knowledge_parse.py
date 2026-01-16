
import re
from pathlib import Path

def parse_data_master(path):
    content = Path(path).read_text(encoding='utf-8')
    # Regex to find table rows
    # Look for lines starting with | and not being separator lines |---|
    data_definitions = []
    
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('|') and '---|' not in line and '카테고리' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 6:
                category = parts[0]
                data_name = parts[1]
                why = parts[5] # WHY column is index 5 usually? Let's check headers
                # Headers: | 카테고리 | 수집 데이터 | 수집처 | 방식 | 무료 여부 | 상태 | WHY | ...
                # Indices: 0       1          2      3     4         5     6
                # Wait, split('|') on "| A | B |" gives ['', 'A', 'B', '']
                # if I perform split('|')[1:-1] I get the inner content.
                
                parts_clean = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts_clean) >= 7:
                     data_definitions.append({
                         "category": parts_clean[0],
                         "name": parts_clean[1],
                         "why": parts_clean[6]
                     })
    return data_definitions

def parse_anomaly_logic(path):
    content = Path(path).read_text(encoding='utf-8')
    logic_entries = []
    current_section = ""
    
    lines = content.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('### '):
            current_section = line.replace('###', '').strip()
        
        # logic pattern: **(A) Title**
        # followed by - 조건: ...
        if line.startswith('**(') and ') ' in line:
            title = line.replace('**', '').strip()
            # Look ahead for condition
            condition = ""
            meaning = ""
            for j in range(i+1, min(i+5, len(lines))):
                subline = lines[j].strip()
                if subline.startswith('- 조건:'):
                    condition = subline.replace('- 조건:', '').strip()
                elif subline.startswith('- 의미:'):
                    meaning = subline.replace('- 의미:', '').strip()
            
            if condition:
                logic_entries.append({
                    "section": current_section,
                    "title": title,
                    "condition": condition,
                    "meaning": meaning
                })
    return logic_entries

# Test run
dm_path = "docs/DATA_COLLECTION_MASTER.md"
al_path = "docs/ANOMALY_DETECTION_LOGIC.md"

print(f"--- Parsing {dm_path} ---")
d_items = parse_data_master(dm_path)
for item in d_items[:3]:
    print(item)
print(f"Total Data Definitions: {len(d_items)}")

print(f"\n--- Parsing {al_path} ---")
l_items = parse_anomaly_logic(al_path)
for item in l_items[:3]:
    print(item)
print(f"Total Logic Definitions: {len(l_items)}")
