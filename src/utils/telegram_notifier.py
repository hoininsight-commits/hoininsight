
import os
import requests
import json
import re
from typing import Optional

class TelegramNotifier:
    """
    Simple Telegram Notification Utility.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
    """
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None, target: Optional[str] = None):
        from dotenv import load_dotenv
        load_dotenv()
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        
        # [v19.0] 다중 채널 지원: target이 지정되면 해당 접미사가 붙은 환경변수를 찾음
        if target:
            env_key = f"TELEGRAM_CHAT_ID_{target.upper()}"
            self.chat_id = chat_id or os.environ.get(env_key) or os.environ.get("TELEGRAM_CHAT_ID")
        else:
            self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
            
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def _sanitize_for_html(self, text: str) -> str:
        """마크다운 형식을 텔레그램용 HTML로 변환 및 특수문자 이스케이프"""
        if not text: return ""
        
        # 1. 기본 HTML 특수문자 치환 (중요)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # 2. 마크다운 헤더 (# Header) -> 볼드 처리
        text = re.sub(r'^#+\s*(.*)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # 3. 마크다운 볼드 (**Bold** or __Bold__) -> <b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
        
        # 4. 마크다운 이탤릭 (*Italic* or _Italic_) -> <i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
        
        return text

    def send_message(self, message: str, parse_mode: Optional[str] = "HTML") -> bool:
        if not self.token or not self.chat_id:
            print("[Telegram] Skipping notification (Token or Chat ID missing)")
            return False

        # HTML 모드일 경우 마크다운 기법들을 HTML 태그로 변환
        if parse_mode == "HTML":
            message = self._sanitize_for_html(message)

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "disable_web_page_preview": True
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode
                
            response = requests.post(url, json=payload, timeout=10)
            
            # [RETRY LOGIC] 만약 마크다운 파싱 에러(400) 발생 시, 일반 텍스트로 재시도
            if response.status_code != 200 and parse_mode:
                print(f"  ⚠️ [Telegram] Markdown parsing failed. Retrying as plain text...")
                payload.pop("parse_mode")
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

    def send_message_in_chunks(self, text: str, parse_mode: str = "HTML") -> bool:
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
