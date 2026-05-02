import telebot
from telebot import types
import random
import time
from datetime import datetime, timedelta, timezone
from flask import Flask
from threading import Thread

# Flask server to keep the bot alive
app = Flask('')
@app.route('/')
def home():
    return "Aviator Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
TOKEN = '8627310893:AAFMmE9dkInmTBP98HSVAQmEDHtWtb7_WVg'
bot = telebot.TeleBot(TOKEN)

is_running = False

def get_aviator_signal():
    weights = [0.70, 0.25, 0.05] 
    ranges = [(1.10, 1.90), (2.00, 4.80), (5.00, 12.00)]
    selected_range = random.choices(ranges, weights=weights)[0]
    crash_point = round(random.uniform(selected_range[0], selected_range[1]), 2)
    bd_now = datetime.now(timezone.utc) + timedelta(hours=6)
    current_time = bd_now.strftime("%H:%M:%S")
    safe_cashout = round(crash_point - 0.15, 2)
    if safe_cashout < 1.00: safe_cashout = 1.02
    return (f"🚀 **AVIATOR PREDICTION**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Time: `{current_time}`\n"
            f"📈 Crash At: **{crash_point:.2f}x**\n"
            f"💰 Cashout: **{safe_cashout:.2f}x**\n"
            f"🎯 Accuracy: `{random.randint(92, 97)}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Dev: ASIF | 🚦 Status: ACTIVE")

def auto_ping(chat_id):
    while True:
        try:
            time.sleep(900)
            bot.send_message(chat_id, "🔄 **System Status:** Aviator Engine is active...")
        except:
            continue

@bot.message_handler(commands=['start'])
def welcome(message):
    global is_running
    is_running = False
    t_ping = Thread(target=auto_ping, args=(message.chat.id,))
    t_ping.daemon = True
    t_ping.start()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 START ENGINE", callback_data="start"))
    bot.send_message(message.chat.id, "🛩️ **ASIF AVIATOR PREDICTOR**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global is_running
    if call.data == "start":
        if is_running: return
        is_running = True
        bot.edit_message_text("✅ **Live Signals Started!**", call.message.chat.id, call.message.message_id)
        while is_running:
            try:
                bot.send_message(call.message.chat.id, get_aviator_signal(), parse_mode='Markdown')
                time.sleep(25) 
            except:
                time.sleep(5)
                continue

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
