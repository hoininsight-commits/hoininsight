
import os
import requests
import json
from typing import Optional

class TelegramNotifier:
    """
    Simple Telegram Notification Utility.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
    """
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, message: str) -> bool:
        if not self.token or not self.chat_id:
            print("[Telegram] Skipping notification (Token or Chat ID missing)")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("[Telegram] Message sent successfully")
                return True
            else:
                print(f"[Telegram] Failed to send: {response.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Error: {e}")
            return False
