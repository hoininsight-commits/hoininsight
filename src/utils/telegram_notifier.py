
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
                print(f"[Telegram] Failed to send message: {response.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Message Error: {e}")
            return False

    def send_message_in_chunks(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Sends a long message by splitting it into smaller chunks."""
        MAX_LEN = 4000
        if len(text) <= MAX_LEN:
            return self.send_message(text)

        chunks = []
        while text:
            if len(text) <= MAX_LEN:
                chunks.append(text)
                break
            
            # Try to find the last newline within the limit to avoid breaking lines
            split_idx = text.rfind("\n", 0, MAX_LEN)
            if split_idx == -1:
                split_idx = MAX_LEN
            
            chunks.append(text[:split_idx])
            text = text[split_idx:].lstrip()

        success = True
        for i, chunk in enumerate(chunks):
            # Add index if multiple chunks
            prefix = f"📄 *Part {i+1}/{len(chunks)}*\n\n" if len(chunks) > 1 else ""
            success &= self.send_message(prefix + chunk)
        
        return success

    def send_document(self, file_path: str, caption: Optional[str] = None) -> bool:
        """Sends a file (document) to the chat."""
        if not self.token or not self.chat_id:
            print("[Telegram] Skipping document (Token or Chat ID missing)")
            return False

        if not os.path.exists(file_path):
            print(f"[Telegram] File not found: {file_path}")
            return False

        try:
            url = f"{self.base_url}/sendDocument"
            data = {"chat_id": self.chat_id}
            if caption:
                data["caption"] = caption
                data["parse_mode"] = "Markdown"
            
            with open(file_path, "rb") as f:
                files = {"document": f}
                response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.status_code == 200:
                print(f"[Telegram] Document sent successfully: {os.path.basename(file_path)}")
                return True
            else:
                print(f"[Telegram] Failed to send document: {response.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Document Error: {e}")
            return False
