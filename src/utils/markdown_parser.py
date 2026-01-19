
def parse_markdown(text: str) -> str:
    """Simple Markdown to HTML parser."""
    html_lines = []
    
    # Pre-process: standardize newlines
    lines = text.replace('\r\n', '\n').split('\n')
    
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Headers
        if stripped.startswith('# '):
            html_lines.append(f"<h3 style='margin-top:10px; margin-bottom:5px;'>{stripped[2:]}</h3>")
        elif stripped.startswith('## '):
            html_lines.append(f"<h4 style='margin-top:10px; margin-bottom:5px;'>{stripped[3:]}</h4>")
        elif stripped.startswith('### '):
            html_lines.append(f"<h5 style='margin-top:5px; margin-bottom:5px;'>{stripped[4:]}</h5>")
            
        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append("<ul style='margin-bottom:10px; padding-left:20px;'>")
                in_list = True
            # Bold processing inside list items
            content = stripped[2:]
            while '**' in content:
                content = content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            html_lines.append(f"<li>{content}</li>")
            
        # Empty line
        elif not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            
        # Regular text
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            
            # Bold processing
            content = line
            while '**' in content:
                content = content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            
            html_lines.append(f"<p style='margin-bottom:8px;'>{content}</p>")
            
    if in_list:
        html_lines.append("</ul>")
        
    return "".join(html_lines)
