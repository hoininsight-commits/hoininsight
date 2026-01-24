
import re
import json
import sys
from pathlib import Path

def main():
    html_path = Path("chatgpt_raw.html")
    if not html_path.exists():
        print("Error: chatgpt_raw.html not found")
        return

    content = html_path.read_text(encoding="utf-8")
    
    # 1. Try to find the inner text of the conversation
    # ChatGPT shares often put data in a script tag or just render it.
    
    # Simple regex to find text blocks that look like conversation parts
    # We look for "message" or "content" type structures if it's JSON
    
    print("Extracting content...")
    
    # Strategy 1: Look for standard HTML text elements if SSR
    # (But read_url_content failed, so it might be minimal HTML)
    
    # Strategy 2: Look for JSON payload
    # Often keys are "message", "content", "parts"
    
    # Let's try to extract strings that contain "HOIN" and surrounding context
    # Or just dump all text that looks like Korean/English sentences.
    
    # Less efficient but effective: Use simple HTML tag stripper
    clean_text = re.sub(r'<[^>]+>', ' ', content)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # If the text is inside a JS string, it might be escaped.
    # Let's try to find large JSON blobs
    
    json_candidates = re.findall(r'\{.*\}', content)
    
    extracted_messages = []
    
    for candidate in json_candidates:
        if len(candidate) > 1000: # specific large blobs
            try:
                # It might be part of a variable assignment, e.g. window.__remixContext = { ... };
                # We need to be careful.
                pass
            except:
                pass

    # New Approach: Just dump everything that looks like a user message.
    # We know the specific phrase "HOIN Engine" is in there.
    
    # Let's just output the whole text first? No, too big.
    
    # Let's try to find the "linear_conversation" or "mapping" in the JSON.
    
    # Search for specific Next.js/Remix data patterns
    # Remix: window.__remixContext = 
    
    remix_match = re.search(r'window\.__remixContext\s*=\s*(\{.*?\});', content, re.DOTALL)
    if remix_match:
        print("Found Remix Context!")
        try:
            data = json.loads(remix_match.group(1))
            # Traverse data to find conversation
            # This is complex, let's just print structure keys
            print(data.keys())
        except:
            print("Failed to parse Remix JSON")

    # Target Header
    target_header = "# ✅ HOIN ENGINE vNext — Economic Hunter Compatibility (Final Spec for Antigravity)"
    
    # regex for the json string containing this header
    # It seems to be inside a JSON string value.
    
    # We will search for the header and then capture everything until the end of that string.
    # The string likely ends with a quote " or similar, but since it has newlines escaped as \n, 
    # and quotes escaped as \", we need to be careful.
    
    start_idx = content.find(target_header)
    if start_idx == -1:
        # Try without the emoji if encoding is weird
        target_header = "HOIN ENGINE vNext — Economic Hunter Compatibility (Final Spec for Antigravity)"
        start_idx = content.find(target_header)
        
    if start_idx != -1:
        print(f"Found header at {start_idx}")
        
        # Look forward for the end of the JSON string.
        # This is heuristics based. We assume it's a long string in a JSON list/obj.
        # We will take the next 10000 chars and try to parse/clean distinctively.
        
        raw_snippet = content[start_idx:start_idx+15000]
        
        # Find the next unescaped quote that isn't part of the text?
        # Actually, let's just dump it and clean it.
        
        # Clean common JSON escapes
        clean_spec = raw_snippet.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        
        # It might be followed by ", "timestamp" or similar JSON keys.
        # Let's try to cut it off at a likely end point.
        # Often these messages end with "---" or just end of user prompt.
        
        print("\n\n=== EXTRACTED SPECIFICATION ===\n")
        print(clean_spec)
        print("\n===============================\n")
        
        # Save to a file for easier reading
        Path("extracted_spec.md").write_text(clean_spec, encoding="utf-8")
        
    else:
        print("Could not find the specific header.")
        # Fallback: Print all HOIN occurrences again if needed


if __name__ == "__main__":
    main()
