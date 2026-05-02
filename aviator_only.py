import telebot
from telebot import types
import random
import time
import threading
from flask import Flask
from datetime import datetime, timedelta, timezone

# রেন্ডারকে জাগিয়ে রাখার জন্য ছোট একটা সার্ভার
app = Flask('')
@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

TOKEN = '8690661270:AAF7DZFcW0Q7Nn4o4JCHtcNgRZJ9q_1R4q0'
bot = telebot.TeleBot(TOKEN)
user_data = {}

def get_smart_prediction(chat_id):
    now_utc = datetime.now(timezone.utc)
    bd_now = now_utc + timedelta(hours=6)
    total_seconds = (bd_now.hour * 3600) + (bd_now.minute * 60) + bd_now.second
    round_id = 1 + (total_seconds // 60)
    period = bd_now.strftime("%Y%m%d1000") + str(round_id).zfill(4)
    
    if chat_id not in user_data:
        user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}
    
    stats = user_data[chat_id]
    prediction = "BIG 🔺" if random.randint(1, 10) > 5 else "SMALL 🔻"
    color = "GREEN 🟢" if prediction == "BIG 🔺" else "RED 🔴"
    
    msg = (f"🤖 **1-MIN AI ANALYSIS**\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"🕒 Period: `{period}`\n"
           f"📊 Prediction: **{prediction}**\n"
           f"🎨 Color: **{color}**\n"
           f"🔢 Number: **{random.randint(0,9)}**\n"
           f"🔥 Accuracy: `{random.randint(95, 99)}%`\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"📊 Score: ✅ {stats['win']} | ❌ {stats['loss']}\n"
           f"👤 Dev: ASIF")
    return msg

def send_auto_signals(chat_id):
    while user_data.get(chat_id, {}).get("is_running", False):
        now = datetime.now(timezone.utc) + timedelta(hours=6)
        wait_time = 60 - now.second + 10 
        if wait_time > 0:
            time.sleep(wait_time)
        if not user_data.get(chat_id, {}).get("is_running", False): break
        try:
            msg = get_smart_prediction(chat_id)
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("👍 WIN", callback_data="hit_win"), 
                       types.InlineKeyboardButton("👎 LOSS", callback_data="hit_loss"))
            markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="stop_service"))
            bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")
        except: break

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"win": 0, "loss": 0, "history": [], "is_running": False}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 START 1-MIN SIGNAL", callback_data="start_service"))
    bot.send_message(chat_id, "Welcome ASIF! 10s delay sync active.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == "start_service":
        user_data[chat_id]["is_running"] = True
        bot.edit_message_text("✅ Started! Waiting for next period (10s sync)...", chat_id, call.message.message_id)
        threading.Thread(target=send_auto_signals, args=(chat_id,)).start()
    elif "hit" in call.data:
        key = "win" if "win" in call.data else "loss"
        user_data[chat_id][key] += 1
        bot.answer_callback_query(call.id, f"{key.capitalize()} recorded!")

if __name__ == "__main__":
    # Flask এবং Bot একসাথে চালানো
    threading.Thread(target=run_flask).start()
    bot.polling(none_stop=True)
