import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# توکن از محیط میاد (در Render تنظیم می‌کنی)
TOKEN = os.environ.get("TOKEN", "")
CHANNEL_LINK = "https://t.me/MaDoSiNPlus"
CHANNEL_USERNAME = "@MaDoSiNPlus"
BOT_USERNAME = "@MadoSiNYouTube_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
user_data = {}

# =================== دستور /start ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
✨ **سلام {user.first_name} عزیز!** ✨

🎬 **ربات دانلودر یوتیوب** خوش اومدی!

🔔 **برای استفاده از ربات، حتماً باید عضو کانال زیر بشی:**
{CHANNEL_LINK}

✅ بعد از جوین، دوباره /start رو بفرست.
    """
    keyboard = [
        [InlineKeyboardButton("🔗 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# =================== چک کردن عضویت ===================
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text(
                "✅ **عالی! حالا لینک یوتیوب خودت رو برام بفرست.**\n\n"
                "📥 لینک رو می‌تونی از اشتراک‌گذاری ویدیو کپی کنی.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **هنوز عضو کانال نشدی!**\n\n"
                f"لطفاً اول در {CHANNEL_LINK} عضو بشو.",
                parse_mode='Markdown'
            )
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در بررسی عضویت: {e}")

# =================== دریافت لینک یوتیوب ===================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id
    
    # چک عضویت
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                f"❌ **برای استفاده باید عضو کانال بشی!**\n{CHANNEL_LINK}"
            )
            return
    except Exception as e:
        await update.message.reply_text("❌ خطا در بررسی عضویت.")
        return
    
    # ذخیره لینک
    user_data[user_id] = url
    
    # دکمه‌های کیفیت
    keyboard = [
        [
            InlineKeyboardButton("🎵 MP3 (صوت)", callback_data="format_mp3"),
            InlineKeyboardButton("🎬 720p", callback_data="format_720"),
        ],
        [
            InlineKeyboardButton("🎬 1080p", callback_data="format_1080"),
            InlineKeyboardButton("📥 بهترین کیفیت", callback_data="format_best"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **لینک دریافت شد!**\n\n"
        "🔻 حالا کیفیت مورد نظرت رو انتخاب کن:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# =================== پردازش انتخاب کیفیت ===================
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
    
    await query.edit_message_text(f"⏳ **در حال دانلود {selected['name']}...**\nلطفاً صبر کن!", parse_mode='Markdown')
    
    try:
        # تنظیمات yt-dlp
        ydl_opts = {
            'format': selected['format'],
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        if selected['ext'] == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        # دانلود
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = 'video.mp4' if selected['ext'] != 'mp3' else 'video.mp3'
            
            if os.path.exists(file_path):
                caption = f"✅ **دانلود شده توسط {BOT_USERNAME}**"
                
                # ارسال فایل
                if selected['ext'] == 'mp3':
                    await context.bot.send_audio(
                        chat_id=user_id,
                        audio=open(file_path, 'rb'),
                        caption=caption,
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=open(file_path, 'rb'),
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                # حذف فایل موقت
                os.remove(file_path)
                await query.message.reply_text(
                    "✅ **دانلود با موفقیت انجام شد!**\n\n"
                    "📥 لینک جدید بفرست یا /start",
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_text("❌ خطا در پیدا کردن فایل دانلود شده!")
    
    except Exception as e:
        await query.message.reply_text(f"❌ **خطا:**\n`{str(e)}`", parse_mode='Markdown')

# =================== تابع اصلی ===================
def main():
    if not TOKEN:
        logger.error("❌ توکن تنظیم نشده! لطفاً متغیر محیطی TOKEN را در Render تنظیم کنید.")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(handle_quality, pattern="^format_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 ربات فعال شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
