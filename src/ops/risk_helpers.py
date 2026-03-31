def generate_invalidation(theme):
    """
    Returns a human-readable invalidation condition based on the theme name.
    """
    theme_upper = theme.upper()
    
    if "AI" in theme_upper:
        return "AI 관련 Capex 감소 또는 전력 전용 인프라 투자 둔화"
    
    if "LIQUIDITY" in theme_upper or "금리" in theme_upper:
        return "금리 인상 또는 중앙은행 유동성 회수"
    
    if "CHIP" in theme_upper or "반도체" in theme_upper:
        return "반도체 리드타임 단축 또는 재고 급증"
    
    if "ENERGY" in theme_upper or "에너지" in theme_upper:
        return "유가 급락 또는 신재생 에너지 정책 철회"

    return "핵심 지표 약화 및 내러티브 가속도 임계치 하회"
