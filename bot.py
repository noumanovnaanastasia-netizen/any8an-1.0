import os
import time
import threading
import urllib.request
import telebot
from telebot import types
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
SUB_URL = "https://githubusercontent.com"


bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Я не сплю! Бот работает."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Встроенный будильник каждые 7 минут
def keep_alive():
    # Render сам подставляет адрес твоего сервиса в эту переменную
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    while True:
        time.sleep(420)  # Ждем ровно 7 минут (420 секунд)
        if app_url:
            try:
                urllib.request.urlopen(app_url, timeout=10)
            except Exception:
                pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Получить VPN подписку")
    btn2 = types.KeyboardButton("📱 Как подключить?")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "Привет! Нажми кнопку ниже, чтобы получить свою личную подписку.\n"
        "Внутри 5 лучших обычных серверов и 5 серверов для обхода белых списков. Они обновляются сами каждый час!",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🚀 Получить VPN подписку")
def send_sub(message):
    bot.send_message(
        message.chat.id,
        f"Вот твоя ссылка на подписку (нажми на неё, чтобы скопировать):\n\n`{SUB_URL}`\n\n"
        "Просто вставь её в приложение Hiddify или v2rayNG.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text == "📱 Как подключить?")
def send_help(message):
    bot.send_message(
        message.chat.id,
        "1. Скачай бесплатное приложение **Hiddify** (есть на iPhone, Android и ПК) или **v2rayNG**.\n"
        "2. Скопируй ссылку из кнопки «Получить VPN подписку».\n"
        "3. В приложении нажми **+** (Добавить) -> **Добавить из буфера обмена**.\n"
        "4. Нажми большую кнопку подключения в центре экрана!",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.infinity_polling()
