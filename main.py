import telebot
import json
import os

# ============================
#   CARGAR TOKEN DEL BOT
# ============================
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

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

# ============================
#   COMANDO /start
# ============================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    get_user_memory(user_id)

    welcome = (
        "Soy PlanMate. Estoy aquí para ayudarte a organizar tu vida, tu estudio y tu día.\n\n"
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
#   INICIAR BOT
# ============================

print("PlanMate está activo.")
bot.infinity_polling()
