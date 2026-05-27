import datetime
import threading
import time

# Este diccionario actuará como memoria simple por usuario
user_memory = {}

def get_user_memory(chat_id):
    if chat_id not in user_memory:
        user_memory[chat_id] = {
            "mood_history": [],
            "goals_history": [],
            "last_checkin_date": None
        }
    return user_memory[chat_id]

# -----------------------------
#   CHECK-IN INTELIGENTE
# -----------------------------

def start_checkin(bot, chat_id):
    bot.send_message(chat_id, "Buenos días, Diego-Alexander. Vamos a hacer tu Check-in inteligente.")
    ask_mood(bot, chat_id)

def ask_mood(bot, chat_id):
    bot.send_message(chat_id, "¿Cómo amaneciste hoy? (bien / normal / mal)")

def process_mood(bot, chat_id, mood):
    memory = get_user_memory(chat_id)
    memory["mood_history"].append((str(datetime.date.today()), mood))
    bot.send_message(chat_id, "Perfecto. Ahora dime 1 o 2 cosas importantes que quieras lograr hoy.")
    
def process_goals(bot, chat_id, goals):
    memory = get_user_memory(chat_id)
    memory["goals_history"].append((str(datetime.date.today()), goals))

    analysis = analyze_user(memory)
    suggestions = generate_suggestions(memory)

    bot.send_message(chat_id, analysis)
    bot.send_message(chat_id, suggestions)
    bot.send_message(chat_id, "Listo, Diego-Alexander. Ya tengo tu día organizado. Vamos a por ello.")

def analyze_user(memory):
    mood_history = memory["mood_history"]
    goals_history = memory["goals_history"]

    analysis = "📊 *Análisis del día*\n"

    if len(mood_history) >= 2:
        yesterday = mood_history[-2][1]
        today = mood_history[-1][1]

        if yesterday == "mal" and today == "bien":
            analysis += "Veo que hoy estás mejor que ayer. Buen progreso.\n"
        elif yesterday == "bien" and today == "mal":
            analysis += "Ayer estabas mejor que hoy. Tómatelo con calma.\n"

    if len(goals_history) >= 2:
        prev_goals = goals_history[-2][1]
        analysis += f"Ayer querías lograr: {prev_goals}\n"

    return analysis

def generate_suggestions(memory):
    suggestions = "🧭 *Sugerencias para hoy*\n"

    if memory["mood_history"][-1][1] == "mal":
        suggestions += "- Prioriza tareas ligeras.\n- No te sobrecargues.\n"

    if len(memory["goals_history"]) >= 2:
        prev_goals = memory["goals_history"][-2][1]
        suggestions += f"- Revisa si quieres retomar lo pendiente de ayer: {prev_goals}\n"

    suggestions += "- Mantén el enfoque en 1 o 2 objetivos importantes.\n"

    return suggestions

# -----------------------------
#   CHECK-IN AUTOMÁTICO 7:00
# -----------------------------

def daily_checkin_thread(bot, chat_id):
    while True:
        now = datetime.datetime.now()
        if now.hour == 7 and now.minute == 0:
            start_checkin(bot, chat_id)
            time.sleep(60)  # Evita repetir dentro del mismo minuto
        time.sleep(20)  # Revisa cada 20 segundos
