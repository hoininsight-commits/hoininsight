from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class TrapReason(Enum):
    NO_CAPITAL_EVIDENCE = "NO_CAPITAL_EVIDENCE"
    NO_FORCED_BUYER = "NO_FORCED_BUYER"
    NO_MUST_ITEM = "NO_MUST_ITEM"
    NO_TIME_WINDOW = "NO_TIME_WINDOW"
    TIME_ASYMMETRY_TRAP = "TIME_ASYMMETRY_TRAP"

class TrapEngine:
    """
    (IS-24) Detects fake moves and structural traps using three criteria:
    A) Capital Confirmation Score
    B) Exit Visibility Check
    C) Time Asymmetry Trap
    """
    VALID_ACTORS = {"GOV", "BIGTECH", "OEM", "UTILITY", "BANK", "DEFENSE", "CONSUMER", "EXPORTER"}

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def evaluate(self, signal: Dict[str, Any], evidence_pack: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Evaluates a signal for traps.
        Returns: (is_passed, reason_code, debug_info)
        """
        debug = {}
        
        # A) CAPITAL_CONFIRMATION_SCORE
        cap_score, used_evidence = self._calculate_capital_score(evidence_pack)
        debug["capital_score"] = cap_score
        debug["evidence_used"] = used_evidence
        
        if cap_score < 50:
            return False, TrapReason.NO_CAPITAL_EVIDENCE.value, debug

        # B) EXIT_VISIBILITY_CHECK
        exit_passed, exit_fail_code = self._check_exit_visibility(signal)
        debug["exit_check"] = "PASS" if exit_passed else "FAIL"
        
        if not exit_passed:
            return False, exit_fail_code, debug

        # C) TIME_ASYMMETRY_TRAP
        time_passed, is_asymmetry_trap = self._check_time_asymmetry(signal, cap_score >= 50 and any(e["type"] == "STRONG" for e in used_evidence))
        debug["time_asymmetry"] = "PASS" if time_passed else "FAIL"
        
        if not time_passed:
            return False, TrapReason.TIME_ASYMMETRY_TRAP.value, debug

        return True, None, debug

    def _calculate_capital_score(self, evidence_pack: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
        score = 0
        used = []
        
        evidence_list = evidence_pack.get("evidence", [])
        for ev in evidence_list:
            ev_type = ev.get("type", "WEAK").upper()
            if ev_type == "STRONG":
                score += 50
                used.append({"type": "STRONG", "desc": ev.get("desc")})
            elif ev_type == "MEDIUM":
                score += 30
                used.append({"type": "MEDIUM", "desc": ev.get("desc")})
            else:
                used.append({"type": "WEAK", "desc": ev.get("desc")})
                
        return min(score, 100), used

    def _check_exit_visibility(self, signal: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        actor = signal.get("actor", "").upper()
        if actor not in self.VALID_ACTORS:
            return False, TrapReason.NO_FORCED_BUYER.value
            
        if not signal.get("must_item"):
            return False, TrapReason.NO_MUST_ITEM.value
            
        # Basic validation for time window (needs specific format like 72h, 2w, 1q)
        time_window = signal.get("time_window", "")
        if not any(unit in time_window for unit in ["h", "w", "q", "m"]):
            return False, TrapReason.NO_TIME_WINDOW.value
            
        return True, None

    def _check_time_asymmetry(self, signal: Dict[str, Any], has_strong_commitment: bool) -> Tuple[bool, bool]:
        # EntryLatency: 0 (fast) to 3 (slow)
        # ExitShock: 0 (instant) to 3 (slow)
        entry_latency = signal.get("entry_latency", 2) # Default Medium-Slow
        exit_shock = signal.get("exit_shock", 0)       # Default Instant
        
        # Exception: Already committed capital passes even if entry is slow
        if has_strong_commitment:
            return True, False
            
        # Trap: Entry is slow, but Exit is instant
        # If entry_latency > exit_shock, it's a trap
        if entry_latency > exit_shock:
            return False, True
            
        return True, False
