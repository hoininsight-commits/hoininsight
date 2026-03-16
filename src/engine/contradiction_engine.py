import os
import json
from datetime import datetime
from pathlib import Path

class MarketContradictionEngine:
    """
    Engine for detecting structural market contradictions.
    Logic designed to find 'tensions' that lead to early theme discovery.
    """
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.data_ops_dir = self.project_root / "data" / "ops"
        self.data_features_dir = self.project_root / "data" / "features" / "anomalies"
        self.output_dir = self.project_root / "data" / "contradictions"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_json(self, path):
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _get_latest_anomaly(self, metric_name):
        # Look for latest date folder in data/features/anomalies
        date_folders = sorted([d for d in self.data_features_dir.iterdir() if d.is_dir()], reverse=True)
        for folder in date_folders:
            path = folder / f"{metric_name}.json"
            if path.exists():
                return self._load_json(path)
        return None

    def run_all(self):
        print("[MarketContradictionEngine] Starting Contradiction Detection...")
        
        contradictions = []
        
        # 1. Load context
        benchmark = self._load_json(self.data_ops_dir / "market_prediction_benchmark.json") or {}
        narratives = self._load_json(self.data_ops_dir / "narrative_intelligence_v2.json") or {}
        capital_flow = self._load_json(self.data_ops_dir / "capital_flow_impact.json") or {}
        
        # Rule Group A: Growth vs Capacity (AI/Semiconductor vs Foundry)
        contradiction_a = self._detect_growth_vs_capacity(benchmark, narratives)
        if contradiction_a:
            contradictions.append(contradiction_a)
            
        # Rule Group B: Policy vs Market (Rates expectation vs Yields)
        contradiction_b = self._detect_policy_vs_market(benchmark)
        if contradiction_b:
            contradictions.append(contradiction_b)
            
        # Rule Group C: Liquidity vs Risk (M2 expansion vs Asset decline)
        contradiction_c = self._detect_liquidity_vs_risk(benchmark)
        if contradiction_c:
            contradictions.append(contradiction_c)
            
        # Rule Group D: Narrative vs Data (Media hype vs Real data)
        contradiction_d = self._detect_narrative_vs_data(narratives)
        if contradiction_d:
            contradictions.append(contradiction_d)
            
        # Output results
        output_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "contradictions": contradictions,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        output_path = self.output_dir / "contradiction_state.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        print(f"[MarketContradictionEngine] Found {len(contradictions)} contradictions. Saved to {output_path}")
        return output_data

    def _detect_growth_vs_capacity(self, benchmark, narratives):
        # AI/Semiconductor narrative is strong?
        ai_strength = 0
        topics = narratives.get("topics", [])
        for t in topics:
            if any(k in t.get("title", "").upper() for k in ["AI", "SEMICONDUCTOR", "CHIP"]):
                ai_strength = max(ai_strength, t.get("final_narrative_score", 0))
        
        # Any supply chain or foundry constraints mentioned in benchmark shifts?
        constraint_detected = False
        shifts = benchmark.get("structural_shift", {}).get("active_shifts", [])
        for s in shifts:
            if "Reshuffle" in s.get("theme", "") or "Constraint" in s.get("theme", ""):
                constraint_detected = True
                
        if ai_strength > 60 and constraint_detected:
            return {
                "name": "AI & Semiconductor Capacity Friction",
                "type": "Growth vs Capacity",
                "strength": round(ai_strength / 100, 2),
                "confidence": "HIGH",
                "affected_sectors": ["Technology", "Semiconductors", "Infrastructure"],
                "reason": "AI narrative remains hyper-strong while fundamental foundry/capacity reshuffle is ongoing."
            }
        return None

    def _detect_policy_vs_market(self, benchmark):
        # Macro regime tightening but bond yields rising (standard, but when diverged from expectation)
        regime = benchmark.get("macro_regime", {}).get("regime", "")
        
        # Check yield curve anomaly
        yield_anomaly = self._get_latest_anomaly("derived_yield_curve_10y_2y")
        is_inverted = False
        if yield_anomaly and yield_anomaly.get("z_score", 0) > 1.5:
            is_inverted = True
            
        if "TIGHTENING" in regime and is_inverted:
            return {
                "name": "Monetary Policy & Yield Divergence",
                "type": "Policy vs Market",
                "strength": 0.75,
                "confidence": "MEDIUM",
                "affected_sectors": ["Financials", "Real Estate"],
                "reason": "Official regime is Tightening, but yield curve inversion signals recessionary expectation contradiction."
            }
        return None

    def _detect_liquidity_vs_risk(self, benchmark):
        liq_state = benchmark.get("liquidity", {}).get("state", "")
        risk_state = benchmark.get("risk", {}).get("state", "")
        
        # Contradiction: Liquidity easing but Risk OFF?
        if liq_state == "EXPANSION" and risk_state == "RISK_OFF":
            return {
                "name": "Liquidity-Risk Disconnect",
                "type": "Liquidity vs Risk",
                "strength": 0.88,
                "confidence": "HIGH",
                "affected_sectors": ["Growth Stocks", "Crypto"],
                "reason": "M2/Liquidity is expanding, yet risk appetite remains suppressed, indicating a structural bottleneck."
            }
        elif liq_state == "NEUTRAL" and risk_state == "RISK_OFF":
             return {
                "name": "Precautionary Risk Aversion",
                "type": "Liquidity vs Risk",
                "strength": 0.62,
                "confidence": "MEDIUM",
                "affected_sectors": ["Broad Market"],
                "reason": "Liquidity is stable but markets are fleeing to safety, suggesting hidden structural stress."
            }
        return None

    def _detect_narrative_vs_data(self, narratives):
        # Find high narrative vs low data confirmation topics
        topics = narratives.get("topics", [])
        for t in topics:
            # Low cross-axis count but high final score?
            if t.get("final_narrative_score", 0) > 75 and t.get("cross_axis_count", 0) <= 2:
                return {
                    "name": f"Speculative Bubble: {t.get('title')[:30]}...",
                    "type": "Narrative vs Data",
                    "strength": 0.82,
                    "confidence": "MEDIUM",
                    "affected_sectors": t.get("causal_chain", {}).get("affected_sector", "Various"),
                    "reason": "Narrative score is pushed by sentiment despite low structural axis confirmation (Cross-axis < 3)."
                }
        return None

if __name__ == "__main__":
    # For local test
    import sys
    root = Path(__file__).parent.parent.parent
    engine = MarketContradictionEngine(root)
    engine.run_all()
