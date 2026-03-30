import json
from pathlib import Path
from datetime import datetime

class RankingIntegrityAudit:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.report_path = self.project_root / "data" / "ops" / "ranking_integrity_report.json"
        self.order_map = {
            "solver_direct": 0,
            "direct": 1,
            "indirect": 2
        }

    def check_solver_priority(self, impact_chain):
        """
        RULE 1: solver_direct must be at the top positions (0-2).
        RULE 4: Top 3 must contain at least one solver_direct.
        """
        solver_positions = [
            i for i, x in enumerate(impact_chain)
            if x.get("directness") == "solver_direct"
        ]

        errors = []
        if not solver_positions:
            errors.append("No solver_direct found in impact_chain")
        else:
            first_solver = solver_positions[0]
            if first_solver > 2:
                errors.append(f"Solver appears too late (position {first_solver}). Must be in Top 3.")
            
            # Additional Rule 4 overlap
            top3 = impact_chain[:3]
            has_solver = any(x.get("directness") == "solver_direct" for x in top3)
            if not has_solver:
                errors.append("Top 3 has no solver_direct (Rules 1 & 4 violated)")

        return errors

    def check_directness_order(self, impact_chain):
        """
        RULE 2: solver_direct (0) < direct (1) < indirect (2).
        """
        errors = []
        for i in range(len(impact_chain) - 1):
            curr_dir = impact_chain[i].get("directness", "indirect")
            next_dir = impact_chain[i+1].get("directness", "indirect")
            
            curr_rank = self.order_map.get(curr_dir, 99)
            next_rank = self.order_map.get(next_dir, 99)

            if curr_rank > next_rank:
                errors.append(
                    f"Directness order broken at index {i}: {curr_dir}({curr_rank}) followed by {next_dir}({next_rank})"
                )

        return errors

    def check_score_sorting(self, impact_chain):
        """
        RULE 3: Within the same directness, selection_score must be descending.
        """
        errors = []
        for i in range(len(impact_chain) - 1):
            curr = impact_chain[i]
            nxt = impact_chain[i+1]
            
            if curr.get("directness") == nxt.get("directness"):
                curr_score = float(curr.get("selection_score", 0))
                nxt_score = float(nxt.get("selection_score", 0))
                
                if curr_score < nxt_score:
                    errors.append(
                        f"Score sorting broken for {curr.get('directness')} at index {i}: {curr_score} < {nxt_score}"
                    )
        return errors

    def run_audit(self, impact_chain):
        """
        Runs all ranking integrity checks.
        """
        errors = []
        if not impact_chain:
            errors.append("Empty impact_chain provided for ranking audit.")
        else:
            errors += self.check_solver_priority(impact_chain)
            errors += self.check_directness_order(impact_chain)
            errors += self.check_score_sorting(impact_chain)

        report = {
            "status": "PASS" if not errors else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_candidates": len(impact_chain),
                "top3_directness": [x.get("directness") for x in impact_chain[:3]],
                "has_solver_top3": any(x.get("directness") == "solver_direct" for x in impact_chain[:3])
            },
            "errors": errors,
            "top3": impact_chain[:3]
        }

        # Save locally
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Sync to docs for server check
        public_path = self.project_root / "docs" / "data" / "ops" / "ranking_integrity_report.json"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        with open(public_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

def run_ranking_integrity(impact_chain, project_root):
    auditor = RankingIntegrityAudit(project_root)
    return auditor.run_audit(impact_chain)
