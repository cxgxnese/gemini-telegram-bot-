import os
from flask import Flask, request
import telebot
import google.generativeai as genai

TG_TOKEN = os.environ.get('TG_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY') or os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TG_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/')
def index():
    webhook_url = f"https://{request.host}/{TG_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return "Webhook установлен!"

@app.route('/' + TG_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Привет! Я бот на базе Gemini. Напиши мне что-нибудь :)")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка Gemini: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
