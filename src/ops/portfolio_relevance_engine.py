#!/usr/bin/env python3
"""
STEP-20: Portfolio Relevance Engine
Converts Topic / Narrative / Capital Flow data into a Priority Stock Basket.

Scoring Model (Max 100):
  1. Topic Relevance      (0-25): Confidence × theme keyword match
  2. Narrative Fit        (0-20): Propagation score × momentum
  3. Capital Flow Exposure(0-25): Stock impact_score from capital_flow_impact
  4. Structural Alignment (0-15): Regime × Allocation mode
  5. Actionability        (0-15): Timing gear × Investment OS stance

Baskets:
  CORE      >= 80
  TACTICAL  65-79
  WATCHLIST 50-64
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PortfolioRelevance")


class PortfolioRelevanceEngine:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_path = self.base_dir / "data/ops/portfolio_relevance.json"

    # ─────────────────────────────────────────────────────────────────────────
    # I/O helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _load(self, rel_path: str) -> Optional[Any]:
        p = self.base_dir / rel_path
        if not p.exists():
            logger.warning(f"[LOAD] Missing: {rel_path}")
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"[LOAD] JSON parse error {rel_path}: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Axis 1 — Topic Relevance (0-25)
    # ─────────────────────────────────────────────────────────────────────────
    def _topic_relevance(self, stock_name: str, stock_theme: str,
                         predictions: Optional[Dict], top_theme: str) -> int:
        score = 10  # base
        if not predictions:
            return score
        top_pred = predictions.get("predictions", [{}])[0] if predictions.get("predictions") else {}
        confidence = top_pred.get("confidence_score", 50)
        score += round((confidence / 100) * 10)  # 0-10 from confidence

        # Keyword match bonus (0-5)
        kw = (stock_name + " " + stock_theme + " " + top_theme).lower()
        if any(w in kw for w in ["semiconductor", "반도체", "ai", "nvidia", "hbm"]):
            score += 5
        elif any(w in kw for w in ["inflation", "금리", "fed", "policy", "관세"]):
            score += 3
        elif any(w in kw for w in ["energy", "power", "전력", "lithium", "배터리"]):
            score += 2

        return min(score, 25)

    # ─────────────────────────────────────────────────────────────────────────
    # Axis 2 — Narrative Fit (0-20)
    # ─────────────────────────────────────────────────────────────────────────
    def _narrative_fit(self, propagation: Optional[Dict], top_theme: str,
                       stock_sector: str) -> int:
        score = 8  # base
        if not propagation:
            return score
        results = propagation.get("results", [])
        if not results:
            return score
        top_prop = results[0]
        prop_score = top_prop.get("propagation_score", 50)
        score += round((prop_score / 100) * 8)  # 0-8
        
        # Momentum bonus (0-4)
        momentum = top_prop.get("momentum_class", "STABLE")
        if momentum == "ACCELERATING":
            score += 4
        elif momentum == "STABILIZING":
            score += 2
        
        return min(score, 20)

    # ─────────────────────────────────────────────────────────────────────────
    # Axis 3 — Capital Flow Exposure (0-25)
    # ─────────────────────────────────────────────────────────────────────────
    def _capital_flow_exposure(self, stock_name: str, capital_flow: Optional[Dict]) -> int:
        if not capital_flow:
            return 12  # neutral base
        
        stock_impacts = capital_flow.get("stock_impacts", [])
        for impact in stock_impacts:
            if impact.get("name", "") == stock_name:
                raw = impact.get("impact_score", 50)
                direction = impact.get("impact_direction", "POSITIVE")
                score = round((raw / 100) * 25)
                if direction == "NEGATIVE":
                    # negative exposure still relevant but discounted
                    score = round(score * 0.7)
                return min(score, 25)
        
        # Not explicitly listed — use sector-level impact
        sector_impacts = capital_flow.get("sector_impacts", [])
        if sector_impacts:
            top_si = sector_impacts[0]
            direction = top_si.get("impact_direction", "POSITIVE")
            base = 14 if direction == "POSITIVE" else 8
            return base
        
        return 12

    # ─────────────────────────────────────────────────────────────────────────
    # Axis 4 — Structural Alignment (0-15)
    # ─────────────────────────────────────────────────────────────────────────
    def _structural_alignment(self, stock_sector: str, regime: Optional[Dict],
                               allocation: Optional[Dict]) -> int:
        score = 7  # base
        
        # Regime contribution
        if regime:
            policy_state = regime.get("regime", {}).get("policy_state", "")
            liquidity = regime.get("regime", {}).get("liquidity_state", "")
            s = stock_sector.lower()
            if "TIGHTENING" in policy_state and any(w in s for w in ["financial", "bank", "금융"]):
                score += 5
            elif "EASING" in policy_state and any(w in s for w in ["growth", "tech", "semiconductor"]):
                score += 5
            if "TIGHTENING" in liquidity and any(w in s for w in ["defensive", "utility", "consumer"]):
                score += 3
        
        # Allocation mode
        if allocation:
            mode = allocation.get("allocation_profile", {}).get("mode", "")
            s = stock_sector.lower()
            if "OFFENSIVE" in mode and any(w in s for w in ["tech", "semiconductor", "growth"]):
                score += 3
            elif "DEFENSIVE" in mode and any(w in s for w in ["defensive", "utility", "healthcare"]):
                score += 3
        
        return min(score, 15)

    # ─────────────────────────────────────────────────────────────────────────
    # Axis 5 — Actionability (0-15)
    # ─────────────────────────────────────────────────────────────────────────
    def _actionability(self, timing: Optional[Dict], investment_os: Optional[Dict]) -> int:
        score = 6  # base
        
        if timing:
            gear = timing.get("timing_gear", {}).get("level", 1)
            # Higher gear = more actionable
            score += min(gear * 2, 6)  # gear 1→+2, 2→+4, 3→+6
        
        if investment_os:
            stance = investment_os.get("os_summary", {}).get("stance", "")
            if "OFFENSIVE" in stance:
                score += 3
            elif "BALANCED" in stance:
                score += 1
        
        return min(score, 15)

    # ─────────────────────────────────────────────────────────────────────────
    # Basket classification
    # ─────────────────────────────────────────────────────────────────────────
    def _classify_basket(self, score: int) -> Optional[str]:
        if score >= 80:
            return "CORE"
        elif score >= 65:
            return "TACTICAL"
        elif score >= 50:
            return "WATCHLIST"
        return None

    def _action_note(self, basket: str) -> str:
        return {
            "CORE": "현재 구조상 핵심 수혜 축",
            "TACTICAL": "단기 이벤트 드리븐 대응 가능",
            "WATCHLIST": "추가 확인 전 관찰 우선",
        }.get(basket, "")

    # ─────────────────────────────────────────────────────────────────────────
    # Main
    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        logger.info("Running Portfolio Relevance Engine (STEP-20)...")

        # Load all inputs
        predictions    = self._load("data/ops/topic_predictions.json")
        probability    = self._load("data/ops/topic_probability_ranking.json")
        propagation    = self._load("data/ops/narrative_propagation.json")
        capital_flow   = self._load("data/ops/capital_flow_impact.json")
        mentionables   = self._load("data/decision/mentionables.json")
        regime         = self._load("data/ops/regime_state.json")
        timing         = self._load("data/ops/timing_state.json")
        allocation     = self._load("data/ops/capital_allocation_state.json")

        # Determine top theme
        top_theme = "Unknown"
        portfolio_focus = "Diversified"
        topic_id = ""
        summary = ""

        if predictions and predictions.get("predictions"):
            top_pred = predictions["predictions"][0]
            top_theme = top_pred.get("theme", top_theme)
            topic_id = top_pred.get("topic_id", "")
            portfolio_focus = top_pred.get("sector_focus", top_theme)
            summary = top_pred.get("investment_thesis", f"{top_theme} 관련 종목군이 현재 가장 높은 관련성을 가짐")
        elif propagation and propagation.get("results"):
            top_prop = propagation["results"][0]
            top_theme = top_prop.get("theme", top_theme)
            topic_id = top_prop.get("topic_id", "")

        # Get stocks from mentionables
        stocks: List[Dict] = []
        if mentionables:
            stocks = mentionables.get("mentionables", [])

        if not stocks:
            logger.warning("No mentionable stocks found. Generating fallback basket.")
            # Fallback: use stock_impacts from capital_flow
            if capital_flow:
                for si in capital_flow.get("stock_impacts", []):
                    stocks.append({
                        "name": si.get("name", "Unknown"),
                        "ticker": si.get("ticker", "N/A"),
                        "theme": top_theme,
                        "sector": si.get("sector", "Unknown"),
                    })

        # Score each stock
        core_picks, tactical_picks, watchlist_picks = [], [], []

        for stock in stocks:
            name   = stock.get("name", "Unknown")
            ticker = stock.get("ticker", "N/A")
            theme  = stock.get("theme", top_theme)
            sector = stock.get("sector", "Unknown")

            axis1 = self._topic_relevance(name, theme, predictions, top_theme)
            axis2 = self._narrative_fit(propagation, top_theme, sector)
            axis3 = self._capital_flow_exposure(name, capital_flow)
            axis4 = self._structural_alignment(sector, regime, allocation)
            axis5 = self._actionability(timing, None)

            total = axis1 + axis2 + axis3 + axis4 + axis5
            basket = self._classify_basket(total)

            if basket is None:
                continue  # Score < 50 — not output

            # Determine impact direction from capital_flow
            impact_direction = "POSITIVE"
            risk = "시장 변동성 및 이벤트 리스크 주의"
            if capital_flow:
                for si in capital_flow.get("stock_impacts", []):
                    if si.get("name") == name:
                        impact_direction = si.get("impact_direction", "POSITIVE")
                        risk = si.get("risk", risk)
                        break

            entry: Dict[str, Any] = {
                "name": name,
                "ticker": ticker,
                "theme": theme,
                "sector": sector,
                "portfolio_relevance_score": total,
                "basket": basket,
                "impact_direction": impact_direction,
                "reason": f"{top_theme} 테마와의 구조적 연결 (TopicRel={axis1}, NarrFit={axis2}, CapFlow={axis3}, StrAlign={axis4}, Action={axis5})",
                "risk": risk,
                "action_note": self._action_note(basket),
                "score_breakdown": {
                    "topic_relevance": axis1,
                    "narrative_fit": axis2,
                    "capital_flow_exposure": axis3,
                    "structural_alignment": axis4,
                    "actionability": axis5,
                },
            }

            if basket == "CORE":
                core_picks.append(entry)
            elif basket == "TACTICAL":
                tactical_picks.append(entry)
            else:
                watchlist_picks.append(entry)

        # Sort each basket by score descending
        for basket_list in [core_picks, tactical_picks, watchlist_picks]:
            basket_list.sort(key=lambda x: x["portfolio_relevance_score"], reverse=True)

        output = {
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "top_portfolio_theme": {
                "topic_id": topic_id,
                "theme": top_theme,
                "portfolio_focus": portfolio_focus,
                "summary": summary,
            },
            "core_picks": core_picks,
            "tactical_picks": tactical_picks,
            "watchlist_picks": watchlist_picks,
            "stats": {
                "total_scored": len(core_picks) + len(tactical_picks) + len(watchlist_picks),
                "core_count": len(core_picks),
                "tactical_count": len(tactical_picks),
                "watchlist_count": len(watchlist_picks),
            },
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        logger.info(
            f"Portfolio Relevance complete. "
            f"CORE={len(core_picks)}, TACTICAL={len(tactical_picks)}, WATCHLIST={len(watchlist_picks)}"
        )
        return output


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    engine = PortfolioRelevanceEngine(str(base_dir))
    engine.run()


if __name__ == "__main__":
    main()
