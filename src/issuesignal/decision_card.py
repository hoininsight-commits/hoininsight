from pathlib import Path
from datetime import datetime

class DecisionCardGenerator:
    """
    (IS-15) Generates a concise Decision Card for 10-second processing.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "data" / "issuesignal" / "decisions"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_card(self, trigger: dict, tickers: list, kill_switches: list) -> Path:
        """
        Synthesizes the final decision card in markdown format.
        """
        # 1. Validation Logic
        if not tickers or not kill_switches or len(tickers) > 3:
            print("[INFO] Decision Card rejected: Incomplete data or too many tickers.")
            return None
            
        # 2. Build Card Content
        issue_id = trigger.get("id", "UNKNOWN")
        content = [
            f"# DECISION CARD: {issue_id}",
            f"**Generated at**: {datetime.now().isoformat()}\n",
            "## 1. WHAT (Trigger)",
            f"- {trigger.get('content', 'No content available')}\n",
            "## 2. WHY (Forced Capital Movement)",
            f"- {trigger.get('why_now', 'No focus identified')}\n",
            "## 3. WHERE (Bottleneck)",
            f"- {trigger.get('ignore_reason', 'No bottleneck identified')}\n",
            "## 4. WHO (1–3 Tickers)",
        ]
        
        for t in tickers:
            role = t.get("role", "OWNER")
            content.append(f"- **{t['ticker']}** ({role}): Derived from {trigger.get('source')} trigger.")
            
        content.append("\n## 5. WHEN (Kill-switch)")
        for ks in kill_switches:
            content.append(f"- **{ks['ticker']}**: {ks['condition']}")
            content.append(f"  *Watch*: {ks['monitoring_signal']}")
            
        # 3. Save to Markdown
        card_content = "\n".join(content)
        file_path = self.output_dir / f"DECISION_{datetime.now().strftime('%Y%m%d')}_{issue_id}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(card_content)
            
        return file_path
