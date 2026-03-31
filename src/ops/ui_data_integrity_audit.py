import json
from pathlib import Path
from datetime import datetime

class UIDataIntegrityAudit:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.report_path = self.project_root / "data" / "ops" / "ui_data_integrity_report.json"

    def validate_top3(self, impact_chain, ui_top_stocks):
        """
        Validates that the top 3 stocks in the impact chain match the UI contract.
        """
        errors = []
        # Check if both lists are long enough
        if len(impact_chain) < 3:
            errors.append(f"Impact chain size ({len(impact_chain)}) is less than 3.")
        if len(ui_top_stocks) < 3:
            errors.append(f"UI top stocks size ({len(ui_top_stocks)}) is less than 3.")
            
        if errors:
            return errors

        for i in range(3):
            ic = impact_chain[i]
            ui = ui_top_stocks[i]

            # 1. Ticker Check
            ic_ticker = ic.get("ticker")
            ui_ticker = ui.get("ticker")
            if ic_ticker != ui_ticker:
                errors.append(f"Rank {i+1} Ticker mismatch: Engine({ic_ticker}) != UI({ui_ticker})")

            # 2. Industry Check
            ic_industry = ic.get("industry_link")
            ui_industry = ui.get("industry")
            if ic_industry != ui_industry:
                errors.append(f"Rank {i+1} Industry mismatch for {ic_ticker}: Engine({ic_industry}) != UI({ui_industry})")

            # 3. Directness Check
            ic_directness = ic.get("directness")
            ui_directness = ui.get("directness")
            if ic_directness != ui_directness:
                errors.append(f"Rank {i+1} Directness mismatch for {ic_ticker}: Engine({ic_directness}) != UI({ui_directness})")

        return errors

    def run_integrity_check(self, impact_chain, brief):
        """
        Runs the full integrity audit against the today_operator_brief.
        """
        ui_today = brief.get("ui_today", {})
        ui_top_stocks = ui_today.get("top_stocks", [])
        
        # Also check top-level ui_top_stocks if present
        alt_ui_top_stocks = brief.get("ui_top_stocks", [])
        
        errors = self.validate_top3(impact_chain, ui_top_stocks)
        
        # Structural theme check
        ic_theme_type = impact_chain[0].get("theme_type", "UNKNOWN") if impact_chain else "UNKNOWN"
        ui_theme_type = ui_today.get("theme_type")
        if ic_theme_type != ui_theme_type:
            errors.append(f"Theme Type mismatch: Engine({ic_theme_type}) != UI({ui_theme_type})")

        report = {
            "status": "PASS" if len(errors) == 0 else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "engine_ticker_top1": impact_chain[0].get("ticker") if impact_chain else None,
                "ui_ticker_top1": ui_top_stocks[0].get("ticker") if ui_top_stocks else None,
                "theme_alignment": ic_theme_type == ui_theme_type
            },
            "errors": errors
        }

        # Save report
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Also sync to docs for public URL check
        public_path = self.project_root / "docs" / "data" / "ops" / "ui_data_integrity_report.json"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        with open(public_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

def run_integrity_check(impact_chain, brief, project_root):
    auditor = UIDataIntegrityAudit(project_root)
    return auditor.run_integrity_check(impact_chain, brief)
