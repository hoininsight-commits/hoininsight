
import os
import asyncio
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# 보안을 위해 특정 사용자(본인) 및 지정된 방의 메시지만 처리
ALLOWED_CHAT_IDS = [
    os.environ.get("TELEGRAM_CHAT_ID"),
    "-5108828037" # Hoin Dev 방 추가
]

class TelegramCommandAgent:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.allowed_ids = [str(i) for i in ALLOWED_CHAT_IDS if i]
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """인사 및 사용법 안내"""
        chat = update.effective_chat
        print(f"[TelegramAgent] 수신 메시지 - 방: {chat.title or '개인'} | ID: {chat.id}")
        
        if self.allowed_ids and str(chat.id) not in self.allowed_ids:
            return

        welcome_text = """
🎯 *HOIN Insight Command Center* 🤖
사용자님의 지시를 기다리고 있습니다.

*주요 명령어:*
/hunt - 오늘의 지능형 10대 토픽 사냥 즉시 시작
/memo [내용] - 다음 세션을 위한 인수인계 메모 (Chronicle 기록)
/status - 시스템 가동 상태 확인
/help - 도움말 보기
        """
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def hunt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """지능형 토픽 사냥 실행"""
        chat_id = str(update.effective_chat.id)
        print(f"[TelegramAgent] hunt 명령 수신 - ID: {chat_id}")
        if self.allowed_ids and chat_id not in self.allowed_ids: return
        
        await update.message.reply_text("🏹 *사냥을 시작합니다.* (제미나이 기반 10대 토픽 추출 중...)")
        
        try:
            # 외부 프로세스로 사냥 실행 (SentimentAgent 실행)
            cmd = "source venv/bin/activate && python -c 'from src.agents.collector import CollectorAgent; from src.agents.collectors.sentiment_agent import SentimentAgent; c=CollectorAgent(); s=SentimentAgent(c.output_dir); s.run()'"
            process = subprocess.Popen(cmd, shell=True, executable="/bin/zsh", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                await update.message.reply_text("✅ *사냥 완료!* 최신 10대 토픽이 추출되어 캐시에 저장되었습니다.")
            else:
                await update.message.reply_text(f"❌ *사냥 실패:* {stderr.decode()[-200:]}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ *오류 발생:* {str(e)}")

    async def memo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """CHRONICLE.md에 메모 남기기"""
        chat_id = str(update.effective_chat.id)
        print(f"[TelegramAgent] memo 명령 수신 - ID: {chat_id}")
        if self.allowed_ids and chat_id not in self.allowed_ids: return
        
        content = " ".join(context.args)
        if not content:
            await update.message.reply_text("📝 메모 내용을 입력해주세요. 예: `/memo DART API 키 확인해줘`")
            return

        try:
            chronicle_path = "docs/CHRONICLE.md"
            with open(chronicle_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n- 📩 [Telegram Memo] ({timestamp}): {content}\n")
            
            await update.message.reply_text(f"📑 *메모가 기록되었습니다.* 다음 세션에서 제가 확인하겠습니다.")
        except Exception as e:
            await update.message.reply_text(f"❌ *메모 기록 실패:* {str(e)}")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """시스템 상태 보고"""
        chat_id = str(update.effective_chat.id)
        print(f"[TelegramAgent] status 명령 수신 - ID: {chat_id}")
        if self.allowed_ids and chat_id not in self.allowed_ids: return
        
        status_text = f"""
📊 *System Status*
- Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- AI Model: Gemini-2.5-Flash (Tier 3)
- Command Agent: Online 🟢 (Chat: {update.effective_chat.title or 'Private'})
        """
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """자연어 지시 처리 (즉각 응답 후 실행)"""
        chat = update.effective_chat
        if self.allowed_ids and str(chat.id) not in self.allowed_ids: return
        
        user_text = update.message.text
        print(f"[TelegramAgent] 자연어 지시 수신: {user_text}")

        # 의도 파악 및 즉각 응답
        if any(k in user_text for k in ["사냥", "토픽", "수집", "파이프라인", "잡아"]):
            await update.message.reply_text(f"🫡 *지시 수신:* 파이프라인 가동(사냥)을 요청하셨군요. 즉시 시작합니다!")
            await self.hunt(update, context)
        elif any(k in user_text for k in ["메모", "기록", "기억"]):
            memo_content = user_text.replace("메모", "").replace("해줘", "").replace("기록", "").strip()
            await update.message.reply_text(f"📝 *지시 수신:* 다음 세션을 위해 '{memo_content[:20]}...' 내용을 기록하겠습니다.")
            context.args = [memo_content] if memo_content else ["(내용 없음)"]
            await self.memo(update, context)
        elif any(k in user_text for k in ["상태", "보고", "체크"]):
            await update.message.reply_text("📊 *지시 수신:* 현재 시스템 가동 상태를 점검하여 보고해 드리겠습니다.")
            await self.status(update, context)
        else:
            await update.message.reply_text("🤔 사용자님의 말씀을 분석 중입니다. 사냥, 메모, 상태 확인 중 어떤 것을 도와드릴까요?")

    def run(self):
        """에이전트 가동"""
        print("[TelegramAgent] 텔레그램 명령 센터 가동 시작...")
        app = ApplicationBuilder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("hunt", self.hunt))
        app.add_handler(CommandHandler("memo", self.memo))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("help", self.start))
        
        # 자연어 메시지 핸들러 (명령어가 아닌 일반 텍스트 처리)
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        app.run_polling()

if __name__ == "__main__":
    agent = TelegramCommandAgent()
    agent.run()
