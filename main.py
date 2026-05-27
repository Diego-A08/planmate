import telebot
import json
import os
from flask import Flask, request
import threading
from checkin import start_checkin, process_mood, process_goals, daily_checkin_thread

# ============================
#   CONFIGURACIÓN DEL BOT
# ============================

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

WEBHOOK_URL = "https://planmate-zwen.onrender.com/webhook"

app = Flask(__name__)

# ============================
#   MEMORIA BÁSICA DEL USUARIO
# ============================

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

memory = load_memory()

def get_user_memory(user_id):
    user_id = str(user_id)
    if user_id not in memory:
        memory[user_id] = {"tone": "equilibrado"}
        save_memory(memory)
    return memory[user_id]

# ==============================
# COMANDO /checkin
# ==============================
@bot.message_handler(commands=['checkin'])
def manual_checkin(message):
    chat_id = message.chat.id
    start_checkin(bot, chat_id)

# ============================
#   COMANDO /start
# ============================

@bot.message_handler(commands=["start"])
def start(message):
    print("CHAT_ID:", message.chat.id)
    user_id = message.from_user.id
    get_user_memory(user_id)

    welcome = (
        "Soy PlanMate. Estoy aquí para ayudarte a organizar tu vida.\n\n"
        "Antes de empezar, dime: ¿cómo te gusta que te hable?\n"
        "1) Directo\n"
        "2) Serio\n"
        "3) Suave\n"
        "4) Equilibrado"
    )

    bot.send_message(message.chat.id, welcome)

# ============================
#   MANEJAR TONO
# ============================

@bot.message_handler(func=lambda m: m.text in ["1", "2", "3", "4"])
def set_tone(message):
    user_id = str(message.from_user.id)
    tones = {
        "1": "directo",
        "2": "serio",
        "3": "suave",
        "4": "equilibrado"
    }

    memory[user_id]["tone"] = tones[message.text]
    save_memory(memory)

    bot.send_message(message.chat.id, "Perfecto. Ajusto mi tono. Vamos a empezar.")

# ==============================
# MANEJAR RESPUESTAS DEL CHECK-IN
# ==============================
@bot.message_handler(func=lambda msg: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text.lower()

    # Procesar estado de ánimo
    if text in ["bien", "normal", "mal"]:
        process_mood(bot, chat_id, text)
        return

    # Procesar objetivos (si el usuario escribe una frase con 2+ palabras)
    if len(text.split()) >= 2:
        process_goals(bot, chat_id, text)
        return

    # Respuesta por defecto
    bot.send_message(chat_id, "No entendí eso, Diego-Alexander. Usa /checkin para empezar tu rutina.")

# ============================
#   RESPUESTA GENERAL
# ============================

@bot.message_handler(func=lambda m: True)
def general_response(message):
    user_id = str(message.from_user.id)
    user_data = get_user_memory(user_id)
    tone = user_data["tone"]

    responses = {
        "directo": "Dime qué necesitas y vamos al grano.",
        "serio": "Estoy listo para ayudarte. ¿Qué necesitas?",
        "suave": "Aquí estoy para ayudarte con calma. ¿Qué te gustaría hacer?",
        "equilibrado": "Perfecto, ¿en qué puedo ayudarte hoy?"
    }

    bot.send_message(message.chat.id, responses[tone])

# ============================
#   WEBHOOK
# ============================

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "PlanMate está activo con webhook.", 200

# ============================
#   INICIAR WEBHOOK
# ============================

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=10000)
