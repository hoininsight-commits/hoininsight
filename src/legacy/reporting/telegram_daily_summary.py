
import json
import os
from datetime import datetime
from pathlib import Path
from src.utils.telegram_notifier import TelegramNotifier

def generate_and_send_summary(base_dir: Path):
    """
    Reads today's health.json and sends a summary via Telegram.
    """
    ymd = datetime.now().strftime("%Y/%m/%d")
    health_path = base_dir / "data" / "reports" / ymd / "health.json"
    
    if not health_path.exists():
        print(f"[TelegramReport] No health report found for {ymd}")
        return

    try:
        data = json.loads(health_path.read_text(encoding='utf-8'))
        
        # Build Message
        status_emoji = "✅" if data.get("status") == "SUCCESS" else "⚠️"
        lines = [
            f"🤖 *HOIN ENGINE 일일 리포트* ({ymd})",
            f"시스템 상태: {status_emoji} *{data.get('status')}*",
            "",
            "📊 *데이터 수집 모듈 상태:*"
        ]
        
        # Format per-dataset status
        for item in data.get("per_dataset", []):
            ds_id = item.get("dataset_id", "unknown").replace("_", " ").title()
            # Shorten names for readability
            if "Stooq" in ds_id: ds_id = ds_id.replace("Stooq", "").strip()
            if "Yfinance" in ds_id: ds_id = ds_id.replace("Yfinance", "").strip()
            
            st = item.get("status", "UNKNOWN")
            icon = "✅" if st == "OK" else ("⏭️" if st == "SKIPPED" else "❌")
            
            lines.append(f"{icon} {ds_id}: `{st}`")
            
        lines.append("")
        lines.append("🔗 [대시보드 바로가기](https://hoininsight-commits.github.io/hoininsight/)")
        
        message = "\n".join(lines)
        
        # Send
        notifier = TelegramNotifier()
        notifier.send_message(message)
        
    except Exception as e:
        print(f"[TelegramReport] Error generating report: {e}")

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent
    generate_and_send_summary(base_path)
