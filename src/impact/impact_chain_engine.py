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
        Maps a structural causality chain to a list of stock candidates.
        """
        print(f"[ImpactChainEngine] Building structural chain for {len(candidates)} candidates...")
        results = []

        for stock_raw in candidates:
            stock_name = stock_raw.get("stock")
            ticker = self.TICKER_MAP.get(stock_name, stock_name)
            
            # Derive structural links
            industry = self._derive_industry(stock_name, stock_raw.get("sector"))
            directness = self._classify_directness(stock_name, core_theme)
            
            chain = {
                "ticker": ticker,
                "name": stock_name,
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

    def _classify_directness(self, stock, theme):
        """
        Classifies how directly the theme impacts the company's core revenue path.
        """
        direct_map = {
            "NVIDIA": ["AI", "Compute", "Power"],
            "Vertiv": ["Data Center", "Power", "Cooling"],
            "Vistra": ["Nuclear", "Power", "Energy"],
            "Microsoft": ["AI", "Software", "Cloud"]
        }
        
        for k, themes in direct_map.items():
            if stock == k and any(t in theme for t in themes):
                return "direct"
        
        # Indirect / Proxy detection
        if "Semiconductor" in theme or "Infrastructure" in theme:
            return "indirect"
            
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
