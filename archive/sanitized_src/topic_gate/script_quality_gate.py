import re
from typing import Dict, List, Optional
from src.utils.i18n_ko import I18N_KO

class ScriptQualityGate:
    """
    Evaluates the quality of a generated script outline to decide content readiness.
    Status: READY | HOLD | DROP
    """
    
    def evaluate(self, topic_id: str, script_text: Optional[str]) -> Dict:
        """
        Main evaluation method.
        Input: Script outline text (Markdown)
        Output: JSON dict with status and reason codes.
        """
        if not script_text:
            return {
                "topic_id": topic_id,
                "quality_status": "DROP",
                "failure_codes": ["NO_SCRIPT_TEXT"],
                "summary_reason": "Script generation failed or returned empty.",
                "missing_requirements": ["Script content"]
            }

        sections = self._parse_sections(script_text)
        checks = self._run_checks(sections)
        decision = self._decide_status(checks)
        
        return {
            "topic_id": topic_id,
            "quality_status": decision["status"],
            "failure_codes": decision["codes"],
            "summary_reason": decision["reason"],
            "missing_requirements": decision["missing"]
        }

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parses Markdown sections into a dictionary.
        Target sections: Hook, Expectation, Move, Divergence, Evidence, Watchlist, Risk
        """
        # Mapping known headers in I18N or raw text to internal keys
        # Based on script_generator.py format:
        # ### 1) 훅 (모순점)
        # ### 2) 시장 기대치 ...
        
        section_map = {
            "1)": "hook",
            "2)": "expectation",
            "3)": "move",
            "4)": "divergence",
            "5)": "evidence",
            "6)": "watchlist",
            "7)": "risk"
        }
        
        parsed = {}
        current_key = None
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith("###"):
                # Identify section
                for marker, key in section_map.items():
                    if marker in line:
                        current_key = key
                        parsed[key] = ""
                        break
            elif current_key:
                parsed[current_key] += line + "\n"
                
        return parsed

    def _run_checks(self, sections: Dict[str, str]) -> Dict:
        """
        Executes specific logic checks A, B, C, D
        """
        results = {
            "hook_valid": False,
            "evidence_count": 0,
            "watch_count": 0,
            "consistent": True,
            "codes": []
        }
        
        # Helper: check for placeholder
        # I18N_KO['NEEDS_DATA'] is typically "[데이터 부족/필요]"
        # But we should check loosely for "부족" or "필요" or "NEEDS DATA" just in case
        placeholder_pattern = re.compile(r"\[.*(부족|필요|NEEDS).*\]")
        
        # A) HOOK / DIVERGENCE
        # Must NOT have placeholders in Hook or Divergence
        hook_text = sections.get("hook", "")
        div_text = sections.get("divergence", "")
        
        has_placeholder_hook = bool(placeholder_pattern.search(hook_text))
        has_placeholder_div = bool(placeholder_pattern.search(div_text))
        
        if has_placeholder_hook or has_placeholder_div or not hook_text.strip() or not div_text.strip():
            results["hook_valid"] = False
            results["codes"].append("FAIL_HOOK")
        else:
            results["hook_valid"] = True
            
        # B) EVIDENCE SUFFICIENCY
        # Count lines starting with "- **" in evidence section
        ev_text = sections.get("evidence", "")
        # script_generator output format: "- **Label**: Value ..."
        ev_items = re.findall(r"-\s*\*\*", ev_text)
        results["evidence_count"] = len(ev_items)
        
        if results["evidence_count"] == 0:
            results["codes"].append("NO_EVIDENCE")
        elif results["evidence_count"] == 1:
            results["codes"].append("WEAK_EVIDENCE")
            
        # C) WATCH NEXT QUALITY
        # Count bullet points in watchlist
        watch_text = sections.get("watchlist", "")
        # exclude placeholders if they appear as bullets
        watch_lines = [line for line in watch_text.split('\n') if line.strip().startswith("-")]
        valid_watch_items = 0
        for w in watch_lines:
            if not placeholder_pattern.search(w):
                valid_watch_items += 1
        
        results["watch_count"] = valid_watch_items
        if valid_watch_items < 2:
            results["codes"].append("NO_FORWARD_SIGNAL")

        # D) INTERNAL CONSISTENCY
        # Logic: If Divergence claims specific reasons, but Evidence is ZERO -> INCONSISTENT
        # (Claiming Mismatch without backing data)
        if results["hook_valid"] and results["evidence_count"] == 0:
            results["consistent"] = False
            results["codes"].append("INCONSISTENT")
        
        return results

    def _decide_status(self, checks: Dict) -> Dict:
        """
        Applies Decision Rules to return final status.
        """
        status = "DROP"
        reason = ""
        missing = []
        
        # Status Logic
        # DROP conditions
        if (not checks["hook_valid"]) or (checks["evidence_count"] == 0) or (not checks["consistent"]):
            status = "DROP"
            if not checks["hook_valid"]: missing.append("Clear Hook/Divergence")
            if checks["evidence_count"] == 0: missing.append("Any Evidence")
            if not checks["consistent"]: missing.append("Internal Consistency")
            
        # HOLD conditions
        # Pass A (Hook valid) AND (Evidence == 1 OR Watch < 2)
        elif checks["hook_valid"] and (checks["evidence_count"] == 1 or checks["watch_count"] < 2):
            status = "HOLD"
            if checks["evidence_count"] == 1: missing.append("More Evidence (Need >= 2)")
            if checks["watch_count"] < 2: missing.append("More Forward Signals (Need >= 2)")
            
        # READY conditions
        # Pass A, Evidence >= 2, Watch >= 2, Consistent
        elif checks["hook_valid"] and checks["evidence_count"] >= 2 and checks["watch_count"] >= 2 and checks["consistent"]:
            status = "READY"
        
        # Fallback (should be covered, but safety)
        else:
            status = "DROP"
            missing.append("Unknown State")

        # Summary Reason
        if status == "READY":
            reason = "Passes all quality checks."
        elif status == "HOLD":
            reason = "Core logic valid but lacks sufficient backing or future signals."
        else: # DROP
            reason = "Fundamental flaws in hook, evidence, or consistency."
            
        return {
            "status": status,
            "codes": checks["codes"],
            "reason": reason,
            "missing": missing
        }
