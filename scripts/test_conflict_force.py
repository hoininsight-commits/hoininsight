import json
from pathlib import Path
from src.ops.narrative_intelligence_layer import NarrativeIntelligenceLayer

def test_force():
    base = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    ni = NarrativeIntelligenceLayer(base)
    
    test_cases = [
        {
            "name": "Case 1: CPI Spike + Rate Hike (Macro Divergence Test)",
            "card": {
                "title": "CPI SHOCK: Inflation surges 5%, FED FUNDS RATE HIKE expected immediately",
                "rationale_natural": "CPI matches MacroEvent, RATE HIKE matches Tightening. Since Tightening isn't in Divergence, let's see.",
                "intensity": 80
            }
        },
        {
            "name": "Case 2: VIX Spike + Index Crash (Risk-Off Conflict Test)",
            "card": {
                "title": "VIX SURGE: Market risk indices at record highs as S&P 500 PRICE DECLINE accelerates",
                "rationale_natural": "VIX matches GeoRisk, PRICE DECLINE matches PriceDecline. Should trigger GeoRisk_Rally if rally? No, wait.",
                "intensity": 90
            }
        },
        {
            "name": "Case 3: Yield Curve Inversion (Policy Gap Test)",
            "card": {
                "title": "YIELD CURVE INVERSION: Macro signal of upcoming recession, TIGHTENING continues",
                "rationale_natural": "Requires specific keywords.",
                "intensity": 70
            }
        }
    ]
    
    print("# Conflict Force Test Results\n")
    results = []
    for case in test_cases:
        card = case["card"]
        # Simulate detection
        conflict = ni._detect_conflict(card, [], False)
        patterns = card.get("_diag_conflict_patterns", [])
        
        res_str = f"## {case['name']}\n"
        res_str += f"- **Title**: {card['title']}\n"
        res_str += f"- **Conflict Detected**: {conflict}\n"
        res_str += f"- **Matched Patterns**: {patterns}\n\n"
        print(res_str)
        results.append(res_str)
        
    report_path = base / "data_outputs/ops/conflict_force_test.md"
    report_path.write_text("".join(results), encoding="utf-8")
    print(f"Force test report saved to {report_path}")

if __name__ == "__main__":
    test_force()
