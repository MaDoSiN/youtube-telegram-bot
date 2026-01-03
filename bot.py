import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN", "")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات Railway فعال شد!")

def main():
    if not TOKEN:
        logging.error("❌ توکن وجود ندارد! لطفاً در Railway Variables تنظیم کن.")
        return
    
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        logging.info("🤖 ربات در حال راه‌اندازی...")
        app.run_polling()
    except Exception as e:
        logging.error(f"❌ خطا: {e}")

if __name__ == '__main__':
    main()
