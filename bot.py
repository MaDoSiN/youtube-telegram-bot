import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("TOKEN", "8537394978:AAFv51qNimsibcKVvk69r_-lMoOqWrjrCv8")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context):
    await update.message.reply_text("✅ ربات فعال است!")

def main():
    if not TOKEN:
        print("❌ توکن وجود ندارد!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("🤖 ربات فعال شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
