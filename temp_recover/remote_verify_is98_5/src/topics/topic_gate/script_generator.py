import json
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.i18n_ko import I18N_KO

class ScriptGenerator:
    """
    Transforms Gate topic analysis into a structured, factual content script outline.
    Strictly follows the 7-section template without conversational tone or hype.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def generate_script(self, ymd: str) -> Optional[str]:
        """
        Generates a script for the Gate topic of a specific date.
        """
        tg_base = self.base_dir / "data" / "topics" / "gate" / ymd.replace("-", "/")
        tg_output_path = tg_base / "topic_gate_output.json"
        tc_path = tg_base / "topic_gate_candidates.json"

        if not tg_output_path.exists():
            return None

        try:
            tg_data = json.loads(tg_output_path.read_text(encoding="utf-8"))
            
            # Load candidates to map evidence sources
            cand_map = {}
            if tc_path.exists():
                tc_data = json.loads(tc_path.read_text(encoding="utf-8"))
                for cand in tc_data.get("candidates", []):
                    cand_map[cand["candidate_id"]] = cand

            return self._format_markdown(tg_data, cand_map)
        except Exception as e:
            return f"Error generating script: {e}"

    def _format_markdown(self, data: Dict, cand_map: Dict) -> str:
        as_of = data.get("as_of_date", "N/A")
        title = data.get("title", "No Title")
        
        sections = []
        
        # 1) Hook
        hook_text = data.get("question", I18N_KO["NEEDS_DATA"])
        sections.append(f"{I18N_KO['STEP_HOOK']}\n- {hook_text}")
        
        # 2) Market Expectation
        expectation = data.get("why_people_confused", I18N_KO["NEEDS_DATA"])
        sections.append(f"{I18N_KO['STEP_EXPECTATION']}\n- {expectation}")
        
        # 3) Actual Market Move
        # Note: current gate data doesn't explicitly have 'reaction' data yet
        sections.append(f"{I18N_KO['STEP_MOVE']}\n- [{I18N_KO['NEEDS_DATA']}] Immediate price/index reaction details not yet available in current pipe.")
        
        # 4) Divergence (Why mismatch)
        reasons = data.get("key_reasons", [])
        reasons_text = "\n".join([f"- {r}" for r in reasons]) if reasons else f"- {I18N_KO['NEEDS_DATA']}"
        sections.append(f"{I18N_KO['STEP_DIVERGENCE']}\n{reasons_text}")
        
        # 5) Evidence Comparison
        numbers = data.get("numbers", [])
        evidence_text = ""
        if numbers:
            for n in numbers:
                # Find source from linked candidates
                source_info = "N/A"
                for cand_id in data.get("source_candidates", []):
                    cand = cand_map.get(cand_id)
                    if cand:
                        for num in cand.get("numbers", []):
                            if num.get("label") == n.get("label"):
                                # This is a simple heuristic, ideally we'd have exact event refs
                                source_info = cand.get("category", "Gate Output")
                
                evidence_text += f"- **{n.get('label')}**: {n.get('value')} {n.get('unit')} (Ref: {source_info})\n"
        else:
            evidence_text = f"- {I18N_KO['NEEDS_DATA']}"
        sections.append(f"{I18N_KO['STEP_EVIDENCE']}\n{evidence_text}")
        
        # 6) What to watch next
        watchlist = [
            data.get("risk_one", I18N_KO["NEEDS_DATA"]),
            "Structural trend correlation confirmation",
            "Alternative source cross-check"
        ]
        watchlist_text = "\n".join([f"- {w}" for w in watchlist])
        sections.append(f"{I18N_KO['STEP_WATCHLIST']}\n{watchlist_text}")
        
        # 7) Risk note
        risk_note = data.get("risk_one", I18N_KO["NEEDS_DATA"])
        sections.append(f"{I18N_KO['STEP_RISK']}\n- {risk_note}")
        
        header = f"# Content Script Outline: {title}\nDate: {as_of}\n\n"
        return header + "\n\n".join(sections)

if __name__ == "__main__":
    # Standalone test
    import sys
    base = Path("/Users/taehunlim/.gemini/antigravity/scratch/HoinInsight")
    ymd = "2026-01-24"
    gen = ScriptGenerator(base)
    output = gen.generate_script(ymd)
    if output:
        print(output)
    else:
        print(f"No output for {ymd}")
