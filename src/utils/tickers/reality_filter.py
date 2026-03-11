from typing import List, Tuple
from src.tickers.company_map_registry import CandidateCompany

def run_reality_filter(candidates: List[CandidateCompany]) -> Tuple[List[CandidateCompany], List[str]]:
    """
    Apply 5-Point Reality Check.
    Reject if fail count >= 2.
    Returns (Passed Candidates, Rejection Reasons)
    """
    passed = []
    rejections = []
    
    for c in candidates:
        failures = []
        if not c.revenue_exists: failures.append("No Revenue")
        if not c.delivery_record: failures.append("No Delivery")
        if not c.certification: failures.append("No Cert")
        if not c.capacity_scale: failures.append("No Scale")
        if not c.leadtime_ok: failures.append("Bad Leadtime")
        
        if len(failures) >= 2:
            rejections.append(f"{c.company_name}: Reality Fail ({', '.join(failures)})")
        else:
            passed.append(c)
            
    return passed, rejections
