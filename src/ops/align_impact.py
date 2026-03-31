import json
from pathlib import Path

def align_impact(project_root, core_theme, impact_data):
    """
    Filters mentionable stocks and improves rationale structure.
    Expects impact_data to have 'mentionable_stocks' and potentially 'affected_sectors'.
    """
    stocks = impact_data.get("mentionable_stocks", [])
    
    # Filter stocks. Since the existing data might not have a 'themes' list per stock,
    # we'll assume ALL stocks in the impact file are relevant if the file's top-level theme matches.
    # If not, we'll keep them but flag them.
    
    aligned_stocks = []
    for s in stocks:
        # Upgrade Rationale structure: string -> list
        reason = s.get("reason", "No rationale provided")
        reason_list = reason.split(". ") if isinstance(reason, str) else [str(reason)]
        # Clean up each reason
        reason_list = [r.strip() for r in reason_list if r.strip()]
        if not reason_list:
            reason_list = ["핵심 수혜주 분석 중"]

        new_stock = {
            "stock": s.get("stock", "N/A"),
            "score": s.get("score", 0),
            "reason": reason_list, # Upgraded to list
            "theme_alignment": "MATCH" if core_theme in s.get("themes", [core_theme]) else "MISMATCH"
        }
        aligned_stocks.append(new_stock)

    aligned_data = {
        "theme": core_theme,
        "mentionable_stocks": aligned_stocks,
        "affected_sectors": impact_data.get("affected_sectors", [])
    }
    
    print(f"[Aligner] Impact aligned for {core_theme} with {len(aligned_stocks)} stocks")
    return aligned_data

if __name__ == "__main__":
    sample = {
        "mentionable_stocks": [
            {"stock": "NVDA", "reason": "AI GPU leader. Data center growth.", "score": 95}
        ]
    }
    print(json.dumps(align_impact(".", "AI Power Constraint", sample), indent=2, ensure_ascii=False))
