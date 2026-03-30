import json
from pathlib import Path

class ImpactRootCauseAnalyzer:
    """
    [STEP-H-2] Failure Root Cause Analyzer
    Deconstructs why the Impact Chain failed to align with outcomes.
    """
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.report_path = self.project_root / "data" / "ops" / "impact_root_cause_report.json"

    def run_analysis(self, tracking_data, impact_chain, theme):
        """
        Main entry point for analysis.
        """
        print(f"[RootCause] Analyzing failure for theme: {theme}")
        
        results = []
        for run in tracking_data:
            # Analyze all runs where stocks failed (Outcome Alignment was low)
            if run.get("failure_type") == "THEME_RIGHT_STOCK_WRONG" or run.get("outcome_alignment", 1.0) < 0.5:
                for stock in impact_chain:
                    cause = self.classify_cause(stock, theme)
                    results.append({
                        "ticker": stock.get("ticker", "UNKNOWN"),
                        "theme": theme,
                        "failure_type": run.get("failure_type", "THEME_RIGHT_STOCK_WRONG"),
                        "root_cause": cause,
                        "structural_context": stock.get("structural_context", "N/A")
                    })

        # Deduplicate results by ticker
        unique_results = {r["ticker"]: r for r in results}.values()
        final_results = list(unique_results)

        summary = self.summarize_causes(final_results)
        
        report = {
            "results": final_results,
            "summary": summary
        }

        self.save_report(report)
        return report

    def classify_cause(self, stock, theme):
        """
        Heuristic classification of the root cause.
        """
        industry = stock.get("industry_link", "").lower()
        company_link = stock.get("company_link", "")
        directness = stock.get("directness", "proxy")
        evidence = stock.get("evidence_basis", [])

        # 1. INDUSTRY_MAPPING_ERROR
        # Example: Theme "AI Power Constraint" should link to "Power", "Infrastructure", "Energy"
        if "power" in theme.lower() and not any(k in industry for k in ["power", "infrastructure", "energy", "utilit", "grid"]):
            return "INDUSTRY_MAPPING_ERROR"

        # 2. COMPANY_MAPPING_ERROR
        # Link is too generic or short
        if len(company_link) < 30:
            return "COMPANY_MAPPING_ERROR"

        # 3. DIRECTNESS_MISCLASSIFICATION
        # T-0 stresstests: Big tech enablers are often indirect in 'Constraint' themes
        if directness == "direct" and any(k in industry for k in ["software", "cloud", "saas"]):
            return "DIRECTNESS_MISCLASSIFICATION"

        # 4. EVIDENCE_MISALIGNMENT
        # Lacks density of proof
        if len(evidence) < 3:
            return "EVIDENCE_MISALIGNMENT"

        # 5. TIMING_MISMATCH
        # Stock is correct, but the impact hasn't materialized yet
        return "TIMING_MISMATCH"

    def summarize_causes(self, results):
        summary = {}
        for r in results:
            cause = r["root_cause"]
            summary[cause] = summary.get(cause, 0) + 1
        return summary

    def save_report(self, report):
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[RootCause] Report saved to {self.report_path}")

if __name__ == "__main__":
    # Test stub
    pass
