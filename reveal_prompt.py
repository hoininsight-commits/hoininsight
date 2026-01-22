from pathlib import Path
import os

def generate_prompt_debug():
    vid = "c19nIAA0Y7Y"
    
    # 1. Load Transcript
    t_path = Path(f"data/narratives/transcripts/2026/01/20/{vid}.txt")
    if not t_path.exists():
        print(f"Transcript not found: {t_path}")
        return
    transcript = t_path.read_text(encoding="utf-8")
    
    # Mock Title (as I don't have the dictionary handy right here easily, will assume from memory of previous step)
    title = {
        "title": "지금, 투자자들이 꼭 알아야 할 2026년 국내 정책 3가지",
    }
    
    # 2. Logic Reconstruction
    engine_root = Path("resources/hoin_engine/v1.11_CONSTITUTIONAL")
    
    # Load System Helper
    sys_instr_path = engine_root / "content" / "01_INSTRUCTION" / "GEMINI_SYSTEM_INSTRUCTION.md"
    if sys_instr_path.exists():
        system_instruction = sys_instr_path.read_text(encoding="utf-8")
    else:
        system_instruction = "SYSTEM INSTRUCTION NOT FOUND"

    # Load Context Docs
    context_docs = []
    if engine_root.exists():
        for md_file in engine_root.rglob("*.md"):
            if md_file.name == "GEMINI_SYSTEM_INSTRUCTION.md": continue
            if md_file.name.startswith("."): continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
                rel_path = md_file.relative_to(engine_root)
                context_docs.append(f"--- DOCUMENT: {rel_path} ---\n{content}\n")
            except Exception as e:
                print(f"Error reading {md_file}: {e}")

    full_context = "\n".join(context_docs)

    prompt = f"""
{system_instruction}

=== CANONICAL REFERENCE LIBRARY (ABSOLUTE TRUTH) ===
You must strictly adhere to the definitions and logic in the following documents.
Do not use outside logic.

{full_context}

====================================================

=== CURRENT TASK ===
Analyze the following video transcript according to the HOIN ENGINE logic defined above.

# Input Data
- **Title**: {title['title']}
- **Transcript**:
{transcript[:25000]}

# Output Requirement
Follow the [OUTPUT FORMAT] defined in the System Instruction.
"""
    
    # Save to file
    out_path = Path("debug_full_prompt.txt")
    out_path.write_text(prompt, encoding="utf-8")
    print(f"Full prompt saved to {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_prompt_debug()
