import json
import os
from pathlib import Path

USAGE_DATA_PATH = "data_outputs/ops/legacy_usage.json"
REPORT_PATH = "docs/ops/LEGACY_USAGE_REPORT.md"

def write_report(project_root: Path = None):
    """Generates a human-readable legacy usage report."""
    if project_root is None:
        project_root = Path(os.getcwd())
        
    data_path = project_root / USAGE_DATA_PATH
    report_path = project_root / REPORT_PATH
    
    if not data_path.exists():
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    sorted_modules = sorted(data["modules"].items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_modules[:5]

    lines = [
        "# Legacy Usage Report (REF-007)",
        f"\n**Date**: {data.get('date', 'N/A')}",
        f"**Total Legacy Hits**: {data.get('total_hits', 0)}",
        "\n## Top 5 Migrations Needed (By Hit Count)",
    ]
    
    if not top_5:
        lines.append("- No legacy hits recorded yet. Clean state! ✅")
    else:
        for mod, count in top_5:
            lines.append(f"- `{mod}`: **{count}** hits")

    lines.append("\n---")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    write_report()
