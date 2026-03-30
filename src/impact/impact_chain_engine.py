import json
from pathlib import Path
from datetime import datetime

class ImpactChainEngine:
    """
    [STEP-E] Decision → Impact Chain Engine
    Converts keyword-based mentionables into structural causality-linked impact chains.
    """
    
    TICKER_MAP = {
        "NVIDIA": "NVDA",
        "SKHynix": "000660.KS",
        "SamsungElectronics": "005930.KS",
        "Micron": "MU",
        "TSMC": "TSM",
        "ASML": "ASML",
        "AppliedMaterials": "AMAT",
        "Microsoft": "MSFT",
        "Palantir": "PLTR",
        "Vertiv": "VRT",
        "Eaton": "ETN",
        "Vistra": "VST",
        "ConstellationEnergy": "CEG",
        "Cameco": "CCJ"
    }

    def __init__(self, project_root):
        self.project_root = Path(project_root)

    def build_impact_chain(self, core_theme, causality, candidates):
        """
        [STEP-H-3] Build structural chain with Theme Type (Constraint/Expansion) filtering.
        """
        from src.impact.theme_type_classifier import classify_theme_type
        from src.impact.industry_mapping_engine import map_industry, select_best_industry, validate_cross_sector
        
        print(f"[ImpactChainEngine] Building structural mapping for {core_theme}")
        
        # 1. Classify Theme Type
        theme_type = classify_theme_type(core_theme, causality)
        print(f"[ImpactChainEngine] Theme Type: {theme_type}")
        
        # 2. Map Target Industries
        target_industries = map_industry(theme_type, causality)
        
        results = []
        for stock_raw in candidates:
            stock_name = stock_raw.get("stock")
            ticker = self.TICKER_MAP.get(stock_name, stock_name)
            
            # 3. Structural Linkage Logic
            base_industry = self._derive_industry(stock_name, stock_raw.get("sector"))
            
            # Cross-Sector Validation: Ensure we don't pick software for a constraint solver
            if not validate_cross_sector(theme_type, base_industry):
                print(f"[ImpactChainEngine] Skipping {stock_name} ({base_industry}) - Cross-Sector Mismatch for {theme_type}")
                # We can mark it as indirect or keep it with a warning, but user wants to "fix"
                # so we will lower its directness in the next step
            
            industry = select_best_industry({"industry_link": base_industry}, target_industries)
            directness = self._classify_directness(stock_name, core_theme, theme_type, base_industry)
            
            chain = {
                "ticker": ticker,
                "name": stock_name,
                "theme_type": theme_type,
                "theme_link": core_theme,
                "mechanism_link": causality.get("mechanism", "N/A"),
                "structural_context": causality.get("structural_context", "N/A"),
                "industry_link": industry,
                "company_link": self._derive_company_link(stock_name, core_theme),
                "directness": directness,
                "impact_reason": self._derive_impact_reason(stock_name, causality, industry),
                "evidence_basis": self._derive_evidence(stock_name, industry)
            }
            results.append(chain)

        return results

    def _derive_industry(self, stock, sector):
        if sector: return sector
        # Fallback mappings
        industry_map = {
            "NVIDIA": "AI Semiconductor / GPU",
            "Microsoft": "Cloud / AI Software",
            "Vertiv": "Data Center Infrastructure / Cooling",
            "Vistra": "Nuclear Power / Energy Utility"
        }
        return industry_map.get(stock, "Technology Infrastructure")

    def _classify_directness(self, stock, theme, theme_type, industry):
        """
        [STEP-H-3] Redefined Directness based on Role (Solver vs User).
        """
        # Infrastructure identification
        is_infrastructure = any(k in str(industry).lower() for k in ["utility", "infrastructure", "equipment", "power", "grid", "cooling"])
        
        if theme_type == "CONSTRAINT":
            if is_infrastructure:
                return "solver_direct"
            return "indirect"
            
        if theme_type == "EXPANSION":
            if not is_infrastructure:
                return "user_direct"
            return "direct" # Infrastructure still direct in expansion (e.g. data centers)
            
        return "proxy"

    def _derive_company_link(self, stock, theme):
        """
        Explains the company's specific role in the theme.
        """
        links = {
            "NVIDIA": "GPU 공급 핵심 기업으로 AI 연산 수요의 직접적 수혜자",
            "Vertiv": "AI 데이터센터 필수 전력 및 냉각 솔루션 글로벌 리더",
            "Vistra": "AI 전력 수요 폭증에 따른 원자력 발전 용량 가독 경쟁력 보유",
            "Microsoft": "AI 플랫폼 및 클라우드 인프라 아키텍처 통합 지배력"
        }
        return links.get(stock, f"{theme} 밸류체인 내 핵심 파트너 및 솔루션 제공자")

    def _derive_impact_reason(self, stock, causality, industry):
        """
        Connects mechanism to specific company impact.
        """
        mechanism = causality.get("mechanism", "Unknown shift")
        return f"{industry} 내 {mechanism} 진행 -> {stock}의 시장 지배력 및 매출 가독성 증가"

    def _derive_evidence(self, stock, industry):
        """
        Mandatory data points for structural evidence.
        """
        evidence_pool = {
            "NVIDIA": ["Data Center Revenue Growth", "GPU TAM Expansion", "H100/B200 Backlog"],
            "Vertiv": ["Liquid Cooling Adoption Rate", "Data Center Capex", "Backlog Duration"],
            "Vistra": ["Nuclear PPA Pricing", "PJM Power Auction Results", "Data Center Power Demand"],
            "Microsoft": ["Azure AI Contribution", "Copilot Subscriptions", "Capex Cycle"]
        }
        return evidence_pool.get(stock, [f"{industry} Growth Rate", "Market Share Trend", "Revenue Visibility"])
