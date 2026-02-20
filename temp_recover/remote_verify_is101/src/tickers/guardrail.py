from typing import List, Tuple
from src.tickers.company_map_registry import CandidateCompany

def run_guardrail(candidates: List[CandidateCompany]) -> Tuple[List[CandidateCompany], List[str]]:
    """
    Apply Anti-Hallucination Guardrail.
    1. Must have >= 2 fact tokens.
    2. Must NOT have 'FACT_PR_ONLY' token.
    """
    passed = []
    rejections = []
    
    for c in candidates:
        # Check 1: Fact Count
        if len(c.fact_tokens) < 2:
            rejections.append(f"{c.company_name}: Insufficient Facts ({len(c.fact_tokens)}<2)")
            continue
            
        # Check 2: PR Only pollution
        is_pr_only = any("FACT_PR_ONLY" in t for t in c.fact_tokens)
        if is_pr_only:
            rejections.append(f"{c.company_name}: PR_ONLY Detected")
            continue
            
        passed.append(c)
        
    return passed, rejections
