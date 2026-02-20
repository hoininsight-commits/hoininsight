from __future__ import annotations

def validate_evidence(raw_event: dict) -> bool:
    """
    HARD FILTER RULES for Step 9:
    1. numbers array must have length >= 1
    2. At least one element in numbers must have a non-None 'value'
    """
    numbers = raw_event.get("numbers", [])
    if not isinstance(numbers, list) or len(numbers) == 0:
        return False
    
    for n in numbers:
        if n.get("value") is not None:
            return True
            
    return False
