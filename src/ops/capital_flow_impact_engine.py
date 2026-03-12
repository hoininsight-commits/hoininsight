#!/usr/bin/env python3
"""
STEP-19: Capital Flow Impact Engine
Analyzes narrative impact on capital rotation, sector flows, and stock-level pressure/benefit.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CapitalFlowImpact")

class CapitalFlowImpactEngine:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_path = self.base_dir / "data/ops/capital_flow_impact.json"

    def _load_json(self, path: Path):
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _calculate_impact_score(self, propagation: Dict, theme: str) -> Dict[str, Any]:
        """
        Scoring Model (Max 100):
        1. Propagation Score (25): Normalized from propagation engine.
        2. Sector Impact Strength (25): Based on theme structural importance.
        3. Capital Rotation Likelihood (25): Probability of money moving between sectors.
        4. Narrative-to-Money Conversion (25): Ease of translation to investment action.
        """
        prop_score_raw = propagation.get("propagation_score", 50)
        prop_score = (prop_score_raw / 100) * 25

        theme_l = theme.lower()
        sector_strength = 15
        if any(k in theme_l for k in ["semiconductor", "ai", "nvidia", "inflation", "macro", "shock"]):
            sector_strength = 25
        elif any(k in theme_l for k in ["policy", "reg", "정부"]):
            sector_strength = 20

        rotation_likelihood = 18
        if "shock" in theme_l or "inflation" in theme_l or "금리" in theme_l:
            rotation_likelihood = 25 # High rotation during macro shifts
        
        conversion_score = 15
        if any(k in theme_l for k in ["ai", "crypto", "반도체"]):
            conversion_score = 25 # High retail/institutional conversion

        total_score = round(prop_score + sector_strength + rotation_likelihood + conversion_score, 2)

        return {
            "total_score": min(total_score, 100),
            "breakdown": {
                "propagation_weight": prop_score,
                "sector_impact": sector_strength,
                "rotation_likelihood": rotation_likelihood,
                "money_conversion": conversion_score
            }
        }

    def _analyze_sector_impacts(self, theme: str) -> List[Dict]:
        theme_l = theme.lower()
        impacts = []
        
        if "inflation" in theme_l or "금리" in theme_l or "fed" in theme_l:
            impacts.append({
                "sector": "Financials",
                "impact_direction": "POSITIVE",
                "impact_strength": "HIGH",
                "reason": "금리 상승 기조에 따른 순이자마진(NIM) 개선 기대"
            })
            impacts.append({
                "sector": "Growth / Tech",
                "impact_direction": "NEGATIVE",
                "impact_strength": "MEDIUM",
                "reason": "할인율 상승에 따른 밸류에이션 부담 가중"
            })
        elif "semiconductor" in theme_l or "ai" in theme_l:
            impacts.append({
                "sector": "Semiconductors",
                "impact_direction": "POSITIVE",
                "impact_strength": "HIGH",
                "reason": "AI 인프라 투자 지속 및 고대역폭메모리(HBM) 수요 폭증"
            })
        elif "policy" in theme_l or "횡령" in theme_l or "수사" in theme_l:
            impacts.append({
                "sector": "Regulatory Impact / Finance",
                "impact_direction": "NEGATIVE",
                "impact_strength": "MEDIUM",
                "reason": "지배구조 리스크 및 규제 불확실성 증대"
            })

        return impacts

    def _analyze_stock_impacts(self, stocks: List[Dict], theme: str) -> List[Dict]:
        # Simple heuristic mapping for demonstration
        theme_l = theme.lower()
        impacted_stocks = []
        
        for stock in stocks:
            name = stock.get("name", "")
            impact_type = "INDIRECT_BENEFIT"
            impact_direction = "POSITIVE"
            impact_score = 65
            
            if "반도체" in theme_l and any(k in name for k in ["SK하이닉스", "삼성전자", "한미반도체"]):
                impact_type = "DIRECT_BENEFIT"
                impact_score = 85
            elif ("수사" in theme_l or "정부" in theme_l) and any(k in name for k in ["금융", "지주"]):
                impact_type = "DIRECT_PRESSURE"
                impact_direction = "NEGATIVE"
                impact_score = 75

            impacted_stocks.append({
                "name": name,
                "ticker": stock.get("ticker", "N/A"),
                "sector": stock.get("sector", "Unknown"),
                "impact_direction": impact_direction,
                "impact_score": impact_score,
                "impact_type": impact_type,
                "reason": f"{theme} 테마와의 구조적 연결성에 기반한 {impact_type} 예상",
                "risk": "매크로 변동성 및 개별 기업 이슈에 따른 변동성 주의"
            })
            
        return sorted(impacted_stocks, key=lambda x: x["impact_score"], reverse=True)

    def run(self):
        logger.info("Running Capital Flow Impact Engine...")
        
        # Load inputs
        propagation = self._load_json(self.base_dir / "data/ops/narrative_propagation.json")
        mentionables = self._load_json(self.base_dir / "data/decision/mentionables.json")
        regime = self._load_json(self.base_dir / "data/ops/regime_state.json")
        
        if not propagation:
            logger.error("Missing propagation data.")
            return

        results = propagation.get("results", [])
        if not results:
            logger.warning("No propagation results to analyze.")
            return

        # Analyze top theme
        top_prop = results[0]
        theme = top_prop.get("theme", "Unknown")
        
        i_score_data = self._calculate_impact_score(top_prop, theme)
        sector_impacts = self._analyze_sector_impacts(theme)
        
        # Get stocks from mentionables
        relevant_stocks = []
        if mentionables and "structural_stocks" in mentionables:
            relevant_stocks = mentionables["structural_stocks"]
        
        stock_impacts = self._analyze_stock_impacts(relevant_stocks, theme)

        output_data = {
            "generated_at": datetime.now().isoformat(),
            "top_capital_flow_theme": {
                "topic_id": top_prop.get("topic_id"),
                "theme": theme,
                "capital_flow_impact_score": i_score_data["total_score"],
                "primary_sector": sector_impacts[0]["sector"] if sector_impacts else "Diversified",
                "impact_direction": sector_impacts[0]["impact_direction"] if sector_impacts else "NEUTRAL",
                "reason": f"{theme} 확산에 따른 자본 재배치 압력 분석 결과",
                "score_breakdown": i_score_data["breakdown"]
            },
            "sector_impacts": sector_impacts,
            "stock_impacts": stock_impacts
        }

        # Save output
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        logger.info("Generated Capital Flow Impact analysis.")

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    engine = CapitalFlowImpactEngine(base_dir)
    engine.run()

if __name__ == "__main__":
    main()
