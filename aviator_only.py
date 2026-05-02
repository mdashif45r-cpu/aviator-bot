import telebot
import random
import time
import threading
from telebot import types

TOKEN = "7729227189:AAG-I_uN3X6r743o4f49I2iN80pW5r38t5Y"
bot = telebot.TeleBot(TOKEN)

is_running = {}

def send_auto_signals(chat_id):
    while is_running.get(chat_id, False):
        prediction = round(random.uniform(1.20, 3.80), 2)
        safe_exit = round(prediction - 0.15, 2)
        
        msg = (
            f"🚀 **GO-RUSH/AVIATOR SIGNAL** 🚀\n\n"
            f"✅ **Next Round:** {prediction}x\n"
            f"⚠️ **Safe Cashout:** {safe_exit}x\n\n"
            f"⌛ Next signal in 15 seconds..."
        )
        
        try:
            bot.send_message(chat_id, msg, parse_mode="Markdown")
        except:
            break
            
        time.sleep(15)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start = types.KeyboardButton("🟢 START SIGNAL")
    btn_stop = types.KeyboardButton("🔴 STOP SIGNAL")
    markup.add(btn_start, btn_stop)
    
    bot.send_message(message.chat.id, "Welcome! Use the buttons below.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🟢 START SIGNAL")
def start_logic(message):
    chat_id = message.chat.id
    if not is_running.get(chat_id, False):
        is_running[chat_id] = True
        bot.send_message(chat_id, "Signal Service: ON ✅")
        threading.Thread(target=send_auto_signals, args=(chat_id,)).start()

@bot.message_handler(func=lambda message: message.text == "🔴 STOP SIGNAL")
def stop_logic(message):
    is_running[message.chat.id] = False
    bot.send_message(message.chat.id, "Signal Service: OFF 🛑")

bot.polling(none_stop=True)
