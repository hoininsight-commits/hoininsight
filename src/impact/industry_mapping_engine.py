def map_industry(theme_type, context=None):
    """
    [STEP-H-3] Maps theme types to specific industrial sectors.
    """
    if theme_type == "CONSTRAINT":
        return [
            "Utilities",
            "Electrical Equipment",
            "Energy Infrastructure",
            "Grid / Power Systems",
            "Data Center Infrastructure",
            "Thermal Management"
        ]
    elif theme_type == "EXPANSION":
        return [
            "Software",
            "Semiconductors",
            "Platform",
            "Application Layer",
            "Consumer AI",
            "Enterprise SaaS"
        ]
    return []

def validate_cross_sector(theme_type, industry):
    """
    Prevents mismapping of industries based on theme type.
    """
    industry_lower = str(industry).lower()
    if theme_type == "CONSTRAINT":
        # In a constraint regime, pure software/app layers are usually NOT the primary solvers
        if any(k in industry_lower for k in ["software", "application", "saas", "consumer"]):
            return False
    return True

def select_best_industry(stock, target_industries):
    """
    Heuristically selects the best matching industry from a target list for a given stock.
    """
    stock_industry = str(stock.get("industry_link", "")).lower()
    for target in target_industries:
        if target.lower() in stock_industry:
            return target
    # Fallback to first if no match, or keep original if valid
    return target_industries[0] if target_industries else stock_industry
