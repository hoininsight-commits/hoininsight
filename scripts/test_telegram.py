import os
from pathlib import Path
from src.utils.telegram_notifier import TelegramNotifier

def test_send():
    # 4/30일자 가장 긴 스크립트 하나 선택
    transcript_dir = Path("data/transcripts/youtube/2026/04/30")
    files = list(transcript_dir.glob("*.txt"))
    if not files:
        print("No transcripts found to send.")
        return
    
    target_file = files[0]
    content = target_file.read_text(encoding="utf-8")
    title = target_file.name
    
    msg = f"📺 *[테스트: 유튜브 수집 발송]*\n\n"
    msg += f"📌 *파일명*: {title}\n"
    msg += f"⏰ *회차*: 테스트 전송\n\n"
    msg += f"📜 *스크립트 전문 (일부)*:\n{content[:2000]}..." # 테스트용으로 일부만 전송

    print(f"Sending test message for: {title}")
    
    # [v19.0] 전용 채널 타겟으로 발송 시도
    notifier = TelegramNotifier(target="TRANSCRIPT")
    success = notifier.send_message_in_chunks(msg)
    
    if success:
        print(f"✅ Telegram Test Sent Successfully to Chat ID: {notifier.chat_id}")
    else:
        print("❌ Telegram Test Failed.")

if __name__ == "__main__":
    test_send()
