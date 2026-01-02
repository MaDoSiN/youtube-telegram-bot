import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

TOKEN = os.environ.get("8537394978:AAFv51qNimsibcKVvk69r_-lMoOqWrjrCv8", "")
CHANNEL_LINK = "https://t.me/MaDoSiNPlus"
CHANNEL_USERNAME = "@MaDoSiNPlus"
BOT_USERNAME = "@MadoSiNYouTube_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"سلام {user.first_name} عزیز!\n\nربات دانلودر یوتیوب خوش اومدی!\n\nبرای استفاده از ربات، حتماً باید عضو کانال زیر بشی:\n{CHANNEL_LINK}\n\nبعد از جوین، دوباره /start رو بفرست."
    keyboard = [[InlineKeyboardButton("عضویت در کانال", url=CHANNEL_LINK)],[InlineKeyboardButton("عضو شدم", callback_data="check_join")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text("✅ عالی! حالا لینک یوتیوب خودت رو برام بفرست.\n\n📥 لینک رو می‌تونی از اشتراک‌گذاری ویدیو کپی کنی.")
        else:
            await query.edit_message_text(f"❌ هنوز عضو کانال نشدی!\n\nلطفاً اول در {CHANNEL_LINK} عضو بشو.")
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در بررسی عضویت: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text(f"❌ برای استفاده باید عضو کانال بشی!\n{CHANNEL_LINK}")
            return
    except:
        await update.message.reply_text("❌ خطا در بررسی عضویت.")
        return
    user_data[user_id] = url
    keyboard = [[InlineKeyboardButton("🎵 MP3 (صوت)", callback_data="format_mp3"),InlineKeyboardButton("🎬 720p", callback_data="format_720")],[InlineKeyboardButton("🎬 1080p", callback_data="format_1080"),InlineKeyboardButton("📥 بهترین کیفیت", callback_data="format_best")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 لینک دریافت شد!\n\n🔻 حالا کیفیت مورد نظرت رو انتخاب کن:", reply_markup=reply_markup)

async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    url = user_data.get(user_id)
    if not url:
        await query.edit_message_text("❌ لینک یافت نشد! دوباره لینک رو بفرست.")
        return
    quality_map = {
        "format_mp3": {"format": "bestaudio[ext=m4a]", "ext": "mp3", "name": "MP3 (صوت)"},
        "format_720": {"format": "best[height<=720]", "ext": "mp4", "name": "720p"},
        "format_1080": {"format": "best[height<=1080]", "ext": "mp4", "name": "1080p"},
        "format_best": {"format": "best", "ext": "mp4", "name": "بهترین کیفیت"}
    }
    selected = quality_map.get(query.data)
    if not selected:
        await query.edit_message_text("❌ گزینه نامعتبر!")
        return
    await query.edit_message_text(f"⏳ در حال دانلود {selected['name']}...\nلطفاً صبر کن!")
    try:
        ydl_opts = {'format': selected['format'], 'outtmpl': 'video.%(ext)s', 'quiet': True}
        if selected['ext'] == 'mp3':
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = 'video.mp4' if selected['ext'] != 'mp3' else 'video.mp3'
            if os.path.exists(file_path):
                caption = f"✅ دانلود شده توسط {BOT_USERNAME}"
                if selected['ext'] == 'mp3':
                    await context.bot.send_audio(chat_id=user_id, audio=open(file_path, 'rb'), caption=caption)
                else:
                    await context.bot.send_video(chat_id=user_id, video=open(file_path, 'rb'), caption=caption)
                os.remove(file_path)
                await query.message.reply_text("✅ دانلود با موفقیت انجام شد!\n\n📥 لینک جدید بفرست یا /start")
            else:
                await query.message.reply_text("❌ خطا در پیدا کردن فایل دانلود شده!")
    except Exception as e:
        await query.message.reply_text(f"❌ خطا:\n{str(e)}")

def main():
    if not TOKEN:
        logger.error("❌ توکن تنظیم نشده! لطفاً متغیر محیطی TOKEN را تنظیم کن.")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(handle_quality, pattern="^format_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 ربات فعال شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
