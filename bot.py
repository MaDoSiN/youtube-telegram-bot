import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler

TOKEN = os.environ.get("TOKEN", "")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context):
    update.message.reply_text("✅ ربات Railway فعال است!")

def main():
    if not TOKEN:
        print("❌ توکن وجود ندارد!")
        return
    
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    
    print("🤖 ربات Railway فعال شد...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
