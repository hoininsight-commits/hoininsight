import os
import sys
from datetime import datetime
from src.utils.telegram_notifier import TelegramNotifier

def test_telegram():
    print("--- Telegram Connection Test ---")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing in environment.")
        sys.exit(1)
    
    print(f"Target Chat ID: {chat_id}")
    
    notifier = TelegramNotifier()
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🚀 *HOIN Insight 연결 테스트*\n\n날짜: {today}\n상태: 정상 작동 중\n발신자: Antigravity Bot"
    
    success = notifier.send_message(message)
    if success:
        print("Success: Message sent to Telegram.")
    else:
        print("Failure: Failed to send message. Check Bot Token or Chat ID.")

if __name__ == "__main__":
    test_telegram()
