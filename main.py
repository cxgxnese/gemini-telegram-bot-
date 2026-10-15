import os
import telebot
from flask import Flask, request
from google import genai

TG_TOKEN = os.environ.get("TG_TOKEN", "8622991408:AAG8WvGCAD5lp_FaZfwpgBl7E0jKf2SMlGU")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyAooFtGvodf8fjDZ9Itke_mlHabaaM7Cnw")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TG_TOKEN)
ai_client = genai.Client(api_key=GEMINI_KEY)
app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    bot.reply_to(message, "Привет! Я твой личный ИИ-помощник на базе Gemini. Задай мне любой вопрос :)")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@app.route('/' + TG_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    if RENDER_EXTERNAL_URL:
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TG_TOKEN}")
        return "Webhook установлен!", 200
    return "Сервер работает!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)