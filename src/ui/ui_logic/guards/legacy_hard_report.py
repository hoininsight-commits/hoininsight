import json
import os
from pathlib import Path
from datetime import datetime

BLOCK_LEDGER_PATH = "data_outputs/ops/legacy_block_ledger.json"
ALLOWLIST_PATH = "registry/ops/legacy_allowlist_v1.yml"
READINESS_REPORT_PATH = "docs/ops/LEGACY_HARD_READINESS.md"

def generate_readiness_report(project_root: Path = None):
    """Generates the Hard Readiness report based on ledger and allowlist."""
    if project_root is None:
        project_root = Path(os.getcwd())
        
    ledger_path = project_root / BLOCK_LEDGER_PATH
    allowlist_path = project_root / ALLOWLIST_PATH
    report_path = project_root / READINESS_REPORT_PATH
    
    if not ledger_path.exists():
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    # Load allowlist briefly to show status
    import yaml
    try:
        with open(allowlist_path, "r", encoding="utf-8") as f:
            allowlist = yaml.safe_load(f) or {"allow": []}
    except Exception:
        allowlist = {"allow": []}

    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    
    lines = [
        "# Legacy Hard Readiness Report (REF-008)",
        f"\n**Status Date**: {ledger.get('date', 'N/A')}",
        f"**Hard Mode Active**: {ledger.get('hard_mode', False)}",
        "\n## Active Allowlist (Current Safety Net)",
    ]
    
    for entry in allowlist.get("allow", []):
        expires_str = entry.get("expires", "N/A")
        try:
            exp_dt = datetime.strptime(expires_str, "%Y-%m-%d")
            days_left = (exp_dt - now).days
            status = f"({days_left} days left)" if days_left >= 0 else "EXPIRED"
        except Exception:
            status = ""
            
        lines.append(f"- `{entry.get('module')}`: {entry.get('reason')} **{expires_str}** {status}")

    lines.append("\n## Top Blocked Attempts (Failed in Test/CI)")
    blocked = ledger.get("blocked", [])
    if not blocked:
        lines.append("- No blocked attempts recorded. ✅")
    else:
        # Simple count and unique
        counts = {}
        for b in blocked:
            counts[b['module']] = counts.get(b['module'], 0) + 1
        
        sorted_blocked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for mod, count in sorted_blocked:
            lines.append(f"- `{mod}`: **{count}** blocks")

    lines.append("\n---")
    lines.append("> [!IMPORTANT]")
    lines.append("> 이 리포트는 `HOIN_LEGACY_HARD=1` 환경에서 실행된 결과를 기반으로 작성됩니다.")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"[HardGate] Readiness report generated at {READINESS_REPORT_PATH}")

if __name__ == "__main__":
    generate_readiness_report()
